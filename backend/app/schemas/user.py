from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


def _strip_str(v: str) -> str:
    return v.strip() if isinstance(v, str) else v


class UserBase(BaseModel):
    username: str
    email: EmailStr

    @field_validator("username")
    @classmethod
    def username_strip(cls, v: str) -> str:
        return _strip_str(v)

    @field_validator("email")
    @classmethod
    def email_strip(cls, v: str) -> str:
        return _strip_str(v)


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_no_leading_trailing(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v


class UserLogin(BaseModel):
    username: str
    password: str

    @field_validator("username", "password")
    @classmethod
    def strip_fields(cls, v: str) -> str:
        return _strip_str(v)

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None


class ChangePassword(BaseModel):
    old_password: str
    new_password: str
