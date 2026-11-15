import io
import pytest
from backend.app.services.storage import LocalStorageService
from backend.app.core.exceptions import ValidationException, AppException


def test_local_storage_lifecycle(tmp_path):
    storage = LocalStorageService(root_dir=str(tmp_path))

    # Create dummy content
    data = b"Simulated image content for quality inspection"
    file_obj = io.BytesIO(data)

    # Save
    key = storage.save(
        file_obj=file_obj,
        tenant_id="org_12345",
        original_filename="sample_metal_surface.png",
        subfolder="inspections"
    )

    assert key.startswith("org_12345/inspections/")
    assert key.endswith(".png")
    assert storage.exists(key) is True

    # Read back
    retrieved = storage.get(key)
    assert retrieved == data

    # Delete
    deleted = storage.delete(key)
    assert deleted is True
    assert storage.exists(key) is False


def test_path_traversal_prevention(tmp_path):
    storage = LocalStorageService(root_dir=str(tmp_path))

    # Test malicious storage key attempting path traversal
    with pytest.raises(ValidationException):
        storage.get("../../../etc/passwd")

    with pytest.raises(ValidationException):
        storage.save(io.BytesIO(b"data"), tenant_id="../malicious", original_filename="test.png")
