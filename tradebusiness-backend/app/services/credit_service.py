"""积分扣减服务。"""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.billing import CreditTransaction, CreditWallet

DEFAULT_CREDIT_BALANCE = 100


class CreditService:
    """统一处理积分余额和流水。"""

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def validate_debit_amount(amount: int) -> None:
        """确保扣费金额为正数，避免通过负数反向增加余额。"""
        if amount <= 0:
            raise HTTPException(status_code=400, detail="扣费积分必须为正数")

    async def debit(self, user_id: str, amount: int, action: str, description: str) -> CreditWallet:
        self.validate_debit_amount(amount)
        result = await self.session.execute(
            select(CreditWallet).where(CreditWallet.user_id == user_id).with_for_update()
        )
        wallet = result.scalar_one_or_none()
        if not wallet:
            wallet = CreditWallet(user_id=user_id, balance=DEFAULT_CREDIT_BALANCE)
            self.session.add(wallet)
            await self.session.flush()
        if wallet.balance < amount:
            raise HTTPException(status_code=402, detail=f"积分不足，需要 {amount} 积分")
        wallet.balance -= amount
        self.session.add(
            CreditTransaction(
                user_id=user_id,
                amount=-amount,
                balance_after=wallet.balance,
                action=action,
                description=description,
            )
        )
        await self.session.flush()
        return wallet
