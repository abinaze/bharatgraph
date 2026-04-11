import os
from dotenv import load_dotenv
from loguru import logger
from neo4j import GraphDatabase

load_dotenv()

_driver = None


def get_driver():
    global _driver
    if _driver is not None:
        return _driver
    uri  = os.getenv("NEO4J_URI", "")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd  = os.getenv("NEO4J_PASSWORD", "")
    if not uri:
        logger.warning("[API] NEO4J_URI not set — running without database")
        return None
    try:
        _driver = GraphDatabase.driver(uri, auth=(user, pwd))
        _driver.verify_connectivity()
        logger.success(f"[API] Neo4j connected: {uri[:30]}...")
    except Exception as e:
        logger.error(f"[API] Neo4j connection failed: {e}")
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
    """FastAPI dependency — returns driver or raises 503 if unavailable."""
    from fastapi import HTTPException
    driver = get_driver()
    if driver is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Graph database unavailable. "
                "Check NEO4J_URI and NEO4J_PASSWORD in environment secrets."
            )
        )
    return driver
