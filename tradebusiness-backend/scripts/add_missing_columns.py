"""
添加缺失的字段到scraped_leads表
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.db.session import engine


async def add_missing_columns():
    """添加缺失的列到scraped_leads表"""

    try:
        print("连接数据库...")

        async with engine.begin() as conn:
            # 检查表是否已存在
            result = await conn.execute(text("SHOW TABLES LIKE 'scraped_leads'"))

            if not result.fetchone():
                print("❌ 表 scraped_leads 不存在")
                return

            print("✅ 表 scraped_leads 已存在")

            # 检查需要添加的列
            columns_to_add = {
                "source_url": "VARCHAR(500) NULL COMMENT '来源URL'",
                "company_name_en": "VARCHAR(200) NULL COMMENT '英文名称'",
                "city": "VARCHAR(100) NULL COMMENT '城市'",
                "whatsapp": "VARCHAR(50) NULL COMMENT 'WhatsApp'",
                "website": "VARCHAR(200) NULL COMMENT '网站'",
                "business_type": "VARCHAR(50) NULL COMMENT '业务类型'",
                "description": "TEXT NULL COMMENT '公司描述'",
                "reviewed_at": "DATETIME NULL COMMENT '审核时间'",
                "imported_at": "DATETIME NULL COMMENT '导入时间'",
                "matched_by": "CHAR(36) NULL COMMENT '匹配/导入操作人ID'",
                "duplicate_of": "CHAR(36) NULL COMMENT '重复的scraped_lead ID'",
                "similarity_score": "INT NULL COMMENT '与重复记录的相似度（0-100）'",
            }

            # 获取现有列
            existing_columns = await conn.execute(text("SHOW COLUMNS FROM scraped_leads"))
            existing_column_names = {row[0] for row in existing_columns}

            # 添加缺失的列
            added_count = 0
            for column_name, column_def in columns_to_add.items():
                if column_name not in existing_column_names:
                    print(f"添加列: {column_name}")
                    await conn.execute(
                        text(f"ALTER TABLE scraped_leads ADD COLUMN {column_name} {column_def}")
                    )
                    added_count += 1
                else:
                    print(f"列 {column_name} 已存在，跳过")

            # 检查并添加索引
            indexes_to_add = {
                "idx_company_name": "ALTER TABLE scraped_leads ADD INDEX idx_company_name (company_name)",
                "idx_country_code": "ALTER TABLE scraped_leads ADD INDEX idx_country_code (country_code)",
                "idx_scraping_task": "ALTER TABLE scraped_leads ADD INDEX idx_scraping_task (scraping_task_id)",
            }

            # 获取现有索引
            existing_indexes = await conn.execute(text("SHOW INDEX FROM scraped_leads"))
            existing_index_names = {row[2] for row in existing_indexes}

            # 添加缺失的索引
            for index_name, index_sql in indexes_to_add.items():
                if index_name not in existing_index_names:
                    print(f"添加索引: {index_name}")
                    await conn.execute(text(index_sql))
                else:
                    print(f"索引 {index_name} 已存在，跳过")

            print(f"✅ 成功添加 {added_count} 个列")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("添加缺失的字段到 scraped_leads 表")
    print("=" * 60)
    print()

    asyncio.run(add_missing_columns())

    print()
    print("=" * 60)
    print("完成！")
    print("=" * 60)
