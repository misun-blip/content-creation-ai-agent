# backend/app/initial_data.py
import logging
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)


def init_db_data():
    """初始化数据库表及基础数据（仅创建管理员账号）"""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # ── 管理员账号（确保至少有一个可登录用户）────────────────
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            logger.info("正在创建初始管理员账号...")
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password_hash=get_password_hash("admin123"),
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            logger.info("初始管理员账号就绪，默认登录：admin / admin123")
        else:
            logger.info("管理员账号已存在，跳过创建")

    except Exception as e:
        logger.error(f"初始化数据失败: {e}")
        db.rollback()
    finally:
        db.close()