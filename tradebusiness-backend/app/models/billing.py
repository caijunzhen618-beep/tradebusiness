"""积分钱包和流水模型。"""

from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class CreditWallet(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "credit_wallets"
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class CreditTransaction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "credit_transactions"
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class SubscriptionPlan(Base, UUIDMixin, TimestampMixin):
    """积分套餐。"""

    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    price: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    credits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    interval: Mapped[str] = mapped_column(String(20), default="month", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class UserSubscription(Base, UUIDMixin, TimestampMixin):
    """用户当前订阅。"""

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("subscription_plans.id", ondelete="RESTRICT"), index=True
    )
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)


class PaymentOrder(Base, UUIDMixin, TimestampMixin):
    """支付订单预留。"""

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("subscription_plans.id", ondelete="RESTRICT"), index=True
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    provider: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False, index=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
