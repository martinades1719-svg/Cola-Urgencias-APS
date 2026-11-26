from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Role, User
from schemas import (
    CreateUserRequest,
    ManagedUserDataResponse,
    ManagedUserListResponse,
    ManagedUserResponse,
    UpdateUserStatusRequest,
)
from security import get_current_user, hash_password
from services.audit import create_audit_log


router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


def require_admin(
    current_user: User,
) -> None:
    if current_user.role.name != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Solo administración puede "
                "gestionar usuarios."
            ),
        )


def serialize_user(
    user: User,
) -> ManagedUserResponse:
    return ManagedUserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.name,
        active=user.active,
    )


def load_user(
    database: Session,
    user_id: UUID,
) -> User | None:
    return database.scalar(
        select(User)
        .options(
            joinedload(User.role)
        )
        .where(
            User.id == user_id
        )
    )


@router.get(
    "",
    response_model=ManagedUserListResponse,
)
def list_users(
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ManagedUserListResponse:
    require_admin(current_user)

    users = list(
        database.scalars(
            select(User)
            .options(
                joinedload(User.role)
            )
            .order_by(
                User.email.asc()
            )
        )
    )

    return ManagedUserListResponse(
        data=[
            serialize_user(user)
            for user in users
        ],
    )


@router.post(
    "",
    response_model=ManagedUserDataResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    request: CreateUserRequest,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ManagedUserDataResponse:
    require_admin(current_user)

    normalized_email = (
        request.email
        .lower()
        .strip()
    )

    existing_user = database.scalar(
        select(User.id).where(
            User.email == normalized_email
        )
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Ya existe un usuario registrado "
                "con ese correo."
            ),
        )

    role = database.scalar(
        select(Role).where(
            Role.name == request.role
        )
    )

    if role is None or not role.active:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El rol seleccionado no está disponible.",
        )

    user = User(
        role_id=role.id,
        name=" ".join(
            request.name.strip().split()
        ),
        email=normalized_email,
        password_hash=hash_password(
            request.password
        ),
        active=True,
    )

    database.add(user)
    database.flush()

    create_audit_log(
        database,
        user_id=current_user.id,
        action="USER_CREATED",
        entity="User",
        entity_id=str(user.id),
        previous_values=None,
        new_values={
            "email": user.email,
            "role": role.name,
            "active": True,
        },
        result="SUCCESS",
    )

    database.commit()

    created_user = load_user(
        database,
        user.id,
    )

    if created_user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No fue posible recuperar "
                "el usuario creado."
            ),
        )

    return ManagedUserDataResponse(
        data=serialize_user(
            created_user
        ),
    )


@router.patch(
    "/{user_id}/status",
    response_model=ManagedUserDataResponse,
)
def update_user_status(
    user_id: UUID,
    request: UpdateUserStatusRequest,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ManagedUserDataResponse:
    require_admin(current_user)

    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No puedes desactivar "
                "tu propia cuenta."
            ),
        )

    user = load_user(
        database,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )

    previous_active = user.active
    user.active = request.active

    create_audit_log(
        database,
        user_id=current_user.id,
        action=(
            "USER_ENABLED"
            if request.active
            else "USER_DISABLED"
        ),
        entity="User",
        entity_id=str(user.id),
        previous_values={
            "active": previous_active,
        },
        new_values={
            "active": request.active,
        },
        result="SUCCESS",
    )

    database.commit()
    database.refresh(user)

    return ManagedUserDataResponse(
        data=serialize_user(user),
    )