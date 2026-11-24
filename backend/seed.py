from argon2 import PasswordHasher
from sqlalchemy import select

from database import SessionLocal
from models import Role, User


password_hasher = PasswordHasher()

ROLE_DATA = [
    {
        "name": "RECEPTION",
        "description": "Registro de pacientes y gestión administrativa.",
    },
    {
        "name": "TRIAGE",
        "description": "Triage inicial, reevaluaciones y prioridad clínica.",
    },
    {
        "name": "CLINICAL_MANAGER",
        "description": "Supervisión clínica, indicadores y auditoría.",
    },
    {
        "name": "ADMIN",
        "description": "Administración de usuarios y configuración técnica.",
    },
]

USER_DATA = [
    {
        "name": "Recepción Demo",
        "email": "recepcion@demo.cl",
        "password": "Demo_2026!Seguro",
        "role": "RECEPTION",
    },
    {
        "name": "Triage Demo",
        "email": "triage@demo.cl",
        "password": "Demo_2026!Seguro",
        "role": "TRIAGE",
    },
    {
        "name": "Jefatura Demo",
        "email": "jefatura@demo.cl",
        "password": "Demo_2026!Seguro",
        "role": "CLINICAL_MANAGER",
    },
    {
        "name": "Administrador Demo",
        "email": "admin@demo.cl",
        "password": "Demo_2026!Seguro",
        "role": "ADMIN",
    },
]


def create_roles(database) -> dict[str, Role]:
    roles: dict[str, Role] = {}

    for role_data in ROLE_DATA:
        existing_role = database.scalar(
            select(Role).where(Role.name == role_data["name"])
        )

        if existing_role is None:
            existing_role = Role(
                name=role_data["name"],
                description=role_data["description"],
                active=True,
            )
            database.add(existing_role)
            database.flush()

            print(f"Rol creado: {existing_role.name}")
        else:
            print(f"Rol existente: {existing_role.name}")

        roles[existing_role.name] = existing_role

    return roles


def create_users(database, roles: dict[str, Role]) -> None:
    for user_data in USER_DATA:
        existing_user = database.scalar(
            select(User).where(User.email == user_data["email"])
        )

        if existing_user is not None:
            print(f"Usuario existente: {existing_user.email}")
            continue

        role = roles[user_data["role"]]

        user = User(
            name=user_data["name"],
            email=user_data["email"],
            password_hash=password_hasher.hash(user_data["password"]),
            role_id=role.id,
            active=True,
        )

        database.add(user)
        print(f"Usuario creado: {user.email}")


def seed_database() -> None:
    database = SessionLocal()

    try:
        roles = create_roles(database)
        create_users(database, roles)

        database.commit()
        print("Carga inicial completada correctamente.")

    except Exception:
        database.rollback()
        print("La carga inicial falló. Se revirtieron los cambios.")
        raise

    finally:
        database.close()


if __name__ == "__main__":
    seed_database()