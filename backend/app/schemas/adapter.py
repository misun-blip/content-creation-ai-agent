from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class PlatformEnum(str, Enum):
    """支持的平台枚举"""
    DOUYIN = "douyin"
    XIAOHONGSHU = "xiaohongshu"
    WECHAT = "wechat"


class ContentRequest(BaseModel):
    """内容适配请求"""
    content: str = Field(..., description="原始内容")
    platform: PlatformEnum = Field(..., description="目标平台")
    title: Optional[str] = Field(None, description="标题")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    auto_format: bool = Field(True, description="是否自动排版")
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """验证内容字段"""
        if not v or not v.strip():
            raise ValueError("内容不能为空")
        return v.strip()


class FormatResult(BaseModel):
    """格式化结果"""
    title: str
    content: str
    tags: List[str]
    preview: str
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class AdapterResponse(BaseModel):
    """适配响应"""
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="适配成功", description="响应消息")
    data: FormatResult


class ValidationError(BaseModel):
    """验证错误"""
    field: str = Field(..., description="错误字段")
    message: str = Field(..., description="错误消息")
    value: str = Field(..., description="错误值")
