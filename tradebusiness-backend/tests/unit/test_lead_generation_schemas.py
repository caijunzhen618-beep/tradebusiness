"""AI 获客与跟进 Schema 的边界测试。"""

import inspect
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.api.v1 import lead_generation
from app.schemas.lead_generation import (
    FollowupTaskCreate,
    FollowupTaskResponse,
    LeadEmailSendRequest,
    LeadGenerationStatsResponse,
)


def test_followup_retry_resets_due_time_for_immediate_pickup() -> None:
    """重试任务必须立即进入 Celery 到期扫描范围。"""
    assert "task.due_at = datetime.utcnow()" in inspect.getsource(lead_generation.retry_followup)


def test_lead_email_request_validates_recipient_and_content() -> None:
    """开发信请求必须包含合法邮箱和正文。"""
    request = LeadEmailSendRequest(
        to_email="buyer@example.com",
        subject="Freight proposal",
        body="Hello, we can help.",
    )

    assert str(request.to_email) == "buyer@example.com"


def test_lead_email_request_rejects_invalid_email() -> None:
    """非法收件地址必须被拒绝。"""
    with pytest.raises(ValidationError):
        LeadEmailSendRequest(
            to_email="not-an-email",
            subject="Subject",
            body="Body",
        )


def test_lead_generation_stats_has_stable_grouped_fields() -> None:
    """统计响应必须稳定提供各分组字段。"""
    stats = LeadGenerationStatsResponse(leads=2, countries={"NG": 2})

    assert stats.countries == {"NG": 2}
    assert stats.channels == {}
    assert stats.reply_rate == 0.0


def test_followup_create_accepts_supported_channels() -> None:
    """支持的渠道可以创建跟进任务。"""
    task = FollowupTaskCreate(
        lead_id="lead-1",
        channel="email",
        content="Follow up",
        due_at=datetime(2026, 7, 15, 12, 0),
    )

    assert task.channel == "email"


def test_followup_create_rejects_unknown_channel() -> None:
    """未知渠道必须被 Schema 拒绝。"""
    with pytest.raises(ValidationError):
        FollowupTaskCreate(
            lead_id="lead-1",
            channel="sms",
            content="Follow up",
            due_at=datetime(2026, 7, 15, 12, 0),
        )


def test_followup_response_rejects_unknown_status() -> None:
    """未知状态不能进入 API 响应。"""
    with pytest.raises(ValidationError):
        FollowupTaskResponse(
            lead_id="lead-1",
            channel="email",
            content="Follow up",
            due_at=datetime(2026, 7, 15, 12, 0),
            id="task-1",
            user_id="user-1",
            status="unknown",
            created_at=datetime(2026, 7, 15, 12, 0),
            updated_at=datetime(2026, 7, 15, 12, 0),
        )
