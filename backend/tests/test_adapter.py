"""
平台适配模块验收级测试（对齐真实实现）

接口：
- GET  /api/v1/adapter/platforms
- POST /api/v1/adapter/adapt
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.adapter
def test_get_platforms(client: TestClient):
    r = client.get("/api/v1/adapter/platforms")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    codes = {p["code"] for p in body["data"]}
    assert {"douyin", "xiaohongshu", "wechat"}.issubset(codes)


@pytest.mark.adapter
def test_adapt_content_douyin_title_truncation_and_tag_limit(client: TestClient):
    long_title = "T" * 100
    tags = [f"t{i}" for i in range(10)]
    r = client.post(
        "/api/v1/adapter/adapt",
        json={
            "content": "这是原始内容。这里有两段。\n第二段。",
            "platform": "douyin",
            "title": long_title,
            "tags": tags,
            "auto_format": True,
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    data = body["data"]
    assert len(data["title"]) <= 30
    assert len(data["tags"]) <= 5
    assert isinstance(data["preview"], str) and data["preview"]


@pytest.mark.adapter
def test_adapt_content_wechat_ignores_tags_and_warns(client: TestClient):
    r = client.post(
        "/api/v1/adapter/adapt",
        json={
            "content": "这是原始内容。",
            "platform": "wechat",
            "title": "标题",
            "tags": ["a", "b"],
            "auto_format": True,
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    data = body["data"]
    assert data["tags"] == []
    assert any("不支持标签" in w for w in (data.get("warnings") or []))


@pytest.mark.adapter
def test_adapt_invalid_platform_422(client: TestClient):
    r = client.post(
        "/api/v1/adapter/adapt",
        json={"content": "x", "platform": "invalid"},
    )
    assert r.status_code == 422, r.text
    body = r.json()
    assert body["code"] == 422
