from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AuditLogResponse(BaseModel):
    id: UUID
    created_at: datetime = Field(alias="createdAt")
    user: str
    role: str
    action: str
    entity: str
    ticket: str
    previous: str
    next: str
    result: str

    model_config = ConfigDict(
        populate_by_name=True,
    )


class AuditLogListResponse(BaseModel):
    data: list[AuditLogResponse]