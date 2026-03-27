import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import verify_password, get_password_hash, create_access_token
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    def register(db: Session, user_data: UserCreate) -> User:
        """用户注册"""
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        
        # 创建新用户（邮箱统一小写存储，便于登录时用 ilike 匹配）
        email_lower = (user_data.email or "").strip().lower()
        db_user = User(
            username=user_data.username,
            email=email_lower,
            password_hash=get_password_hash(user_data.password),
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def login(db: Session, login_data: UserLogin) -> dict:
        """用户登录"""
        lookup = (login_data.username or "").strip()
        if not lookup:
            logger.info("登录失败: 用户名为空")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        # 用户名精确匹配，邮箱忽略大小写匹配（与常见邮箱登录行为一致）
        user = db.query(User).filter(
            (User.username == lookup)
            | (User.email.ilike(lookup))
        ).first()

        if not user:
            logger.info("登录失败: 未找到用户 (username/email=%r)", lookup)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )

        if not verify_password(login_data.password, user.password_hash):
            logger.info("登录失败: 密码错误 (user_id=%s)", user.id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 更新最后登录时间
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
        
        # 生成访问令牌
        access_token = create_access_token(data={"sub": user.username})
        
        return {
            "access_token": access_token,
            "user": user
        }
