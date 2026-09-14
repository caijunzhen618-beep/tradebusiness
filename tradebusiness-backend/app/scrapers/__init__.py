"""
数据采集（爬虫）模块
包含所有爬虫相关的功能
"""

from .base import AFRICAN_COUNTRIES, SEARCH_KEYWORDS, BaseScraper, CustomerData, SearchQuery
from .google_search import GoogleSearchScraper

__all__ = [
    "BaseScraper",
    "CustomerData",
    "SearchQuery",
    "AFRICAN_COUNTRIES",
    "SEARCH_KEYWORDS",
    "GoogleSearchScraper",
]
