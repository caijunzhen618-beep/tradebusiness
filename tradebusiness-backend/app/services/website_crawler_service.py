"""官网公开内容抓取服务。"""

import re
import socket
from ipaddress import ip_address
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup


class WebsiteCrawlerService:
    """读取官网首页的公开文本，作为企业背调上下文。"""

    MAX_TEXT_LENGTH = 12000
    MAX_RESPONSE_BYTES = 2 * 1024 * 1024

    async def fetch_homepage_text(self, website: str | None) -> str:
        """抓取官网首页并提取可读文本，失败时返回空字符串。"""
        if not website or not self._is_safe_public_url(website):
            return ""
        timeout = aiohttp.ClientTimeout(total=12)
        headers = {"User-Agent": "TradebaseResearchBot/1.0 (+public-research)"}
        try:
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(website, allow_redirects=False) as response:
                    if response.status >= 400:
                        return ""
                    content_type = response.headers.get("Content-Type", "").lower()
                    if content_type and not any(
                        value in content_type for value in ("text/html", "application/xhtml+xml")
                    ):
                        return ""
                    body = await response.content.read(self.MAX_RESPONSE_BYTES + 1)
                    if len(body) > self.MAX_RESPONSE_BYTES:
                        return ""
                    html = body.decode(response.charset or "utf-8", errors="ignore")
        except (aiohttp.ClientError, TimeoutError):
            return ""

        soup = BeautifulSoup(html, "html.parser")
        for node in soup(["script", "style", "noscript", "svg"]):
            node.decompose()
        text = soup.get_text(" ", strip=True)
        return re.sub(r"\s+", " ", text)[: self.MAX_TEXT_LENGTH]

    @staticmethod
    def _is_safe_public_url(website: str) -> bool:
        """仅允许访问公开 HTTP(S) 官网，阻止常见 SSRF 地址。"""
        try:
            parsed = urlparse(website)
            if parsed.scheme not in {"http", "https"} or not parsed.hostname:
                return False
            if parsed.username or parsed.password:
                return False
            hostname = parsed.hostname.lower().rstrip(".")
            if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(
                ".localhost"
            ):
                return False
            try:
                address = ip_address(hostname)
            except ValueError:
                try:
                    resolved_addresses = {
                        ip_address(item[4][0]) for item in socket.getaddrinfo(hostname, None)
                    }
                except socket.gaierror:
                    return True
                return bool(resolved_addresses) and all(
                    not (
                        address.is_private
                        or address.is_loopback
                        or address.is_link_local
                        or address.is_multicast
                        or address.is_reserved
                    )
                    for address in resolved_addresses
                )
            return not (
                address.is_private
                or address.is_loopback
                or address.is_link_local
                or address.is_multicast
                or address.is_reserved
            )
        except ValueError:
            return False
