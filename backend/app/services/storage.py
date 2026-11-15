import os
import re
import uuid
import pathlib
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional, Tuple
from backend.app.core.config import settings
from backend.app.core.exceptions import ValidationException, AppException


class BaseStorageService(ABC):
    """Abstract storage service interface for local and cloud object storage."""

    @abstractmethod
    def save(self, file_obj: BinaryIO, tenant_id: str, original_filename: str, subfolder: str = "uploads") -> str:
        """Saves a file and returns its storage key/relative path."""
        pass

    @abstractmethod
    def get(self, storage_key: str) -> bytes:
        """Retrieves file bytes given a storage key."""
        pass

    @abstractmethod
    def delete(self, storage_key: str) -> bool:
        """Deletes a file by its storage key."""
        pass

    @abstractmethod
    def exists(self, storage_key: str) -> bool:
        """Checks if a file exists."""
        pass


class LocalStorageService(BaseStorageService):
    """
    Local filesystem storage adapter.
    Enforces tenant folder isolation, path traversal prevention, and sanitized UUID filenames.
    """

    def __init__(self, root_dir: Optional[str] = None):
        self.root_path = pathlib.Path(root_dir or settings.STORAGE_LOCAL_ROOT).resolve()
        self.root_path.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        # Strip path characters
        clean_name = os.path.basename(filename)
        # Normalize and keep only safe alphanumeric, dots, dashes, underscores
        clean_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", clean_name)
        ext = pathlib.Path(clean_name).suffix.lower()
        if not ext:
            ext = ".bin"
        return f"{uuid.uuid4().hex}{ext}"

    def _resolve_safe_path(self, storage_key: str) -> pathlib.Path:
        # Prevent path traversal vulnerabilities
        target_path = (self.root_path / storage_key).resolve()
        try:
            target_path.relative_to(self.root_path)
        except ValueError:
            raise ValidationException("Illegal path traversal detected in storage key")
        return target_path

    def save(self, file_obj: BinaryIO, tenant_id: str, original_filename: str, subfolder: str = "uploads") -> str:
        # Validate tenant_id
        if not tenant_id or re.search(r"[^a-zA-Z0-9_-]", tenant_id) or ".." in tenant_id:
            raise ValidationException("Invalid tenant identifier for storage: contains prohibited characters")

        safe_tenant = tenant_id.strip()
        if not subfolder or re.search(r"[^a-zA-Z0-9_-]", subfolder) or ".." in subfolder:
            raise ValidationException("Invalid subfolder identifier for storage")
        safe_subfolder = subfolder.strip()

        safe_filename = self._sanitize_filename(original_filename)

        relative_key = os.path.join(safe_tenant, safe_subfolder, safe_filename)
        full_path = self._resolve_safe_path(relative_key)

        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write contents safely
        file_obj.seek(0)
        with open(full_path, "wb") as f:
            f.write(file_obj.read())

        return relative_key

    def get(self, storage_key: str) -> bytes:
        full_path = self._resolve_safe_path(storage_key)
        if not full_path.is_file():
            raise AppException(f"Stored file not found: {storage_key}", status_code=404, code="FILE_NOT_FOUND")
        with open(full_path, "rb") as f:
            return f.read()

    def delete(self, storage_key: str) -> bool:
        full_path = self._resolve_safe_path(storage_key)
        if full_path.is_file():
            full_path.unlink()
            return True
        return False

    def exists(self, storage_key: str) -> bool:
        try:
            full_path = self._resolve_safe_path(storage_key)
            return full_path.is_file()
        except ValidationException:
            return False


# Singleton factory for storage service
def get_storage_service() -> BaseStorageService:
    if settings.STORAGE_BACKEND == "local":
        return LocalStorageService()
    raise NotImplementedError(f"Storage backend '{settings.STORAGE_BACKEND}' not supported in Phase 1.")
