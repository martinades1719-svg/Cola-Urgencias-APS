from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Alert, Episode, User
from schemas import (
    AlertDataResponse,
    AlertListDataResponse,
    AlertResponse,
)
from security import get_current_user
from services.audit import create_audit_log


router = APIRouter(
    prefix="/api/alerts",
    tags=["Alerts"],
)


ALERT_ROLES = {
    "RECEPTION",
    "TRIAGE",
    "CLINICAL_MANAGER",
}


CLINICAL_ALERT_ROLES = {
    "TRIAGE",
    "CLINICAL_MANAGER",
}


LONG_WAIT_THRESHOLD_MINUTES = 60


def require_alert_access(
    current_user: User,
) -> None:
    if current_user.role.name not in ALERT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para consultar las alertas.",
        )


def require_clinical_alert_access(
    current_user: User,
) -> None:
    if current_user.role.name not in CLINICAL_ALERT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el personal clínico puede gestionar alertas.",
        )


def serialize_alert(
    alert: Alert,
    episode: Episode,
) -> AlertResponse:
    return AlertResponse(
        id=alert.id,
        episodeId=alert.episode_id,
        ticket=episode.ticket,
        priority=episode.current_priority or "C5",
        type=alert.alert_type,
        status=alert.status,
        createdAt=alert.created_at,
        takenBy=alert.taken_by,
    )


def generate_long_wait_alerts(
    database: Session,
) -> None:
    threshold_time = (
        datetime.now(UTC)
        - timedelta(
            minutes=LONG_WAIT_THRESHOLD_MINUTES
        )
    )

    waiting_statement = (
        select(Episode)
        .where(
            Episode.status == "WAITING"
        )
        .where(
            Episode.triage_at.is_not(None)
        )
        .where(
            Episode.triage_at <= threshold_time
        )
    )

    waiting_episodes = list(
        database.scalars(
            waiting_statement
        )
    )

    created_alert = False

    for episode in waiting_episodes:
        existing_alert = database.scalar(
            select(Alert.id)
            .where(
                Alert.episode_id
                == episode.id
            )
            .where(
                Alert.alert_type
                == "LONG_WAIT"
            )
            .where(
                Alert.status.in_(
                    [
                        "OPEN",
                        "TAKEN",
                    ]
                )
            )
        )

        if existing_alert is not None:
            continue

        alert = Alert(
            episode_id=episode.id,
            alert_type="LONG_WAIT",
            severity="MEDIUM",
            status="OPEN",
            description=(
                "El paciente supera el umbral "
                "de espera configurado."
            ),
        )

        database.add(alert)

        create_audit_log(
            database,
            episode_id=episode.id,
            action="ALERT_CREATED",
            entity="Alert",
            entity_id=None,
            previous_values=None,
            new_values={
                "type": "LONG_WAIT",
                "status": "OPEN",
                "thresholdMinutes":
                    LONG_WAIT_THRESHOLD_MINUTES,
            },
            result="SUCCESS",
        )

        created_alert = True

    if created_alert:
        database.commit()


def load_alert_with_episode(
    database: Session,
    alert_id: UUID,
) -> tuple[Alert, Episode] | None:
    statement = (
        select(
            Alert,
            Episode,
        )
        .join(
            Episode,
            Episode.id == Alert.episode_id,
        )
        .where(
            Alert.id == alert_id
        )
    )

    return database.execute(
        statement
    ).first()


@router.get(
    "",
    response_model=AlertListDataResponse,
)
def list_alerts(
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertListDataResponse:
    require_alert_access(
        current_user
    )

    generate_long_wait_alerts(
        database
    )

    statement = (
        select(
            Alert,
            Episode,
        )
        .join(
            Episode,
            Episode.id == Alert.episode_id,
        )
        .where(
            Alert.status.in_(
                [
                    "OPEN",
                    "TAKEN",
                ]
            )
        )
        .order_by(
            Alert.created_at.asc()
        )
    )

    rows = database.execute(
        statement
    ).all()

    return AlertListDataResponse(
        data=[
            serialize_alert(
                alert,
                episode,
            )
            for alert, episode in rows
        ],
    )


@router.post(
    "/{alert_id}/take",
    response_model=AlertDataResponse,
)
def take_alert(
    alert_id: UUID,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertDataResponse:
    require_clinical_alert_access(
        current_user
    )

    result = load_alert_with_episode(
        database,
        alert_id,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No encontramos la alerta solicitada.",
        )

    alert, episode = result

    if alert.status == "RESOLVED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La alerta ya fue resuelta.",
        )

    if alert.status == "TAKEN":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La alerta ya fue tomada.",
        )

    alert.status = "TAKEN"
    alert.taken_by = current_user.id
    alert.taken_at = datetime.now(UTC)

    create_audit_log(
        database,
        user_id=current_user.id,
        episode_id=episode.id,
        action="ALERT_TAKEN",
        entity="Alert",
        entity_id=str(alert.id),
        previous_values={
            "status": "OPEN",
        },
        new_values={
            "status": "TAKEN",
        },
        result="SUCCESS",
    )

    database.commit()
    database.refresh(alert)

    return AlertDataResponse(
        data=serialize_alert(
            alert,
            episode,
        ),
    )


@router.post(
    "/{alert_id}/resolve",
    response_model=AlertDataResponse,
)
def resolve_alert(
    alert_id: UUID,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertDataResponse:
    require_clinical_alert_access(
        current_user
    )

    result = load_alert_with_episode(
        database,
        alert_id,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No encontramos la alerta solicitada.",
        )

    alert, episode = result

    if alert.status == "RESOLVED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La alerta ya fue resuelta.",
        )

    previous_status = alert.status

    alert.status = "RESOLVED"
    alert.resolved_by = current_user.id
    alert.resolved_at = datetime.now(UTC)

    if alert.taken_by is None:
        alert.taken_by = current_user.id
        alert.taken_at = datetime.now(UTC)

    create_audit_log(
        database,
        user_id=current_user.id,
        episode_id=episode.id,
        action="ALERT_RESOLVED",
        entity="Alert",
        entity_id=str(alert.id),
        previous_values={
            "status": previous_status,
        },
        new_values={
            "status": "RESOLVED",
        },
        result="SUCCESS",
    )

    database.commit()
    database.refresh(alert)

    return AlertDataResponse(
        data=serialize_alert(
            alert,
            episode,
        ),
    )