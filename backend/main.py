from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from api.alerts import router as alerts_router
from api.audit import router as audit_router
from api.auth import router as auth_router
from api.episodes import router as episodes_router
from api.public import router as public_router
from api.queue import router as queue_router
from api.reports import router as reports_router
from api.users import router as users_router
from database import engine
from middleware.security_headers import SecurityHeadersMiddleware


app = FastAPI(
    title="Cola Urgencias APS API",
    description=(
        "API del sistema de gestión "
        "de cola clínica priorizada"
    ),
    version="0.5.0",
)



app.add_middleware(
    SecurityHeadersMiddleware
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:8080",
    "https://cola-urgencias-fub60774-martinades1719-svg.vercel.app",
],

    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PATCH",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)



app.include_router(auth_router)
app.include_router(public_router)
app.include_router(episodes_router)
app.include_router(queue_router)
app.include_router(audit_router)
app.include_router(alerts_router)
app.include_router(reports_router)
app.include_router(users_router)


@app.get("/")
def root():
    return {
        "message": "Cola Urgencias APS API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "cola-urgencias-api",
        "version": "0.5.0",
    }


@app.get("/database-health")
def database_health():
    try:
        with engine.connect() as connection:
            database_name = connection.execute(
                text(
                    "SELECT current_database()"
                )
            ).scalar_one()

            database_user = connection.execute(
                text(
                    "SELECT current_user"
                )
            ).scalar_one()

        return {
            "status": "healthy",
            "database": database_name,
            "user": database_user,
        }

    except SQLAlchemyError:
        return {
            "status": "unhealthy",
            "database": None,
            "user": None,
        }
