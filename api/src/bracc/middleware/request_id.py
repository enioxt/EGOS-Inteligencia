"""X-Request-ID middleware for request tracing.

Generates a unique request ID for each incoming request and adds it
to the response headers. If the client sends X-Request-ID, it is reused.
"""

import uuid

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class RequestIDMiddleware:
    """Attach X-Request-ID to every HTTP response."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract client-provided request ID or generate one
        headers = dict(scope.get("headers", []))
        client_id = headers.get(b"x-request-id", b"").decode() or str(uuid.uuid4())[:12]

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                raw_headers = list(message.get("headers", []))
                raw_headers.append((b"x-request-id", client_id.encode()))
                message["headers"] = raw_headers
            await send(message)

        await self.app(scope, receive, send_wrapper)
