import os, sys, time, hashlib, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

AUDIT_LOG = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "logs", "audit.jsonl")

_previous_hash = "0" * 64


class AuditLoggerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        global _previous_hash
        start = time.time()

        response = await call_next(request)

        elapsed   = round(time.time() - start, 4)
        ip_raw    = request.headers.get("X-Forwarded-For",
                    request.client.host if request.client else "unknown")
        ip_hash   = hashlib.sha256(ip_raw.encode()).hexdigest()[:16]
        q_hash    = hashlib.sha256(
            request.url.query.encode()
        ).hexdigest()[:16] if request.url.query else ""

        entry = {
            "ts":          datetime.utcnow().isoformat() + "Z",
            "ip_hash":     ip_hash,
            "method":      request.method,
            "path":        request.url.path,
            "query_hash":  q_hash,
            "status":      response.status_code,
            "elapsed_s":   elapsed,
            "prev_hash":   _previous_hash,
        }

        entry_str    = json.dumps(entry, separators=(",", ":"))
        current_hash = hashlib.sha256(entry_str.encode()).hexdigest()
        entry["hash"] = current_hash
        _previous_hash = current_hash

        try:
            os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
            with open(AUDIT_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.warning(f"[AuditLogger] Write failed: {e}")

        return response
