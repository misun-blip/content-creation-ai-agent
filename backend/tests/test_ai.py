"""
AI 生成模块验收级测试（Mock 外部调用）

接口：
- POST /api/v1/ai/topics
- POST /api/v1/ai/content
- POST /api/v1/ai/evaluate
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.ai
def test_generate_topics_mocked_ok(client: TestClient, mock_ai_success: None):
    r = client.post(
        "/api/v1/ai/topics",
        json={"keywords": "春天,旅行", "industry": "旅游", "platform": "douyin", "count": 1},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    topics = body["data"]["topics"]
    assert isinstance(topics, list) and len(topics) == 1
    assert topics[0]["platform"] == "douyin"
    assert "title" in topics[0] and "description" in topics[0]


@pytest.mark.ai
def test_generate_content_mocked_ok(client: TestClient, mock_ai_success: None):
    r = client.post(
        "/api/v1/ai/content",
        json={"topic": "春天的旅行", "length": 200, "style": "轻松", "platform": "douyin"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    assert isinstance(body["data"]["content"], str) and body["data"]["content"]


@pytest.mark.ai
def test_evaluate_content_rule_engine(client: TestClient):
    r = client.post(
        "/api/v1/ai/evaluate",
        json={"content": "这是一个内容，包含绝对与100%等词。", "topic": "内容", "target_length": 50},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["code"] == 200
    assert 0 <= body["data"]["score"] <= 100
    suggestions = body["data"]["suggestions"]
    assert isinstance(suggestions, list) and suggestions
    assert any("违禁词" in s for s in suggestions)
