"""
素材库模块验收级测试（对齐真实实现）

接口：
- GET  /api/v1/materials
- POST /api/v1/materials
- PUT  /api/v1/materials/{id}
- DELETE /api/v1/materials/{id}
- GET  /api/v1/materials/categories
- PUT  /api/v1/materials/{id}/tags
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.materials
def test_create_list_update_delete_material(client: TestClient, unique_suffix: str):
    payload = {
        "title": f"素材_{unique_suffix}",
        "description": "这是一个测试素材",
        "category": "促销",
        "preview": "预览文本",
        "type": "template",
        "file_path": None,
    }

    r = client.post("/api/v1/materials", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    mat = body["data"]
    assert mat["title"] == payload["title"]
    assert mat["description"] == payload["description"]
    assert mat["category"] == payload["category"]
    assert mat["type"] == payload["type"]
    assert isinstance(mat["id"], int)

    # list
    r = client.get("/api/v1/materials")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    assert any(x["id"] == mat["id"] for x in body["data"])

    # update
    r = client.put(f"/api/v1/materials/{mat['id']}", json={"title": "更新标题", "description": "更新描述"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    assert body["data"]["title"] == "更新标题"
    assert body["data"]["description"] == "更新描述"

    # delete nonexistent returns deleted=0
    r = client.delete("/api/v1/materials/999999")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    assert body["data"]["deleted"] == 0

    # delete existing
    r = client.delete(f"/api/v1/materials/{mat['id']}")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    assert body["data"]["deleted"] == 1


@pytest.mark.materials
def test_list_categories_reflects_created_materials(client: TestClient, unique_suffix: str):
    r = client.get("/api/v1/materials/categories")
    assert r.status_code == 200
    assert r.json()["code"] == 200

    payload = {
        "title": f"素材_{unique_suffix}",
        "description": "desc",
        "category": "活动",
        "preview": "",
        "type": "template",
    }
    r = client.post("/api/v1/materials", json=payload)
    assert r.status_code == 200

    r = client.get("/api/v1/materials/categories")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    assert "活动" in body["data"]


@pytest.mark.materials
def test_material_filtering_by_q_category_and_tag(client: TestClient, unique_suffix: str):
    # create a tag
    r = client.post("/api/v1/tags", json={"name": f"标签_{unique_suffix}"})
    assert r.status_code == 200, r.text
    tag_id = r.json()["data"]["id"]

    # create two materials
    m1 = client.post(
        "/api/v1/materials",
        json={"title": f"素材A_{unique_suffix}", "description": "含关键词：春天", "category": "C1", "preview": "", "type": "template"},
    ).json()["data"]
    m2 = client.post(
        "/api/v1/materials",
        json={"title": f"素材B_{unique_suffix}", "description": "不相关", "category": "C2", "preview": "", "type": "template"},
    ).json()["data"]

    # bind tag to m1
    r = client.put(f"/api/v1/materials/{m1['id']}/tags", json={"tag_ids": [tag_id]})
    assert r.status_code == 200, r.text

    # q filter (matches description only, per implementation)
    r = client.get("/api/v1/materials", params={"q": "春天"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert any(x["id"] == m1["id"] for x in data)
    assert all(x["id"] != m2["id"] for x in data)

    # category filter
    r = client.get("/api/v1/materials", params={"category": "C2"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert any(x["id"] == m2["id"] for x in data)

    # tag filter (by tag name)
    r = client.get("/api/v1/materials", params={"tag": f"标签_{unique_suffix}"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data) == 1
    assert data[0]["id"] == m1["id"]
