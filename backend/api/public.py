import hashlib
import secrets
import string
from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Episode, Patient
from schemas.public import (
    ArrivalDataResponse,
    ArrivalRequest,
    ArrivalResponse,
    PublicStatusDataResponse,
    PublicStatusResponse,
    QueuePositionResponse,
    WaitEstimateResponse,
)


router = APIRouter(
    prefix="/api/public",
    tags=["Public"],
)


ACTIVE_EPISODE_STATUSES = [
    "PENDING_TRIAGE",
    "WAITING",
    "CALLED",
    "IN_CARE",
]


def normalize_document(
    document: str,
) -> str:
    return (
        document
        .strip()
        .upper()
        .replace(".", "")
        .replace("-", "")
        .replace(" ", "")
    )


def normalize_name(
    value: str,
) -> str:
    return " ".join(
        value.strip().split()
    )


def validate_birth_date(
    birth_date: date,
) -> None:
    today = date.today()

    if birth_date > today:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha de nacimiento no puede estar en el futuro.",
        )

    maximum_age_years = 120

    if birth_date.year < today.year - maximum_age_years:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha de nacimiento no es válida.",
        )


def generate_ticket() -> str:
    alphabet = (
        string.ascii_uppercase +
        string.digits
    )

    random_code = "".join(
        secrets.choice(alphabet)
        for _ in range(6)
    )

    return f"URG-{random_code}"


def generate_public_token() -> str:
    return secrets.token_urlsafe(32)


def hash_public_token(
    raw_token: str,
) -> str:
    return hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()


def create_unique_ticket(
    database: Session,
) -> str:
    for _ in range(10):
        ticket = generate_ticket()

        existing_ticket = database.scalar(
            select(Episode.id).where(
                Episode.ticket == ticket
            )
        )

        if existing_ticket is None:
            return ticket

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="No fue posible generar un ticket. Inténtalo nuevamente.",
    )


def create_unique_public_token(
    database: Session,
) -> tuple[str, str]:
    for _ in range(10):
        raw_token = generate_public_token()
        token_hash = hash_public_token(
            raw_token
        )

        existing_token = database.scalar(
            select(Episode.id).where(
                Episode.public_token_hash ==
                token_hash
            )
        )

        if existing_token is None:
            return raw_token, token_hash

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="No fue posible generar el acceso público. Inténtalo nuevamente.",
    )


@router.post(
    "/arrival",
    response_model=ArrivalDataResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_arrival(
    request: ArrivalRequest,
    database: Session = Depends(get_db),
) -> ArrivalDataResponse:
    if not request.privacy:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Debes aceptar el aviso de privacidad.",
        )

    validate_birth_date(
        request.birth_date
    )

    normalized_document = normalize_document(
        request.document
    )

    if len(normalized_document) < 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El documento ingresado no es válido.",
        )

    patient = database.scalar(
        select(Patient).where(
            Patient.document ==
            normalized_document
        )
    )

    if patient is None:
        patient = Patient(
            document=normalized_document,
            first_name=normalize_name(
                request.first_name
            ),
            last_name=normalize_name(
                request.last_name
            ),
            birth_date=request.birth_date,
        )

        database.add(patient)
        database.flush()

    active_episode = database.scalar(
        select(Episode)
        .where(
            Episode.patient_id ==
            patient.id
        )
        .where(
            Episode.status.in_(
                ACTIVE_EPISODE_STATUSES
            )
        )
        .order_by(
            Episode.arrived_at.desc()
        )
    )

    if active_episode is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El paciente ya posee un episodio activo. "
                "Solicita el ticket en recepción."
            ),
        )

    ticket = create_unique_ticket(
        database
    )

    raw_token, token_hash = (
        create_unique_public_token(
            database
        )
    )

    episode = Episode(
        patient_id=patient.id,
        created_by=None,
        ticket=ticket,
        public_token_hash=token_hash,
        status="PENDING_TRIAGE",
    )

    database.add(episode)
    database.commit()
    database.refresh(episode)

    return ArrivalDataResponse(
        data=ArrivalResponse(
            ticket=episode.ticket,
            token=raw_token,
            arrivedAt=episode.arrived_at,
        ),
    )


@router.get(
    "/status/{token}",
    response_model=PublicStatusDataResponse,
)
def get_public_status(
    token: str,
    database: Session = Depends(get_db),
) -> PublicStatusDataResponse:
    normalized_value = token.strip()

    if not normalized_value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No encontramos ese ticket.",
        )

    if normalized_value.upper().startswith(
        "URG-"
    ):
        episode = database.scalar(
            select(Episode).where(
                Episode.ticket ==
                normalized_value.upper()
            )
        )
    else:
        token_hash = hash_public_token(
            normalized_value
        )

        episode = database.scalar(
            select(Episode).where(
                Episode.public_token_hash ==
                token_hash
            )
        )

    if episode is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No encontramos ese ticket. "
                "Revisa el código e inténtalo nuevamente."
            ),
        )

    updated_at = (
        episode.triage_at
        or episode.called_at
        or episode.care_started_at
        or episode.closed_at
        or episode.arrived_at
    )

    return PublicStatusDataResponse(
        data=PublicStatusResponse(
            ticket=episode.ticket,
            status=episode.status,
            arrivedAt=episode.arrived_at,
            updatedAt=updated_at,
            box=episode.box,
            position=QueuePositionResponse(
                approximate=None,
                estimate=WaitEstimateResponse(
                    min=0,
                    max=0,
                    available=False,
                ),
                reordered=False,
            ),
        ),
    )