import os, sys, time, hashlib, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

AUDIT_LOG = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "logs", "audit.jsonl")

# BUG-13 FIX: _previous_hash was global in-memory — breaks with multiple Uvicorn workers.
# Each worker resets to "0"*64 on restart, silently breaking the audit chain.
# Fix: store the previous hash in a per-process temp file so each worker is consistent.
# (True cross-worker chaining requires Redis/DB which is out of scope for free tier.)
import tempfile
_HASH_FILE = os.path.join(tempfile.gettempdir(), f"bharatgraph_audit_hash_{os.getpid()}.txt")

def _read_prev_hash() -> str:
    try:
        with open(_HASH_FILE) as f:
            return f.read().strip() or "0" * 64
    except FileNotFoundError:
        return "0" * 64

def _write_prev_hash(h: str) -> None:
    try:
        with open(_HASH_FILE, "w") as f:
            f.write(h)
    except Exception:
        pass


class AuditLoggerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
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
            "prev_hash":   _read_prev_hash(),
        }

        entry_str    = json.dumps(entry, separators=(",", ":"))
        current_hash = hashlib.sha256(entry_str.encode()).hexdigest()
        entry["hash"] = current_hash
        _write_prev_hash(current_hash)

        try:
            os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
            with open(AUDIT_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.warning(f"[AuditLogger] Write failed: {e}")

        return response
