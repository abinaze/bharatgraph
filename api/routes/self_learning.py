"""
BharatGraph - Phase 34: Self-Learning API
GET /self-learning/patterns         -- discover new investigation patterns from graph
GET /self-learning/weights          -- current optimised investigator weights
GET /self-learning/audit            -- scraper health check (which sources are live)
GET /self-learning/schema           -- newly detected fields not yet in schema

Pure ASCII.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from fastapi import APIRouter, Depends, Header
from fastapi import HTTPException
from loguru import logger

from api.dependencies import get_db

router = APIRouter(prefix="/self-learning", tags=["SelfLearning"])


def _require_admin(x_admin_secret: str = Header(default="")):
    secret = os.getenv("ADMIN_SECRET", "")
    if secret and x_admin_secret != secret:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/patterns")
def discover_patterns(driver=Depends(get_db)):
    """
    Run the PatternLearner against the current graph to discover
    new investigation motifs not yet in the hardcoded pattern list.
    Returns confirmed patterns (found >= 5 times) and newly discovered motifs.
    """
    logger.info("[SelfLearning] pattern discovery run")
    try:
        from ai.self_learning.pattern_learner import PatternLearner
        pl     = PatternLearner(driver=driver)
        result = pl.discover_patterns()
        result["analyzed_at"] = datetime.now().isoformat()
        return result
    except Exception as e:
        logger.error(f"[SelfLearning] pattern discovery error: {type(e).__name__}")
        return {"status": "error", "detail": str(type(e).__name__),
                "analyzed_at": datetime.now().isoformat()}


@router.get("/weights")
def get_investigator_weights():
    """
    Return the current optimised investigator weights.
    Weights are updated after each investigation outcome is recorded.
    The base weights are overridden by the weight file if it exists.
    """
    logger.info("[SelfLearning] weight lookup")
    try:
        from ai.self_learning.weight_optimizer import WeightOptimizer
        wo = WeightOptimizer()
        return {
            "weights":      wo._load_weights(),
            "outcome_count": len(wo._load_outcomes()),
            "analyzed_at":  datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"[SelfLearning] weights error: {type(e).__name__}")
        return {"status": "error", "detail": str(type(e).__name__)}


@router.get("/audit")
def scraper_audit():
    """
    Run a health check against all registered scrapers.
    Tests whether each source URL is reachable and returns parseable data.
    Expensive -- allow 30 seconds. Use sparingly.
    """
    logger.info("[SelfLearning] scraper audit")
    try:
        from ai.self_learning.self_audit import run
        result = run(timeout_secs=25)
        result["analyzed_at"] = datetime.now().isoformat()
        return result
    except Exception as e:
        logger.error(f"[SelfLearning] audit error: {type(e).__name__}")
        return {"status": "error", "detail": str(type(e).__name__)}


@router.get("/schema")
def pending_schema_fields(driver=Depends(get_db)):
    """
    Return fields that have appeared in scraped records but are not yet
    defined in graph/schema.py. Helps developers identify what new data
    sources are emitting.
    """
    logger.info("[SelfLearning] schema detection")
    try:
        from ai.self_learning.schema_learner import SchemaLearner
        sl = SchemaLearner()
        return {
            "pending_fields": sl.get_pending(),
            "analyzed_at":    datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"[SelfLearning] schema error: {type(e).__name__}")
        return {"status": "error", "detail": str(type(e).__name__)}
