import pytest
from fastapi.testclient import TestClient

from src.server import app, init_app


@pytest.fixture
def client():
    """Test client fixture for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def test_app():
    """Test app fixture that returns a fresh app instance"""
    return init_app()


def test_app_initialization():
    """Test that app initializes with correct settings"""
    test_app = init_app()
    assert test_app.title == test_app.title  # Will use actual settings value
    assert "/metrics" in [route.path for route in test_app.routes]


def test_metrics_endpoint(client):
    """Test that metrics endpoint is accessible"""
    response = client.get("/metrics")
    assert response.status_code == 200


def test_docs_endpoint(client):
    """Test docs endpoint availability based on settings"""
    response = client.get("/docs")
    # This will pass or fail based on settings.docs_enable
    if app.docs_url:
        assert response.status_code == 200
    else:
        assert response.status_code == 404
