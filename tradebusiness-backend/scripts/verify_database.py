"""数据库表完整性验证"""

import asyncio

from sqlalchemy import text

from app.db.session import async_session_maker


async def verify_all_tables():
    """验证所有需要的表都存在"""
    async with async_session_maker() as session:
        # 获取所有表
        result = await session.execute(text("SHOW TABLES"))
        all_tables = [row[0] for row in result]

        print("=" * 70)
        print("数据库表完整性验证")
        print("=" * 70)
        print()

        # 定义所有需要的表
        required_tables = {
            "users": {
                "description": "用户表",
                "model": "app.models.user.User",
            },
            "customers": {
                "description": "客户表",
                "model": "app.models.customer.Customer",
            },
            "emails": {
                "description": "邮件表",
                "model": "app.models.email.Email",
            },
            "email_templates": {
                "description": "邮件模板表",
                "model": "app.models.email.EmailTemplate",
            },
            "tasks": {
                "description": "任务表（待办事项）",
                "model": "app.models.task.Task",
            },
            "notifications": {
                "description": "通知表",
                "model": "app.models.notification.Notification",
            },
            "holidays": {
                "description": "节假日表",
                "model": "app.models.holiday.Holiday",
            },
        }

        print("表状态检查:")
        print("-" * 70)

        all_exist = True
        for table_name, info in required_tables.items():
            exists = table_name in all_tables
            status = "✓ 存在" if exists else "✗ 缺失"
            print(f"  {status:10} {table_name:20} - {info['description']}")

            if exists:
                # 检查记录数
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                print(f"             {'':20} 记录数: {count}")

                # 显示表结构
                result = await session.execute(text(f"DESCRIBE {table_name}"))
                columns = result.fetchall()
                print(f"             {'':20} 字段数: {len(columns)}")
            else:
                all_exist = False
            print()

        print("-" * 70)
        print()

        # 检查额外的表
        extra_tables = set(all_tables) - set(required_tables.keys())
        if extra_tables:
            print("额外存在的表（不在模型中）:")
            for table in extra_tables:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  • {table:20} 记录数: {count}")
            print()

        # 最终结论
        print("=" * 70)
        if all_exist:
            print("✅ 所有必需的表都存在，数据库结构完整！")
        else:
            missing = set(required_tables.keys()) - set(all_tables)
            print(f"❌ 缺失的表: {', '.join(missing)}")
            print("需要运行数据库迁移脚本创建缺失的表")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(verify_all_tables())
