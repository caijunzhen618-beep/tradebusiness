"""积分与钱包 API。"""

import hashlib
import hmac
import json
import os
import time

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.audit import audit_event
from app.models.billing import (
    CreditTransaction,
    CreditWallet,
    PaymentOrder,
    SubscriptionPlan,
    UserSubscription,
)
from app.models.user import User
from app.schemas.billing import (
    CreditAdjustment,
    CreditTransactionResponse,
    CreditWalletResponse,
    PaymentOrderCreate,
    PaymentOrderResponse,
    SubscribeRequest,
    SubscriptionPlanResponse,
    UserSubscriptionResponse,
)
from app.services.credit_service import DEFAULT_CREDIT_BALANCE

router = APIRouter()


async def get_or_create_wallet(user_id: str, db: AsyncSession) -> CreditWallet:
    result = await db.execute(select(CreditWallet).where(CreditWallet.user_id == user_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        wallet = CreditWallet(user_id=user_id, balance=DEFAULT_CREDIT_BALANCE)
        db.add(wallet)
        await db.flush()
    return wallet


@router.get("/wallet", response_model=CreditWalletResponse)
async def get_wallet(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await get_or_create_wallet(str(current_user.id), db)


@router.get("/transactions", response_model=list[CreditTransactionResponse])
async def list_transactions(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CreditTransaction)
        .where(CreditTransaction.user_id == current_user.id)
        .order_by(CreditTransaction.created_at.desc())
        .limit(100)
    )
    return list(result.scalars().all())


@router.post("/adjust", response_model=CreditWalletResponse)
async def adjust_credits(
    data: CreditAdjustment,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    wallet = await get_or_create_wallet(str(current_user.id), db)
    if wallet.balance + data.amount < 0:
        raise HTTPException(status_code=400, detail="积分余额不足")
    wallet.balance += data.amount
    db.add(
        CreditTransaction(
            user_id=str(current_user.id),
            amount=data.amount,
            balance_after=wallet.balance,
            action=data.action,
            description=data.description,
        )
    )
    await db.flush()
    return wallet


@router.get("/plans", response_model=list[SubscriptionPlanResponse])
async def list_plans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SubscriptionPlan)
        .where(SubscriptionPlan.is_active.is_(True))
        .order_by(SubscriptionPlan.price.asc())
    )
    return list(result.scalars().all())


@router.get("/subscription", response_model=UserSubscriptionResponse | None)
async def get_subscription(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UserSubscription).where(UserSubscription.user_id == current_user.id)
    )
    return result.scalar_one_or_none()


@router.post("/subscription", response_model=UserSubscriptionResponse)
async def subscribe(
    data: SubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from fastapi import HTTPException

    from app.config import settings

    if settings.ENVIRONMENT.lower() in {"prod", "production"}:
        raise HTTPException(
            status_code=410,
            detail="Direct subscription activation is disabled in production; complete payment first",
        )
    plan = await db.scalar(
        select(SubscriptionPlan).where(
            SubscriptionPlan.id == data.plan_id, SubscriptionPlan.is_active.is_(True)
        )
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    subscription = await db.scalar(
        select(UserSubscription).where(UserSubscription.user_id == current_user.id)
    )
    if subscription:
        subscription.plan_id = plan.id
        subscription.status = "active"
    else:
        subscription = UserSubscription(
            user_id=str(current_user.id), plan_id=plan.id, status="active"
        )
        db.add(subscription)
    await db.flush()
    return subscription


@router.post("/orders", response_model=PaymentOrderResponse, status_code=201)
async def create_payment_order(
    data: PaymentOrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from fastapi import HTTPException

    plan = await db.scalar(
        select(SubscriptionPlan).where(
            SubscriptionPlan.id == data.plan_id, SubscriptionPlan.is_active.is_(True)
        )
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    order = PaymentOrder(
        user_id=str(current_user.id),
        plan_id=plan.id,
        amount=plan.price,
        provider=data.provider,
        status="pending",
    )
    db.add(order)
    await db.flush()
    return order


@router.get("/orders", response_model=list[PaymentOrderResponse])
async def list_payment_orders(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PaymentOrder)
        .where(PaymentOrder.user_id == current_user.id)
        .order_by(PaymentOrder.created_at.desc())
        .limit(100)
    )
    return list(result.scalars().all())


@router.post("/orders/{order_id}/callback", response_model=PaymentOrderResponse)
async def payment_callback(
    order_id: str,
    status_value: str = Query(..., alias="status"),
    external_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """开发环境支付回调；生产环境必须使用平台 webhook。"""
    from app.config import settings

    if settings.ENVIRONMENT.lower() in {"prod", "production"}:
        raise HTTPException(
            status_code=410, detail="Development payment callback is disabled in production"
        )
    from fastapi import HTTPException

    order = await db.scalar(select(PaymentOrder).where(PaymentOrder.id == order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Payment order not found")
    if status_value == "paid" and order.status != "paid":
        plan = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.id == order.plan_id))
        wallet = await get_or_create_wallet(order.user_id, db)
        wallet.balance += plan.credits
        db.add(
            CreditTransaction(
                user_id=order.user_id,
                amount=plan.credits,
                balance_after=wallet.balance,
                action="subscription_credit",
                description=f"套餐 {plan.name} 充值",
            )
        )
        subscription = await db.scalar(
            select(UserSubscription).where(UserSubscription.user_id == order.user_id)
        )
        if subscription:
            subscription.plan_id = plan.id
            subscription.status = "active"
        else:
            db.add(UserSubscription(user_id=order.user_id, plan_id=plan.id, status="active"))
    order.status = status_value
    order.external_id = external_id or order.external_id
    await db.flush()
    audit_event(
        "payment_callback_processed",
        user_id=str(order.user_id),
        resource_type="payment_order",
        resource_id=str(order.id),
        metadata={"status": order.status, "provider": order.provider},
    )
    return order


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Stripe 生产 webhook：原始 body 验签后处理 checkout.session.completed。"""
    from fastapi import HTTPException

    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    if not secret or not signature:
        raise HTTPException(status_code=400, detail="Stripe webhook is not configured")
    values: dict[str, list[str]] = {}
    for item in signature.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        values.setdefault(key.strip(), []).append(value.strip())
    timestamps = values.get("t", [])
    signatures = values.get("v1", [])
    if len(timestamps) != 1 or not signatures:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook timestamp")
    timestamp = timestamps[0]
    try:
        timestamp_value = int(timestamp)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook timestamp") from exc
    if abs(int(time.time()) - timestamp_value) > 300:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook timestamp")
    signed = timestamp.encode() + b"." + payload
    expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    if not any(hmac.compare_digest(expected, provided) for provided in signatures):
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook signature")
    event = json.loads(payload)
    if event.get("type") != "checkout.session.completed":
        return {"received": True}
    session = event.get("data", {}).get("object", {})
    if session.get("payment_status") != "paid":
        return {"received": True, "ignored": "payment_not_completed"}
    metadata = session.get("metadata", {})
    order_id = metadata.get("payment_order_id")
    if not order_id:
        raise HTTPException(status_code=400, detail="Missing payment_order_id")
    order = await db.scalar(
        select(PaymentOrder).where(PaymentOrder.id == order_id).with_for_update()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Payment order not found")
    if order.status != "paid":
        plan = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.id == order.plan_id))
        wallet = await get_or_create_wallet(order.user_id, db)
        wallet.balance += plan.credits
        db.add(
            CreditTransaction(
                user_id=order.user_id,
                amount=plan.credits,
                balance_after=wallet.balance,
                action="subscription_credit",
                description=f"Stripe 套餐 {plan.name} 充值",
            )
        )
        order.status = "paid"
        order.provider = "stripe"
        order.external_id = session.get("id")
        subscription = await db.scalar(
            select(UserSubscription).where(UserSubscription.user_id == order.user_id)
        )
        if subscription:
            subscription.plan_id = plan.id
            subscription.status = "active"
        else:
            db.add(UserSubscription(user_id=order.user_id, plan_id=plan.id, status="active"))
        await db.flush()
        audit_event(
            "stripe_payment_completed",
            user_id=str(order.user_id),
            resource_type="payment_order",
            resource_id=str(order.id),
            metadata={"provider": "stripe", "external_id": str(order.external_id)},
        )
    return {"received": True}


@router.post("/orders/{order_id}/stripe-session", response_model=dict)
async def create_stripe_session(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建 Stripe Checkout Session。"""
    import httpx
    from fastapi import HTTPException

    secret = os.getenv("STRIPE_SECRET_KEY", "")
    if not secret:
        raise HTTPException(status_code=503, detail="Stripe is not configured")
    from app.config import settings

    success_url = os.getenv("STRIPE_SUCCESS_URL", "http://localhost:3000/settings/plans?success=1")
    cancel_url = os.getenv("STRIPE_CANCEL_URL", "http://localhost:3000/settings/plans?cancelled=1")
    if settings.ENVIRONMENT.lower() in {"prod", "production"} and (
        "localhost" in success_url or "localhost" in cancel_url
    ):
        raise HTTPException(
            status_code=503,
            detail="STRIPE_SUCCESS_URL and STRIPE_CANCEL_URL must be configured for production",
        )
    order = await db.scalar(
        select(PaymentOrder).where(
            PaymentOrder.id == order_id, PaymentOrder.user_id == current_user.id
        )
    )
    if not order or order.status != "pending":
        raise HTTPException(status_code=404, detail="Pending payment order not found")
    plan = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.id == order.plan_id))
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    form = {
        "mode": "payment",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "line_items[0][price_data][currency]": os.getenv("STRIPE_CURRENCY", "usd"),
        "line_items[0][price_data][product_data][name]": plan.name,
        "line_items[0][price_data][unit_amount]": str(plan.price * 100),
        "line_items[0][price_data][product_data][description]": f"{plan.credits} credits",
        "line_items[0][quantity]": "1",
        "metadata[payment_order_id]": order.id,
        "metadata[plan_id]": plan.id,
        "metadata[user_id]": str(current_user.id),
    }
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            "https://api.stripe.com/v1/checkout/sessions", data=form, auth=(secret, "")
        )
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="Stripe Checkout Session creation failed")
    session = response.json()
    order.external_id = session.get("id")
    order.provider = "stripe"
    await db.flush()
    audit_event(
        "stripe_checkout_created",
        user_id=str(current_user.id),
        resource_type="payment_order",
        resource_id=str(order.id),
        metadata={"provider": "stripe"},
    )
    return {
        "order_id": order.id,
        "session_id": session.get("id"),
        "checkout_url": session.get("url"),
    }
