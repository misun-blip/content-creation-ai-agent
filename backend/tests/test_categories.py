"""
分类模块验收级测试

接口：
- GET    /api/v1/categories
- POST   /api/v1/categories
- GET    /api/v1/categories/{id}
- PUT    /api/v1/categories/{id}
- DELETE /api/v1/categories/{id}
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.categories
def test_create_list_get_update_delete_category_flow(client: TestClient, unique_suffix: str):
    name = f"分类_{unique_suffix}"

    r = client.post("/api/v1/categories", json={"name": name, "description": "测试分类"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    category_id = body["data"]["id"]
    assert body["data"]["name"] == name

    r = client.post("/api/v1/categories", json={"name": name})
    assert r.status_code == 400
    assert r.json()["code"] == 400

    r = client.get("/api/v1/categories")
    assert r.status_code == 200
    assert any(c["id"] == category_id for c in r.json()["data"])

    r = client.get("/api/v1/categories", params={"q": unique_suffix})
    assert r.status_code == 200
    assert any(c["id"] == category_id for c in r.json()["data"])

    r = client.get(f"/api/v1/categories/{category_id}")
    assert r.status_code == 200
    assert r.json()["data"]["name"] == name

    new_name = f"分类更新_{unique_suffix}"
    r = client.put(f"/api/v1/categories/{category_id}", json={"name": new_name})
    assert r.status_code == 200
    assert r.json()["data"]["name"] == new_name

    r = client.delete(f"/api/v1/categories/{category_id}")
    assert r.status_code == 200

    r = client.get(f"/api/v1/categories/{category_id}")
    assert r.status_code == 404


@pytest.mark.categories
def test_delete_category_rejected_when_has_children(client: TestClient, unique_suffix: str):
    parent_name = f"父分类_{unique_suffix}"
    child_name = f"子分类_{unique_suffix}"

    r = client.post("/api/v1/categories", json={"name": parent_name})
    assert r.status_code == 200
    parent_id = r.json()["data"]["id"]

    r = client.post("/api/v1/categories", json={"name": child_name, "parent_id": parent_id})
    assert r.status_code == 200
    child_id = r.json()["data"]["id"]

    r = client.delete(f"/api/v1/categories/{parent_id}")
    assert r.status_code == 400
    assert r.json()["code"] == 400

    client.delete(f"/api/v1/categories/{child_id}")
    client.delete(f"/api/v1/categories/{parent_id}")
