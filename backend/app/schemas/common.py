"""
通用 Schema
包含分页请求/响应模型，供所有模块统一使用
"""
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


# --------------- 分页请求 ---------------

class PaginationParams(BaseModel):
    """分页查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, alias="pageSize", description="每页数量")
    keyword: Optional[str] = Field(None, description="搜索关键词")


# --------------- 分页响应 ---------------

class PaginatedData(BaseModel):
    """分页数据"""
    items: List[Any] = Field(default_factory=list, description="数据列表")
    total: int = Field(0, description="总数")
    page: int = Field(1, description="当前页码")
    pageSize: int = Field(10, description="每页数量")
    hasNext: bool = Field(False, description="是否有下一页")


# --------------- 统一响应 ---------------

class BaseResponse(BaseModel):
    """统一响应格式"""
    code: int = Field(200, description="响应状态码")
    message: str = Field("成功", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")


class ErrorResponse(BaseModel):
    """错误响应格式"""
    code: int = Field(400, description="错误状态码")
    message: str = Field("请求失败", description="错误消息")
    details: Optional[Any] = Field(None, description="错误详情")
