"""
请求限流器
控制爬虫请求频率，避免被封禁
"""

import asyncio
import time
from typing import Optional

from loguru import logger


class RateLimiter:
    """
    请求限流器

    控制请求速率，确保不会过快地发送请求
    """

    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """
        初始化限流器

        Args:
            min_delay: 最小延迟（秒）
            max_delay: 最大延迟（秒）
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time: float = 0

    async def acquire(self):
        """
        获取请求许可（阻塞直到可以发送请求）

        计算需要等待的时间并异步等待
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        # 计算需要等待的时间
        delay = max(0, self.min_delay - time_since_last_request)

        # 添加一些随机性
        import random

        random_delay = random.uniform(0, self.max_delay - self.min_delay)
        total_delay = delay + random_delay

        if total_delay > 0:
            logger.debug(f"Rate limiting: waiting {total_delay:.2f}s")
            await asyncio.sleep(total_delay)

        self.last_request_time = time.time()


class ConcurrentRateLimiter:
    """
    并发限流器

    使用信号量控制并发请求数量
    """

    def __init__(self, max_concurrent: int = 5):
        """
        初始化并发限流器

        Args:
            max_concurrent: 最大并发数
        """
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.max_concurrent = max_concurrent

    async def __aenter__(self):
        """
        进入上下文（获取信号量）
        """
        await self.semaphore.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        退出上下文（释放信号量）
        """
        self.semaphore.release()

    def get_available_count(self) -> int:
        """
        获取可用并发数

        Returns:
            可用并发数
        """
        return self.semaphore._value
