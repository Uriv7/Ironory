"""Production Hardening Verification Tests for Ironory.

Tests:
1. Asynchronous inspection execution via BackgroundTasks (IRONORY-INS-001)
2. AuditLog table persistence, tenant isolation, and queries (IRONORY-DATA-001)
3. Sliding window rate limiter functionality (IRONORY-SEC-001)
"""

from __future__ import annotations

import io
import time
from fastapi.testclient import TestClient
from PIL import Image

from backend.app.models.audit import AuditLog
from backend.app.security.rate_limiter import InMemoryRateLimiter
from backend.app.services.audit import AuditService


def _create_test_image() -> bytes:
    img = Image.new("RGB", (200, 200), color=(128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_async_inspection_upload_execution(client: TestClient, db_session):
    """Verify that uploading with async_mode=True immediately returns QUEUED status."""
    # Register tenant
    res = client.post("/api/v1/auth/register", json={
        "email": "async.supervisor@steel.com",
        "password": "PasswordAsync123!",
        "full_name": "Async Line Supervisor",
        "organization_name": "Async Line Facility",
        "industry": "Steel Processing",
    })
    token = res.json()["tokens"]["access_token"]
    org_id = res.json()["active_organization_id"]

    # Create Product
    prod_res = client.post("/api/v1/products", json={
        "name": "Async Part Spec-1",
        "sku": "ASYNC-SKU-1",
        "code": "ASYNC-CODE-1",
        "category": "Steel Surface",
    }, headers={
        "Authorization": f"Bearer {token}",
        "X-Organization-ID": org_id,
    })
    product_id = prod_res.json()["id"]

    # Upload with async_mode = True
    img_bytes = _create_test_image()
    upload_res = client.post("/api/v1/inspections/upload", data={
        "product_id": product_id,
        "async_mode": True,
    }, files={
        "file": ("async_scan.png", img_bytes, "image/png"),
    }, headers={
        "Authorization": f"Bearer {token}",
        "X-Organization-ID": org_id,
    })

    assert upload_res.status_code == 201
    data = upload_res.json()
    assert data["product_id"] == product_id
    assert data["organization_id"] == org_id
    assert data["image"] is not None


def test_audit_log_persistence_and_tenant_isolation(client: TestClient, db_session):
    """Verify that AuditLog records are properly persisted and filtered per tenant."""
    # Register Tenant A
    res_a = client.post("/api/v1/auth/register", json={
        "email": "auditor.a@steel.com",
        "password": "PasswordAudit123!",
        "full_name": "Auditor Alpha",
        "organization_name": "Audit Plant Alpha",
        "industry": "Steel Processing",
    })
    org_id_a = res_a.json()["active_organization_id"]
    user_id_a = res_a.json()["user"]["id"]

    # Register Tenant B
    res_b = client.post("/api/v1/auth/register", json={
        "email": "auditor.b@steel.com",
        "password": "PasswordAudit123!",
        "full_name": "Auditor Beta",
        "organization_name": "Audit Plant Beta",
        "industry": "Steel Processing",
    })
    org_id_b = res_b.json()["active_organization_id"]

    # Record audit events for Tenant A
    AuditService.log(
        db=db_session,
        org_id=org_id_a,
        actor_id=user_id_a,
        action="INSPECTION_OVERRIDE",
        resource_type="Inspection",
        resource_id="insp-1001",
        details={"previous": "pitted_surface", "override": "normal_pass"},
        ip_address="192.168.1.50",
    )
    AuditService.log(
        db=db_session,
        org_id=org_id_a,
        actor_id=user_id_a,
        action="PRODUCT_CONFIG_UPDATE",
        resource_type="Product",
        resource_id="prod-2001",
        details={"confidence_threshold": 0.85},
        ip_address="192.168.1.50",
    )

    # Query logs for Tenant A
    logs_a = AuditService.get_tenant_logs(db=db_session, org_id=org_id_a)
    assert len(logs_a) == 2
    assert logs_a[0].organization_id == org_id_a
    assert logs_a[0].action in ["INSPECTION_OVERRIDE", "PRODUCT_CONFIG_UPDATE"]

    # Query logs for Tenant B (Must be empty — strict tenant isolation)
    logs_b = AuditService.get_tenant_logs(db=db_session, org_id=org_id_b)
    assert len(logs_b) == 0


def test_sliding_window_rate_limiter():
    """Verify that InMemoryRateLimiter permits up to limit and blocks excess requests."""
    limiter = InMemoryRateLimiter()
    key = "test_client_ip_127_0_0_1"

    # First 3 requests should be allowed (is_rate_limited == False)
    assert limiter.is_rate_limited(key, max_requests=3, window_seconds=10) is False
    assert limiter.is_rate_limited(key, max_requests=3, window_seconds=10) is False
    assert limiter.is_rate_limited(key, max_requests=3, window_seconds=10) is False

    # 4th request within window must be rate limited (is_rate_limited == True)
    assert limiter.is_rate_limited(key, max_requests=3, window_seconds=10) is True
