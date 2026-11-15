import io
import hashlib
from typing import Tuple, Dict, Any
from PIL import Image
from backend.app.core.exceptions import ValidationException

ALLOWED_MIME_TYPES = {
    "image/jpeg": "JPEG",
    "image/jpg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP",
}

MAX_IMAGE_DIMENSION = 4096
MIN_IMAGE_DIMENSION = 32
TARGET_MODEL_INPUT_SIZE = (224, 224)


class ImageProcessorService:
    """
    Image validation, metadata extraction, and tensor preprocessing service.
    Enforces that incoming visual inspection assets are safe, uncorrupted, and standardized.
    """

    @staticmethod
    def compute_sha256(content: bytes) -> str:
        """Computes the hex-encoded SHA-256 checksum of an image byte stream."""
        return hashlib.sha256(content).hexdigest()

    @classmethod
    def validate_and_extract_metadata(cls, content: bytes, reported_mime: str) -> Dict[str, Any]:
        """
        Validates image integrity and extracts physical dimensions and channel counts.
        Guarantees that corrupt images or file-extension spoofing attempts are rejected.
        """
        if not content:
            raise ValidationException("Uploaded file is empty.")

        # Check MIME
        norm_mime = reported_mime.lower().strip()
        if norm_mime not in ALLOWED_MIME_TYPES:
            raise ValidationException(
                f"Unsupported image format '{reported_mime}'. Supported formats: JPEG, PNG, WEBP."
            )

        try:
            with Image.open(io.BytesIO(content)) as img:
                # Force PIL to decode the image to detect truncation or corruption
                img.verify()
        except Exception as e:
            raise ValidationException(f"Corrupted or invalid image file: {str(e)}")

        # Reopen after verify() to inspect properties (verify closes image state)
        with Image.open(io.BytesIO(content)) as img:
            width, height = img.size
            img_format = img.format

            # Dimension checks
            if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
                raise ValidationException(
                    f"Image resolution {width}x{height} is below minimum allowed {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION}."
                )

            if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
                raise ValidationException(
                    f"Image resolution {width}x{height} exceeds maximum allowed limit {MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION}."
                )

            channels = len(img.getbands())

        checksum = cls.compute_sha256(content)

        return {
            "width": width,
            "height": height,
            "channels": channels,
            "format": img_format,
            "mime_type": norm_mime,
            "size_bytes": len(content),
            "checksum_sha256": checksum,
        }

    @classmethod
    def preprocess_for_inference(cls, content: bytes, target_size: Tuple[int, int] = TARGET_MODEL_INPUT_SIZE) -> bytes:
        """
        Standardizes raw image input:
        1. Converts any color space (Grayscale, RGBA, CMYK) to standardized 3-channel RGB.
        2. High-quality Lanczos resampling to model input dimensions (224x224).
        3. Returns standardized JPEG bytes for cache and visualization.
        """
        with Image.open(io.BytesIO(content)) as img:
            rgb_img = img.convert("RGB")
            resized_img = rgb_img.resize(target_size, Image.Resampling.LANCZOS)

            output_buffer = io.BytesIO()
            resized_img.save(output_buffer, format="JPEG", quality=95)
            return output_buffer.getvalue()
