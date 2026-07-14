# @generated-by
# Name: elevasyncsolutions-jpg
# Timestamp: 2026-07-14T21:42:00Z
# Startup configuration: Bounty agent for ClankerNation OpenAgents. Adding structured error responses with error codes. Runtime: darwin/arm64
"""Structured error handling middleware with typed error codes."""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

ERROR_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMITED",
    500: "INTERNAL_ERROR",
    502: "BAD_GATEWAY",
    503: "SERVICE_UNAVAILABLE",
}

class StructuredErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            if response.status_code >= 400 and response.status_code < 600:
                body = getattr(response, "body", None)
                if body:
                    import json
                    try:
                        data = json.loads(body)
                    except Exception:
                        data = {}
                else:
                    data = {}
                data["error_code"] = ERROR_CODES.get(response.status_code, "UNKNOWN")
                data["request_id"] = getattr(request.state, "request_id", str(uuid.uuid4()))
                return JSONResponse(status_code=response.status_code, content=data)
            return response
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "detail": exc.detail,
                    "error_code": ERROR_CODES.get(exc.status_code, "UNKNOWN"),
                    "request_id": getattr(request.state, "request_id", str(uuid.uuid4())),
                },
            )
        except Exception as exc:
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "error_code": "INTERNAL_ERROR",
                    "request_id": getattr(request.state, "request_id", str(uuid.uuid4())),
                },
            )
