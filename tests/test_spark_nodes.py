"""Unit tests for Accelerator Resource Provider"""

import pytest
from fastapi.testclient import TestClient
from src.itl_accelerator_provider.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "ITL Accelerator Resource Provider"


def test_create_spark_node(client):
    """Test creating a SparkNode"""
    response = client.post(
        "/subscriptions/sub-123/resourceGroups/rg-prod/providers/ITL.Accelerator/sparkNodes",
        json={
            "name": "dgx-1",
            "location": "us-east-1",
            "sku": {"name": "DGX-H100-8GPU"},
            "properties": {},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "dgx-1"


def test_list_spark_nodes(client):
    """Test listing SparkNodes"""
    response = client.get(
        "/subscriptions/sub-123/resourceGroups/rg-prod/providers/ITL.Accelerator/sparkNodes"
    )
    assert response.status_code == 200
    data = response.json()
    assert "value" in data
    assert "total_count" in data
