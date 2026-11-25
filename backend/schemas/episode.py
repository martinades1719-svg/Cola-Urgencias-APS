from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TriageRequest(BaseModel):
    priority: str = Field(
        pattern=r"^C[1-5]$",
    )

    observation: str = Field(
        min_length=2,
        max_length=2000,
    )

    reason: str = Field(
        default="",
        max_length=1000,
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class CallEpisodeRequest(BaseModel):
    box: str = Field(
        min_length=1,
        max_length=30,
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class CloseEpisodeRequest(BaseModel):
    reason: str = Field(
        min_length=2,
        max_length=500,
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class PatientEpisodeResponse(BaseModel):
    id: UUID
    document: str

    first_name: str = Field(
        alias="firstName",
    )

    last_name: str = Field(
        alias="lastName",
    )

    birth_date: date = Field(
        alias="birthDate",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AssessmentResponse(BaseModel):
    id: UUID
    priority: str
    observation: str

    created_at: datetime = Field(
        alias="createdAt",
    )

    user_id: UUID = Field(
        alias="userId",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class EpisodeResponse(BaseModel):
    id: UUID
    ticket: str
    token: str = ""

    patient: PatientEpisodeResponse
    status: str
    priority: str | None

    arrived_at: datetime = Field(
        alias="arrivedAt",
    )

    updated_at: datetime = Field(
        alias="updatedAt",
    )

    triage_at: datetime | None = Field(
        alias="triageAt",
    )

    called_at: datetime | None = Field(
        alias="calledAt",
    )

    box: str | None

    assessments: list[AssessmentResponse]
    reassessments: list[AssessmentResponse] = []

    closure_reason: str | None = Field(
        alias="closureReason",
    )

    closed_at: datetime | None = Field(
        alias="closedAt",
    )

    closed_by: UUID | None = Field(
        default=None,
        alias="closedBy",
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class EpisodeDataResponse(BaseModel):
    data: EpisodeResponse


class EpisodeListDataResponse(BaseModel):
    data: list[EpisodeResponse]