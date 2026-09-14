"""关键业务操作审计日志。"""

import logging
from typing import Any

logger = logging.getLogger("tradebusiness.audit")


def audit_event(
    action: str,
    *,
    user_id: str | None,
    resource_type: str,
    resource_id: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    """记录不包含敏感数据的结构化审计事件。"""
    safe_metadata = {
        key: value
        for key, value in (metadata or {}).items()
        if key.lower() not in {"password", "token", "access_token", "api_key", "body"}
    }
    logger.info(
        "audit_event",
        extra={
            "audit_action": action,
            "audit_user_id": user_id,
            "audit_resource_type": resource_type,
            "audit_resource_id": resource_id,
            "audit_metadata": safe_metadata,
        },
    )
