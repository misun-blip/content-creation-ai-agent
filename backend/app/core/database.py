from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 根据数据库类型配置引擎参数
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

if _is_sqlite:
    # SQLite: 用于本地开发和测试
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
    )
else:
    # MySQL: 生产环境，启用连接池优化
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,       # 每次使用前检测连接是否存活
        pool_size=10,             # 连接池核心连接数
        max_overflow=20,          # 超出 pool_size 后允许的最大临时连接数
        pool_recycle=1800,        # 连接回收时间(秒)，防止 MySQL 8h 超时断开
        pool_timeout=30,          # 获取连接的超时时间(秒)
        echo=settings.DEBUG,
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """依赖注入：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

