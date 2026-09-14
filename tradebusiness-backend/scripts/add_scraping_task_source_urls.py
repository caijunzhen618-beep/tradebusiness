"""为采集任务表补充 source_urls 字段。"""

import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import engine


async def main() -> None:
    """补充 source_urls 字段，并从旧 config 中回填来源地址。"""
    async with engine.begin() as conn:
        column_result = await conn.execute(text("""
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                  AND table_name = 'scraping_tasks'
                  AND column_name = 'source_urls'
                """))
        column_exists = column_result.scalar() or 0

        if not column_exists:
            await conn.execute(text("""
                    ALTER TABLE scraping_tasks
                    ADD COLUMN source_urls JSON NULL COMMENT '采集数据来源地址列表'
                    """))
            await conn.execute(text("""
                    UPDATE scraping_tasks
                    SET source_urls = COALESCE(
                        JSON_EXTRACT(config, '$.source_urls'),
                        JSON_ARRAY()
                    )
                    """))
            await conn.execute(text("""
                    ALTER TABLE scraping_tasks
                    MODIFY COLUMN source_urls JSON NOT NULL COMMENT '采集数据来源地址列表'
                    """))

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
