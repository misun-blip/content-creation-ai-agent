from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

# 默认使用 MySQL 数据库（新团队开发环境）
# 如需快速本地测试可切换为 SQLite：sqlite:///backend/test.db
_default_sqlite_path = Path(__file__).resolve().parent.parent.parent / "test.db"
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
    
    # AI服务配置（可选，平台适配模块不需要）
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
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
    # 如果加载失败，尝试使用默认值创建（不读取.env文件）
    import logging
    logging.warning(f"加载配置文件失败，使用默认配置: {e}")
    try:
        # 尝试不读取env文件
        import os
        # 临时移除.env文件要求
        settings = Settings(_env_file=None)
    except Exception as e2:
        # 如果还是失败，创建一个最小配置对象
        logging.error(f"无法创建配置对象: {e2}")
        # 如果还是失败，创建一个最小配置对象
        logging.error(f"无法创建配置对象: {e2}")
        # 创建一个简单的配置对象
        class MinimalSettings:
            APP_NAME = "内容创作AI-Agent"
            APP_VERSION = "1.0.0"
            DEBUG = True
            DATABASE_URL = "mysql+pymysql://content_ai:content_ai_password@localhost:3306/content_ai_agent"
            REDIS_URL = "redis://localhost:6379/0"
            SECRET_KEY = "dev-secret-key-change-in-production"
            ALGORITHM = "HS256"
            ACCESS_TOKEN_EXPIRE_MINUTES = 30
            OPENAI_API_KEY = ""
            OPENAI_API_BASE = "https://api.openai.com/v1"
            AI_API_KEY = ""
            AI_API_BASE = "https://api.chatanywhere.tech/v1"
            CORS_ORIGINS = [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://localhost:8000",
                "http://localhost:8080",  # 测试HTML服务器
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3003",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:8080",  # 测试HTML服务器（备用地址）
            ]
        settings = MinimalSettings()
