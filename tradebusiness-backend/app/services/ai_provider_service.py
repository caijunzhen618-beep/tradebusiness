"""AI Provider 服务。"""

import asyncio
import json
import re

import httpx

from app.config import settings
from app.models.lead_generation import Lead


class AIProviderService:
    """AI 内容生成服务。"""

    async def _request_json(self, prompt: str) -> dict | None:
        """调用 OpenAI-compatible Provider，失败时使用本地规则回退。"""
        if settings.AI_PROVIDER.lower() in {"rules", "rule_based", "mock"}:
            return None
        if not settings.AI_API_KEY:
            return None
        payload = {
            "model": settings.AI_MODEL,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
        }
        max_attempts = max(1, settings.AI_MAX_RETRIES + 1)
        for attempt in range(max_attempts):
            try:
                async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
                    response = await client.post(
                        f"{settings.AI_BASE_URL.rstrip('/')}/chat/completions",
                        headers={"Authorization": f"Bearer {settings.AI_API_KEY}"},
                        json=payload,
                    )
                    response.raise_for_status()
                    content = response.json()["choices"][0]["message"]["content"]
                    content = re.sub(r"^```(?:json)?|```$", "", content.strip()).strip()
                    result = json.loads(content)
                    return result if isinstance(result, dict) else None
            except httpx.HTTPError:
                if attempt < max_attempts - 1:
                    await asyncio.sleep(settings.AI_RETRY_BACKOFF_SECONDS * (2**attempt))
                    continue
                return None
            except (KeyError, IndexError, TypeError, json.JSONDecodeError):
                return None
        return None

    async def generate_company_research(
        self, lead: Lead, website_text: str = ""
    ) -> dict[str, str | dict]:
        """生成结构化企业背调内容。"""
        company = lead.company_name
        country = lead.country or "目标市场"
        industry = lead.industry or "相关行业"
        website = lead.website or "暂无官网"
        description = lead.description or "公开资料暂未补充"
        website_context = website_text[:1000] if website_text else "暂无可读取的官网公开文本"
        ai_result = await self._request_json(
            f"Create a B2B company research report as JSON with keys summary, business_model, products, "
            f"target_markets, buying_signals, pain_points, recommended_angle, raw_sources. "
            f"Company: {company}; country: {country}; industry: {industry}; website: {website}; "
            f"description: {description}; website text: {website_context}"
        )
        research_keys = (
            "summary",
            "business_model",
            "products",
            "target_markets",
            "buying_signals",
            "pain_points",
            "recommended_angle",
        )
        if ai_result and all(key in ai_result for key in ("summary", "business_model", "products")):
            raw_sources = (
                dict(ai_result["raw_sources"])
                if isinstance(ai_result.get("raw_sources"), dict)
                else {}
            )
            raw_sources.setdefault("generation_mode", "ai_provider")
            return {
                **{key: str(ai_result.get(key) or "") for key in research_keys},
                "raw_sources": raw_sources,
            }
        return {
            "summary": f"{company} 是位于 {country} 的潜在 B2B 客户，行业方向为 {industry}。当前记录的官网为 {website}。{description} 官网公开信息摘要：{website_context}",
            "business_model": f"初步判断 {company} 可能通过采购、分销、项目合作或长期供应商合作来完成业务增长。",
            "products": f"建议围绕 {industry} 相关产品、物流需求、供应链效率和成本优化继续补充资料。",
            "target_markets": f"重点关注 {country} 及其周边市场的进口、出口和本地分销机会。",
            "buying_signals": "官网、行业关键词、目标国家和业务描述显示其具备进一步人工确认价值。",
            "pain_points": "可能关注交付稳定性、价格透明度、清关效率、响应速度和供应商可靠性。",
            "recommended_angle": "建议以降低跨境运输沟通成本、提升交付确定性和提供稳定航线/空运资源作为切入点。",
            "raw_sources": {
                "website": website,
                "source": lead.source or "manual",
                "generation_mode": "rule_based_mvp",
                "website_text_available": bool(website_text),
            },
        }

    async def generate_sales_copy(
        self,
        lead: Lead,
        channel: str,
        language: str,
        tone: str | None,
        research_summary: str | None = None,
        agent_context: dict | None = None,
        knowledge_context: str = "",
        template_context: str = "",
    ) -> dict[str, str | None]:
        """生成开发信或渠道话术。"""
        company = lead.company_name
        country = lead.country or "your market"
        industry = lead.industry or "your business"
        summary = research_summary or f"We noticed your work in {industry}."
        if agent_context:
            summary = f"{summary} Company: {agent_context.get('company_intro') or ''} Product: {agent_context.get('product_intro') or ''} Value: {agent_context.get('value_proposition') or ''} Target customer: {agent_context.get('target_customer') or ''}"
        if knowledge_context:
            summary = f"{summary} Product knowledge: {knowledge_context[:2000]}"
        ai_result = await self._request_json(
            f"Write a {channel} sales message in {language} with a {tone or 'professional'} tone. "
            f"Return JSON with keys subject, content, tone. Company: {company}; country: {country}; "
            f"industry: {industry}; context: {summary}; template: {template_context[:1000]}"
        )
        if (
            ai_result
            and isinstance(ai_result.get("content"), (str, int, float))
            and ai_result.get("content")
        ):
            return {
                "subject": str(ai_result.get("subject")) if ai_result.get("subject") else None,
                "content": str(ai_result["content"]),
                "tone": str(ai_result.get("tone") or tone or "professional"),
            }
        if language.lower().startswith("zh"):
            subject = f"关于 {company} 的国际物流合作建议" if channel == "email" else None
            content = f"您好，{company} 团队：\n\n{summary}\n\n我们可以协助贵司优化跨境运输、清关沟通和交付稳定性。若您近期有进口、出口或供应链协作需求，我希望可以安排一次简短沟通。\n\n期待交流。"
        else:
            subject = f"Logistics cooperation idea for {company}" if channel == "email" else None
            content = f"Hi {company} team,\n\nI noticed your work in {industry} in {country}. {summary}\n\nWe help B2B companies improve cross-border logistics reliability, customs coordination, and shipment visibility. Would a short conversation next week be useful?"
        if channel == "whatsapp":
            content = content.replace("\n\n", "\n")
        if channel == "linkedin":
            content = content.split("\n\n")[0] + "\n\nWould be glad to connect and exchange ideas."
        return {"subject": subject, "content": content, "tone": tone or "professional"}
