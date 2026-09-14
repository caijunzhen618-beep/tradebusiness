"""创建 AI 获客模块数据表。"""

import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import engine
from app.models.base import Base
from app.models.lead_generation import (  # noqa: F401
    CompanyResearchReport,
    Lead,
    LeadContact,
    LeadSearchTask,
    SalesCopy,
)


async def main() -> None:
    """创建缺失的数据表。"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
