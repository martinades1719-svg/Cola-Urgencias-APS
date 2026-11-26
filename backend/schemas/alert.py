from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AlertResponse(BaseModel):
    id: UUID

    episode_id: UUID = Field(
        alias="episodeId",
    )

    ticket: str
    priority: str
    type: str
    status: str

    created_at: datetime = Field(
        alias="createdAt",
    )

    taken_by: UUID | None = Field(
        default=None,
        alias="takenBy",
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class AlertDataResponse(BaseModel):
    data: AlertResponse


class AlertListDataResponse(BaseModel):
    data: list[AlertResponse]