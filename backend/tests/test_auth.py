from fastapi.testclient import TestClient


def test_user_registration_success(client: TestClient):
    payload = {
        "email": "sarah.connor@cyberdyne-steel.com",
        "password": "Password123!",
        "full_name": "Sarah Connor",
        "organization_name": "Cyberdyne Steel Mills",
        "industry": "Steel Manufacturing"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["user"]["email"] == "sarah.connor@cyberdyne-steel.com"
    assert data["user"]["full_name"] == "Sarah Connor"
    assert len(data["user"]["memberships"]) == 1
    assert data["user"]["memberships"][0]["role"] == "OWNER"
    assert data["tokens"]["access_token"] is not None
    assert data["tokens"]["refresh_token"] is not None
    assert data["active_organization_id"] is not None


def test_user_registration_weak_password(client: TestClient):
    payload = {
        "email": "weak.pw@company.com",
        "password": "weak",
        "full_name": "Weak User",
        "organization_name": "Weak Corp"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_user_registration_duplicate_email(client: TestClient):
    payload = {
        "email": "duplicate@company.com",
        "password": "ValidPassword123!",
        "full_name": "Original User",
        "organization_name": "Original Corp"
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    # Second registration with same email should fail with 409 Conflict
    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["error"]["message"]


def test_login_flow(client: TestClient):
    # Register user
    reg_payload = {
        "email": "login.test@company.com",
        "password": "StrongPassword999!",
        "full_name": "Login Test User",
        "organization_name": "Login Dynamics"
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    # Valid Login
    login_res = client.post("/api/v1/auth/login", json={
        "email": "login.test@company.com",
        "password": "StrongPassword999!"
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["tokens"]["access_token"] is not None

    token = login_data["tokens"]["access_token"]
    refresh_token = login_data["tokens"]["refresh_token"]

    # Invalid Password Login
    bad_login_res = client.post("/api/v1/auth/login", json={
        "email": "login.test@company.com",
        "password": "WrongPassword123!"
    })
    assert bad_login_res.status_code == 401

    # Check /auth/me with Bearer token
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "login.test@company.com"

    # Refresh Token Rotation
    refresh_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 200
    new_tokens = refresh_res.json()
    assert new_tokens["access_token"] is not None
    assert new_tokens["refresh_token"] != refresh_token  # Rotated!

    # Old refresh token should now be rejected
    old_refresh_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert old_refresh_res.status_code == 401

    # Logout
    logout_res = client.post("/api/v1/auth/logout", json={"refresh_token": new_tokens["refresh_token"]})
    assert logout_res.status_code == 200
