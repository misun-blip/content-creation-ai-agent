"""
上传服务验收级测试（对齐真实实现）

接口：
- POST /api/v1/uploads  (multipart file)
并验证静态资源挂载：GET /uploads/{filename}
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.mark.uploads
def test_upload_file_and_static_access(client: TestClient):
    files = {"file": ("hello.txt", b"hello world", "text/plain")}
    r = client.post("/api/v1/uploads", files=files)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    url = body["data"]["url"]
    assert isinstance(url, str) and url.startswith("/uploads/")

    # verify file exists on disk (backend/uploads)
    filename = url.split("/")[-1]
    upload_path = Path(os.getcwd()) / "uploads" / filename
    assert upload_path.exists(), f"uploaded file not found: {upload_path}"

    # verify static access
    r = client.get(url)
    assert r.status_code == 200
    assert r.content == b"hello world"

    # cleanup
    try:
        upload_path.unlink(missing_ok=True)
    except Exception:
        # best-effort cleanup
        pass


