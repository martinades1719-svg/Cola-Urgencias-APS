from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from database import get_db
from models import Assessment, Episode, User
from schemas import (
    AssessmentResponse,
    CallEpisodeRequest,
    CloseEpisodeRequest,
    EpisodeDataResponse,
    EpisodeListDataResponse,
    EpisodeResponse,
    PatientEpisodeResponse,
    ReassessmentRequest,
    ReassessmentResponse,
    TriageRequest,
)
from security import get_current_user
from services.audit import create_audit_log


router = APIRouter(
    prefix="/api/episodes",
    tags=["Episodes"],
)


QUEUE_ROLES = {
    "RECEPTION",
    "TRIAGE",
    "CLINICAL_MANAGER",
}


CLINICAL_ROLES = {
    "TRIAGE",
    "CLINICAL_MANAGER",
}


OPERATIVE_ROLES = {
    "RECEPTION",
    "TRIAGE",
    "CLINICAL_MANAGER",
}


WITHDRAWAL_REASONS = {
    "Retiro voluntario",
    "Abandono",
}


def require_queue_role(
    current_user: User,
) -> None:
    if current_user.role.name not in QUEUE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "No tienes permiso para consultar "
                "la cola clínica."
            ),
        )


def require_clinical_role(
    current_user: User,
) -> None:
    if current_user.role.name not in CLINICAL_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Solo el personal clínico puede "
                "realizar esta acción."
            ),
        )


def require_operative_role(
    current_user: User,
) -> None:
    if current_user.role.name not in OPERATIVE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "No tienes permiso para modificar "
                "el estado del episodio."
            ),
        )


def load_episode(
    database: Session,
    episode_id: UUID,
) -> Episode | None:
    statement = (
        select(Episode)
        .options(
            selectinload(Episode.patient),
            selectinload(Episode.assessments),
        )
        .where(
            Episode.id == episode_id
        )
    )

    return database.scalar(statement)


def serialize_assessment(
    assessment: Assessment,
) -> AssessmentResponse:
    return AssessmentResponse(
        id=assessment.id,
        priority=assessment.priority,
        observation=assessment.observation,
        createdAt=assessment.assessed_at,
        userId=assessment.assessed_by,
    )


def serialize_episode(
    episode: Episode,
) -> EpisodeResponse:
    updated_at = (
        episode.closed_at
        or episode.care_started_at
        or episode.called_at
        or episode.triage_at
        or episode.arrived_at
    )

    initial_assessments = [
        serialize_assessment(assessment)
        for assessment in episode.assessments
        if assessment.assessment_type == "INITIAL"
    ]

    reassessments = [
        ReassessmentResponse(
            id=assessment.id,
            priority=assessment.priority,
            observation=assessment.observation,
            createdAt=assessment.assessed_at,
            userId=assessment.assessed_by,
            previousPriority=(
                assessment.previous_priority
                or assessment.priority
            ),
            reason=(
                assessment.change_reason
                or ""
            ),
        )
        for assessment in episode.assessments
        if assessment.assessment_type == "REASSESSMENT"
    ]

    return EpisodeResponse(
        id=episode.id,
        ticket=episode.ticket,
        token="",
        patient=PatientEpisodeResponse(
            id=episode.patient.id,
            document=episode.patient.document,
            firstName=episode.patient.first_name,
            lastName=episode.patient.last_name,
            birthDate=episode.patient.birth_date,
        ),
        status=episode.status,
        priority=episode.current_priority,
        arrivedAt=episode.arrived_at,
        updatedAt=updated_at,
        triageAt=episode.triage_at,
        calledAt=episode.called_at,
        box=episode.box,
        assessments=initial_assessments,
        reassessments=reassessments,
        closureReason=episode.closure_reason,
        closedAt=episode.closed_at,
        closedBy=None,
    )


def commit_and_reload(
    database: Session,
    episode: Episode,
) -> Episode:
    try:
        database.commit()

    except Exception:
        database.rollback()
        raise

    refreshed_episode = load_episode(
        database,
        episode.id,
    )

    if refreshed_episode is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No fue posible recuperar "
                "el episodio actualizado."
            ),
        )

    return refreshed_episode


@router.get(
    "/pending-triage",
    response_model=EpisodeListDataResponse,
)
def list_pending_triage(
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EpisodeListDataResponse:
    require_queue_role(
        current_user
    )

    statement = (
        select(Episode)
        .options(
            selectinload(Episode.patient),
            selectinload(Episode.assessments),
        )
        .where(
            Episode.status
            == "PENDING_TRIAGE"
        )
        .order_by(
            Episode.arrived_at.asc()
        )
    )

    episodes = list(
        database.scalars(statement)
    )

    return EpisodeListDataResponse(
        data=[
            serialize_episode(episode)
            for episode in episodes
        ],
    )
@router.get(
    "",
    response_model=EpisodeListDataResponse,
)
def list_episodes(
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EpisodeListDataResponse:
    require_queue_role(current_user)

    statement = (
        select(Episode)
        .options(
            selectinload(Episode.patient),
            selectinload(Episode.assessments),
        )
        .order_by(
            Episode.arrived_at.desc()
        )
    )

    episodes = list(
        database.scalars(statement)
    )

    return EpisodeListDataResponse(
        data=[
            serialize_episode(episode)
            for episode in episodes
        ],
    )


@router.get(
    "/{episode_id}",
    response_model=EpisodeDataResponse,
)
def get_episode(
    episode_id: UUID,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EpisodeDataResponse:
    require_queue_role(current_user)

    episode = load_episode(
        database,
        episode_id,
    )

    if episode is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No encontramos el episodio solicitado.",
        )

    return EpisodeDataResponse(
        data=serialize_episode(
            episode
        ),
    )

@router.post(
    "/{episode_id}/triage",
    response_model=EpisodeDataResponse,
)
def register_initial_triage(
    episode_id: UUID,
    request: TriageRequest,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EpisodeDataResponse:
    require_clinical_role(
        current_user
    )

    episode = load_episode(
        database,
        episode_id,
    )

    if episode is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No encontramos el episodio "
                "solicitado."
            ),
        )

    if episode.status != "PENDING_TRIAGE":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Este episodio ya posee un triage "
                "o no se encuentra pendiente."
            ),
        )

    existing_initial_assessment = database.scalar(
        select(Assessment.id)
        .where(
            Assessment.episode_id
            == episode.id
        )
        .where(
            Assessment.assessment_type
            == "INITIAL"
        )
    )

    if existing_initial_assessment is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Este episodio ya posee "
                "un triage inicial."
            ),
        )

    assessment = Assessment(
        episode_id=episode.id,
        assessed_by=current_user.id,
        assessment_type="INITIAL",
        priority=request.priority,
        previous_priority=None,
        observation=request.observation.strip(),
        change_reason=None,
    )

    database.add(assessment)

    current_time = datetime.now(UTC)

    episode.current_priority = request.priority
    episode.triage_at = current_time
    episode.status = "WAITING"

    create_audit_log(
        database,
        user_id=current_user.id,
        episode_id=episode.id,
        action="TRIAGE_CREATED",
        entity="Episode",
        entity_id=str(episode.id),
        previous_values={
            "status": "PENDING_TRIAGE",
            "priority": None,
        },
        new_values={
            "status": "WAITING",
            "priority": request.priority,
        },
        result="SUCCESS",
    )

    refreshed_episode = commit_and_reload(
        database,
        episode,
    )

    return EpisodeDataResponse(
        data=serialize_episode(
            refreshed_episode
        ),
    )


@router.post(
    "/{episode_id}/reassessments",
    response_model=EpisodeDataResponse,
)
def register_reassessment(
    episode_id: UUID,
    request: ReassessmentRequest,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EpisodeDataResponse:
    require_clinical_role(
        current_user
    )

    episode = load_episode(
        database,
        episode_id,
    )

    if episode is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No encontramos el episodio "
                "solicitado."
            ),
        )

    valid_states = {
        "WAITING",
        "CALLED",
        "IN_CARE",
    }

    if episode.status not in valid_states:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El episodio no admite reevaluaciones "
                "en su estado actual."
            ),
        )

    if episode.current_priority is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El episodio no posee una prioridad "
                "clínica previa."
            ),
        )

    previous_priority = episode.current_priority
    reason = request.reason.strip()

    if (
        request.priority != previous_priority
        and len(reason) < 3
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Debes indicar el motivo del cambio "
                "de prioridad."
            ),
        )

    assessment = Assessment(
        episode_id=episode.id,
        assessed_by=current_user.id,
        assessment_type="REASSESSMENT",
        priority=request.priority,
        previous_priority=previous_priority,
        observation=request.observation.strip(),
        change_reason=(
            reason
            if reason
            else None
        ),
    )

    database.add(assessment)

    episode.current_priority = request.priority

    create_audit_log(
        database,
        user_id=current_user.id,
        episode_id=episode.id,
        action=(
            "PRIORITY_CHANGED"
            if request.priority != previous_priority
            else "PATIENT_REASSESSED"
        ),
        entity="Episode",
        entity_id=str(episode.id),
        previous_values={
            "priority": previous_priority,
        },
        new_values={
            "priority": request.priority,
            "reason": reason or None,
        },
        result="SUCCESS",
    )

    refreshed_episode = commit_and_reload(
        database,
        episode,
    )

    return EpisodeDataResponse(
        data=serialize_episode(
            refreshed_episode
        ),
    )


@router.post(
    "/{episode_id}/call",
    response_model=EpisodeDataResponse,
)
def call_episode(
    episode_id: UUID,
    request: CallEpisodeRequest,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EpisodeDataResponse:
    require_operative_role(
        current_user
    )

    episode = load_episode(
        database,
        episode_id,
    )

    if episode is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No encontramos el episodio "
                "solicitado."
            ),
        )

    if episode.status != "WAITING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Solo se puede llamar a un paciente "
                "que se encuentra en espera."
            ),
        )

    episode.status = "CALLED"
    episode.box = request.box.strip()
    episode.called_at = datetime.now(UTC)

    create_audit_log(
        database,
        user_id=current_user.id,
        episode_id=episode.id,
        action="PATIENT_CALLED",
        entity="Episode",
        entity_id=str(episode.id),
        previous_values={
            "status": "WAITING",
            "box": None,
        },
        new_values={
            "status": "CALLED",
            "box": episode.box,
        },
        result="SUCCESS",
    )

    refreshed_episode = commit_and_reload(
        database,
        episode,
    )

    return EpisodeDataResponse(
        data=serialize_episode(
            refreshed_episode
        ),
    )


@router.post(
    "/{episode_id}/start-care",
    response_model=EpisodeDataResponse,
)
def start_episode_care(
    episode_id: UUID,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EpisodeDataResponse:
    require_operative_role(
        current_user
    )

    episode = load_episode(
        database,
        episode_id,
    )

    if episode is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No encontramos el episodio "
                "solicitado."
            ),
        )

    if episode.status != "CALLED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Solo se puede iniciar la atención "
                "de un paciente llamado."
            ),
        )

    episode.status = "IN_CARE"
    episode.care_started_at = datetime.now(UTC)

    create_audit_log(
        database,
        user_id=current_user.id,
        episode_id=episode.id,
        action="CARE_STARTED",
        entity="Episode",
        entity_id=str(episode.id),
        previous_values={
            "status": "CALLED",
        },
        new_values={
            "status": "IN_CARE",
            "box": episode.box,
        },
        result="SUCCESS",
    )

    refreshed_episode = commit_and_reload(
        database,
        episode,
    )

    return EpisodeDataResponse(
        data=serialize_episode(
            refreshed_episode
        ),
    )
@router.post(
    "/{episode_id}/close",
    response_model=EpisodeDataResponse,
)
def close_episode(
    episode_id: UUID,
    request: CloseEpisodeRequest,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EpisodeDataResponse:
    require_operative_role(
        current_user
    )

    episode = load_episode(
        database,
        episode_id,
    )

    if episode is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No encontramos el episodio "
                "solicitado."
            ),
        )

    valid_states = {
        "PENDING_TRIAGE",
        "WAITING",
        "CALLED",
        "IN_CARE",
    }

    if episode.status not in valid_states:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El episodio ya se encuentra cerrado."
            ),
        )

    previous_status = episode.status
    normalized_reason = request.reason.strip()

    if normalized_reason in WITHDRAWAL_REASONS:
        episode.status = "WITHDRAWN"
        audit_action = "PATIENT_WITHDRAWN"

    else:
        if previous_status != "IN_CARE":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "La atención solo puede finalizar "
                    "cuando el paciente está en atención."
                ),
            )

        episode.status = "CLOSED"
        audit_action = "EPISODE_CLOSED"

    episode.closure_reason = normalized_reason
    episode.closed_at = datetime.now(UTC)

    create_audit_log(
        database,
        user_id=current_user.id,
        episode_id=episode.id,
        action=audit_action,
        entity="Episode",
        entity_id=str(episode.id),
        previous_values={
            "status": previous_status,
        },
        new_values={
            "status": episode.status,
            "reason": normalized_reason,
        },
        result="SUCCESS",
    )

    refreshed_episode = commit_and_reload(
        database,
        episode,
    )

    return EpisodeDataResponse(
        data=serialize_episode(
            refreshed_episode
        ),
    )