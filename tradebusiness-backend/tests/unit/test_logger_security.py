"""日志敏感字段脱敏测试。"""

from app.core.logger import redact_log_message


def test_redact_log_message_removes_sensitive_values() -> None:
    """常见密钥字段的值不应出现在日志消息中。"""
    message = "password=secret api_key=abc123 Authorization=Bearer-token"
    redacted = redact_log_message(message)

    assert "secret" not in redacted
    assert "abc123" not in redacted
    assert "Bearer-token" not in redacted
    assert redacted.count("***") == 3
