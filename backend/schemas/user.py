from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CreateUserRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=120,
    )

    email: EmailStr

    role: str = Field(
        pattern=r"^(RECEPTION|TRIAGE|CLINICAL_MANAGER|ADMIN)$",
    )

    password: str = Field(
        min_length=12,
        max_length=128,
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class UpdateUserStatusRequest(BaseModel):
    active: bool

    model_config = ConfigDict(
        extra="forbid",
    )


class ManagedUserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: str
    active: bool


class ManagedUserDataResponse(BaseModel):
    data: ManagedUserResponse


class ManagedUserListResponse(BaseModel):
    data: list[ManagedUserResponse]