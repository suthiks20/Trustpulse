import io

from PIL import Image, UnidentifiedImageError

from app.config import get_settings
from app.shared.exceptions import ValidationAppError

settings = get_settings()


def validate_image_bytes(file_bytes: bytes) -> None:
    if not file_bytes:
        raise ValidationAppError("Uploaded file is empty")

    if len(file_bytes) > settings.max_upload_size_bytes:
        raise ValidationAppError(f"Image exceeds max size of {settings.MAX_UPLOAD_SIZE_MB}MB")

    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        raise ValidationAppError("Uploaded file is not a valid image")
