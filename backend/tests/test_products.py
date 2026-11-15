from fastapi.testclient import TestClient


def test_product_crud_and_tenant_isolation(client: TestClient):
    # Register Tenant A
    res_a = client.post("/api/v1/auth/register", json={
        "email": "owner.prod.a@steel.com",
        "password": "PasswordProdA123!",
        "full_name": "Prod Owner A",
        "organization_name": "Steel Mill A",
        "industry": "Steel Manufacturing"
    })
    token_a = res_a.json()["tokens"]["access_token"]
    org_id_a = res_a.json()["active_organization_id"]

    # Register Tenant B
    res_b = client.post("/api/v1/auth/register", json={
        "email": "owner.prod.b@steel.com",
        "password": "PasswordProdB123!",
        "full_name": "Prod Owner B",
        "organization_name": "Steel Mill B",
        "industry": "Steel Manufacturing"
    })
    token_b = res_b.json()["tokens"]["access_token"]
    org_id_b = res_b.json()["active_organization_id"]

    # 1. Create Product in Tenant A
    product_payload = {
        "name": "Hot Rolled Steel Coil 1020",
        "sku": "HR-STEEL-1020",
        "code": "PROD-COIL-01",
        "description": "High tensile hot-rolled carbon steel coil for chassis components",
        "category": "Steel Surface",
        "configuration": {
            "model_type": "BASELINE_CNN",
            "confidence_threshold": 0.80,
            "anomaly_threshold": 0.05,
            "defect_classes": ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]
        }
    }
    create_res = client.post("/api/v1/products", json=product_payload, headers={
        "Authorization": f"Bearer {token_a}",
        "X-Organization-ID": org_id_a
    })
    assert create_res.status_code == 201
    prod_a = create_res.json()
    assert prod_a["code"] == "PROD-COIL-01"
    assert prod_a["configuration"]["confidence_threshold"] == 0.80

    prod_id = prod_a["id"]

    # 2. Duplicate Code Rejection within Tenant A
    dup_res = client.post("/api/v1/products", json=product_payload, headers={
        "Authorization": f"Bearer {token_a}",
        "X-Organization-ID": org_id_a
    })
    assert dup_res.status_code == 409
    assert "already exists" in dup_res.json()["error"]["message"]

    # 3. Same Code IS Allowed in Tenant B (Multi-tenant scoped code uniqueness)
    create_b_res = client.post("/api/v1/products", json=product_payload, headers={
        "Authorization": f"Bearer {token_b}",
        "X-Organization-ID": org_id_b
    })
    assert create_b_res.status_code == 201

    # 4. List Products in Tenant A
    list_res = client.get("/api/v1/products", headers={
        "Authorization": f"Bearer {token_a}",
        "X-Organization-ID": org_id_a
    })
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # 5. CROSS-TENANT ISOLATION: Tenant B tries to fetch Tenant A's product
    cross_res = client.get(f"/api/v1/products/{prod_id}", headers={
        "Authorization": f"Bearer {token_b}",
        "X-Organization-ID": org_id_b
    })
    assert cross_res.status_code == 404

    # 6. Update Product in Tenant A
    update_res = client.patch(f"/api/v1/products/{prod_id}", json={
        "name": "Updated Coil 1020-Pro"
    }, headers={
        "Authorization": f"Bearer {token_a}",
        "X-Organization-ID": org_id_a
    })
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Updated Coil 1020-Pro"

    # 7. Soft Delete
    del_res = client.delete(f"/api/v1/products/{prod_id}", headers={
        "Authorization": f"Bearer {token_a}",
        "X-Organization-ID": org_id_a
    })
    assert del_res.status_code == 200
