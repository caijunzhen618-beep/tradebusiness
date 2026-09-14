"""数据采集器实现。

当前支持两类执行路径：
- 已配置真实搜索/目录适配器时，由对应适配器采集。
- 未配置外部搜索服务时，可对用户填写的来源地址做轻量公开页面采集。
"""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from uuid import uuid4

import aiohttp
from bs4 import BeautifulSoup

from app.config import settings
from app.core.logger import get_logger
from app.scrapers.google_search import GoogleSearchScraper
from app.services.website_crawler_service import WebsiteCrawlerService

logger = get_logger(__name__)

MAX_RESPONSE_BYTES = 2 * 1024 * 1024
GOOGLE_TASK_TYPES = {"google", "google_search"}
DIRECTORY_TASK_TYPES = {
    "directory",
    "kompass",
    "yellow_pages",
    "kompass_africa",
    "yellowpages_africa",
}
SPECIFIC_SITE_TASK_TYPES = {"specific_site", "port_authorities"}


class ExampleScraper:
    """采集器门面，统一调度搜索、目录和指定来源地址采集。"""

    DIRECTORY_SEARCH_SITES = {
        "NG": ["businesslist.com.ng", "finelib.com"],
        "KE": ["businesslist.co.ke", "yellowpageskenya.com"],
        "ZA": ["brabys.com", "yellosa.co.za"],
        "GH": ["businessghana.com", "ghanayello.com"],
        "EG": ["egyptyello.com", "yellowpages.com.eg"],
    }
    SOURCE_SEARCH_SITES = {
        "kompass": ["kompass.com"],
        "kompass_africa": ["kompass.com"],
        "yellow_pages": [
            "businesslist.com.ng",
            "businesslist.co.ke",
            "yellowpageskenya.com",
            "yellowpages.com.eg",
            "yellosa.co.za",
            "ghanayello.com",
        ],
        "yellowpages_africa": [
            "businesslist.com.ng",
            "businesslist.co.ke",
            "yellowpageskenya.com",
            "yellowpages.com.eg",
            "yellosa.co.za",
            "ghanayello.com",
        ],
        "port_authorities": [
            "nigerianports.gov.ng",
            "kpa.co.ke",
            "transnetnationalportsauthority.net",
            "gpha.com.gh",
            "sczone.eg",
        ],
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.client: Optional[object] = None
        self.config = config or {}

    async def __aenter__(self) -> "ExampleScraper":
        """初始化采集器上下文。"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """关闭采集器上下文。"""

    async def search_companies(
        self,
        keywords: List[str],
        countries: List[str],
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """搜索公司信息。

        Args:
            keywords: 关键词列表
            countries: 国家列表
            max_results: 最大结果数

        Returns:
            公司信息列表
        """
        logger.info(
            "No default scraping source configured: keywords=%s countries=%s " "max_results=%s",
            keywords,
            countries,
            max_results,
        )
        return []

    async def google_search(
        self,
        keywords: List[str],
        countries: List[str],
        max_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """执行 Google 搜索采集。

        Args:
            keywords: 关键词列表
            countries: 国家列表
            max_results: 最大结果数

        Returns:
            搜索结果列表
        """
        scraper_config = {
            **self.config,
            "google_api_key": self.config.get("google_api_key") or settings.GOOGLE_API_KEY,
            "search_engine_id": self.config.get("search_engine_id")
            or settings.GOOGLE_SEARCH_ENGINE_ID,
        }
        async with GoogleSearchScraper(scraper_config) as scraper:
            results = await scraper.scrape(
                keywords=keywords,
                countries=countries,
                max_results=max_results,
            )
        return [item.to_dict() for item in results]

    async def directory_search(
        self,
        keywords: List[str],
        countries: List[str],
        max_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """执行商业目录采集。

        Args:
            keywords: 关键词列表
            countries: 国家列表
            max_results: 最大结果数

        Returns:
            公司信息列表
        """
        directory_keywords = build_directory_keywords(
            keywords=keywords,
            countries=countries,
            configured_sites=self.config.get("directory_sites") or [],
        )
        return await self.google_search(
            keywords=directory_keywords or keywords,
            countries=countries,
            max_results=max_results,
        )

    async def crawl_source_url(
        self,
        url: str,
        countries: List[str],
    ) -> tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
        """采集一个用户指定来源地址的公开页面信息。"""
        normalized_url = normalize_url(url)
        check: Dict[str, Any] = {
            "url": normalized_url,
            "ok": False,
            "reason": "",
            "found_fields": [],
        }

        if not WebsiteCrawlerService._is_safe_public_url(normalized_url):
            check["reason"] = "来源地址不是公开 HTTP(S) 地址，已跳过"
            return None, check

        timeout = aiohttp.ClientTimeout(total=15)
        headers = {"User-Agent": "TradeBusinessScraper/1.0 (+public-contact-discovery)"}
        try:
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(normalized_url, allow_redirects=True) as response:
                    check["status_code"] = response.status
                    if response.status >= 400:
                        check["reason"] = f"页面返回 HTTP {response.status}"
                        return None, check

                    content_type = response.headers.get("Content-Type", "").lower()
                    if content_type and not any(
                        value in content_type for value in ("text/html", "application/xhtml+xml")
                    ):
                        check["reason"] = f"非 HTML 页面：{content_type}"
                        return None, check

                    body = await response.content.read(MAX_RESPONSE_BYTES + 1)
                    if len(body) > MAX_RESPONSE_BYTES:
                        check["reason"] = "页面超过 2MB，已跳过"
                        return None, check
                    html = body.decode(response.charset or "utf-8", errors="ignore")
        except TimeoutError:
            check["reason"] = "访问超时"
            return None, check
        except aiohttp.ClientError as exc:
            check["reason"] = f"网络访问失败：{exc}"
            return None, check

        soup = BeautifulSoup(html, "html.parser")
        for node in soup(["script", "style", "noscript", "svg"]):
            node.decompose()

        text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
        title = extract_title(soup)
        emails = extract_emails(text)
        phones = extract_phones(text)
        country_code = countries[0] if countries else ""

        company = {
            "company_name": infer_company_name(title, normalized_url),
            "email": emails[0] if emails else None,
            "phone": phones[0] if phones else None,
            "website": normalized_url,
            "source_url": normalized_url,
            "country_code": country_code,
            "country": country_code,
            "business_type": "freight_forwarder",
            "description": text[:500],
        }
        company = {key: value for key, value in company.items() if value}

        check["ok"] = True
        check["reason"] = "页面读取成功"
        check["found_fields"] = [
            field
            for field in ("company_name", "email", "phone", "website", "description")
            if company.get(field)
        ]
        return company, check


async def run_scraping_task(
    task_id: str,
    task_type: str,
    keywords: List[str],
    countries: List[str],
    config: Dict[str, Any],
    progress_callback=None,
    session=None,
    save_to_db=True,
) -> Dict[str, Any]:
    """
    运行数据采集任务

    Args:
        task_id: 任务ID
        task_type: 任务类型
        keywords: 关键词列表
        countries: 国家列表
        config: 任务配置
        progress_callback: 进度回调函数
        session: 数据库会话
        save_to_db: 是否保存到数据库

    Returns:
        采集结果统计
    """
    logger.info(f"Starting scraping task {task_id} of type {task_type}")

    total_found = 0
    all_companies = []
    diagnostics: List[str] = []
    source_checks: List[Dict[str, Any]] = []

    task_type = normalize_task_type(task_type)
    max_results_per_keyword = config.get("max_results_per_keyword", 5)
    source_urls = normalize_source_urls(config.get("source_urls") or [])
    total_steps = calculate_total_steps(task_type, keywords, source_urls)

    async with ExampleScraper(config) as scraper:
        try:
            if progress_callback:
                await progress_callback(
                    0,
                    total_steps,
                    build_start_message(task_type, keywords, countries, source_urls),
                )

            current_step = 0

            if task_type in GOOGLE_TASK_TYPES:
                # Google搜索
                for i, keyword in enumerate(keywords):
                    current_step += 1
                    if progress_callback:
                        await progress_callback(
                            current_step,
                            total_steps,
                            f"Searching Google for: {keyword}",
                        )

                    companies = await scraper.google_search(
                        keywords=[keyword],
                        countries=countries,
                        max_results=max_results_per_keyword,
                    )

                    all_companies.extend(companies)
                    total_found += len(companies)

            elif task_type in DIRECTORY_TASK_TYPES:
                # 商业目录搜索
                for i, keyword in enumerate(keywords):
                    current_step += 1
                    if progress_callback:
                        await progress_callback(
                            current_step,
                            total_steps,
                            f"Searching directory for: {keyword}",
                        )

                    companies = await scraper.directory_search(
                        keywords=build_source_keywords(task_type, [keyword]),
                        countries=countries,
                        max_results=max_results_per_keyword,
                    )

                    all_companies.extend(companies)
                    total_found += len(companies)

            elif task_type in SPECIFIC_SITE_TASK_TYPES:
                diagnostics.append("该数据源会优先读取来源地址，并用公开搜索补充发现")
                if progress_callback:
                    await progress_callback(current_step, total_steps, "准备读取来源地址")

                companies = await scraper.google_search(
                    keywords=build_source_keywords(task_type, keywords),
                    countries=countries,
                    max_results=max_results_per_keyword * len(keywords),
                )

                all_companies.extend(companies)
                total_found += len(companies)

            else:
                diagnostics.append(f"未知任务类型：{task_type}")

            for source_url in source_urls:
                current_step += 1
                if progress_callback:
                    await progress_callback(
                        current_step,
                        total_steps,
                        f"读取来源地址：{source_url}",
                    )
                company, check = await scraper.crawl_source_url(source_url, countries)
                source_checks.append(check)
                if company:
                    all_companies.append(company)
                    total_found += 1

            if not source_urls and not all_companies:
                diagnostics.append(build_no_result_diagnostic(task_type))

            # 保存到数据库（新增）
            total_saved = 0
            if save_to_db and session:
                from app.models.scraped_lead import ScrapedLead
                from app.scrapers.data_normalizer import DataNormalizer

                logger.info(f"Saving {len(all_companies)} companies to database...")

                for company_data in all_companies:
                    # 标准化数据
                    normalized = DataNormalizer.normalize_company(company_data, task_type)

                    # 创建 ScrapedLead 对象
                    lead = ScrapedLead(
                        id=str(uuid4()),
                        raw_data=company_data,
                        data_source=task_type,
                        source_url=normalized["source_url"],
                        company_name=normalized["company_name"],
                        company_name_en=normalized.get("company_name_en"),
                        country=normalized["country"],
                        country_code=normalized["country_code"],
                        city=normalized.get("city"),
                        email=normalized.get("email"),
                        phone=normalized.get("phone"),
                        whatsapp=normalized.get("whatsapp"),
                        website=normalized.get("website"),
                        business_type=normalized.get("business_type"),
                        description=normalized.get("description"),
                        confidence_score=normalized["confidence_score"],
                        scraping_task_id=task_id,
                    )

                    session.add(lead)
                    total_saved += 1

                # 提交到数据库
                await session.commit()
                logger.info(f"Saved {total_saved} companies to scraped_leads table")

            else:
                # 不保存数据库，只返回数据
                total_saved = len(all_companies)
                if all_companies:
                    logger.info(
                        "Task %s collected %s companies:",
                        task_id,
                        len(all_companies),
                    )
                    for company in all_companies[:5]:
                        logger.info(f"  - {company.get('company_name')} ({company.get('country')})")
                    if len(all_companies) > 5:
                        logger.info(f"  ... and {len(all_companies) - 5} more")

            logger.info(
                "Scraping task %s completed: found=%s, saved=%s",
                task_id,
                total_found,
                total_saved,
            )

            return {
                "total_found": total_found,
                "total_saved": total_saved,
                "companies": all_companies,
                "diagnostics": diagnostics,
                "source_checks": source_checks,
                "progress_current": total_steps,
                "progress_total": total_steps,
                "message": build_result_message(total_found, total_saved, diagnostics),
            }

        except Exception as e:
            logger.error(f"Error in scraping task {task_id}: {e}")
            raise


def normalize_source_urls(source_urls: List[Any]) -> List[str]:
    """Normalize and de-duplicate user-entered source URLs."""
    normalized_urls = []
    seen = set()
    for item in source_urls:
        url = normalize_url(str(item).strip())
        if not url or url in seen:
            continue
        seen.add(url)
        normalized_urls.append(url)
    return normalized_urls


def normalize_url(url: str) -> str:
    """Ensure a URL has an HTTP scheme."""
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        return f"https://{url}"
    return url


def calculate_total_steps(task_type: str, keywords: List[str], source_urls: List[str]) -> int:
    """Calculate progress denominator."""
    task_type = normalize_task_type(task_type)
    keyword_steps = len(keywords) if task_type in GOOGLE_TASK_TYPES | DIRECTORY_TASK_TYPES else 1
    return max(keyword_steps + len(source_urls), 1)


def normalize_task_type(task_type: str) -> str:
    """Normalize legacy task type aliases."""
    aliases = {
        "google_search": "google",
        "kompass_africa": "kompass",
        "yellowpages_africa": "yellow_pages",
    }
    return aliases.get(task_type, task_type)


def build_source_keywords(task_type: str, keywords: List[str]) -> List[str]:
    """Add source-specific search restrictions when a source has known sites."""
    sites = ExampleScraper.SOURCE_SEARCH_SITES.get(task_type, [])
    if not sites:
        return keywords

    source_keywords = []
    for keyword in keywords:
        for site in sites[:6]:
            source_keywords.append(f"{keyword} site:{site}")
    return source_keywords[:12]


def build_directory_keywords(
    keywords: List[str],
    countries: List[str],
    configured_sites: List[str],
) -> List[str]:
    """Build search keywords limited to common business directory sites."""
    sites = list(configured_sites)
    for country in countries:
        sites.extend(ExampleScraper.DIRECTORY_SEARCH_SITES.get(country.upper(), []))

    sites = sorted({site.strip() for site in sites if site and site.strip()})
    if not sites:
        return keywords

    directory_keywords = []
    for keyword in keywords:
        for site in sites[:4]:
            directory_keywords.append(f"{keyword} site:{site}")
    return directory_keywords[:12]


def build_no_result_diagnostic(task_type: str) -> str:
    """Build a helpful no-result diagnostic without reporting missing adapters."""
    if task_type == "google":
        return (
            "Google 搜索已执行，但未发现可保存线索；可尝试更具体的关键词，"
            "或配置 Google Custom Search API 提高稳定性"
        )
    if task_type in DIRECTORY_TASK_TYPES:
        return "商业目录搜索已执行，但未发现可保存线索；可填写具体目录页面来源地址提高命中率"
    if task_type == "port_authorities":
        return "港口管理局数据源已执行，但未发现可保存线索；可填写具体港口官网或企业名录页面"
    return "任务未填写可直接采集的来源地址，也没有发现可保存线索"


def build_start_message(
    task_type: str,
    keywords: List[str],
    countries: List[str],
    source_urls: List[str],
) -> str:
    """Build start message for task details."""
    return (
        f"开始执行 {task_type} 采集：关键词 {len(keywords)} 个，"
        f"国家 {len(countries)} 个，来源地址 {len(source_urls)} 个"
    )


def build_result_message(total_found: int, total_saved: int, diagnostics: List[str]) -> str:
    """Build final user-facing result message."""
    if total_saved:
        return f"采集完成：发现 {total_found} 条，保存 {total_saved} 条线索"
    if diagnostics:
        return f"采集完成但未保存线索：{diagnostics[0]}"
    return "采集完成但未发现可保存线索"


def extract_title(soup: BeautifulSoup) -> str:
    """Extract a useful page title."""
    h1 = soup.find("h1")
    if h1:
        text = h1.get_text(" ", strip=True)
        if text:
            return text
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return ""


def infer_company_name(title: str, url: str) -> str:
    """Infer company name from title or domain."""
    if title:
        return re.split(r"[|-]", title, maxsplit=1)[0].strip()[:200]
    hostname = urlparse(url).hostname or "Unknown Company"
    parts = hostname.replace("www.", "").split(".")
    return parts[0].replace("-", " ").title() if parts else "Unknown Company"


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text."""
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return sorted(set(email.lower() for email in emails))


def extract_phones(text: str) -> List[str]:
    """Extract likely phone numbers from text."""
    candidates = re.findall(r"(?:\+?\d[\d\s().-]{6,}\d)", text)
    phones = []
    seen = set()
    for candidate in candidates:
        cleaned = re.sub(r"\s+", " ", candidate).strip()
        digits = re.sub(r"\D", "", cleaned)
        if 7 <= len(digits) <= 18 and cleaned not in seen:
            seen.add(cleaned)
            phones.append(cleaned)
    return phones[:5]
