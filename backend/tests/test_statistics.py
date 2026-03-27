"""
统计分析模块验收级测试（对齐真实实现）

接口：
- GET /api/v1/statistics/daily
- GET /api/v1/statistics/platform
- GET /api/v1/statistics/type
- GET /api/v1/statistics/keywords
- GET /api/v1/statistics/total_words
- GET /api/v1/statistics/export_report
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.statistics
def test_statistics_requires_auth(client: TestClient):
    r = client.get("/api/v1/statistics/daily")
    assert r.status_code == 401


@pytest.mark.statistics
def test_daily_platform_type_keywords_total_words_ok(client: TestClient, auth_headers: dict):
    # seed some records via API
    client.post(
        "/api/v1/records/",
        headers=auth_headers,
        json={"title": "春天旅行攻略", "platform": "douyin", "content": "春天 旅行 攻略", "status": "draft"},
    )

    r = client.get("/api/v1/statistics/daily", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    assert isinstance(body["data"], dict)

    r = client.get("/api/v1/statistics/platform", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["code"] == 200
    assert isinstance(r.json()["data"], list)

    r = client.get("/api/v1/statistics/type", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["code"] == 200

    r = client.get("/api/v1/statistics/keywords", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["code"] == 200
    assert isinstance(r.json()["data"], list)

    r = client.get("/api/v1/statistics/total_words", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["code"] == 200
    assert isinstance(r.json()["data"], int)
    assert r.json()["data"] > 0


@pytest.mark.statistics
def test_daily_invalid_date_range_returns_400(client: TestClient, auth_headers: dict):
    r = client.get(
        "/api/v1/statistics/daily",
        headers=auth_headers,
        params={"start_date": "2026-02-02", "end_date": "2026-01-01"},
    )
    assert r.status_code == 400, r.text
    assert r.json()["code"] == 400


@pytest.mark.statistics
def test_export_report_csv_stream(client: TestClient, auth_headers: dict):
    client.post(
        "/api/v1/records/",
        headers=auth_headers,
        json={"title": "记录", "platform": "douyin", "content": "内容", "status": "draft"},
    )
    r = client.get("/api/v1/statistics/export_report", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "text/csv" in r.headers.get("content-type", "")
