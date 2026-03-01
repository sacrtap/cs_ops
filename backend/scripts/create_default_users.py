#!/usr/bin/env python3
"""
创建默认用户数据
"""
import asyncio
import sys
sys.path.insert(0, '/Users/sacrtap/Documents/trae_projects/cs_ops/backend')

from app.database import async_session_maker
from app.models.user import User
import bcrypt

def get_password_hash(password: str) -> str:
    """密码哈希"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


async def create_default_users():
    """创建默认用户"""
    async with async_session_maker() as session:
        # 检查是否已有用户
        from sqlalchemy import select
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        if len(users) > 0:
            print(f'✓ 已存在 {len(users)} 个用户，无需创建')
            return
        
        print('创建默认用户...')
        
        # 创建 Admin 用户
        admin = User(
            username='admin',
            password_hash=get_password_hash('admin123'),
            real_name='系统管理员',
            role='admin',
            email='admin@example.com'
        )
        
        # 创建 Manager 用户
        manager = User(
            username='manager',
            password_hash=get_password_hash('manager123'),
            real_name='经理',
            role='manager',
            email='manager@example.com'
        )
        
        # 创建 Sales 用户
        sales = User(
            username='sales',
            password_hash=get_password_hash('sales123'),
            real_name='销售代表',
            role='sales',
            email='sales@example.com'
        )
        
        session.add_all([admin, manager, sales])
        await session.commit()
        
        print('✓ 已创建 3 个默认用户:')
        print('  - admin / admin123 (管理员)')
        print('  - manager / manager123 (经理)')
        print('  - sales / sales123 (销售)')


if __name__ == '__main__':
    asyncio.run(create_default_users())
