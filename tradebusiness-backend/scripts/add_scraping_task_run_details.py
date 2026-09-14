"""Add run detail columns to scraping_tasks.

This script is intentionally idempotent so it can be run during production
deployment without depending on Alembic state.
"""

import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.session import engine  # noqa: E402

TABLE_NAME = "scraping_tasks"


async def column_exists(conn, column_name: str) -> bool:
    """Return whether a column exists in scraping_tasks."""
    result = await conn.execute(
        text("""
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = :table_name
              AND column_name = :column_name
            """),
        {"table_name": TABLE_NAME, "column_name": column_name},
    )
    return bool(result.scalar())


async def add_column_if_missing(conn, column_name: str, definition: str) -> None:
    """Add a column when it is missing."""
    if await column_exists(conn, column_name):
        print(f"{column_name}: exists")
        return
    await conn.execute(text(f"ALTER TABLE {TABLE_NAME} ADD COLUMN {definition}"))
    print(f"{column_name}: added")


async def main() -> None:
    """Apply the migration."""
    try:
        async with engine.begin() as conn:
            await add_column_if_missing(
                conn,
                "progress_current",
                "progress_current INT NOT NULL DEFAULT 0 COMMENT '当前执行步骤'",
            )
            await add_column_if_missing(
                conn,
                "progress_total",
                "progress_total INT NOT NULL DEFAULT 0 COMMENT '总执行步骤'",
            )
            await add_column_if_missing(
                conn,
                "status_message",
                "status_message TEXT NULL COMMENT '当前状态说明'",
            )
            await add_column_if_missing(
                conn,
                "last_run_summary",
                "last_run_summary JSON NULL COMMENT '最近一次执行摘要'",
            )
            await add_column_if_missing(
                conn,
                "execution_log",
                "execution_log JSON NULL COMMENT '执行日志'",
            )
            await conn.execute(text("""
                UPDATE scraping_tasks
                SET execution_log = JSON_ARRAY()
                WHERE execution_log IS NULL
                """))
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
