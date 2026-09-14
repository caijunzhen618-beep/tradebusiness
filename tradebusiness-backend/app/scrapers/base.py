"""
爬虫基类
定义所有爬虫的通用接口和功能
"""

import asyncio
import logging
import random
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import aiohttp
from fake_useragent import UserAgent

from app.config import settings

logger = logging.getLogger(__name__)


class CustomerData:
    """客户数据结构"""

    def __init__(
        self,
        company_name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        website: Optional[str] = None,
        country: str = "",
        country_code: str = "",
        city: Optional[str] = None,
        address: Optional[str] = None,
        business_type: Optional[str] = None,
        **kwargs,
    ):
        self.company_name = company_name
        self.email = email
        self.phone = phone
        self.website = website
        self.country = country
        self.country_code = country_code
        self.city = city
        self.address = address
        self.business_type = business_type
        self.extra = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = {
            "company_name": self.company_name,
            "email": self.email,
            "phone": self.phone,
            "website": self.website,
            "country": self.country,
            "country_code": self.country_code,
            "city": self.city,
            "address": self.address,
            "business_type": self.business_type,
        }
        data.update(self.extra)
        return {k: v for k, v in data.items() if v is not None}

    def __repr__(self) -> str:
        return f"<CustomerData({self.company_name}, {self.country})>"


class BaseScraper(ABC):
    """
    爬虫基类

    所有爬虫都应该继承这个类并实现相应的方法
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化爬虫

        Args:
            config: 爬虫配置
        """
        self.config = config or {}
        self.user_agent = UserAgent()
        self.session = None
        self.results: List[CustomerData] = []

        # 获取配置
        self.timeout = self.config.get("timeout", settings.SCRAPER_TIMEOUT)
        self.delay_min = self.config.get("delay_min", settings.SCRAPER_DELAY_MIN)
        self.delay_max = self.config.get("delay_max", settings.SCRAPER_DELAY_MAX)

    async def __aenter__(self):
        """进入上下文管理器"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器"""
        await self.close()

    async def start(self):
        """启动爬虫（创建会话等）"""
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=self._get_headers(),
        )
        logger.info(f"{self.__class__.__name__} started")

    async def close(self):
        """关闭爬虫（关闭会话等）"""
        if self.session:
            await self.session.close()
        logger.info(f"{self.__class__.__name__} closed")

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "User-Agent": self.config.get(
                "user_agent",
                settings.SCRAPER_USER_AGENT,
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

    async def _delay(self):
        """请求之间的随机延迟"""
        delay = random.uniform(self.delay_min, self.delay_max)
        await asyncio.sleep(delay)

    async def fetch_page(
        self,
        url: str,
        method: str = "GET",
        **kwargs,
    ) -> str:
        """
        获取页面内容

        Args:
            url: 目标URL
            method: 请求方法
            **kwargs: 其他请求参数

        Returns:
            页面HTML内容
        """
        if not self.session:
            raise RuntimeError("Scraper not started. Use 'async with' or call start() first.")

        try:
            async with self.session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return await response.text()

        except Exception as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            raise

    @abstractmethod
    async def scrape(
        self,
        **kwargs,
    ) -> List[CustomerData]:
        """
        执行爬取任务（子类必须实现）

        Args:
            **kwargs: 爬取参数

        Returns:
            爬取到的客户数据列表
        """
        pass

    def validate_email(self, email: str) -> bool:
        """
        验证邮箱格式

        Args:
            email: 邮箱地址

        Returns:
            是否有效
        """
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def validate_phone(self, phone: str) -> bool:
        """
        验证电话号码格式

        Args:
            phone: 电话号码

        Returns:
            是否有效
        """
        import re

        # 简单验证：包含数字，可能包含 +、-、空格、括号
        pattern = r"^[\d\s\-\+\(\)]+$"
        return re.match(pattern, phone) is not None and len(re.sub(r"[^\d]", "", phone)) >= 7

    def normalize_data(self, data: CustomerData) -> CustomerData:
        """
        标准化数据

        Args:
            data: 原始客户数据

        Returns:
            标准化后的客户数据
        """
        # 标准化邮箱
        if data.email:
            data.email = data.email.lower().strip()

        # 标准化网址
        if data.website:
            if not data.website.startswith(("http://", "https://")):
                data.website = "https://" + data.website

        # 标准化电话号码
        if data.phone:
            data.phone = data.phone.strip()

        return data

    async def scrape_with_retry(
        self,
        max_retries: int = 3,
        **kwargs,
    ) -> List[CustomerData]:
        """
        带重试的爬取

        Args:
            max_retries: 最大重试次数
            **kwargs: 爬取参数

        Returns:
            爬取到的客户数据列表
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                logger.info(f"Scraping attempt {attempt + 1}/{max_retries}")
                results = await self.scrape(**kwargs)
                return results

            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")

                if attempt < max_retries - 1:
                    # 指数退避
                    wait_time = 2**attempt
                    logger.info(f"Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)

        # 所有重试都失败
        logger.error(f"All {max_retries} attempts failed")
        raise last_error or Exception("Scraping failed")


class SearchQuery:
    """搜索查询"""

    def __init__(
        self,
        keywords: List[str],
        countries: List[str],
        business_types: Optional[List[str]] = None,
    ):
        """
        初始化搜索查询

        Args:
            keywords: 关键词列表
            countries: 国家列表
            business_types: 业务类型列表
        """
        self.keywords = keywords
        self.countries = countries
        self.business_types = business_types or []

    def build_search_queries(self) -> List[str]:
        """
        构建搜索查询字符串列表

        Returns:
            搜索查询列表
        """
        queries = []

        for country in self.countries:
            for keyword in self.keywords:
                # 基础查询
                query = f"{keyword} {country}"
                queries.append(query)

                # 如果指定了业务类型
                if self.business_types:
                    for business_type in self.business_types:
                        query = f"{keyword} {business_type} {country}"
                        queries.append(query)

        return queries


# 非洲国家配置
AFRICAN_COUNTRIES = {
    # 第一优先级（主要经济体）
    "tier_1": [
        {"name": "Nigeria", "code": "NG", "ports": ["Lagos", "Tincan", "Apapa"]},
        {"name": "South Africa", "code": "ZA", "ports": ["Durban", "Cape Town", "Port Elizabeth"]},
        {"name": "Egypt", "code": "EG", "ports": ["Alexandria", "Port Said", "Damtietta"]},
        {"name": "Kenya", "code": "KE", "ports": ["Mombasa", "Lamu"]},
        {"name": "Morocco", "code": "MA", "ports": ["Tangier", "Casablanca", "Agadir"]},
    ],
    # 第二优先级（增长市场）
    "tier_2": [
        {"name": "Ghana", "code": "GH", "ports": ["Tema", "Takoradi"]},
        {"name": "Ethiopia", "code": "ET", "ports": []},
        {"name": "Tanzania", "code": "TZ", "ports": ["Dar es Salaam"]},
        {"name": "Ivory Coast", "code": "CI", "ports": ["Abidjan"]},
        {"name": "Senegal", "code": "SN", "ports": ["Dakar"]},
    ],
    # 第三优先级（新兴市场）
    "tier_3": [
        {"name": "Uganda", "code": "UG", "ports": []},
        {"name": "Rwanda", "code": "RW", "ports": []},
        {"name": "Cameroon", "code": "CM", "ports": ["Douala", "Kribi"]},
        {"name": "Angola", "code": "AO", "ports": ["Luanda"]},
        {"name": "Mozambique", "code": "MZ", "ports": ["Maputo", "Beira"]},
        {"name": "Zambia", "code": "ZM", "ports": []},
        {"name": "Zimbabwe", "code": "ZW", "ports": []},
    ],
}

# 搜索关键词模板
SEARCH_KEYWORDS = {
    "sea_freight": [
        "freight forwarder",
        "sea cargo agent",
        "shipping agent",
        "ocean freight",
        "logistics company",
        "cargo services",
    ],
    "air_freight": [
        "air cargo agent",
        "air freight forwarder",
        "aviation logistics",
        "air cargo services",
    ],
    "general": [
        "cargo agent",
        "logistics provider",
        "supply chain",
        "transportation company",
    ],
}
