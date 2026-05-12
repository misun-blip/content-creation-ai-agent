from pydantic_settings import BaseSettings
from typing import List
import os

# 默认数据库地址（MySQL 8.0，Docker 容器）
_default_database_url = "mysql+pymysql://content_ai:content_ai_password@localhost:3306/content_ai_agent"


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "内容创作AI-Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置（可选，提供默认值）
    DATABASE_URL: str = _default_database_url
    
    # Redis配置（可选，提供默认值）
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT配置（可选，提供默认值）
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI服务配置（统一使用 AI_API_KEY / AI_API_BASE）
    AI_API_KEY: str = ""
    AI_API_BASE: str = "https://api.chatanywhere.tech/v1"
    
    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost:8080",  # 测试HTML服务器
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3003",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",  # 测试HTML服务器（备用地址）
    ]
    
    class Config:
        env_file = ".env"
        # 允许从环境变量覆盖，即使.env文件不存在
        env_file_encoding = "utf-8"
        case_sensitive = False

# 创建settings实例，如果.env文件不存在也不会报错
try:
    settings = Settings()
except Exception as e:
    import logging
    logging.warning(f"加载配置文件失败，使用默认配置: {e}")
    try:
        settings = Settings(_env_file=None)
    except Exception as e2:
        logging.error(f"无法创建配置对象: {e2}")
        class MinimalSettings:
            APP_NAME = "内容创作AI-Agent"
            APP_VERSION = "1.0.0"
            DEBUG = True
            DATABASE_URL = _default_database_url
            REDIS_URL = "redis://localhost:6379/0"
            SECRET_KEY = "dev-secret-key-change-in-production"
            ALGORITHM = "HS256"
            ACCESS_TOKEN_EXPIRE_MINUTES = 30
            AI_API_KEY = ""
            AI_API_BASE = "https://api.chatanywhere.tech/v1"
            CORS_ORIGINS = [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://localhost:8000",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
            ]
        settings = MinimalSettings()
