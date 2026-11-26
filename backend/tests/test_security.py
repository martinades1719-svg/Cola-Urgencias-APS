from uuid import uuid4

import pytest
from fastapi import HTTPException

from security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_does_not_store_plain_text() -> None:
    plain_password = "Prueba_2026!Segura"

    password_hash = hash_password(
        plain_password
    )

    assert password_hash != plain_password
    assert password_hash.startswith(
        "$argon2"
    )


def test_valid_password_is_accepted() -> None:
    plain_password = "Prueba_2026!Segura"

    password_hash = hash_password(
        plain_password
    )

    result = verify_password(
        plain_password=plain_password,
        password_hash=password_hash,
    )

    assert result is True


def test_invalid_password_is_rejected() -> None:
    password_hash = hash_password(
        "Prueba_2026!Segura"
    )

    result = verify_password(
        plain_password="ContraseñaIncorrecta_2026",
        password_hash=password_hash,
    )

    assert result is False


def test_invalid_hash_is_rejected() -> None:
    result = verify_password(
        plain_password="Prueba_2026!Segura",
        password_hash="esto-no-es-un-hash-valido",
    )

    assert result is False


def test_access_token_contains_expected_claims() -> None:
    user_id = uuid4()

    token, expires_in = create_access_token(
        user_id=user_id,
        role="TRIAGE",
    )

    payload = decode_access_token(
        token
    )

    assert payload["sub"] == str(user_id)
    assert payload["role"] == "TRIAGE"
    assert payload["type"] == "access"
    assert "iat" in payload
    assert "exp" in payload
    assert expires_in == 900


def test_modified_token_is_rejected() -> None:
    user_id = uuid4()

    token, _ = create_access_token(
        user_id=user_id,
        role="TRIAGE",
    )

    modified_token = (
        token[:-1]
        + (
            "a"
            if token[-1] != "a"
            else "b"
        )
    )

    with pytest.raises(
        HTTPException
    ) as exception:
        decode_access_token(
            modified_token
        )

    assert (
        exception.value.status_code
        == 401
    )