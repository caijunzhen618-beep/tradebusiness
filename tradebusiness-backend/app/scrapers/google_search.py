"""
Google 搜索爬虫
使用 Google 搜索 API 或直接爬取搜索结果来发现潜在客户
"""

import logging
import re
import urllib.parse
from typing import List, Optional

from bs4 import BeautifulSoup

from app.scrapers.base import (
    AFRICAN_COUNTRIES,
    SEARCH_KEYWORDS,
    BaseScraper,
    CustomerData,
    SearchQuery,
)

logger = logging.getLogger(__name__)


class GoogleSearchScraper(BaseScraper):
    """
    Google 搜索爬虫

    通过 Google 搜索发现潜在的货运代理公司
    """

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.google_api_key = self.config.get("google_api_key")
        self.search_engine_id = self.config.get("search_engine_id")
        self.use_api = bool(self.google_api_key and self.search_engine_id)

    async def scrape(
        self,
        keywords: Optional[List[str]] = None,
        countries: Optional[List[str]] = None,
        business_types: Optional[List[str]] = None,
        max_results: int = 100,
    ) -> List[CustomerData]:
        """
        执行 Google 搜索爬取

        Args:
            keywords: 搜索关键词列表
            countries: 目标国家列表
            business_types: 业务类型筛选
            max_results: 最大结果数

        Returns:
            爬取到的客户数据列表
        """
        # 使用默认关键词和国家
        if not keywords:
            keywords = SEARCH_KEYWORDS["sea_freight"] + SEARCH_KEYWORDS["air_freight"]

        if not countries:
            # 使用非洲主要国家
            countries = [c["name"] for tier in AFRICAN_COUNTRIES.values() for c in tier]

        # 构建搜索查询
        search_queries = []
        for country in countries[:5]:  # 限制国家数量
            for keyword in keywords[:3]:  # 限制关键词数量
                query = f"{keyword} in {country}"
                search_queries.append(query)

        logger.info(f"Built {len(search_queries)} search queries")

        # 执行搜索
        all_results = []

        if self.use_api:
            # 使用 Google Custom Search API
            results = await self._search_with_api(search_queries, max_results)
        else:
            # 直接爬取 Google 搜索结果页
            results = await self._search_by_scraping(search_queries, max_results)

        # 从搜索结果中提取客户信息
        for result in results:
            customer = await self._extract_from_url(result["url"], result.get("title", ""))
            if customer:
                all_results.append(customer)

        logger.info(f"Extracted {len(all_results)} customer data from search results")
        return all_results

    async def _search_with_api(
        self,
        queries: List[str],
        max_results: int,
    ) -> List[dict]:
        """
        使用 Google Custom Search API 进行搜索

        Args:
            queries: 搜索查询列表
            max_results: 每个查询的最大结果数

        Returns:
            搜索结果列表
        """
        all_results = []

        for query in queries[:10]:  # API 限制
            try:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    "key": self.google_api_key,
                    "cx": self.search_engine_id,
                    "q": query,
                    "num": min(max_results, 10),  # API 限制每次最多10个结果
                }

                async with self.session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()

                    items = data.get("items", [])
                    for item in items:
                        all_results.append(
                            {
                                "url": item["link"],
                                "title": item.get("title", ""),
                                "snippet": item.get("snippet", ""),
                                "query": query,
                            }
                        )

                # 延迟避免请求过快
                await self._delay()

            except Exception as e:
                logger.error(f"API search failed for query '{query}': {str(e)}")

        return all_results

    async def _search_by_scraping(
        self,
        queries: List[str],
        max_results: int,
    ) -> List[dict]:
        """
        通过爬取 Google 搜索结果页进行搜索

        Args:
            queries: 搜索查询列表
            max_results: 每个查询的最大结果数

        Returns:
            搜索结果列表
        """
        all_results = []

        for query in queries[:5]:  # 限制查询数量
            try:
                # 构建搜索 URL
                search_url = (
                    f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={max_results}"
                )

                # 获取搜索结果页
                html = await self.fetch_page(search_url)

                # 解析结果
                results = self._parse_google_results(html)
                for result in results:
                    result["query"] = query
                    all_results.append(result)

                await self._delay()

            except Exception as e:
                logger.error(f"Scraping failed for query '{query}': {str(e)}")

        return all_results

    def _parse_google_results(self, html: str) -> List[dict]:
        """
        解析 Google 搜索结果页面

        Args:
            html: 页面 HTML

        Returns:
            搜索结果列表
        """
        soup = BeautifulSoup(html, "html.parser")
        results = []

        # Google 搜索结果的 HTML 结构可能会变化
        # 这里使用常见的选择器
        for div in soup.select("div.g"):
            try:
                # 提取标题和链接
                title_elem = div.select_one("h3")
                link_elem = div.select_one("a")
                snippet_elem = div.select_one("div.VwiC3b") or div.select_one("span.st")

                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    url = link_elem.get("href", "")
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                    # 清理 URL（Google 搜索结果中可能包含重定向）
                    if url.startswith("/url?"):
                        # 提取真实 URL
                        parsed = urllib.parse.urlparse(url)
                        real_url = urllib.parse.parse_qs(parsed.query).get("q", [""])[0]
                    else:
                        real_url = url

                    results.append(
                        {
                            "url": real_url,
                            "title": title,
                            "snippet": snippet,
                        }
                    )

            except Exception as e:
                logger.debug(f"Failed to parse search result: {str(e)}")
                continue

        return results

    async def _extract_from_url(
        self,
        url: str,
        title: str,
    ) -> Optional[CustomerData]:
        """
        从 URL 中提取客户信息

        Args:
            url: 网站 URL
            title: 页面标题

        Returns:
            客户数据或 None
        """
        try:
            # 获取页面内容
            html = await self.fetch_page(url)
            soup = BeautifulSoup(html, "html.parser")

            # 提取公司信息
            company_name = self._extract_company_name(soup, title)
            email = self._extract_email(soup)
            phone = self._extract_phone(soup)
            country = self._extract_country(soup, url)

            if company_name:
                return CustomerData(
                    company_name=company_name,
                    email=email,
                    phone=phone,
                    website=url,
                    country=country,
                    country_code=self._get_country_code(country),
                )

        except Exception as e:
            logger.debug(f"Failed to extract from {url}: {str(e)}")

        return None

    def _extract_company_name(self, soup: BeautifulSoup, title: str) -> Optional[str]:
        """提取公司名称"""
        # 尝试从 meta 标签获取
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]

        # 尝试从标题获取
        if title:
            # 清理标题（去除后缀等）
            company_name = re.sub(r"\s*[-–|]\s*(Freight|Logistics|Cargo|Shipping).*$", "", title)
            return company_name.strip()

        # 尝试从页面内容获取
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        return None

    def _extract_email(self, soup: BeautifulSoup) -> Optional[str]:
        """提取邮箱"""
        # 从邮件链接中提取
        mailto_links = soup.find_all("a", href=re.compile(r"^mailto:"))
        for link in mailto_links:
            email = link.get("href", "").replace("mailto:", "")
            if self.validate_email(email):
                return email

        # 使用正则从页面文本中提取
        text = soup.get_text()
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, text)
        for email in emails:
            if self.validate_email(email):
                return email

        return None

    def _extract_phone(self, soup: BeautifulSoup) -> Optional[str]:
        """提取电话号码"""
        # 从 tel: 链接提取
        tel_links = soup.find_all("a", href=re.compile(r"^tel:"))
        for link in tel_links:
            phone = link.get("href", "").replace("tel:", "")
            if self.validate_phone(phone):
                return phone

        # 使用正则从页面文本中提取
        text = soup.get_text()
        phone_pattern = r"(\+\d{1,3}[- ]?)?\(?\d{1,4}\)?[- ]?\d{1,4}[- ]?\d{1,9}"
        phones = re.findall(phone_pattern, text)
        for phone in phones:
            if self.validate_phone(phone):
                return phone

        return None

    def _extract_country(self, soup: BeautifulSoup, url: str) -> str:
        """从 URL 或页面内容提取国家"""
        # 从 URL 提取
        try:
            from urllib.parse import urlparse

            domain = urlparse(url).netloc.lower()

            # 域名后缀映射
            tld_to_country = {
                ".ng": "Nigeria",
                ".za": "South Africa",
                ".eg": "Egypt",
                ".ke": "Kenya",
                ".ma": "Morocco",
                ".gh": "Ghana",
                ".et": "Ethiopia",
                ".tz": "Tanzania",
                ".ci": "Ivory Coast",
                ".sn": "Senegal",
            }

            for tld, country in tld_to_country.items():
                if domain.endswith(tld):
                    return country

        except:
            pass

        # 默认返回
        return ""

    def _get_country_code(self, country: str) -> str:
        """根据国家名称获取国家代码"""
        country_code_map = {
            "Nigeria": "NG",
            "South Africa": "ZA",
            "Egypt": "EG",
            "Kenya": "KE",
            "Morocco": "MA",
            "Ghana": "GH",
            "Ethiopia": "ET",
            "Tanzania": "TZ",
            "Ivory Coast": "CI",
            "Senegal": "SN",
        }
        return country_code_map.get(country, "")
