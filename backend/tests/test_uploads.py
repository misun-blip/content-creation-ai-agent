"""
上传服务验收级测试（对齐真实实现）

接口：
- POST /api/v1/uploads  (multipart file)
并验证静态资源挂载：GET /uploads/{subdir}/{filename}
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.mark.uploads
def test_upload_document_and_static_access(client: TestClient):
    files = {"file": ("hello.txt", b"hello world", "text/plain")}
    r = client.post("/api/v1/uploads", files=files)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    data = body["data"]
    url = data["url"]
    assert url.startswith("/uploads/documents/")
    assert data["file_type"] == "document"
    assert data["size"] == len(b"hello world")

    upload_path = Path(os.getcwd()) / "uploads" / url.replace("/uploads/", "")
    assert upload_path.exists(), f"uploaded file not found: {upload_path}"

    r = client.get(url)
    assert r.status_code == 200
    assert r.content == b"hello world"

    upload_path.unlink(missing_ok=True)


@pytest.mark.uploads
def test_upload_image(client: TestClient):
    files = {"file": ("photo.jpg", b"\xff\xd8\xff fake jpeg", "image/jpeg")}
    r = client.post("/api/v1/uploads", files=files)
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["url"].startswith("/uploads/images/")
    assert data["file_type"] == "image"

    upload_path = Path(os.getcwd()) / "uploads" / data["url"].replace("/uploads/", "")
    assert upload_path.exists()
    upload_path.unlink(missing_ok=True)


@pytest.mark.uploads
def test_upload_rejects_unsupported_type(client: TestClient):
    files = {"file": ("script.exe", b"bad", "application/octet-stream")}
    r = client.post("/api/v1/uploads", files=files)
    assert r.status_code == 400
    assert r.json()["code"] == 400


@pytest.mark.uploads
def test_upload_rejects_empty_file(client: TestClient):
    files = {"file": ("empty.txt", b"", "text/plain")}
    r = client.post("/api/v1/uploads", files=files)
    assert r.status_code == 400
    assert r.json()["code"] == 400
