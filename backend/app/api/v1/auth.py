from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User, UserProfile
from app.schemas.user import UserCreate, UserLogin, ChangePassword
from app.services.auth_service import AuthService
from app.core.security import verify_password, get_password_hash, create_access_token
from fastapi import HTTPException, status

router = APIRouter()

BEIJING_TZ = timezone(timedelta(hours=8))


def to_beijing_iso(dt: datetime | None) -> str | None:
  """
  将后端存储的时间统一转换为北京时间再输出，避免前端/浏览器时区差异导致显示不正确。
  """
  if dt is None:
      return None
  # 若无 tz 信息，按 UTC 处理再转为 +08:00
  if dt.tzinfo is None:
      dt = dt.replace(tzinfo=timezone.utc)
  return dt.astimezone(BEIJING_TZ).isoformat(timespec="seconds")


@router.get("/me", response_model=dict)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """获取当前登录用户信息（需 JWT）"""
    return {
        "code": 200,
        "message": "成功",
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "created_at": to_beijing_iso(current_user.created_at),
            "updated_at": to_beijing_iso(current_user.updated_at),
            "last_login": to_beijing_iso(current_user.last_login_at),
            # 头像路径（相对路径，例如 /uploads/xxx.jpg），前端自行拼接完整 URL
            "avatar": current_user.profile.avatar_url if getattr(current_user, "profile", None) else None,
        },
    }


@router.put("/password", response_model=dict)
async def change_password(
    body: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """修改当前用户密码（需 JWT）"""
    # current_user 来自另一个依赖 Session，可能是 detached 对象；这里用本 Session 重新加载以保证更新可落库
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if not verify_password(body.old_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前密码错误")
    if len(body.new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码至少 6 位")
    user.password_hash = get_password_hash(body.new_password)
    db.commit()
    return {"code": 200, "message": "密码已修改"}


@router.post("/register", response_model=dict)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    user = AuthService.register(db, user_data)
    return {
        "code": 200,
        "message": "注册成功",
        "data": {"id": user.id}
    }

@router.post("/login", response_model=dict)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    result = AuthService.login(db, login_data)
    u = result["user"]
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "token": result["access_token"],
            "user": {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "avatar": u.profile.avatar_url if getattr(u, "profile", None) else None,
                "created_at": to_beijing_iso(u.created_at),
                "updated_at": to_beijing_iso(u.updated_at),
                "last_login": to_beijing_iso(u.last_login_at),
            },
        },
    }


@router.put("/profile", response_model=dict)
async def update_profile(
    payload: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    更新个人资料：目前支持修改用户名与头像。
    修改成功后会颁发新的访问令牌（sub=最新用户名），前端需替换本地 token。
    """
    new_username = (payload.get("username") or "").strip()
    new_avatar = (payload.get("avatar") or "").strip() or None

    # 从当前会话重新获取用户对象，确保是持久化的
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 用户名校验与唯一性检查
    if new_username and new_username != user.username:
        exists = db.query(User).filter(User.username == new_username).first()
        if exists and exists.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被占用",
            )
        user.username = new_username

    # 头像信息存储在独立的 UserProfile 表中
    from sqlalchemy.orm import joinedload
    user_with_profile = db.query(User).options(joinedload(User.profile)).filter(User.id == user.id).first()
    profile = user_with_profile.profile
    if profile is None:
        profile = UserProfile(user_id=user.id, avatar_url=new_avatar)
        db.add(profile)
    else:
        profile.avatar_url = new_avatar

    db.commit()
    db.refresh(user)

    # 颁发新的访问令牌（sub 为最新用户名）
    access_token = create_access_token(data={"sub": user.username})

    return {
        "code": 200,
        "message": "个人资料已更新",
        "data": {
            "token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar": profile.avatar_url if profile else None,
                "created_at": to_beijing_iso(user.created_at),
                "updated_at": to_beijing_iso(user.updated_at),
                "last_login": to_beijing_iso(user.last_login_at),
            },
        },
    }
