from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ArrivalRequest(BaseModel):
    document: str = Field(
        min_length=5,
        max_length=50,
    )

    first_name: str = Field(
        alias="firstName",
        min_length=2,
        max_length=100,
    )

    last_name: str = Field(
        alias="lastName",
        min_length=2,
        max_length=100,
    )

    birth_date: date = Field(
        alias="birthDate",
    )

    privacy: bool

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )


class ArrivalResponse(BaseModel):
    ticket: str
    token: str
    arrived_at: datetime = Field(
        alias="arrivedAt",
    )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class WaitEstimateResponse(BaseModel):
    min: int = 0
    max: int = 0
    available: bool = False


class QueuePositionResponse(BaseModel):
    approximate: int | None = None
    estimate: WaitEstimateResponse
    reordered: bool = False


class PublicStatusResponse(BaseModel):
    ticket: str
    status: str

    arrived_at: datetime = Field(
        alias="arrivedAt",
    )

    updated_at: datetime = Field(
        alias="updatedAt",
    )

    box: str | None
    position: QueuePositionResponse

    model_config = ConfigDict(
        populate_by_name=True,
    )


class ArrivalDataResponse(BaseModel):
    data: ArrivalResponse


class PublicStatusDataResponse(BaseModel):
    data: PublicStatusResponse