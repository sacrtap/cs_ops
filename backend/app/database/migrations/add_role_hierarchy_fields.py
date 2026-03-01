"""
数据库迁移脚本 - 添加角色层级字段

迁移内容:
- 在 roles 表中添加 level 字段（角色层级）
- 在 roles 表中添加 parent_role_id 字段（父角色 ID，用于权限继承）

执行方式:
    python -m app.database.migrations.add_role_hierarchy_fields
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.database import async_engine


async def migrate():
    """执行数据库迁移"""
    
    print("开始迁移：添加角色层级字段...")
    
    async with async_engine.begin() as conn:
        try:
            # 1. 添加 level 字段
            print("添加 level 字段到 roles 表...")
            await conn.execute(text("""
                ALTER TABLE roles 
                ADD COLUMN IF NOT EXISTS level INTEGER NOT NULL DEFAULT 1
            """))
            print("✅ level 字段添加成功")
            
            # 2. 添加 parent_role_id 字段
            print("添加 parent_role_id 字段到 roles 表...")
            await conn.execute(text("""
                ALTER TABLE roles 
                ADD COLUMN IF NOT EXISTS parent_role_id INTEGER
            """))
            print("✅ parent_role_id 字段添加成功")
            
            # 3. 添加外键约束
            print("添加 parent_role_id 外键约束...")
            await conn.execute(text("""
                ALTER TABLE roles 
                ADD CONSTRAINT fk_roles_parent_role 
                FOREIGN KEY (parent_role_id) 
                REFERENCES roles(id) 
                ON DELETE SET NULL
            """))
            print("✅ 外键约束添加成功")
            
            # 4. 更新现有角色的层级
            print("更新现有角色的层级...")
            await conn.execute(text("""
                UPDATE roles SET level = 4 WHERE name = 'admin'
            """))
            await conn.execute(text("""
                UPDATE roles SET level = 3 WHERE name = 'manager'
            """))
            await conn.execute(text("""
                UPDATE roles SET level = 2 WHERE name = 'specialist'
            """))
            await conn.execute(text("""
                UPDATE roles SET level = 1 WHERE name = 'sales'
            """))
            print("✅ 角色层级更新成功")
            
            # 5. 设置角色继承关系
            print("设置角色继承关系...")
            # 经理的父角色是专员
            await conn.execute(text("""
                UPDATE roles 
                SET parent_role_id = (SELECT id FROM roles WHERE name = 'specialist')
                WHERE name = 'manager'
            """))
            # 专员的父角色是销售
            await conn.execute(text("""
                UPDATE roles 
                SET parent_role_id = (SELECT id FROM roles WHERE name = 'sales')
                WHERE name = 'specialist'
            """))
            # 销售的父角色为 NULL（最低级别）
            await conn.execute(text("""
                UPDATE roles 
                SET parent_role_id = NULL
                WHERE name = 'sales'
            """))
            # Admin 没有父角色（最高级别）
            await conn.execute(text("""
                UPDATE roles 
                SET parent_role_id = NULL
                WHERE name = 'admin'
            """))
            print("✅ 角色继承关系设置成功")
            
            # 6. 添加索引以优化查询性能
            print("添加角色层级索引...")
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_roles_level ON roles(level)
            """))
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_roles_parent_role_id ON roles(parent_role_id)
            """))
            print("✅ 索引添加成功")
            
            print("\n🎉 迁移完成！")
            print("\n迁移摘要:")
            print("- 添加 level 字段（角色层级）")
            print("- 添加 parent_role_id 字段（父角色 ID）")
            print("- 设置角色层级：admin(4) > manager(3) > specialist(2) > sales(1)")
            print("- 设置继承关系：manager → specialist → sales")
            print("- 添加索引优化查询性能")
            
        except Exception as e:
            print(f"\n❌ 迁移失败：{e}")
            raise


if __name__ == "__main__":
    print("=" * 60)
    print("数据库迁移：添加角色层级字段")
    print("=" * 60)
    print()
    
    asyncio.run(migrate())
    
    print()
    print("=" * 60)
    print("迁移执行完毕")
    print("=" * 60)
