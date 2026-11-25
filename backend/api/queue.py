import math
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, select
from sqlalchemy.orm import Session, selectinload

from api.episodes import serialize_episode
from database import get_db
from models import Episode, User
from schemas import (
    QueueItemResponse,
    QueueListDataResponse,
    QueuePositionDataResponse,
    QueuePositionResponse,
    WaitEstimateResponse,
)
from security import get_current_user


router = APIRouter(
    prefix="/api/queue",
    tags=["Queue"],
)


ALLOWED_QUEUE_ROLES = {
    "RECEPTION",
    "TRIAGE",
    "CLINICAL_MANAGER",
}


PRIORITY_ORDER = {
    "C1": 1,
    "C2": 2,
    "C3": 3,
    "C4": 4,
    "C5": 5,
}


AVERAGE_ATTENTION_MINUTES = {
    "C1": 5,
    "C2": 15,
    "C3": 30,
    "C4": 45,
    "C5": 60,
}


def require_queue_access(
    current_user: User,
) -> None:
    if current_user.role.name not in ALLOWED_QUEUE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para consultar la cola clínica.",
        )


def priority_order_expression():
    return case(
        (Episode.current_priority == "C1", 1),
        (Episode.current_priority == "C2", 2),
        (Episode.current_priority == "C3", 3),
        (Episode.current_priority == "C4", 4),
        (Episode.current_priority == "C5", 5),
        else_=99,
    )


def load_waiting_queue(
    database: Session,
) -> list[Episode]:
    statement = (
        select(Episode)
        .options(
            selectinload(Episode.patient),
            selectinload(Episode.assessments),
        )
        .where(
            Episode.status == "WAITING"
        )
        .where(
            Episode.current_priority.is_not(None)
        )
        .order_by(
            priority_order_expression(),
            Episode.triage_at.asc(),
            Episode.arrived_at.asc(),
        )
    )

    return list(
        database.scalars(statement)
    )


def calculate_wait_estimate(
    queue: list[Episode],
    position_index: int,
) -> WaitEstimateResponse:
    episodes_before = queue[:position_index]

    if not episodes_before:
        return WaitEstimateResponse(
            min=0,
            max=10,
            available=True,
        )

    estimated_minutes = 0

    for episode in episodes_before:
        priority = (
            episode.current_priority
            or "C5"
        )

        estimated_minutes += (
            AVERAGE_ATTENTION_MINUTES[
                priority
            ]
        )

    minimum_minutes = math.floor(
        estimated_minutes * 0.8
    )

    maximum_minutes = math.ceil(
        estimated_minutes * 1.2
    )

    return WaitEstimateResponse(
        min=max(0, minimum_minutes),
        max=max(
            minimum_minutes + 5,
            maximum_minutes,
        ),
        available=True,
    )


def calculate_reordered(
    episode: Episode,
    queue: list[Episode],
    position_index: int,
) -> bool:
    if episode.triage_at is None:
        return False

    current_priority_order = PRIORITY_ORDER.get(
        episode.current_priority or "C5",
        5,
    )

    for previous_episode in queue[:position_index]:
        if previous_episode.triage_at is None:
            continue

        previous_priority_order = PRIORITY_ORDER.get(
            previous_episode.current_priority or "C5",
            5,
        )

        entered_after = (
            previous_episode.triage_at >
            episode.triage_at
        )

        has_higher_priority = (
            previous_priority_order <
            current_priority_order
        )

        if entered_after and has_higher_priority:
            return True

    return False


@router.get(
    "",
    response_model=QueueListDataResponse,
)
def list_queue(
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QueueListDataResponse:
    require_queue_access(
        current_user
    )

    queue = load_waiting_queue(
        database
    )

    items: list[QueueItemResponse] = []

    for index, episode in enumerate(queue):
        serialized_episode = serialize_episode(
            episode
        )

        item = QueueItemResponse(
            **serialized_episode.model_dump(
                by_alias=True
            ),
            position=index + 1,
            estimate=calculate_wait_estimate(
                queue,
                index,
            ),
            hasAlert=False,
        )

        items.append(item)

    return QueueListDataResponse(
        data=items
    )


@router.get(
    "/{episode_id}/position",
    response_model=QueuePositionDataResponse,
)
def get_queue_position(
    episode_id: UUID,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QueuePositionDataResponse:
    require_queue_access(
        current_user
    )

    queue = load_waiting_queue(
        database
    )

    position_index = next(
        (
            index
            for index, episode
            in enumerate(queue)
            if episode.id == episode_id
        ),
        None,
    )

    if position_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El episodio no se encuentra actualmente en la cola.",
        )

    episode = queue[position_index]

    return QueuePositionDataResponse(
        data=QueuePositionResponse(
            approximate=position_index + 1,
            estimate=calculate_wait_estimate(
                queue,
                position_index,
            ),
            reordered=calculate_reordered(
                episode,
                queue,
                position_index,
            ),
        ),
    )