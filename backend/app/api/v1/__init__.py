# app/api/v1/__init__.py
from fastapi import APIRouter

# 导入所有模块的路由
from app.api.v1.auth import router as auth_router
from app.api.v1.statistics import router as statistics_router
from app.api.v1.materials import router as materials_router
from app.api.v1.ai import router as ai_router
from app.api.v1.adapter import router as adapter_router
from app.api.v1.records import router as records_router
from app.api.v1.uploads import router as uploads_router
from app.api.v1.tags import router as tags_router
from app.api.v1.categories import router as categories_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.test import router as test_router

# 初始化v1版本路由
api_router = APIRouter()

# 注册所有接口
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(materials_router, tags=["素材管理"])
api_router.include_router(tags_router, tags=["标签"])
api_router.include_router(categories_router, tags=["分类"])
api_router.include_router(ai_router, tags=["AI生成"])
api_router.include_router(adapter_router, tags=["平台适配"])
api_router.include_router(records_router, prefix="/records", tags=["创作记录"])
api_router.include_router(statistics_router, prefix="/statistics", tags=["统计分析"])
api_router.include_router(uploads_router, prefix="/uploads", tags=["上传服务"])
api_router.include_router(dashboard_router, tags=["仪表盘"])
api_router.include_router(test_router, tags=["测试"])
