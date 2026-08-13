"""Standard API error format — Backend_architecture.txt §13 and
Api_design.txt §13 both specify the same shape:

    {"success": false, "error": {"code": "...", "message": "..."}}

`APIError` is what route/service code raises; the handler registered in
`main.py` turns it into that exact JSON shape. Using a dedicated exception
type (rather than raising `HTTPException` with a plain string everywhere)
keeps the `code` field consistent instead of ad-hoc per route.
"""

from __future__ import annotations

from fastapi import Request, status
from fastapi.responses import JSONResponse


class APIError(Exception):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": exc.code, "message": exc.message}},
    )


# Common, reusable errors — route modules raise these directly instead of
# re-deriving the code string each time.
class AuthError(APIError):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__("AUTH_ERROR", message, status.HTTP_401_UNAUTHORIZED)


class NotFoundError(APIError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__("NOT_FOUND", message, status.HTTP_404_NOT_FOUND)


class ValidationAPIError(APIError):
    def __init__(self, message: str):
        super().__init__("VALIDATION_ERROR", message, 422)


class SessionError(APIError):
    def __init__(self, message: str = "Session not found"):
        super().__init__("SESSION_ERROR", message, status.HTTP_404_NOT_FOUND)
