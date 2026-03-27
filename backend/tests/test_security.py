"""
安全相关验收级测试（JWT / 密码存储）

目标：对齐详细设计文档中的安全需求：
- 无 token / 非法 token / 过期 token 必须 401
- 密码不可明文存储
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient


@pytest.mark.security
def test_no_token_access_me_401(client: TestClient):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401
    assert r.json()["code"] == 401


@pytest.mark.security
def test_invalid_token_401(client: TestClient):
    r = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert r.status_code == 401
    assert r.json()["code"] == 401


@pytest.mark.security
def test_tampered_token_401(client: TestClient, auth_token: str):
    # modify token tail -> signature invalid
    tampered = auth_token[:-1] + ("a" if auth_token[-1] != "a" else "b")
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tampered}"})
    assert r.status_code == 401
    assert r.json()["code"] == 401


@pytest.mark.security
def test_expired_token_401(client: TestClient):
    from app.core.security import create_access_token

    expired = create_access_token({"sub": "any"}, expires_delta=timedelta(minutes=-1))
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert r.status_code == 401
    assert r.json()["code"] == 401


@pytest.mark.security
def test_password_not_stored_plaintext(client: TestClient, register_user_payload: dict):
    r = client.post("/api/v1/auth/register", json=register_user_payload)
    assert r.status_code == 200

    from app.core.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        u = db.query(User).filter(User.username == register_user_payload["username"]).first()
        assert u is not None
        assert u.password_hash != register_user_payload["password"]
        # bcrypt hashes commonly start with $2b$ / $2a$ / $2y$
        assert u.password_hash.startswith("$2")
    finally:
        db.close()


