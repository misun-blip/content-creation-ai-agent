"""
pytest fixtures（验收级启动测试）

目标：
- 测试数据库隔离（避免依赖仓库自带 backend/test.db）
- 统一 TestClient / 鉴权 token 获取
- Mock 外部 AI 调用（稳定、可重复）
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Generator

import pytest
from fastapi.testclient import TestClient

# 添加 backend 目录到 Python 路径（使 `import app.*` 生效）
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# 确保测试在 backend 目录下运行（uploads 静态目录/相对路径更稳定）
os.chdir(str(BACKEND_DIR))

# 在导入 app 之前指定测试数据库与密钥（Settings 会从环境变量读取）
_TMP_DB = BACKEND_DIR / ".pytest_tmp_test.db"
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_TMP_DB.as_posix()}")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("DEBUG", "0")
# 添加AI相关配置（避免测试时因缺少API密钥而失败）
os.environ.setdefault("OPENAI_API_KEY", "test-api-key")
os.environ.setdefault("OPENAI_API_BASE", "https://api.openai.com/v1")
os.environ.setdefault("AI_API_KEY", "test-ai-api-key")
os.environ.setdefault("AI_API_BASE", "https://api.chatanywhere.tech/v1")
# 添加Redis配置（测试环境使用mock，不需要真实Redis）
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")


@pytest.fixture(autouse=True)
def _reset_database() -> Generator[None, None, None]:
    """
    每个用例执行前重建数据库 schema，确保测试互不干扰。
    """
    from app.core.database import Base, engine

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    """
    FastAPI TestClient（禁用 init_db_data 种子数据，避免测试对 admin/预置记录产生隐式依赖）
    """
    import app.main as main_mod

    monkeypatch.setattr(main_mod, "init_db_data", lambda: None, raising=True)
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def unique_suffix() -> str:
    return uuid.uuid4().hex[:10]


@pytest.fixture()
def register_user_payload(unique_suffix: str) -> Dict[str, Any]:
    return {
        "username": f"u_{unique_suffix}",
        "password": "Testpass123!",
        "email": f"u_{unique_suffix}@example.com",
    }


@pytest.fixture()
def login_payload(register_user_payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "username": register_user_payload["username"],
        "password": register_user_payload["password"],
    }


@pytest.fixture()
def auth_token(client: TestClient, register_user_payload: Dict[str, Any], login_payload: Dict[str, Any]) -> str:
    """
    注册并登录，返回 JWT token（Bearer）。
    """
    r = client.post("/api/v1/auth/register", json=register_user_payload)
    assert r.status_code == 200, r.text
    assert r.json().get("code") == 200

    r = client.post("/api/v1/auth/login", json=login_payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("code") == 200
    token = body["data"]["token"]
    assert isinstance(token, str) and token
    return token


@pytest.fixture()
def auth_headers(auth_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture()
def mock_ai_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mock 外部 AI：topics/content 返回可预测结果。
    """
    import app.api.v1.ai as ai_mod

    class _Msg:
        def __init__(self, content: str):
            self.content = content

    class _Choice:
        def __init__(self, content: str):
            self.message = _Msg(content)

    class _Resp:
        def __init__(self, content: str):
            self.choices = [_Choice(content)]

    async def _fake_create(*args: Any, **kwargs: Any) -> Any:
        # 根据调用类型返回不同内容：topics 要求 JSON；content 返回纯文本即可
        msgs = (kwargs.get("messages") or [])
        prompt = (msgs[-1].get("content") if msgs and isinstance(msgs[-1], dict) else "") or ""
        if "topics" in prompt or "选题" in prompt or "JSON" in prompt:
            return _Resp('{"topics":[{"title":"春日旅行","description":"关于春天出游的短视频创意"}]}')
        return _Resp("这是生成的文案内容。")

    # 直接替换底层 create 方法
    monkeypatch.setattr(ai_mod.AI_CLIENT.chat.completions, "create", _fake_create, raising=True)
