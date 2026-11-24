from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import User
from schemas import (
    LoginRequest,
    RoleResponse,
    TokenResponse,
    UserResponse,
)
from security import (
    create_access_token,
    get_current_user,
    verify_password,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    credentials: LoginRequest,
    database: Session = Depends(get_db),
) -> TokenResponse:
    """
    Autentica a un funcionario utilizando correo y contraseña.

    Si las credenciales son correctas, devuelve un token JWT
    y los datos básicos del usuario autenticado.
    """

    normalized_email = credentials.email.lower().strip()

    statement = (
        select(User)
        .options(joinedload(User.role))
        .where(User.email == normalized_email)
    )

    user = database.scalar(statement)

    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Correo o contraseña incorrectos.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    if user is None:
        raise invalid_credentials

    if not verify_password(
        plain_password=credentials.password,
        password_hash=user.password_hash,
    ):
        raise invalid_credentials

    if not user.active or not user.role.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta está desactivada.",
        )

    access_token, expires_in = create_access_token(
        user_id=user.id,
        role=user.role.name,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            active=user.active,
            role=RoleResponse(
                id=user.role.id,
                name=user.role.name,
            ),
        ),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def get_authenticated_user(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Devuelve los datos del usuario identificado por el token JWT.
    """

    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        active=current_user.active,
        role=RoleResponse(
            id=current_user.role.id,
            name=current_user.role.name,
        ),
    )