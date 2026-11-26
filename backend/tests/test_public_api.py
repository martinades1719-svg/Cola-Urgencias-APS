from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_root_endpoint_returns_running_status() -> None:
    response = client.get("/")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "running"
    assert (
        body["message"]
        == "Cola Urgencias APS API"
    )


def test_health_endpoint_returns_healthy_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "healthy"
    assert (
        body["service"]
        == "cola-urgencias-api"
    )


def test_auth_me_requires_authentication() -> None:
    response = client.get(
        "/api/auth/me"
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Autenticación requerida."
    }


def test_users_endpoint_requires_authentication() -> None:
    response = client.get(
        "/api/users"
    )

    assert response.status_code == 401


def test_audit_endpoint_requires_authentication() -> None:
    response = client.get(
        "/api/audit-logs"
    )

    assert response.status_code == 401


def test_invalid_public_ticket_returns_not_found() -> None:
    response = client.get(
        "/api/public/status/URG-NOEXISTE"
    )

    assert response.status_code == 404

    assert (
        "No encontramos"
        in response.json()["detail"]
    )


def test_security_headers_are_present() -> None:
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert (
        response.headers[
            "x-content-type-options"
        ]
        == "nosniff"
    )

    assert (
        response.headers[
            "x-frame-options"
        ]
        == "DENY"
    )

    assert (
        response.headers[
            "referrer-policy"
        ]
        == "strict-origin-when-cross-origin"
    )

    assert (
        response.headers[
            "content-security-policy"
        ]
        == (
            "default-src 'none'; "
            "frame-ancestors 'none'; "
            "base-uri 'none'; "
            "form-action 'self'"
        )
    )


def test_api_responses_disable_cache() -> None:
    response = client.get(
        "/api/auth/me"
    )

    assert response.status_code == 401

    assert (
        response.headers[
            "cache-control"
        ]
        == "no-store"
    )