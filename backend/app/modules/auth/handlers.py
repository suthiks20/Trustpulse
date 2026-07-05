from app.modules.auth import services
from app.shared.schemas import ok


def handle_login(email: str, password: str) -> tuple[dict, str, str]:
    access_token, refresh_token = services.authenticate(email, password)
    body = ok({"email": email, "access_token": access_token, "refresh_token": refresh_token})
    return body, access_token, refresh_token


def handle_refresh(refresh_token: str) -> tuple[dict, str]:
    access_token = services.refresh(refresh_token)
    body = ok({"refreshed": True, "access_token": access_token})
    return body, access_token