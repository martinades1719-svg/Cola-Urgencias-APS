from uuid import UUID

from sqlalchemy.orm import Session

from models import AuditLog


def create_audit_log(
    database: Session,
    *,
    action: str,
    entity: str,
    user_id: UUID | None = None,
    episode_id: UUID | None = None,
    entity_id: str | None = None,
    previous_values: dict | None = None,
    new_values: dict | None = None,
    ip_address: str | None = None,
    result: str = "SUCCESS",
) -> AuditLog:
    audit_log = AuditLog(
        user_id=user_id,
        episode_id=episode_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        previous_values=previous_values,
        new_values=new_values,
        ip_address=ip_address,
        result=result,
    )

    database.add(audit_log)

    return audit_log