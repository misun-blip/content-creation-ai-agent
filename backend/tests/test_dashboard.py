"""
仪表盘聚合 API 验收级测试（对齐真实实现）

接口：
- GET /api/v1/dashboard/stats
- GET /api/v1/dashboard/trend
- GET /api/v1/dashboard/platform
- GET /api/v1/dashboard/type
- GET /api/v1/dashboard/activities
- GET /api/v1/dashboard/tags
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.dashboard
def test_dashboard_requires_auth(client: TestClient):
    r = client.get("/api/v1/dashboard/stats")
    assert r.status_code == 401


@pytest.mark.dashboard
def test_dashboard_endpoints_shapes(client: TestClient, auth_headers: dict, unique_suffix: str):
    # seed: records + materials + tags
    client.post(
        "/api/v1/records/",
        headers=auth_headers,
        json={"title": f"记录_{unique_suffix}", "platform": "douyin", "content": "内容", "status": "draft"},
    )
    client.post(
        "/api/v1/materials",
        json={"title": f"素材_{unique_suffix}", "description": "desc", "category": "默认", "preview": "", "type": "template"},
    )
    client.post("/api/v1/tags", json={"name": f"标签_{unique_suffix}"})

    r = client.get("/api/v1/dashboard/stats", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    data = body["data"]
    assert set(data.keys()) == {"totalMaterials", "totalCreations", "aiGenerations", "platformAdapts"}
    assert all(isinstance(v, int) for v in data.values())

    r = client.get("/api/v1/dashboard/trend", headers=auth_headers, params={"months": 3})
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data["xAxis"]) == 3
    assert len(data["data"]) == 3

    r = client.get("/api/v1/dashboard/platform", headers=auth_headers)
    assert r.status_code == 200
    items = r.json()["data"]
    assert isinstance(items, list)
    assert all("name" in x and "value" in x for x in items)

    r = client.get("/api/v1/dashboard/type", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()["data"]
    assert "xAxis" in data and "data" in data

    r = client.get("/api/v1/dashboard/activities", headers=auth_headers, params={"limit": 5})
    assert r.status_code == 200
    activities = r.json()["data"]
    assert isinstance(activities, list)
    assert activities, "should have at least one activity after creating a record"

    r = client.get("/api/v1/dashboard/tags", headers=auth_headers, params={"limit": 5})
    assert r.status_code == 200
    tags = r.json()["data"]
    assert isinstance(tags, list)
    assert all("name" in x and "type" in x for x in tags)


