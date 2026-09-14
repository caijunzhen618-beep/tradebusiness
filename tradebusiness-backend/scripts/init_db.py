"""
数据库初始化脚本
创建数据库表和初始数据
"""

import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))


from app.config import settings
from app.core.security import hash_password
from app.db.session import async_session_maker
from app.models.base import Base
from app.models.user import User, UserRole


async def create_tables():
    """创建所有数据库表"""
    from app.db.session import engine

    async with engine.begin() as conn:
        # 导入所有模型，确保它们被注册到 Base.metadata
        from app.models import user  # noqa

        await conn.run_sync(Base.metadata.create_all)
        await _ensure_lead_contact_policy_columns(conn)

    print("✓ Database tables created successfully")


async def _ensure_lead_contact_policy_columns(conn) -> None:
    """为已有数据库补齐潜客退订字段。"""
    columns = (
        ("do_not_contact", "BOOLEAN NOT NULL DEFAULT FALSE"),
        ("do_not_contact_reason", "VARCHAR(300) NULL"),
    )
    for column_name, column_definition in columns:
        result = await conn.execute(
            text(
                "SELECT COUNT(*) FROM information_schema.columns "
                "WHERE table_schema = DATABASE() AND table_name = 'leads' "
                "AND column_name = :column_name"
            ),
            {"column_name": column_name},
        )
        if result.scalar_one() == 0:
            await conn.execute(
                text(f"ALTER TABLE leads ADD COLUMN {column_name} " f"{column_definition}")
            )


async def create_initial_users():
    """创建初始用户数据"""
    async with async_session_maker() as session:
        # 检查是否已有管理员用户
        from sqlalchemy import select

        result = await session.execute(select(User).where(User.username == "admin"))
        admin_user = result.scalar_one_or_none()

        if admin_user:
            print("✓ Admin user already exists")
            return

        # 创建管理员用户
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hash_password("Admin123"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
            is_superuser=True,
        )
        session.add(admin)

        # 创建测试业务员
        sales = User(
            username="sales01",
            email="sales01@example.com",
            hashed_password=hash_password("Sales123"),
            full_name="Sales Representative 01",
            role=UserRole.SALES,
            is_active=True,
        )
        session.add(sales)

        await session.commit()
        print("✓ Initial users created successfully")
        print("  - Admin: username='admin', password='Admin123'")
        print("  - Sales: username='sales01', password='Sales123'")


async def init_db():
    """初始化数据库"""
    print("=" * 50)
    print("Initializing database...")
    print("=" * 50)

    try:
        await create_tables()
        await create_initial_users()

        print("=" * 50)
        print("Database initialization completed!")
        print("=" * 50)
    finally:
        # 在事件循环关闭前显式释放连接池，避免 aiomysql 在 __del__ 中
        # 尝试使用已关闭的事件循环，从而产生 RuntimeError 警告。
        from app.db.session import engine

        await engine.dispose()


def reset_db():
    """重置数据库（删除所有数据并重新创建）。"""
    answer = input("This will delete all data. Are you sure? [y/N] ")
    if answer.lower() == "y":
        asyncio.run(init_db())


def seed_db():
    """填充初始数据（不删除现有数据）。"""
    asyncio.run(create_initial_users())


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        reset_db()
    else:
        asyncio.run(init_db())
