import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from loguru import logger
from fastapi import HTTPException

load_dotenv()

_driver = None


def get_driver():
    global _driver
    if _driver is None:
        try:
            from neo4j import GraphDatabase
            uri  = os.getenv("NEO4J_URI", "")
            user = os.getenv("NEO4J_USER", "neo4j")
            pwd  = os.getenv("NEO4J_PASSWORD", "")
            if not uri or not pwd:
                raise ValueError("NEO4J_URI and NEO4J_PASSWORD must be set in .env")
            _driver = GraphDatabase.driver(uri, auth=(user, pwd))
            _driver.verify_connectivity()
            logger.success("[API] Neo4j driver initialised")
        except Exception as e:
            logger.error(f"[API] Neo4j connection failed: {e}")
            _driver = None
    return _driver


def get_db():
    driver = get_driver()
    if driver is None:
        raise HTTPException(
            status_code=503,
            detail="Graph database unavailable. Check NEO4J_URI and NEO4J_PASSWORD in .env"
        )
    return driver


def close_driver():
    global _driver
    if _driver:
        _driver.close()
        _driver = None
        logger.info("[API] Neo4j driver closed")
