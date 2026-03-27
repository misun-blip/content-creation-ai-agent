import time
import logging
import os
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from app.api.v1 import api_router

from app.core.config import settings
from app.core.database import Base, engine
# 确保导入了初始化函数
from app.initial_data import init_db_data 

# --------------- 日志配置 ---------------
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --------------- 生命周期管理 (Lifespan) ---------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    管理应用启动和关闭时的逻辑
    """
    # 【启动阶段】
    try:
        logger.info("系统启动：正在初始化数据库...")
        # 1. 自动创建数据库表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建/校验完成")
        
        # 2. 执行数据初始化 (如管理员账号、初始素材等)
        init_db_data()
        logger.info("基础数据初始化流程结束")
        
    except Exception as e:
        logger.error(f"系统启动初始化失败: {e}", exc_info=True)
        # 如果初始化失败且对系统运行至关重要，可以考虑在此处 raise

    yield
    # 【关闭阶段】
    logger.info("系统正在关闭...")

# --------------- 应用初始化 ---------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="面向流媒体/自媒体营销的内容创作AI-Agent",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan, # 注册生命周期管理
)

# --------------- CORS 处理逻辑 ---------------
def parseCorsOrigins(value):
    """
    强制解析 settings.CORS_ORIGINS 为 list[str]
    """
    if value is None:
        return ["http://localhost:5173", "http://127.0.0.1:5173"]
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return ["http://localhost:5173", "http://127.0.0.1:5173"]
        if s.startswith("["):
            try:
                arr = json.loads(s)
                if isinstance(arr, list): return arr
            except Exception: pass
        if "," in s:
            return [x.strip() for x in s.split(",") if x.strip()]
        return [s]
    return ["http://localhost:5173", "http://127.0.0.1:5173"]

corsOrigins = parseCorsOrigins(getattr(settings, "CORS_ORIGINS", None))
# 添加对file://协议的支持（用于本地HTML文件）
corsOrigins.append("null")
logger.info(f"CORS origins effective: {corsOrigins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=corsOrigins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# --------------- 静态文件服务 ---------------
# 用于访问上传的图片/视频素材
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# --------------- 请求日志中间件 ---------------
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000, 2)
    logger.info(
        "%s %s -> %s (%.2fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response

# --------------- 全局异常处理 ---------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail},
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": "请求参数验证失败", "errors": exc.errors()},
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    FastAPI 请求参数校验错误（常见于 body/query/path 校验失败）
    统一转换为接口设计文档约定的 {code,message,errors} 结构。
    """
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": "请求参数验证失败", "errors": exc.errors()},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("未处理异常: %s %s -> %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误"},
    )

# --------------- API 路由注册 ---------------
try:
    # 使用统一的 api_router
    app.include_router(api_router, prefix="/api/v1")
    logger.info("所有API路由注册成功")
except Exception as e:
    logger.error(f"注册路由失败: {e}", exc_info=True)

# --------------- 基础端点 ---------------
@app.get("/")
async def root():
    return {"message": "欢迎使用内容创作AI-Agent", "version": settings.APP_VERSION}

@app.get("/health")
async def health_check():

    return {"status": "healthy"}
