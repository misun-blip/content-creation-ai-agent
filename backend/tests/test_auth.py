"""
认证模块验收级测试

对齐真实实现：
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET  /api/v1/auth/me（需 JWT）
- PUT  /api/v1/auth/profile（需 JWT）
- PUT  /api/v1/auth/password（需 JWT）
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.auth
def test_health_check(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}


@pytest.mark.auth
def test_root_endpoint(client: TestClient):
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert "message" in body
    assert "version" in body


@pytest.mark.auth
def test_register_success(client: TestClient, register_user_payload: dict):
    r = client.post("/api/v1/auth/register", json=register_user_payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    assert body["message"] == "注册成功"
    assert isinstance(body["data"]["id"], int)


@pytest.mark.auth
def test_register_duplicate_username_rejected(client: TestClient, register_user_payload: dict):
    r1 = client.post("/api/v1/auth/register", json=register_user_payload)
    assert r1.status_code == 200, r1.text

    r2 = client.post("/api/v1/auth/register", json=register_user_payload)
    assert r2.status_code == 400, r2.text
    body = r2.json()
    assert body["code"] == 400
    assert "用户名已存在" in body["message"]


@pytest.mark.auth
def test_login_success_returns_token(client: TestClient, register_user_payload: dict, login_payload: dict):
    r = client.post("/api/v1/auth/register", json=register_user_payload)
    assert r.status_code == 200, r.text

    r = client.post("/api/v1/auth/login", json=login_payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    assert body["message"] == "登录成功"
    assert isinstance(body["data"]["token"], str) and body["data"]["token"]
    assert body["data"]["user"]["username"] == register_user_payload["username"]
    assert body["data"]["user"]["email"] == register_user_payload["email"].lower()


@pytest.mark.auth
def test_login_wrong_password_401(client: TestClient, register_user_payload: dict):
    r = client.post("/api/v1/auth/register", json=register_user_payload)
    assert r.status_code == 200

    r = client.post(
        "/api/v1/auth/login",
        json={"username": register_user_payload["username"], "password": "wrong-password"},
    )
    assert r.status_code == 401, r.text
    body = r.json()
    assert body["code"] == 401
    assert "用户名或密码错误" in body["message"]


@pytest.mark.auth
def test_me_requires_token(client: TestClient):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401, r.text
    body = r.json()
    assert body["code"] == 401


@pytest.mark.auth
def test_me_with_token_ok(client: TestClient, auth_headers: dict, register_user_payload: dict):
    r = client.get("/api/v1/auth/me", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    assert body["data"]["username"] == register_user_payload["username"]


@pytest.mark.auth
def test_update_profile_username_issues_new_token(client: TestClient, auth_headers: dict, unique_suffix: str):
    new_name = f"new_{unique_suffix}"
    r = client.put("/api/v1/auth/profile", headers=auth_headers, json={"username": new_name, "avatar": "/uploads/a.png"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    assert isinstance(body["data"]["token"], str) and body["data"]["token"]
    assert body["data"]["user"]["username"] == new_name
    assert body["data"]["user"]["avatar"] == "/uploads/a.png"


@pytest.mark.auth
def test_change_password_flow(client: TestClient, auth_headers: dict, login_payload: dict):
    # 旧密码错误 -> 400
    r = client.put("/api/v1/auth/password", headers=auth_headers, json={"old_password": "bad", "new_password": "Newpass123!"})
    assert r.status_code == 400
    assert r.json()["code"] == 400

    # 新密码太短 -> 400
    r = client.put("/api/v1/auth/password", headers=auth_headers, json={"old_password": login_payload["password"], "new_password": "123"})
    assert r.status_code == 400
    assert r.json()["code"] == 400

    # 成功修改 -> 200
    new_pw = "Newpass123!"
    r = client.put("/api/v1/auth/password", headers=auth_headers, json={"old_password": login_payload["password"], "new_password": new_pw})
    assert r.status_code == 200, r.text
    assert r.json()["code"] == 200

    # 使用新密码可以登录
    r = client.post("/api/v1/auth/login", json={"username": login_payload["username"], "password": new_pw})
    assert r.status_code == 200, r.text
    assert r.json()["code"] == 200
