from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel

from app.config import get_settings
from app.modules.auth import handlers
from app.modules.auth.schemas import LoginRequest
from app.shared.exceptions import UnauthorizedError
from app.shared.rate_limit import STRICT_LIMIT, limiter
from app.shared.security import ACCESS_COOKIE_NAME, REFRESH_COOKIE_NAME, get_current_admin
from app.shared.schemas import ok

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


class RefreshRequest(BaseModel):
    refresh_token: str | None = None


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    secure = settings.is_production
    response.set_cookie(
        ACCESS_COOKIE_NAME,
        access_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        refresh_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/auth",
    )


@router.post("/login")
@limiter.limit(STRICT_LIMIT)
async def login(request: Request, payload: LoginRequest, response: Response):
    body, access_token, refresh_token = handlers.handle_login(payload.email, payload.password)
    _set_auth_cookies(response, access_token, refresh_token)
    return body


@router.post("/refresh")
async def refresh(request: Request, response: Response, payload: RefreshRequest = None):
    refresh_token = None
    if payload is not None:
        refresh_token = payload.refresh_token
    if not refresh_token:
        refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise UnauthorizedError("Missing refresh token")
    body, access_token = handlers.handle_refresh(refresh_token)
    response.set_cookie(
        ACCESS_COOKIE_NAME,
        access_token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return body


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/auth")
    return ok({"logged_out": True})


@router.get("/me")
async def me(admin: str = Depends(get_current_admin)):
    return ok({"email": admin})