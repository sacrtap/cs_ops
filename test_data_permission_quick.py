"""
数据权限过滤器快速验证脚本

用于在完整测试套件修复前验证核心实现
"""
import sys
import os

# 添加 backend 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, select, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base, class_mapper
from sqlalchemy.event import listens_for
from typing import Optional

Base = declarative_base()

# 简化的 Customer 模型用于测试
class Customer(Base):
    __tablename__ = 'customers_test'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    sales_rep_id = Column(Integer)
    org_id = Column(Integer)

# 简化的 User 模型
class User(Base):
    __tablename__ = 'users_test'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    role = Column(String(20))
    org_id = Column(Integer)

# 创建内存数据库
engine = create_engine('sqlite:///:memory:', echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

print("=" * 60)
print("数据权限过滤器验证脚本")
print("=" * 60)

# 测试数据
print("\n✅ 步骤 1: 创建测试数据...")
session = SessionLocal()

admin_user = User(id=1, username='admin', role='admin', org_id=None)
manager_user = User(id=2, username='manager', role='manager', org_id=5)
sales_user1 = User(id=3, username='sales1', role='sales', org_id=5)
sales_user2 = User(id=4, username='sales2', role='sales', org_id=5)

customers = [
    Customer(id=1, name='客户 1', sales_rep_id=3, org_id=5),  # sales1 的客户
    Customer(id=2, name='客户 2', sales_rep_id=3, org_id=5),  # sales1 的客户
    Customer(id=3, name='客户 3', sales_rep_id=4, org_id=5),  # sales2 的客户
    Customer(id=4, name='客户 4', sales_rep_id=4, org_id=5),  # sales2 的客户
    Customer(id=5, name='客户 5', sales_rep_id=3, org_id=6),  # sales1 的客户（不同组织）
]

session.add_all([admin_user, manager_user, sales_user1, sales_user2] + customers)
session.commit()
print(f"   创建了 {len(customers)} 个客户和 4 个用户")

# 验证函数
def verify_filter(user: User, expected_count: int, description: str):
    """验证过滤器行为"""
    print(f"\n   测试：{description}")
    print(f"   用户：{user.username} (role={user.role}, org_id={user.org_id}, id={user.id})")
    
    # 设置用户上下文
    from app.utils.data_permission_filter import (
        set_current_user_context,
        apply_data_permission_filter
    )
    
    user_context = set_current_user_context(
        user_id=user.id,
        role=user.role,
        org_id=user.org_id
    )
    
    # 创建新会话应用过滤器
    test_session = SessionLocal()
    
    # 应用过滤器到查询
    query = select(Customer)
    filtered_query = apply_data_permission_filter(query, Customer, user_context)
    
    result = test_session.execute(filtered_query)
    filtered_customers = result.scalars().all()
    
    print(f"   预期：{expected_count} 个客户")
    print(f"   实际：{len(filtered_customers)} 个客户")
    
    if len(filtered_customers) == expected_count:
        print(f"   ✅ PASS")
        test_session.close()
        return True
    else:
        print(f"   ❌ FAIL - 客户列表：{[c.name for c in filtered_customers]}")
        test_session.close()
        return False

# 运行测试
print("\n" + "=" * 60)
print("运行数据权限过滤器测试")
print("=" * 60)

results = []

# 测试 1: Admin 应该看到所有客户
results.append(verify_filter(
    admin_user,
    expected_count=5,
    description="Admin 用户 - 应该看到所有客户"
))

# 测试 2: Manager 应该看到本组织所有客户
results.append(verify_filter(
    manager_user,
    expected_count=4,  # org_id=5 的 4 个客户
    description="Manager 用户 - 应该看到本组织所有客户"
))

# 测试 3: Sales1 应该只看到自己的客户
results.append(verify_filter(
    sales_user1,
    expected_count=3,  # sales_rep_id=3 的 3 个客户（客户 1, 2, 5）
    description="Sales 用户 1 - 应该只看到自己的客户（包括不同组织）"
))

# 测试 4: Sales2 应该只看到自己的客户
results.append(verify_filter(
    sales_user2,
    expected_count=2,  # sales_rep_id=4 的 2 个客户
    description="Sales 用户 2 - 应该只看到自己的客户"
))

# 汇总结果
print("\n" + "=" * 60)
print("测试结果汇总")
print("=" * 60)
passed = sum(results)
total = len(results)
print(f"通过：{passed}/{total}")

if passed == total:
    print("\n🎉 所有测试通过！数据权限过滤器实现正确！")
    sys.exit(0)
else:
    print(f"\n❌ {total - passed} 个测试失败")
    sys.exit(1)
