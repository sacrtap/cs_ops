"""
Token 黑名单清理定时任务

用途：
- 定期清理过期的黑名单记录
- 释放数据库空间
- 保持系统性能

使用方法：
1. 手动执行：python -m app.jobs.cleanup_blacklist
2. 定时任务（cron）：0 2 * * * cd /path/to/backend && python -m app.jobs.cleanup_blacklist
3. 系统服务（systemd）：配置为每日运行
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.database import get_db_session
from app.services.token_blacklist_service import TokenBlacklistService
from datetime import datetime, timezone


async def cleanup_blacklist(days_old: int = 30):
    """
    清理黑名单记录
    
    Args:
        days_old: 清理多少天之前的记录，默认 30 天
    """
    print(f"[{datetime.now(timezone.utc).isoformat()}] 开始清理黑名单记录...")
    
    try:
        # 获取数据库会话
        async with get_db_session() as session:
            service = TokenBlacklistService(session)
            
            # 清理过期记录
            expired_count = await service.cleanup_expired()
            print(f"  - 清理过期记录：{expired_count} 条")
            
            # 清理旧记录
            old_count = await service.cleanup_old_blacklist_records(days_old)
            print(f"  - 清理{days_old}天前的记录：{old_count} 条")
            
            total = expired_count + old_count
            print(f"[{datetime.now(timezone.utc).isoformat()}] 清理完成，共删除 {total} 条记录")
            
    except Exception as e:
        print(f"[{datetime.now(timezone.utc).isoformat()}] 清理失败：{e}")
        raise


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='清理 Token 黑名单记录')
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='清理多少天之前的记录（默认：30）'
    )
    
    args = parser.parse_args()
    
    print(f"=== Token 黑名单清理任务 ===")
    print(f"配置：清理 {args.days} 天前的记录")
    print()
    
    # 运行异步任务
    asyncio.run(cleanup_blacklist(args.days))


if __name__ == '__main__':
    main()
