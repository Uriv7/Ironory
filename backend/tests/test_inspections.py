import io
from PIL import Image
from fastapi.testclient import TestClient


def _create_sample_png_bytes(width: int = 128, height: int = 128, color=(200, 200, 200)) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_inspection_session_lifecycle(client: TestClient):
    # Register Tenant A
    res_a = client.post("/api/v1/auth/register", json={
        "email": "owner.insp@steel.com",
        "password": "PasswordInsp123!",
        "full_name": "Inspection Supervisor",
        "organization_name": "Steel Rolling Plant Alpha",
        "industry": "Steel Processing"
    })
    token_a = res_a.json()["tokens"]["access_token"]
    org_id_a = res_a.json()["active_organization_id"]

    # Register Tenant B
    res_b = client.post("/api/v1/auth/register", json={
        "email": "owner.other@steel.com",
        "password": "PasswordOther123!",
        "full_name": "Other Supervisor",
        "organization_name": "Other Facility",
        "industry": "Steel Processing"
    })
    token_b = res_b.json()["tokens"]["access_token"]
    org_id_b = res_b.json()["active_organization_id"]

    # 1. Create Product
    prod_res = client.post("/api/v1/products", json={
        "name": "Surface Sheet Spec-A",
        "sku": "SHEET-A",
        "code": "PROD-SHEET-A",
        "category": "Steel Surface"
    }, headers={
        "Authorization": f"Bearer {token_a}",
        "X-Organization-ID": org_id_a
    })
    product_id = prod_res.json()["id"]

    # 2. Test Invalid Image Upload (Corrupted byte stream)
    corrupted_res = client.post("/api/v1/inspections/upload", data={
        "product_id": product_id
    }, files={
        "file": ("corrupted.png", b"this is completely fake not an image", "image/png")
    }, headers={
        "Authorization": f"Bearer {token_a}",
        "X-Organization-ID": org_id_a
    })
    assert corrupted_res.status_code == 422
    assert "Corrupted or invalid image" in corrupted_res.json()["error"]["message"]

    # 3. Test Valid Image Upload
    png_bytes = _create_sample_png_bytes(width=200, height=200)
    upload_res = client.post("/api/v1/inspections/upload", data={
        "product_id": product_id
    }, files={
        "file": ("steel_surface_sample_01.png", png_bytes, "image/png")
    }, headers={
        "Authorization": f"Bearer {token_a}",
        "X-Organization-ID": org_id_a
    })
    assert upload_res.status_code == 201
    inspection = upload_res.json()
    assert inspection["status"] == "QUEUED"
    assert inspection["image"]["width"] == 200
    assert inspection["image"]["height"] == 200
    assert inspection["image"]["checksum_sha256"] is not None

    inspection_id = inspection["id"]

    # 4. Stream Image back
    stream_res = client.get(f"/api/v1/inspections/{inspection_id}/image", headers={
        "Authorization": f"Bearer {token_a}",
        "X-Organization-ID": org_id_a
    })
    assert stream_res.status_code == 200
    assert stream_res.content == png_bytes

    # 5. CROSS-TENANT CHECK: Tenant B attempts to stream Tenant A's image
    cross_stream_res = client.get(f"/api/v1/inspections/{inspection_id}/image", headers={
        "Authorization": f"Bearer {token_b}",
        "X-Organization-ID": org_id_b
    })
    assert cross_stream_res.status_code == 404

    # 6. Submit Human Review
    review_res = client.post(f"/api/v1/inspections/{inspection_id}/review", json={
        "decision": "CONFIRMED",
        "final_class": "crazing",
        "is_defective": True,
        "notes": "Verified surface crazing defect during automated QA shift."
    }, headers={
        "Authorization": f"Bearer {token_a}",
        "X-Organization-ID": org_id_a
    })
    assert review_res.status_code == 200
    updated_insp = review_res.json()
    assert updated_insp["status"] == "COMPLETED"
    assert updated_insp["review"]["final_class"] == "crazing"
    assert updated_insp["review"]["is_defective"] is True

    # 7. List Inspections with Filter
    list_res = client.get("/api/v1/inspections", params={
        "product_id": product_id
    }, headers={
        "Authorization": f"Bearer {token_a}",
        "X-Organization-ID": org_id_a
    })
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1


def test_batch_inspection_upload(client: TestClient):
    # Register tenant
    res = client.post("/api/v1/auth/register", json={
        "email": "batch.owner@steel.com",
        "password": "PasswordBatch123!",
        "full_name": "Batch Supervisor",
        "organization_name": "Batch Steel Works",
        "industry": "Steel Processing"
    })
    token = res.json()["tokens"]["access_token"]
    org_id = res.json()["active_organization_id"]

    # Create Product
    prod_res = client.post("/api/v1/products", json={
        "name": "Coil Strip Batch Spec",
        "sku": "COIL-BATCH-01",
        "code": "PROD-COIL-01",
        "category": "Steel Coil"
    }, headers={
        "Authorization": f"Bearer {token}",
        "X-Organization-ID": org_id
    })
    prod_id = prod_res.json()["id"]

    # Prepare 3 images
    img1 = _create_sample_png_bytes(100, 100)
    img2 = _create_sample_png_bytes(100, 100)
    img3 = _create_sample_png_bytes(100, 100)

    batch_res = client.post(
        "/api/v1/inspections/batch",
        data={"product_id": prod_id},
        files=[
            ("files", ("sample_1.png", img1, "image/png")),
            ("files", ("sample_2.png", img2, "image/png")),
            ("files", ("sample_3.png", img3, "image/png")),
        ],
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-ID": org_id,
        }
    )

    assert batch_res.status_code == 201
    data = batch_res.json()
    assert data["batch_size"] == 3
    assert data["successful_count"] == 3
    assert data["failed_count"] == 0
    assert len(data["inspections"]) == 3


def test_export_inspections_csv(client: TestClient):
    # Register tenant
    res = client.post("/api/v1/auth/register", json={
        "email": "csv.owner@steel.com",
        "password": "PasswordCsv123!",
        "full_name": "Audit Manager",
        "organization_name": "CSV Audit Mill",
        "industry": "Steel Processing"
    })
    token = res.json()["tokens"]["access_token"]
    org_id = res.json()["active_organization_id"]

    # Export CSV
    csv_res = client.get(
        "/api/v1/inspections/export/csv",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-ID": org_id,
        }
    )

    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    assert "Inspection ID" in csv_res.text
    assert "Predicted Class" in csv_res.text

