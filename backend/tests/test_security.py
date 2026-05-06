from datetime import timedelta

from src.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hash_roundtrip():
    password = "S3curePassw0rd!"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_jwt_create_and_decode_contains_subject():
    token = create_access_token({"sub": "123"}, expires_delta=timedelta(minutes=5))
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "123"
    assert "exp" in payload


def test_jwt_decode_invalid_returns_none():
    assert decode_access_token("not-a-jwt") is None

