from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from api.auth import router as auth_router
from api.public import router as public_router
from database import engine


app = FastAPI(
    title="Cola Urgencias APS API",
    description="API del sistema de gestión de cola priorizada",
    version="0.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public_router)


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
        "version": "0.3.0",
    }


@app.get("/database-health")
def database_health():
    try:
        with engine.connect() as connection:
            database_name = connection.execute(
                text("SELECT current_database()")
            ).scalar_one()

            database_user = connection.execute(
                text("SELECT current_user")
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