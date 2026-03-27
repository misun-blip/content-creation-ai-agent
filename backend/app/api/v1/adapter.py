from fastapi import APIRouter, HTTPException
import logging
from ...schemas.adapter import (
    ContentRequest,
    AdapterResponse,
    PlatformEnum
)
from ...services.adapter_service import adapter_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/adapter", tags=["平台适配"])


@router.post("/adapt", response_model=AdapterResponse)
async def adapt_content(request: ContentRequest):
    """
    适配内容到指定平台
    
    Args:
        request: 内容适配请求
        
    Returns:
        适配响应
    """
    try:
        result = adapter_service.adapt_content(
            content=request.content,
            platform=request.platform.value,
            title=request.title,
            tags=request.tags,
            auto_format=request.auto_format
        )
        
        return AdapterResponse(
            code=200,
            message="适配成功",
            data=result
        )
    except FileNotFoundError as e:
        logger.error(f"平台配置文件缺失: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"平台配置文件缺失: {str(e)}"
        )
    except ValueError as e:
        logger.warning(f"请求参数错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError as e:
        logger.error(f"配置键缺失: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"平台配置错误: 缺少必需的配置项 {str(e)}"
        )
    except Exception as e:
        logger.error(f"适配失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"适配失败: {str(e)}"
        )


@router.get("/platforms")
async def get_platforms():
    """
    获取支持的平台列表
    
    Returns:
        平台列表响应
    """
    try:
        from ...config.platform_config import platform_config
        
        platforms = platform_config.get_all_platforms()
        
        if not platforms:
            logger.warning("平台配置为空，返回空列表")
            return {
                "code": 200,
                "message": "获取成功",
                "data": []
            }
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": [
                {
                    "code": code,
                    "name": config.get("name", ""),
                    "title": config.get("title", {}),
                    "content": config.get("content", {}),
                    "tags": config.get("tags", {}),
                    "cover": config.get("cover", {})
                }
                for code, config in platforms.items()
            ]
        }
    except FileNotFoundError as e:
        logger.error(f"平台配置文件缺失: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"平台配置文件缺失: {str(e)}"
        )
    except Exception as e:
        logger.error(f"获取平台列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取平台列表失败: {str(e)}"
        )
