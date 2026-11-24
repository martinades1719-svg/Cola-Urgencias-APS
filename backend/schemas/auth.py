from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=12,
        max_length=128,
    )


class RoleResponse(BaseModel):
    id: int
    name: str


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: RoleResponse
    active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse