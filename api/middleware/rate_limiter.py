import os, sys, time, hashlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

LIMITS = {
    "/search":    (100, 60),
    "/profile":   (100, 60),
    "/risk":      (100, 60),
    "/graph":     (50,  60),
    "/investigate":(30, 60),
    "/export":    (10,  60),
    "/translate": (10,  60),
    "/health":    (1000,60),
    "/admin":     (5,   60),
    "default":    (200, 60),
}


class SlidingWindowRateLimiter(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)
        self._windows: dict[str, list[float]] = defaultdict(list)

    def _get_limit(self, path: str) -> tuple[int, int]:
        for prefix, limit in LIMITS.items():
            if prefix != "default" and path.startswith(prefix):
                return limit
        return LIMITS["default"]

    def _get_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For", "")
        raw = forwarded.split(",")[0].strip() if forwarded else (
            request.client.host if request.client else "unknown"
        )
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    async def dispatch(self, request: Request, call_next):
        ip  = self._get_ip(request)
        path = request.url.path
        max_req, window = self._get_limit(path)
        key = f"{ip}:{path.split('/')[1]}"
        now = time.time()

        self._windows[key] = [t for t in self._windows[key] if now - t < window]

        if len(self._windows[key]) >= max_req:
            retry = int(window - (now - self._windows[key][0]))
            logger.warning(f"[RateLimit] {ip} exceeded {max_req}/min on {path}")
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Retry after {retry} seconds.",
                headers={"Retry-After": str(retry)},
            )

        self._windows[key].append(now)
        return await call_next(request)
