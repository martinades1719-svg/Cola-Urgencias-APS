from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import User
from settings import settings


password_hasher = PasswordHasher()

bearer_scheme = HTTPBearer(
    auto_error=False,
)


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    try:
        return password_hasher.verify(
            password_hash,
            plain_password,
        )
    except (
        VerifyMismatchError,
        InvalidHashError,
    ):
        return False


def hash_password(
    plain_password: str,
) -> str:
    return password_hasher.hash(
        plain_password
    )


def create_access_token(
    user_id: UUID,
    role: str,
) -> tuple[str, int]:
    expires_in_seconds = (
        settings.access_token_expire_minutes
        * 60
    )

    now = datetime.now(UTC)

    expiration = now + timedelta(
        minutes=(
            settings.access_token_expire_minutes
        )
    )

    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "iat": now,
        "exp": expiration,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    return token, expires_in_seconds


def decode_access_token(
    token: str,
) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[
                settings.jwt_algorithm
            ],
            options={
                "require": [
                    "sub",
                    "role",
                    "type",
                    "iat",
                    "exp",
                ],
            },
        )

    except InvalidTokenError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Token inválido o expirado.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from error

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Token inválido o expirado.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return payload


def get_current_user(
    credentials: (
        HTTPAuthorizationCredentials
        | None
    ) = Depends(bearer_scheme),
    database: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Autenticación requerida.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Método de autenticación inválido."
            ),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    payload = decode_access_token(
        credentials.credentials
    )

    user_id = payload.get("sub")

    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Token inválido o expirado.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        parsed_user_id = UUID(user_id)

    except ValueError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Token inválido o expirado.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from error

    statement = (
        select(User)
        .options(
            joinedload(User.role)
        )
        .where(
            User.id == parsed_user_id
        )
    )

    user = database.scalar(statement)

    if user is None:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Usuario no encontrado.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if (
        not user.active
        or not user.role.active
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail="La cuenta está desactivada.",
        )

    token_role = payload.get("role")

    if token_role != user.role.name:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "El rol de la sesión "
                "ya no es válido."
            ),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return user