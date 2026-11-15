from fastapi.testclient import TestClient


def test_tenant_isolation_and_rbac(client: TestClient):
    # 1. Register Tenant A (Apex Metal Corp)
    res_a = client.post("/api/v1/auth/register", json={
        "email": "owner.apex@apex-metal.com",
        "password": "PasswordApex123!",
        "full_name": "Apex Owner",
        "organization_name": "Apex Metal Corp",
        "industry": "Metal Processing"
    })
    assert res_a.status_code == 201
    data_a = res_a.json()
    token_a = data_a["tokens"]["access_token"]
    org_id_a = data_a["active_organization_id"]

    # 2. Register Tenant B (Titanium Industries)
    res_b = client.post("/api/v1/auth/register", json={
        "email": "owner.titanium@titanium.com",
        "password": "PasswordTitanium123!",
        "full_name": "Titanium Owner",
        "organization_name": "Titanium Industries",
        "industry": "Aerospace Alloys"
    })
    assert res_b.status_code == 201
    data_b = res_b.json()
    token_b = data_b["tokens"]["access_token"]
    org_id_b = data_b["active_organization_id"]

    # 3. Verify Tenant A can fetch its own profile
    profile_a = client.get("/api/v1/organizations/current", headers={
        "Authorization": f"Bearer {token_a}",
        "X-Organization-ID": org_id_a
    })
    assert profile_a.status_code == 200
    assert profile_a.json()["name"] == "Apex Metal Corp"

    # 4. CROSS-TENANT ATTACK TEST:
    # Tenant A attempts to access Tenant B's data using Tenant A's token
    cross_tenant_res = client.get("/api/v1/organizations/current", headers={
        "Authorization": f"Bearer {token_a}",
        "X-Organization-ID": org_id_b  # Attempting to access Tenant B!
    })
    assert cross_tenant_res.status_code == 403
    assert cross_tenant_res.json()["error"]["code"] == "CROSS_TENANT_ACCESS_DENIED"

    # 5. Member Invite & RBAC Test
    # First, register inspector user account
    client.post("/api/v1/auth/register", json={
        "email": "inspector.apex@apex-metal.com",
        "password": "PasswordInsp123!",
        "full_name": "Apex Inspector",
        "organization_name": "Apex Secondary Unit",
        "industry": "Metal Processing"
    })

    # Add this user to Tenant A as an INSPECTOR
    invite_res = client.post("/api/v1/organizations/invitations", json={
        "email": "inspector.apex@apex-metal.com",
        "role": "INSPECTOR"
    }, headers={
        "Authorization": f"Bearer {token_a}",
        "X-Organization-ID": org_id_a
    })
    assert invite_res.status_code == 201

    # Verify members list in Tenant A
    members_res = client.get("/api/v1/organizations/members", headers={
        "Authorization": f"Bearer {token_a}",
        "X-Organization-ID": org_id_a
    })
    assert members_res.status_code == 200
    members = members_res.json()
    assert len(members) >= 2  # Owner + Added Inspector

    # Login as Inspector
    inspector_login = client.post("/api/v1/auth/login", json={
        "email": "inspector.apex@apex-metal.com",
        "password": "PasswordInsp123!"
    })
    assert inspector_login.status_code == 200
    inspector_token = inspector_login.json()["tokens"]["access_token"]

    # RBAC TEST: Inspector attempts to update Tenant A's organization profile (Requires OWNER or ADMIN)
    rbac_fail_res = client.patch("/api/v1/organizations/current", json={
        "name": "Hacked Name"
    }, headers={
        "Authorization": f"Bearer {inspector_token}",
        "X-Organization-ID": org_id_a
    })
    assert rbac_fail_res.status_code == 403
    assert "role permissions" in rbac_fail_res.json()["error"]["message"]
