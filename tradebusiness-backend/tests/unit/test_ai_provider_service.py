"""AI Provider 回退逻辑测试。"""

from types import SimpleNamespace

import httpx
import pytest

from app.services.ai_provider_service import AIProviderService


@pytest.mark.asyncio
async def test_rules_provider_generates_research_without_remote_call() -> None:
    """规则模式无需密钥即可生成企业背调。"""
    lead = SimpleNamespace(
        company_name="Example Logistics",
        country="Nigeria",
        industry="Freight",
        website="https://example.com",
        description="Importer",
        source="manual",
    )

    result = await AIProviderService().generate_company_research(lead)

    assert result["raw_sources"]["generation_mode"] == "rule_based_mvp"
    assert "Example Logistics" in result["summary"]


@pytest.mark.asyncio
async def test_missing_api_key_falls_back_to_rules(monkeypatch) -> None:
    """Provider 已启用但缺少 API Key 时不应阻断业务。"""
    from app.config import settings

    monkeypatch.setattr(settings, "AI_PROVIDER", "openai_compatible")
    monkeypatch.setattr(settings, "AI_API_KEY", None)

    result = await AIProviderService()._request_json("test")

    assert result is None


@pytest.mark.asyncio
async def test_openai_compatible_response_is_parsed(monkeypatch) -> None:
    """远程 Provider 返回 JSON 代码块时可以正确解析。"""
    from app.config import settings

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"choices": [{"message": {"content": '```json\n{"content": "hello"}\n```'}}]}

    class FakeClient:
        def __init__(self, **kwargs) -> None:
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args) -> None:
            return None

        async def post(self, *args, **kwargs) -> FakeResponse:
            return FakeResponse()

    monkeypatch.setattr(settings, "AI_PROVIDER", "openai_compatible")
    monkeypatch.setattr(settings, "AI_API_KEY", "test-key")
    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)

    result = await AIProviderService()._request_json("test")

    assert result == {"content": "hello"}


@pytest.mark.asyncio
async def test_provider_retries_http_failure(monkeypatch) -> None:
    """首次网络失败后应重试一次。"""
    from app.config import settings

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"choices": [{"message": {"content": '{"content": "recovered"}'}}]}

    class FakeClient:
        calls = 0

        def __init__(self, **kwargs) -> None:
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args) -> None:
            return None

        async def post(self, *args, **kwargs) -> FakeResponse:
            type(self).calls += 1
            if type(self).calls == 1:
                raise httpx.ConnectError("temporary failure")
            return FakeResponse()

    monkeypatch.setattr(settings, "AI_PROVIDER", "openai_compatible")
    monkeypatch.setattr(settings, "AI_API_KEY", "test-key")
    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)

    result = await AIProviderService()._request_json("test")

    assert result == {"content": "recovered"}


@pytest.mark.asyncio
async def test_provider_retry_count_can_be_disabled(monkeypatch) -> None:
    """将重试次数设为 0 时只执行一次远程请求。"""
    from app.config import settings

    class FakeClient:
        calls = 0

        def __init__(self, **kwargs) -> None:
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args) -> None:
            return None

        async def post(self, *args, **kwargs):
            type(self).calls += 1
            raise httpx.ConnectError("permanent failure")

    monkeypatch.setattr(settings, "AI_PROVIDER", "openai_compatible")
    monkeypatch.setattr(settings, "AI_API_KEY", "test-key")
    monkeypatch.setattr(settings, "AI_MAX_RETRIES", 0)
    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)

    assert await AIProviderService()._request_json("test") is None
    assert FakeClient.calls == 1
