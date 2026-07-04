from app.config import get_settings
from app.shared.exceptions import UnauthorizedError
from app.shared.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)

settings = get_settings()


def authenticate(email: str, password: str) -> tuple[str, str]:
    if not settings.ADMIN_PASSWORD_HASH:
        raise UnauthorizedError("Admin account is not seeded — run the seed_admin script")

    if email != settings.ADMIN_EMAIL or not verify_password(password, settings.ADMIN_PASSWORD_HASH):
        raise UnauthorizedError("Invalid email or password")

    return create_access_token(email), create_refresh_token(email)


def refresh(refresh_token: str) -> str:
    payload = decode_token(refresh_token, "refresh")
    return create_access_token(payload["sub"])
