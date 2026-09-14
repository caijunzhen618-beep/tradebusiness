"""潜客触达资格规则测试。"""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services.lead_generation_service import LeadGenerationService


def test_invalid_lead_cannot_be_contacted() -> None:
    """无效潜客不能进入发送或跟进流程。"""
    with pytest.raises(HTTPException) as exc_info:
        LeadGenerationService.ensure_lead_contactable(SimpleNamespace(status="invalid"))

    assert exc_info.value.status_code == 409


def test_active_lead_can_be_contacted() -> None:
    """有效潜客允许继续触达。"""
    LeadGenerationService.ensure_lead_contactable(SimpleNamespace(status="new"))


def test_opted_out_lead_cannot_be_contacted() -> None:
    """已退订潜客不能进入发送或跟进流程。"""
    with pytest.raises(HTTPException) as exc_info:
        LeadGenerationService.ensure_lead_contactable(
            SimpleNamespace(status="new", do_not_contact=True)
        )

    assert exc_info.value.status_code == 409


def test_opted_in_lead_can_be_contacted() -> None:
    """恢复联系后潜客可以继续触达。"""
    LeadGenerationService.ensure_lead_contactable(
        SimpleNamespace(status="new", do_not_contact=False)
    )
