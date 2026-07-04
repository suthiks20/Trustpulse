from datetime import timedelta

import pytest
from jose import jwt

from app.shared import security
from app.shared.exceptions import UnauthorizedError


def test_access_token_round_trips():
    token = security.create_access_token("admin@example.com")
    payload = security.decode_token(token, "access")

    assert payload["sub"] == "admin@example.com"
    assert payload["type"] == "access"


def test_refresh_token_rejected_as_access_token():
    token = security.create_refresh_token("admin@example.com")

    with pytest.raises(UnauthorizedError):
        security.decode_token(token, "access")


def test_tampered_signature_is_rejected():
    token = security.create_access_token("admin@example.com")
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")

    with pytest.raises(UnauthorizedError):
        security.decode_token(tampered, "access")


def test_expired_token_is_rejected():
    token = security._create_token("admin@example.com", timedelta(seconds=-1), "access")

    with pytest.raises(UnauthorizedError):
        security.decode_token(token, "access")


def test_password_hash_roundtrip_and_rejects_wrong_password():
    hashed = security.hash_password("correct-horse-battery-staple")

    assert security.verify_password("correct-horse-battery-staple", hashed) is True
    assert security.verify_password("wrong-password", hashed) is False


def test_token_signed_with_wrong_secret_is_rejected():
    forged = jwt.encode(
        {"sub": "admin@example.com", "type": "access"}, "a-different-secret", algorithm=security.settings.JWT_ALGORITHM
    )

    with pytest.raises(UnauthorizedError):
        security.decode_token(forged, "access")
