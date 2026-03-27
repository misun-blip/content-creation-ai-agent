"""
统一响应格式工具
符合接口设计文档规范: {code, message, data}
"""
from typing import Any, Optional


def success(data: Any = None, message: str = "成功", code: int = 200) -> dict:
    """成功响应"""
    return {"code": code, "message": message, "data": data}


def error(message: str = "请求失败", code: int = 400, details: Any = None) -> dict:
    """错误响应"""
    resp = {"code": code, "message": message}
    if details is not None:
        resp["details"] = details
    return resp


def paginated(
    items: list,
    total: int,
    page: int = 1,
    page_size: int = 10,
    message: str = "成功",
) -> dict:
    """分页响应"""
    return {
        "code": 200,
        "message": message,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "pageSize": page_size,
            "hasNext": (page * page_size) < total,
        },
    }
