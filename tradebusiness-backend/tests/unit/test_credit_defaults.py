"""积分初始余额策略测试。"""

import pytest
from fastapi import HTTPException

from app.services.credit_service import DEFAULT_CREDIT_BALANCE, CreditService


def test_credit_default_balance_is_positive_and_shared() -> None:
    """首次查询和首次扣费应使用统一的正向初始额度。"""
    assert DEFAULT_CREDIT_BALANCE == 100


def test_credit_debit_rejects_non_positive_amount() -> None:
    """扣费金额不能为零或负数。"""
    with pytest.raises(HTTPException) as exc_info:
        CreditService.validate_debit_amount(0)

    assert exc_info.value.status_code == 400
