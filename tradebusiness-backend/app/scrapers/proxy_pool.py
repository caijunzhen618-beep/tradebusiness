"""
代理池管理
用于管理爬虫使用的代理服务器
"""

import asyncio
import random
from typing import List, Optional

from loguru import logger


class ProxyPool:
    """
    代理池管理器

    管理和轮换代理服务器，避免IP被封禁
    """

    def __init__(self):
        # 代理列表：格式: ["http://user:pass@ip:port", ...]
        self.proxies: List[str] = []
        self.failed_proxies: set = set()  # 失败的代理
        self.current_index = 0

        # 加载代理列表（可以从环境变量、数据库或配置文件）
        self._load_proxies()

    def _load_proxies(self):
        """
        加载代理列表

        可以从以下来源加载：
        1. 环境变量
        2. 配置文件
        3. 数据库
        4. 代理API
        """
        import os

        # 从环境变量加载（逗号分隔）
        proxy_list = os.getenv("SCRAPER_PROXIES", "")
        if proxy_list:
            self.proxies = [p.strip() for p in proxy_list.split(",") if p.strip()]

        # 如果没有配置代理，使用空列表（直接连接）
        if not self.proxies:
            logger.info("No proxies configured, using direct connection")

        logger.info(f"Loaded {len(self.proxies)} proxies")

    def get_proxy(self) -> Optional[str]:
        """
        获取一个可用的代理

        Returns:
            代理URL或None（如果没有配置代理）
        """
        if not self.proxies:
            return None

        # 过滤掉失败的代理
        available_proxies = [p for p in self.proxies if p not in self.failed_proxies]

        if not available_proxies:
            logger.warning("No available proxies, resetting failed list")
            self.failed_proxies.clear()
            available_proxies = self.proxies

        # 随机选择一个代理
        proxy = random.choice(available_proxies)
        return proxy

    def mark_failed(self, proxy: str):
        """
        标记代理为失败

        Args:
            proxy: 代理URL
        """
        self.failed_proxies.add(proxy)
        logger.warning(f"Proxy marked as failed: {proxy}")

    def mark_success(self, proxy: str):
        """
        标记代理为成功（从失败列表中移除）

        Args:
            proxy: 代理URL
        """
        if proxy in self.failed_proxies:
            self.failed_proxies.remove(proxy)
            logger.info(f"Proxy restored: {proxy}")

    def get_stats(self) -> dict:
        """
        获取代理池统计信息

        Returns:
            统计数据字典
        """
        return {
            "total_proxies": len(self.proxies),
            "available_proxies": len(self.proxies) - len(self.failed_proxies),
            "failed_proxies": len(self.failed_proxies),
        }


# 全局代理池实例
proxy_pool = ProxyPool()


class UserAgentPool:
    """
    User-Agent 池

    管理多个User-Agent，避免被检测为爬虫
    """

    def __init__(self):
        self.user_agents = [
            # Chrome on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            # Firefox on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            # Edge on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            # Chrome on Mac
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            # Safari on Mac
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            # Chrome on Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        ]

    def get_random(self) -> str:
        """
        随机获取一个User-Agent

        Returns:
            User-Agent字符串
        """
        return random.choice(self.user_agents)

    def get_all(self) -> List[str]:
        """
        获取所有User-Agent

        Returns:
            User-Agent列表
        """
        return self.user_agents.copy()


# 全局User-Agent池实例
user_agent_pool = UserAgentPool()
