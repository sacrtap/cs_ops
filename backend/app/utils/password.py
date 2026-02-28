"""
密码服务 - bcrypt 加密与验证
"""
from passlib.context import CryptContext
from app.config.settings import settings


# bcrypt 密码上下文
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS,
)


def hash_password(password: str) -> str:
    """
    对密码进行 bcrypt 加密
    
    Args:
        password: 明文密码
        
    Returns:
        str: bcrypt 加密后的密码哈希
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: bcrypt 加密的密码哈希
        
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    """
    检查密码哈希是否需要重新加密（例如 rounds 升级）
    
    Args:
        hashed_password: 当前的密码哈希
        
    Returns:
        bool: 是否需要重新加密
    """
    return pwd_context.needs_update(hashed_password)
