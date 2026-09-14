from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CreditWalletResponse(BaseModel):
    id: str
    user_id: str
    balance: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class CreditTransactionResponse(BaseModel):
    id: str
    amount: int
    balance_after: int
    action: str
    description: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class CreditAdjustment(BaseModel):
    amount: int = Field(..., ge=-100000, le=100000)
    action: str = "manual_adjustment"
    description: str | None = None


class SubscriptionPlanResponse(BaseModel):
    id: str
    name: str
    price: int
    credits: int
    interval: str
    is_active: bool
    model_config = {"from_attributes": True}


class SubscribeRequest(BaseModel):
    plan_id: str


class UserSubscriptionResponse(BaseModel):
    id: str
    user_id: str
    plan_id: str
    status: str
    model_config = {"from_attributes": True}


class PaymentOrderCreate(BaseModel):
    plan_id: str
    provider: Literal["stripe", "wechat", "alipay", "pending"] = "pending"


class PaymentOrderResponse(BaseModel):
    id: str
    user_id: str
    plan_id: str
    amount: int
    provider: str
    status: str
    external_id: str | None = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
