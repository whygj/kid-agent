"""Health check and monitoring endpoint tests"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def health_client():
    """Create test client with health endpoints"""
    from src.web.app import create_app
    return TestClient(create_app())


class TestHealthEndpoint:
    """Basic health check endpoint tests"""

    def test_health_endpoint_exists(self, health_client):
        """Test that /health endpoint exists and returns 200"""
        response = health_client.get("/health")
        assert response.status_code == 200

    def test_health_response_structure(self, health_client):
        """Test that /health returns correct structure"""
        response = health_client.get("/health")
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "version" in data

    def test_health_status_healthy(self, health_client):
        """Test that /health returns healthy status"""
        response = health_client.get("/health")
        data = response.json()

        assert data["status"] == "healthy"

    def test_health_version_format(self, health_client):
        """Test that health endpoint returns version in correct format"""
        response = health_client.get("/health")
        data = response.json()

        assert isinstance(data["version"], str)
        assert "." in data["version"]  # Simple version check

    def test_health_timestamp_format(self, health_client):
        """Test that health endpoint returns ISO 8601 timestamp"""
        response = health_client.get("/health")
        data = response.json()

        assert isinstance(data["timestamp"], str)
        # ISO 8601 format should have T in it
        assert "T" in data["timestamp"]


class TestDetailedHealthEndpoint:
    """Detailed health check endpoint tests"""

    def test_detailed_health_endpoint_exists(self, health_client):
        """Test that /health/detailed endpoint exists and returns 200"""
        response = health_client.get("/health/detailed")
        assert response.status_code == 200

    def test_detailed_health_response_structure(self, health_client):
        """Test that /health/detailed returns correct structure"""
        response = health_client.get("/health/detailed")
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "uptime_seconds" in data
        assert "components" in data

    def test_detailed_health_has_checks(self, health_client):
        """Test that /health/detailed has component checks"""
        response = health_client.get("/health/detailed")
        data = response.json()

        components = data["components"]
        assert "checks" in components

        checks = components["checks"]
        # Should have at least some checks
        assert len(checks) > 0

    def test_detailed_health_database_check(self, health_client):
        """Test that /health/detailed has database check"""
        response = health_client.get("/health/detailed")
        data = response.json()

        checks = data["components"]["checks"]
        assert "database" in checks

        db_check = checks["database"]
        assert "status" in db_check

    def test_detailed_health_llm_check(self, health_client):
        """Test that /health/detailed has LLM API check"""
        response = health_client.get("/health/detailed")
        data = response.json()

        checks = data["components"]["checks"]
        assert "llm_api" in checks

        llm_check = checks["llm_api"]
        assert "status" in llm_check
        assert "provider" in llm_check

    def test_detailed_health_uptime(self, health_client):
        """Test that /health/detailed includes uptime"""
        response = health_client.get("/health/detailed")
        data = response.json()

        uptime = data["uptime_seconds"]
        assert isinstance(uptime, (int, float))
        assert uptime >= 0

    def test_detailed_health_status_values(self, health_client):
        """Test that component statuses are valid"""
        response = health_client.get("/health/detailed")
        data = response.json()

        valid_statuses = ["healthy", "unhealthy", "warning", "degraded"]

        overall_status = data["status"]
        assert overall_status in valid_statuses

        for check_name, check_data in data["components"]["checks"].items():
            assert "status" in check_data
            assert check_data["status"] in valid_statuses


class TestMetricsEndpoint:
    """Prometheus metrics endpoint tests"""

    def test_metrics_endpoint_exists(self, health_client):
        """Test that /metrics endpoint exists and returns 200"""
        response = health_client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_content_type(self, health_client):
        """Test that /metrics returns text/plain"""
        response = health_client.get("/metrics")
        assert response.headers["content-type"] == "text/plain; charset=utf-8"

    def test_metrics_has_help_and_type(self, health_client):
        """Test that metrics have HELP and TYPE comments"""
        response = health_client.get("/metrics")
        content = response.text

        assert "# HELP" in content
        assert "# TYPE" in content

    def test_metrics_has_uptime(self, health_client):
        """Test that /metrics includes uptime metric"""
        response = health_client.get("/metrics")
        content = response.text

        assert "kid_agent_uptime_seconds" in content

    def test_metrics_has_health_status(self, health_client):
        """Test that /metrics includes health status metric"""
        response = health_client.get("/metrics")
        content = response.text

        assert "kid_agent_health_status" in content

    def test_metrics_has_version(self, health_client):
        """Test that /metrics includes version metric"""
        response = health_client.get("/metrics")
        content = response.text

        assert "kid_agent_version" in content

    def test_metrics_numeric_values(self, health_client):
        """Test that metrics have numeric values"""
        response = health_client.get("/metrics")
        content = response.text

        lines = content.split("\n")
        metric_lines = [line for line in lines if line and not line.startswith("#")]

        # Each metric line should have a value
        for line in metric_lines:
            parts = line.split()
            assert len(parts) >= 2, f"Invalid metric line: {line}"
            # Check if second part is numeric
            try:
                float(parts[1])
            except ValueError:
                pytest.fail(f"Metric value is not numeric: {line}")


class TestPingEndpoint:
    """Ping endpoint tests"""

    def test_ping_endpoint_exists(self, health_client):
        """Test that /ping endpoint exists and returns 200"""
        response = health_client.get("/ping")
        assert response.status_code == 200

    def test_ping_pong(self, health_client):
        """Test that /ping returns pong"""
        response = health_client.get("/ping")
        data = response.json()

        assert "ping" in data
        assert data["ping"] == "pong"


class TestHealthIntegration:
    """Integration tests for health endpoints"""

    def test_all_health_endpoints_accessible(self, health_client):
        """Test that all health endpoints are accessible"""
        endpoints = ["/health", "/health/detailed", "/metrics", "/ping"]

        for endpoint in endpoints:
            response = health_client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} not accessible"

    def test_health_and_detailed_consistent(self, health_client):
        """Test that /health and /health/detailed return consistent version"""
        health_response = health_client.get("/health")
        detailed_response = health_client.get("/health/detailed")

        health_data = health_response.json()
        detailed_data = detailed_response.json()

        assert health_data["version"] == detailed_data["version"]
        assert health_data["status"] == detailed_data["status"]
