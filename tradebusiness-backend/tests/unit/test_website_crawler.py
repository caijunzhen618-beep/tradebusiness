"""官网抓取安全边界测试。"""

from app.services.website_crawler_service import WebsiteCrawlerService


def test_crawler_rejects_private_and_local_urls() -> None:
    """抓取器不能访问本机或内网地址。"""
    assert not WebsiteCrawlerService._is_safe_public_url("http://127.0.0.1:8000")
    assert not WebsiteCrawlerService._is_safe_public_url("http://10.0.0.1")
    assert not WebsiteCrawlerService._is_safe_public_url("http://localhost/admin")


def test_crawler_accepts_public_https_url() -> None:
    """公开 HTTPS 官网可以进入抓取流程。"""
    assert WebsiteCrawlerService._is_safe_public_url("https://example.com")
