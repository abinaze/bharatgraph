"""
BharatGraph API Dependencies

BUG-20 FIX: verify_connectivity() was called on EVERY single API request.
With 50 concurrent cold-start requests this creates a connection storm where
50 simultaneous verify_connectivity() calls hit Neo4j AuraDB, which rate-limits
verification and causes cascading 503 errors.

Fix: TTL-based health cache -- only re-verify if more than 30 seconds have
elapsed since the last successful verification. A threading.Lock ensures
only one reconnect attempt runs at a time.
"""
import os
import time
import threading
from dotenv import load_dotenv
from loguru import logger
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

load_dotenv()

_driver          = None
_last_verified_at = 0.0
_VERIFY_TTL      = 30.0   # seconds between connectivity re-checks
_driver_lock     = threading.Lock()


def get_driver():
    global _driver, _last_verified_at

    uri  = os.getenv("NEO4J_URI", "")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd  = os.getenv("NEO4J_PASSWORD", "")

    if not uri:
        logger.warning("[API] NEO4J_URI not set -- running without database")
        return None

    now = time.monotonic()

    with _driver_lock:
        # Driver healthy and verified recently -- return immediately without
        # calling verify_connectivity() again (BUG-20 key fix)
        if _driver is not None and (now - _last_verified_at) < _VERIFY_TTL:
            return _driver

        # TTL expired or first call -- need to verify (and reconnect if needed)
        if _driver is not None:
            try:
                _driver.verify_connectivity()
                _last_verified_at = time.monotonic()
                return _driver
            except Exception as e:
                logger.warning(
                    f"[API] Cached Neo4j driver dead ({type(e).__name__}), reconnecting..."
                )
                try:
                    _driver.close()
                except Exception:
                    pass
                _driver = None

        try:
            _driver = GraphDatabase.driver(uri, auth=(user, pwd))
            _driver.verify_connectivity()
            _last_verified_at = time.monotonic()
            logger.success(f"[API] Neo4j connected: {uri[:30]}...")
        except AuthError as e:
            logger.error(f"[API] Neo4j auth failed -- check NEO4J_USER/NEO4J_PASSWORD: {e}")
            _driver = None
        except ServiceUnavailable as e:
            logger.error(f"[API] Neo4j service unavailable: {e}")
            _driver = None
        except Exception as e:
            logger.error(f"[API] Neo4j connection failed: {type(e).__name__}: {e}")
            _driver = None

        return _driver


def close_driver():
    global _driver
    with _driver_lock:
        if _driver:
            try:
                _driver.close()
            except Exception:
                pass
            _driver = None


def get_db():
    """FastAPI dependency -- returns live driver or raises 503."""
    from fastapi import HTTPException
    driver = get_driver()
    if driver is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Graph database unavailable. "
                "Check NEO4J_URI and NEO4J_PASSWORD in environment secrets."
            ),
        )
    return driver
