from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[
            [Request],
            Awaitable[Response],
        ],
    ) -> Response:
        response = await call_next(
            request
        )

        response.headers[
            "X-Content-Type-Options"
        ] = "nosniff"

        response.headers[
            "X-Frame-Options"
        ] = "DENY"

        response.headers[
            "Referrer-Policy"
        ] = "strict-origin-when-cross-origin"

        response.headers[
            "Permissions-Policy"
        ] = (
            "camera=(), "
            "microphone=(), "
            "geolocation=()"
        )

        response.headers[
            "Cross-Origin-Opener-Policy"
        ] = "same-origin"

        response.headers[
            "Cross-Origin-Resource-Policy"
        ] = "same-site"

        response.headers[
            "Cache-Control"
        ] = (
            "no-store"
            if request.url.path.startswith(
                "/api/"
            )
            else "no-cache"
        )

        response.headers[
            "Content-Security-Policy"
        ] = (
            "default-src 'none'; "
            "frame-ancestors 'none'; "
            "base-uri 'none'; "
            "form-action 'self'"
        )

        return response