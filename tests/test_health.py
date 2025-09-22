"""
Health endpoint tests
"""
import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test basic health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "FastAPI Production App"


def test_database_health_check(client: TestClient):
    """Test database health check endpoint"""
    response = client.get("/api/v1/health/database")
    assert response.status_code == 200
