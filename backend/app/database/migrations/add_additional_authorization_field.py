"""
数据库迁移脚本 - 添加额外授权字段

迁移内容:
- 在 role_permissions 表中添加 is_additional 字段
- 区分直接权限和额外授权

执行方式:
    cd backend
    source venv/bin/activate
    python app/database/migrations/add_additional_authorization_field.py
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.database import engine


async def migrate():
    """执行数据库迁移"""
    
    print("开始迁移：添加额外授权字段...")
    
    async with engine.begin() as conn:
        try:
            # 1. 添加 is_additional 字段
            print("添加 is_additional 字段到 role_permissions 表...")
            await conn.execute(text("""
                ALTER TABLE role_permissions 
                ADD COLUMN IF NOT EXISTS is_additional BOOLEAN NOT NULL DEFAULT FALSE
            """))
            print("✅ is_additional 字段添加成功")
            
            # 2. 添加索引优化查询
            print("添加 is_additional 索引...")
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_role_permissions_is_additional 
                ON role_permissions(is_additional)
            """))
            print("✅ 索引添加成功")
            
            # 3. 添加注释
            print("添加字段注释...")
            await conn.execute(text("""
                COMMENT ON COLUMN role_permissions.is_additional IS '是否为额外授权（true=额外授权，false=继承权限）'
            """))
            print("✅ 字段注释添加成功")
            
            print("\n🎉 迁移完成！")
            print("\n迁移摘要:")
            print("- 添加 is_additional 字段（BOOLEAN, DEFAULT FALSE）")
            print("- 添加索引优化额外授权查询")
            print("- 现有权限默认不是额外授权（FALSE）")
            
        except Exception as e:
            print(f"\n❌ 迁移失败：{e}")
            raise


if __name__ == "__main__":
    print("=" * 60)
    print("数据库迁移：添加额外授权字段")
    print("=" * 60)
    print()
    
    asyncio.run(migrate())
    
    print()
    print("=" * 60)
    print("迁移执行完毕")
    print("=" * 60)
