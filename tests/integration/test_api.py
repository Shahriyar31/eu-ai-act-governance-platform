import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Create a test client with mocked database initialisation."""
    with patch("src.database.init_db.init_db"):
        from src.api.main import app
        with TestClient(app) as c:
            yield c


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_healthy_status(self, client):
        data = response = client.get("/health").json()
        assert data["status"] == "healthy"

    def test_health_includes_timestamp(self, client):
        data = client.get("/health").json()
        assert "timestamp" in data

    def test_health_includes_service_name(self, client):
        data = client.get("/health").json()
        assert "EU AI Act" in data["service"]


class TestMetricsEndpoint:
    def test_metrics_returns_200(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_returns_prometheus_format(self, client):
        response = client.get("/metrics")
        # Prometheus metrics always start with # HELP
        assert b"# HELP" in response.content

    def test_metrics_includes_custom_compliance_counter(self, client):
        response = client.get("/metrics")
        assert b"compliance_assessments_total" in response.content