import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from backend.app.models.inspection import InspectionStatus


def _get_auth_headers(client: TestClient, email: str = "analytics.supervisor@steel.com"):
    res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "PasswordAnalytics123!",
        "full_name": "Analytics Supervisor",
        "organization_name": "Precision Steel Works",
        "industry": "Steel Processing",
    })
    data = res.json()
    token = data["tokens"]["access_token"]
    org_id = data["active_organization_id"]
    return {
        "Authorization": f"Bearer {token}",
        "X-Organization-ID": org_id,
    }


def test_analytics_overview_unauthorized(client: TestClient):
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 401


def test_analytics_overview_authorized(client: TestClient):
    headers = _get_auth_headers(client, "overview.analyst@steel.com")
    response = client.get("/api/v1/analytics/overview", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_inspections" in data
    assert "total_defective" in data
    assert "total_passed" in data
    assert "pass_rate_percentage" in data
    assert "pending_reviews" in data
    assert isinstance(data["pass_rate_percentage"], (int, float))


def test_analytics_defect_distribution(client: TestClient):
    headers = _get_auth_headers(client, "defect.analyst@steel.com")
    response = client.get("/api/v1/analytics/defect-distribution", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_analytics_trends(client: TestClient):
    headers = _get_auth_headers(client, "trends.analyst@steel.com")
    response = client.get("/api/v1/analytics/trends?days=7", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_download_inspection_report_pdf(client: TestClient):
    headers = _get_auth_headers(client, "pdf.analyst@steel.com")

    # Create product and upload image
    p_resp = client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "name": "Steel Coil Standard",
            "sku": "SCS-001",
            "code": "PROD-SCS-001",
            "category": "Hot-Rolled Steel",
        },
    )
    assert p_resp.status_code == 201
    prod_id = p_resp.json()["id"]

    img = Image.new("RGB", (224, 224), color=(140, 140, 140))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    upload_resp = client.post(
        "/api/v1/inspections/upload",
        headers=headers,
        data={"product_id": prod_id},
        files={"file": ("test_surface.jpg", buf, "image/jpeg")},
    )
    assert upload_resp.status_code == 201
    inspection_id = upload_resp.json()["id"]

    # Download PDF Report
    pdf_resp = client.get(f"/api/v1/inspections/{inspection_id}/report.pdf", headers=headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 500  # Valid binary PDF with headers and tables
    assert pdf_resp.content.startswith(b"%PDF")
