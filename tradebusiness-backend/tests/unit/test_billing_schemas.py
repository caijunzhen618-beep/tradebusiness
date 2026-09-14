"""支付请求 Schema 边界测试。"""

import pytest
from pydantic import ValidationError

from app.schemas.billing import PaymentOrderCreate


def test_payment_order_accepts_supported_provider() -> None:
    """支持的支付平台可以创建订单。"""
    order = PaymentOrderCreate(plan_id="plan-1", provider="stripe")

    assert order.provider == "stripe"


def test_payment_order_rejects_unknown_provider() -> None:
    """未知支付平台必须被拒绝。"""
    with pytest.raises(ValidationError):
        PaymentOrderCreate(plan_id="plan-1", provider="unknown")
