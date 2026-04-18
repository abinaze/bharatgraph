"""
BharatGraph API Dependencies
BUG-01 FIX: stale Neo4j driver cached forever caused intermittent HTTP 500s.
Now verifies connectivity on every reuse; reconnects automatically on failure.
"""
import os
from dotenv import load_dotenv
from loguru import logger
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

load_dotenv()

_driver = None


def get_driver():
    global _driver

    uri  = os.getenv("NEO4J_URI", "")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd  = os.getenv("NEO4J_PASSWORD", "")

    if not uri:
        logger.warning("[API] NEO4J_URI not set — running without database")
        return None

    if _driver is not None:
        try:
            _driver.verify_connectivity()
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
        logger.success(f"[API] Neo4j connected: {uri[:30]}...")
    except AuthError as e:
        logger.error(f"[API] Neo4j auth failed — check NEO4J_USER/NEO4J_PASSWORD: {e}")
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
    if _driver:
        try:
            _driver.close()
        except Exception:
            pass
        _driver = None


def get_db():
    """FastAPI dependency — returns live driver or raises 503."""
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
