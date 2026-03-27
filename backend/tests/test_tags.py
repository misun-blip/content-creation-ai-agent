"""
标签模块验收级测试（对齐真实实现）

接口：
- GET  /api/v1/tags
- POST /api/v1/tags
- GET  /api/v1/tags/{id}
- DELETE /api/v1/tags/{id}
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.tags
def test_create_list_get_delete_tag_flow(client: TestClient, unique_suffix: str):
    name = f"标签_{unique_suffix}"

    r = client.post("/api/v1/tags", json={"name": name})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    tag_id = body["data"]["id"]
    assert isinstance(tag_id, int)
    assert body["data"]["name"] == name

    # duplicate -> 400
    r = client.post("/api/v1/tags", json={"name": name})
    assert r.status_code == 400, r.text
    assert r.json()["code"] == 400

    # list contains it
    r = client.get("/api/v1/tags")
    assert r.status_code == 200
    body = r.json()
    assert body["code"] == 200
    assert any(t["id"] == tag_id for t in body["data"])

    # search by q
    r = client.get("/api/v1/tags", params={"q": unique_suffix})
    assert r.status_code == 200
    body = r.json()
    assert body["code"] == 200
    assert any(t["id"] == tag_id for t in body["data"])

    # get by id
    r = client.get(f"/api/v1/tags/{tag_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["code"] == 200
    assert body["data"]["name"] == name

    # delete
    r = client.delete(f"/api/v1/tags/{tag_id}")
    assert r.status_code == 200
    assert r.json()["code"] == 200

    # get after delete -> 404
    r = client.get(f"/api/v1/tags/{tag_id}")
    assert r.status_code == 404
    assert r.json()["code"] == 404


