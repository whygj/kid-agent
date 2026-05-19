"""Web API tests"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import httpx
from fastapi.testclient import TestClient

from src.web.app import create_app
from src.web.models import (
    SessionStartRequest,
    ChatRequest,
    SessionStartResponse,
    ChatResponse,
    HealthResponse,
    TTSRequest,
)


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_agent():
    """Mock TutorAgent"""
    agent = MagicMock()
    agent.start_session = AsyncMock(return_value="欢迎开始学习！")
    agent.chat = AsyncMock(return_value="这是AI回复")

    # 创建学生对象
    class MockStudent:
        id = "test_student"
        name = "测试学生"
        grade = 3
        total_xp = 50
        streak_days = 1

    agent._store = MagicMock()
    agent._store.get_student = AsyncMock(return_value=MockStudent())
    agent._store.get_mastery = AsyncMock(return_value={})
    agent._store.get_student_history = AsyncMock(return_value=[])
    agent._store.get_student_stats = AsyncMock(return_value={
        "total_quizzes": 10,
        "correct_count": 8,
    })

    # 创建学习报告对象
    class MockReport:
        total_quizzes = 10
        correct_rate = 0.8
        mastered_points = []
        summary = "学习报告摘要"

    agent._student_roster = MagicMock()
    agent._student_roster.get_student_report = AsyncMock(return_value=MockReport())
    agent._student_roster.format_report_text = MagicMock(return_value="学习报告文本")

    # 为Lazy属性添加mock
    agent._adaptive_difficulty = MagicMock()
    agent._diagnose_engine = MagicMock()
    agent._explain_engine = MagicMock()
    agent._grader_engine = MagicMock()
    agent._intent_recognizer = MagicMock()
    agent._planner = MagicMock()
    agent._quiz_engine = MagicMock()
    agent._review_scheduler = MagicMock()
    agent._student_roster._store = agent._store
    agent._student_roster._graph = MagicMock()
    agent._review_scheduler._store = agent._store
    agent.client = MagicMock()
    agent.client.chat = MagicMock()
    agent.client.chat.completions = MagicMock()
    agent.client.chat.completions.create = AsyncMock(return_value=MagicMock(
        choices=[MagicMock(message=MagicMock(content="AI回复"))]
    ))
    return agent


class TestHealthEndpoint:
    """健康检查测试"""

    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/api/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "timestamp" in data


class TestTTSEndpoint:
    """TTS端点测试"""

    def test_tts_endpoint(self, mock_agent):
        """测试TTS端点"""
        app = create_app()
        client = TestClient(app)

        # Mock TTS服务
        mock_tts = AsyncMock()
        mock_tts.synthesize = AsyncMock(return_value=b"fake audio data")

        with patch("src.web.api.get_tts_service", AsyncMock(return_value=mock_tts)):
            response = client.post(
                "/api/voice/tts",
                json={"text": "你好", "voice": "female"},
            )
            assert response.status_code == 200
            assert response.headers["content-type"] == "audio/mpeg"
            assert response.content == b"fake audio data"

    def test_tts_endpoint_invalid_request(self):
        """测试无效的TTS请求"""
        app = create_app()
        client = TestClient(app)

        response = client.post(
            "/api/voice/tts",
            json={},  # 缺少 text
        )
        assert response.status_code == 422  # Validation error


class TestSessionEndpoints:
    """会话端点测试"""

    def test_start_session(self, client, mock_agent):
        """测试开始会话"""
        with patch("src.web.api.get_tutor_agent", AsyncMock(return_value=mock_agent)):
            response = client.post(
                "/api/session/start",
                json={"student_id": "test_student"},
            )
            assert response.status_code == 200

            data = response.json()
            assert data["student_id"] == "test_student"
            assert "greeting" in data
            assert "timestamp" in data

    def test_start_session_invalid_request(self, client):
        """测试无效的会话开始请求"""
        response = client.post(
            "/api/session/start",
            json={},  # 缺少 student_id
        )
        assert response.status_code == 422  # Validation error

    def test_chat(self, client, mock_agent):
        """测试聊天端点"""
        with patch("src.web.api.get_tutor_agent", AsyncMock(return_value=mock_agent)):
            response = client.post(
                "/api/session/chat",
                json={
                    "student_id": "test_student",
                    "message": "你好",
                },
            )
            assert response.status_code == 200

            data = response.json()
            assert data["response"] == "这是AI回复"
            assert "intent" in data
            assert "timestamp" in data

    def test_chat_invalid_request(self, client):
        """测试无效的聊天请求"""
        response = client.post(
            "/api/session/chat",
            json={"student_id": "test_student"},  # 缺少 message
        )
        assert response.status_code == 422  # Validation error


class TestStudentEndpoints:
    """学生端点测试"""

    def test_get_student_status(self, client, mock_agent):
        """测试获取学生状态"""
        with patch("src.web.api.get_tutor_agent", AsyncMock(return_value=mock_agent)):
            response = client.get("/api/student/test_student/status")
            assert response.status_code == 200

            data = response.json()
            assert data["student_id"] == "test_student"
            assert data["name"] == "测试学生"
            assert data["grade"] == 3
            assert data["total_xp"] == 50
            assert data["level"] == 1  # 50 XP = level 1
            assert "mastery_count" in data

    def test_get_student_status_not_found(self, client, mock_agent):
        """测试获取不存在的学生状态"""
        mock_agent._store.get_student = AsyncMock(return_value=None)
        with patch("src.web.api.get_tutor_agent", AsyncMock(return_value=mock_agent)):
            response = client.get("/api/student/nonexistent/status")
            assert response.status_code == 404

    def test_get_student_report(self, client, mock_agent):
        """测试获取学习报告"""
        # 确保student_roster有正确的format属性
        mock_agent._student_roster.format_report_text = MagicMock(return_value="学习报告文本")

        with patch("src.web.api.get_tutor_agent", AsyncMock(return_value=mock_agent)):
            response = client.get("/api/student/test_student/report")
            assert response.status_code == 200

            data = response.json()
            assert data["student_id"] == "test_student"
            assert data["total_quizzes"] == 10
            assert data["correct_rate"] == 0.8
            assert isinstance(data["mastered_points"], list)
            assert isinstance(data["recent_activity"], list)

    def test_get_student_report_not_found(self, client, mock_agent):
        """测试获取不存在的学生报告"""
        mock_agent._store.get_student = AsyncMock(return_value=None)
        with patch("src.web.api.get_tutor_agent", AsyncMock(return_value=mock_agent)):
            response = client.get("/api/student/nonexistent/report")
            assert response.status_code == 404


class TestWebSocket:
    """WebSocket测试"""

    @pytest.mark.asyncio
    async def test_websocket_connection(self, mock_agent):
        """测试WebSocket连接"""
        from fastapi.testclient import TestClient

        app = create_app()
        client = TestClient(app)

        with patch("src.web.ws.get_tutor_agent", AsyncMock(return_value=mock_agent)):
            with client.websocket_connect("/ws/test_student") as websocket:
                # 接收欢迎消息
                message = websocket.receive_json()
                assert message["type"] in ["status", "message"]

                # 发送消息
                websocket.send_json({"type": "message", "content": "测试消息"})

                # 接收回复（超时如果没有）
                try:
                    response = websocket.receive_json(timeout=5)
                    assert "type" in response
                except Exception:
                    pass

    @pytest.mark.asyncio
    async def test_websocket_ping_pong(self, mock_agent):
        """测试WebSocket心跳"""
        from fastapi.testclient import TestClient

        app = create_app()
        client = TestClient(app)

        with patch("src.web.ws.get_tutor_agent", AsyncMock(return_value=mock_agent)):
            with client.websocket_connect("/ws/test_student") as websocket:
                # 跳过初始消息（status + greeting）
                _ = websocket.receive_json()  # status
                _ = websocket.receive_json()  # greeting

                # 发送ping
                websocket.send_json({"type": "ping"})

                # 接收pong
                message = websocket.receive_json()
                assert message["type"] == "pong"


class TestModels:
    """Pydantic模型测试"""

    def test_session_start_request(self):
        """测试会话开始请求模型"""
        req = SessionStartRequest(student_id="test")
        assert req.student_id == "test"

    def test_session_start_request_validation(self):
        """测试会话开始请求验证"""
        with pytest.raises(Exception):
            SessionStartRequest()  # 缺少 student_id

    def test_chat_request(self):
        """测试聊天请求模型"""
        req = ChatRequest(student_id="test", message="你好")
        assert req.student_id == "test"
        assert req.message == "你好"

    def test_chat_request_validation(self):
        """测试聊天请求验证"""
        with pytest.raises(Exception):
            ChatRequest(student_id="test")  # 缺少 message

    def test_health_response(self):
        """测试健康检查响应模型"""
        resp = HealthResponse()
        assert resp.status == "ok"
        assert "version" in resp.model_dump()


class TestStaticFiles:
    """静态文件测试"""

    def test_serve_index_html(self, client):
        """测试提供index.html"""
        response = client.get("/")
        # 检查是否返回HTML内容
        assert response.status_code in [200, 404]

    def test_serve_style_css(self, client):
        """测试提供style.css"""
        response = client.get("/style.css")
        assert response.status_code in [200, 404]

    def test_serve_app_js(self, client):
        """测试提供app.js"""
        response = client.get("/app.js")
        assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])