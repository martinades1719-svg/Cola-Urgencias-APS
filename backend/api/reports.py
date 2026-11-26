from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from database import get_db
from models import Alert, Assessment, Episode, User
from schemas import (
    DashboardDataResponse,
    DashboardMetricsResponse,
    PriorityMetricResponse,
)
from security import get_current_user


router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"],
)


REPORT_ROLES = {
    "RECEPTION",
    "TRIAGE",
    "CLINICAL_MANAGER",
}


def require_report_access(
    current_user: User,
) -> None:
    if current_user.role.name not in REPORT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "No tienes permiso para consultar "
                "los indicadores operacionales."
            ),
        )


def count_episodes_by_status(
    database: Session,
    episode_status: str,
) -> int:
    result = database.scalar(
        select(func.count(Episode.id))
        .where(
            Episode.status == episode_status
        )
    )

    return int(result or 0)


def calculate_average_minutes(
    database: Session,
    start_column,
    end_column,
) -> int:
    average_seconds = database.scalar(
        select(
            func.avg(
                func.extract(
                    "epoch",
                    end_column - start_column,
                )
            )
        )
        .where(
            start_column.is_not(None)
        )
        .where(
            end_column.is_not(None)
        )
    )

    if average_seconds is None:
        return 0

    return max(
        0,
        round(
            float(average_seconds) / 60
        ),
    )


@router.get(
    "/dashboard",
    response_model=DashboardDataResponse,
)
def get_dashboard_metrics(
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardDataResponse:
    require_report_access(
        current_user
    )

    pending = count_episodes_by_status(
        database,
        "PENDING_TRIAGE",
    )

    waiting = count_episodes_by_status(
        database,
        "WAITING",
    )

    called = count_episodes_by_status(
        database,
        "CALLED",
    )

    in_care = count_episodes_by_status(
        database,
        "IN_CARE",
    )

    withdrawals = count_episodes_by_status(
        database,
        "WITHDRAWN",
    )

    registered = int(
        database.scalar(
            select(
                func.count(Episode.id)
            )
        )
        or 0
    )

    active_alerts = int(
        database.scalar(
            select(
                func.count(Alert.id)
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
        or 0
    )

    resolved_alerts = int(
        database.scalar(
            select(
                func.count(Alert.id)
            )
            .where(
                Alert.status == "RESOLVED"
            )
        )
        or 0
    )

    reassessments = int(
        database.scalar(
            select(
                func.count(Assessment.id)
            )
            .where(
                Assessment.assessment_type
                == "REASSESSMENT"
            )
        )
        or 0
    )

    priority_changes = int(
        database.scalar(
            select(
                func.count(Assessment.id)
            )
            .where(
                Assessment.assessment_type
                == "REASSESSMENT"
            )
            .where(
                Assessment.previous_priority
                != Assessment.priority
            )
        )
        or 0
    )

    arrival_triage = calculate_average_minutes(
        database,
        Episode.arrived_at,
        Episode.triage_at,
    )

    triage_care = calculate_average_minutes(
        database,
        Episode.triage_at,
        Episode.care_started_at,
    )

    average_wait = triage_care

    priority_rows = database.execute(
        select(
            Episode.current_priority,
            func.count(Episode.id),
        )
        .where(
            Episode.current_priority.is_not(None)
        )
        .group_by(
            Episode.current_priority
        )
    ).all()

    priority_counts = {
        priority: int(count)
        for priority, count
        in priority_rows
    }

    by_priority = [
        PriorityMetricResponse(
            priority=priority,
            count=priority_counts.get(
                priority,
                0,
            ),
        )
        for priority in [
            "C1",
            "C2",
            "C3",
            "C4",
            "C5",
        ]
    ]

    return DashboardDataResponse(
        data=DashboardMetricsResponse(
            pending=pending,
            waiting=waiting,
            called=called,
            inCare=in_care,
            alerts=active_alerts,
            averageWait=average_wait,
            registered=registered,
            arrivalTriage=arrival_triage,
            triageCare=triage_care,
            reassessments=reassessments,
            priorityChanges=priority_changes,
            resolvedAlerts=resolved_alerts,
            withdrawals=withdrawals,
            estimateAccuracy=0,
            byPriority=by_priority,
        ),
    )