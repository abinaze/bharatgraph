import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

MAX_QUERY_LEN = 200

# BUG-09 FIX: was re.IGNORECASE — blocked "Union Bank", "Match Point", "Call Centre" etc.
# Fix: require UPPERCASE keywords followed by space, which is how real Cypher injection looks.
# A user searching "union bank" or "call centre" never types uppercase Cypher keywords.
CYPHER_INJECTION = re.compile(
    r'\b(MATCH|CREATE|DELETE|MERGE|SET|REMOVE|DROP|DETACH|UNION|CALL)\s',
    # NO re.IGNORECASE — intentional: real injection is uppercase, real searches are lowercase
)

# Allowed: letters (all scripts), digits, spaces, common punctuation, all Indian scripts
ALLOWED_CHARS = re.compile(
    r'^[\w\s\-\.\,\(\)\'\"\u0900-\u097F\u0B80-\u0BFF\u0C00-\u0C7F'
    r'\u0C80-\u0CFF\u0D00-\u0D7F\u0980-\u09FF\u0A80-\u0AFF'
    r'\u0A00-\u0A7F\u0B00-\u0B7F\u0E00-\u0E7F]+$'
)


class InputValidatorMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        q = request.query_params.get("q", "")

        if len(q) > MAX_QUERY_LEN:
            logger.warning(f"[InputValidator] Query too long: {len(q)} chars")
            raise HTTPException(
                status_code=422,
                detail=f"Query exceeds maximum length of {MAX_QUERY_LEN} characters."
            )

        if q and CYPHER_INJECTION.search(q):
            logger.warning(f"[InputValidator] Cypher injection attempt: {q[:50]}")
            raise HTTPException(
                status_code=422,
                detail="Query contains invalid patterns."
            )

        return await call_next(request)
