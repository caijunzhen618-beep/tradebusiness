"""检查数据库中的表"""

import asyncio

from sqlalchemy import text

from app.db.session import async_session_maker


async def check_tables():
    """检查哪些表存在"""
    async with async_session_maker() as session:
        result = await session.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]

        print("=" * 60)
        print("数据库中现有的表:")
        print("=" * 60)
        for table in sorted(tables):
            print(f"  ✓ {table}")

        print("\n" + "=" * 60)
        print("检查需要的表:")
        print("=" * 60)

        required_tables = [
            "users",
            "customers",
            "emails",
            "email_templates",
            "tasks",
            "notifications",
            "scraping_tasks",
        ]

        missing_tables = []
        for table in required_tables:
            if table in tables:
                print(f"  ✓ {table} - 存在")
            else:
                print(f"  ✗ {table} - 缺失")
                missing_tables.append(table)

        if missing_tables:
            print(f"\n❌ 缺失的表: {', '.join(missing_tables)}")
            print("需要创建这些表!")
        else:
            print("\n✅ 所有表都存在")


if __name__ == "__main__":
    asyncio.run(check_tables())
