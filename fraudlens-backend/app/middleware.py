"""
FraudLens AI - Middleware Layer
Implements request ID tracing, security headers, and rate limiting.
"""

import time
import uuid
from typing import Dict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.logging_config import logger

class RequestTracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        start_time = time.time()

        try:
            response: Response = await call_next(request)
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Unhandled error processing {request.method} {request.url.path}: {str(e)}", extra={"request_id": request_id})
            raise e

        process_time = time.time() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        logger.info(
            f"{request.method} {request.url.path} returned {response.status_code} in {process_time:.4f}s",
            extra={"request_id": request_id}
        )
        return response

class SimpleRateLimiter:
    """In-memory rate limiter with sliding window per client IP."""
    def __init__(self, limit: int = 60, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        if client_ip not in self.requests:
            self.requests[client_ip] = [now]
            return True

        # Clean old timestamps
        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < self.window_seconds]

        if len(self.requests[client_ip]) < self.limit:
            self.requests[client_ip].append(now)
            return True

        return False
