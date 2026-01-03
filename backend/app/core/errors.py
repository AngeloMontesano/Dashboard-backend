from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings

logger = logging.getLogger("app")


def _get_request_id(request: Request) -> str:
    """
    Liefert die Request ID aus dem Request State.
    Fallback ist leerer String, falls Middleware nicht gelaufen ist.
    """
    return getattr(getattr(request, "state", None), "request_id", "") or ""


def _error_response(
    *,
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: Any | None = None,
) -> JSONResponse:
    """
    Erzeugt eine konsistente Error Response inkl. X-Request-Id Header.
    """
    payload: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details

    headers = {}
    request_id = _get_request_id(request)
    if request_id:
        headers["X-Request-Id"] = request_id

    return JSONResponse(status_code=status_code, content=payload, headers=headers)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registriert zentrale Exception Handler für einheitliche Fehlerformate.
    In prod werden keine internen Details zurückgegeben.
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """
        HTTPExceptions in ein einheitliches Fehlerformat überführen.
        Wenn detail bereits im gewünschten Format ist, wird es übernommen.
        """
        request_id = _get_request_id(request)

        # Bereits standardisiertes Format übernehmen
        if isinstance(exc.detail, dict) and "error" in exc.detail:
            headers = {}
            if request_id:
                headers["X-Request-Id"] = request_id
            return JSONResponse(status_code=exc.status_code, content=exc.detail, headers=headers)

        # Sonst normalisieren
        return _error_response(
            request=request,
            status_code=exc.status_code,
            code="http_error",
            message=str(exc.detail) if exc.detail else "Request failed",
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Body, Query, Path Validierungsfehler.
        Details werden zurückgegeben, da sie keine sensiblen Daten enthalten sollen.
        """
        return _error_response(
            request=request,
            status_code=422,
            code="validation_error",
            message="Invalid request",
            details=exc.errors(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Unbehandelte Fehler:
        - dev: message leicht hilfreich, ohne Stacktrace im Response
        - prod: komplett generisch
        Intern wird immer geloggt, inkl. Request ID.
        """
        request_id = _get_request_id(request)

        # Intern loggen, ohne Response Details zu leaken
        if request_id:
            logger.exception("Unhandled exception (request_id=%s)", request_id)
        else:
            logger.exception("Unhandled exception")

        if settings.ENVIRONMENT == "prod":
            return _error_response(
                request=request,
                status_code=500,
                code="internal_error",
                message="Internal server error",
            )

        # dev: minimal hilfreich, aber keine Interna wie Tracebacks im Response
        return _error_response(
            request=request,
            status_code=500,
            code="internal_error",
            message=str(exc) or "Internal server error",
        )
