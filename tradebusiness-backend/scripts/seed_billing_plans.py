"""初始化积分套餐。"""

import asyncio

from sqlalchemy import select

from app.db.session import engine
from app.models.base import Base
from app.models.billing import SubscriptionPlan

PLANS = [("Free", 0, 100), ("Starter", 49, 5000), ("Scale", 99, 12000), ("Pro", 199, 30000)]


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with engine.begin() as conn:
        from sqlalchemy.ext.asyncio import AsyncSession

        async with AsyncSession(bind=conn) as session:
            for name, price, credits in PLANS:
                exists = await session.scalar(
                    select(SubscriptionPlan).where(SubscriptionPlan.name == name)
                )
                if not exists:
                    session.add(
                        SubscriptionPlan(name=name, price=price, credits=credits, interval="month")
                    )
            await session.commit()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
