"""
性能基准（轻量）

注意：这是启动测试中的“可选性能测试”（可通过测试看板的 includePerformance 触发）。
阈值遵循详细设计文档的非功能需求：核心功能响应时间 < 2 秒。
"""

from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient


@pytest.mark.slow
@pytest.mark.performance
def test_health_response_time_under_2s(client: TestClient):
    start = time.perf_counter()
    r = client.get("/health")
    elapsed = time.perf_counter() - start
    assert r.status_code == 200
    assert elapsed < 2.0, f"/health too slow: {elapsed:.3f}s"


@pytest.mark.slow
@pytest.mark.performance
def test_rapid_sequential_health_requests_no_error(client: TestClient):
    for _ in range(50):
        r = client.get("/health")
        assert r.status_code == 200


