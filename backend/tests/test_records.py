"""
创作记录 & 版本管理验收级测试（对齐真实实现）

接口：
- /api/v1/records  (GET/POST)
- /api/v1/records/{id} (GET/PUT/DELETE)
- /api/v1/records/{id}/versions (GET/POST)
- /api/v1/records/{id}/versions/{version_id}/restore (POST)
- /api/v1/records/export/csv|txt|docx|pdf
"""

import importlib.util

import pytest
from fastapi.testclient import TestClient


@pytest.mark.records
def test_records_requires_auth(client: TestClient):
    r = client.get("/api/v1/records/")
    assert r.status_code == 401, r.text
    assert r.json()["code"] == 401


@pytest.mark.records
def test_create_list_get_update_delete_record_flow(client: TestClient, auth_headers: dict):
    # create
    r = client.post(
        "/api/v1/records/",
        headers=auth_headers,
        json={"title": "测试记录", "platform": "douyin", "content": "内容v1", "status": "draft"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    assert body["message"] == "创建成功"
    record = body["data"]
    assert record["title"] == "测试记录"
    assert record["platform"] == "douyin"
    assert record["status"] == "draft"
    assert len(record["versions"]) == 1
    assert record["versions"][0]["version_number"] == 1

    record_id = record["id"]

    # list (pagination schema)
    r = client.get("/api/v1/records/", headers=auth_headers, params={"page": 1, "page_size": 10})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    assert "items" in body["data"]
    assert any(x["id"] == record_id for x in body["data"]["items"])

    # get
    r = client.get(f"/api/v1/records/{record_id}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["data"]["id"] == record_id

    # update
    r = client.put(
        f"/api/v1/records/{record_id}",
        headers=auth_headers,
        json={"title": "更新标题", "status": "published"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    assert body["data"]["title"] == "更新标题"
    assert body["data"]["status"] == "published"

    # delete
    r = client.delete(f"/api/v1/records/{record_id}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["code"] == 200

    # get after delete -> 404
    r = client.get(f"/api/v1/records/{record_id}", headers=auth_headers)
    assert r.status_code == 404, r.text
    assert r.json()["code"] == 404


@pytest.mark.records
def test_version_management_create_restore_delete_rules(client: TestClient, auth_headers: dict):
    # create record
    r = client.post(
        "/api/v1/records/",
        headers=auth_headers,
        json={"title": "记录", "platform": "douyin", "content": "v1", "status": "draft"},
    )
    record_id = r.json()["data"]["id"]

    # create version v2
    r = client.post(
        f"/api/v1/records/{record_id}/versions",
        headers=auth_headers,
        json={"content": "v2", "change_note": "第二版", "is_ai_generated": False},
    )
    assert r.status_code == 200, r.text
    v2 = r.json()["data"]
    assert v2["version_number"] == 2
    assert v2["is_ai_generated"] is False

    # list versions
    r = client.get(f"/api/v1/records/{record_id}/versions", headers=auth_headers)
    assert r.status_code == 200
    versions = r.json()["data"]
    assert [v["version_number"] for v in versions] == [1, 2]

    # restore v1 -> creates v3
    v1_id = versions[0]["id"]
    r = client.post(f"/api/v1/records/{record_id}/versions/{v1_id}/restore", headers=auth_headers)
    assert r.status_code == 200, r.text
    restored = r.json()["data"]
    assert restored["version_number"] == 3
    assert restored["content"] == "v1"

    # cannot delete versions until only 1 remains
    # delete v2
    r = client.delete(f"/api/v1/records/{record_id}/versions/{v2['id']}", headers=auth_headers)
    assert r.status_code == 200

    # delete v1 (now still have v1 and v3)
    r = client.delete(f"/api/v1/records/{record_id}/versions/{v1_id}", headers=auth_headers)
    assert r.status_code == 200

    # delete last remaining should fail (400)
    # list versions again to get remaining id
    r = client.get(f"/api/v1/records/{record_id}/versions", headers=auth_headers)
    remaining = r.json()["data"]
    assert len(remaining) == 1
    last_id = remaining[0]["id"]
    r = client.delete(f"/api/v1/records/{record_id}/versions/{last_id}", headers=auth_headers)
    assert r.status_code == 400, r.text
    assert r.json()["code"] == 400


@pytest.mark.records
def test_export_csv_and_txt(client: TestClient, auth_headers: dict):
    # create some data
    client.post(
        "/api/v1/records/",
        headers=auth_headers,
        json={"title": "记录", "platform": "douyin", "content": "内容", "status": "draft"},
    )

    r = client.get("/api/v1/records/export/csv", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "text/csv" in r.headers.get("content-type", "")

    r = client.get("/api/v1/records/export/txt", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "text/plain" in r.headers.get("content-type", "")


@pytest.mark.records
def test_export_docx_and_pdf_dependency_behavior(client: TestClient, auth_headers: dict):
    client.post(
        "/api/v1/records/",
        headers=auth_headers,
        json={"title": "记录", "platform": "douyin", "content": "内容", "status": "draft"},
    )

    docx_installed = importlib.util.find_spec("docx") is not None
    r = client.get("/api/v1/records/export/docx", headers=auth_headers)
    if docx_installed:
        assert r.status_code == 200, r.text
        assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in r.headers.get("content-type", "")
    else:
        assert r.status_code == 500, r.text
        assert "python-docx" in r.json()["message"]

    reportlab_installed = importlib.util.find_spec("reportlab") is not None
    r = client.get("/api/v1/records/export/pdf", headers=auth_headers)
    if reportlab_installed:
        assert r.status_code == 200, r.text
        assert "application/pdf" in r.headers.get("content-type", "")
    else:
        assert r.status_code == 500, r.text
        assert "reportlab" in r.json()["message"]
