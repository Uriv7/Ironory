from fastapi.testclient import TestClient


def test_root_status(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Ironory"
    assert data["status"] == "online"
    assert "X-Correlation-ID" in response.headers


def test_health_endpoint(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == "Ironory"
    assert "timestamp" in data
    assert "X-Correlation-ID" in response.headers


def test_ready_endpoint(client: TestClient):
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"


def test_system_info_endpoint(client: TestClient):
    response = client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "Ironory"
    assert data["version"] == "1.0.0-foundation"
    assert data["api_prefix"] == "/api/v1"
    # Ensure no secrets or credentials leaked
    assert "password" not in str(data).lower()
    assert "secret" not in str(data).lower()
