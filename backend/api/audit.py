from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import AuditLog, Episode, User
from schemas import (
    AuditLogListResponse,
    AuditLogResponse,
)
from security import get_current_user


router = APIRouter(
    prefix="/api/audit-logs",
    tags=["Audit"],
)


AUDIT_ROLES = {
    "CLINICAL_MANAGER",
    "ADMIN",
}


@router.get(
    "",
    response_model=AuditLogListResponse,
)
def list_audit_logs(
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AuditLogListResponse:
    if current_user.role.name not in AUDIT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para consultar la auditoría.",
        )

    statement = (
        select(
            AuditLog,
            User,
            Episode,
        )
        .outerjoin(
            User,
            User.id == AuditLog.user_id,
        )
        .outerjoin(
            Episode,
            Episode.id == AuditLog.episode_id,
        )
        .order_by(
            AuditLog.created_at.desc()
        )
        .limit(500)
    )

    rows = database.execute(statement).all()

    logs: list[AuditLogResponse] = []

    for audit_log, user, episode in rows:
        role_name = "SYSTEM"

        if user is not None:
            database.refresh(
                user,
                attribute_names=["role"],
            )
            role_name = user.role.name

        logs.append(
            AuditLogResponse(
                id=audit_log.id,
                createdAt=audit_log.created_at,
                user=(
                    user.email
                    if user is not None
                    else "Sistema"
                ),
                role=role_name,
                action=audit_log.action,
                entity=audit_log.entity,
                ticket=(
                    episode.ticket
                    if episode is not None
                    else "—"
                ),
                previous=str(
                    audit_log.previous_values
                    or "—"
                ),
                next=str(
                    audit_log.new_values
                    or "—"
                ),
                result=audit_log.result,
            )
        )

    return AuditLogListResponse(
        data=logs,
    )