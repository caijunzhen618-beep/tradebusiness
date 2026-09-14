"""生产配置安全校验测试。"""

import pytest
from pydantic import ValidationError

from app.config import Settings


def _settings(**overrides):
    values = {
        "ENVIRONMENT": "production",
        "DEBUG": False,
        "DATABASE_URL": "mysql+aiomysql://user:password@localhost/db",
        "SECRET_KEY": "s" * 40,
        "JWT_SECRET_KEY": "j" * 40,
        "CORS_ORIGINS": ["https://admin.example.com"],
        "SMTP_HOST": "smtp.example.com",
        "SMTP_USER": "mailer@example.com",
        "SMTP_PASSWORD": "smtp-password",
        "SMTP_FROM": "mailer@example.com",
    }
    values.update(overrides)
    return Settings(**values)


def test_production_settings_accept_secure_values() -> None:
    """安全的生产配置应通过校验。"""
    assert _settings().ENVIRONMENT == "production"


@pytest.mark.parametrize(
    "overrides",
    [
        {"DEBUG": True},
        {"SECRET_KEY": "short"},
        {"CORS_ORIGINS": ["http://localhost:3000"]},
    ],
)
def test_production_settings_reject_insecure_values(overrides) -> None:
    """生产配置不能启用调试或本地跨域来源。"""
    with pytest.raises(ValidationError):
        _settings(**overrides)
