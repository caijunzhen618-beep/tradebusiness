"""审计日志脱敏测试。"""

from app.core.audit import audit_event


def test_audit_event_filters_sensitive_metadata(caplog) -> None:
    """审计事件不应记录令牌、密钥或正文。"""
    with caplog.at_level("INFO", logger="tradebusiness.audit"):
        audit_event(
            "test_action",
            user_id="user-1",
            resource_type="lead",
            resource_id="lead-1",
            metadata={"token": "secret", "body": "private", "channel": "email"},
        )

    record = caplog.records[-1]
    assert record.audit_metadata == {"channel": "email"}
