"""
BharatGraph - Phase 34: Case Memory API
GET  /case-memory/stats               -- how many cases stored, pattern counts
GET  /case-memory/similar             -- find past cases similar to given findings
POST /case-memory/false-positive      -- record a false positive to improve accuracy

Pure ASCII.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

router = APIRouter(prefix="/case-memory", tags=["CaseMemory"])


class FalsePositiveRequest(BaseModel):
    finding_type: str
    entity_id:    str
    reason:       str = ""


@router.get("/stats")
def case_memory_stats():
    """
    Return how many investigation cases are stored in memory,
    breakdown by finding type, and false positive rates.
    """
    logger.info("[CaseMemory] stats")
    try:
        from ai.case_memory.case_store import CaseStore
        cs = CaseStore()
        return {
            "stats":        cs.get_pattern_stats(),
            "total_cases":  cs.get_case_count(),
            "analyzed_at":  datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"[CaseMemory] stats error: {type(e).__name__}")
        return {"status": "error", "detail": str(type(e).__name__)}


@router.get("/similar")
def find_similar_cases(finding_types: str = ""):
    """
    Find past investigation cases that share the same finding types.
    Pass finding_types as a comma-separated list.
    Example: /case-memory/similar?finding_types=benfords_law_anomaly,ghost_company
    """
    logger.info(f"[CaseMemory] similar lookup: {finding_types[:60]}")
    try:
        from ai.case_memory.case_store import CaseStore
        cs = CaseStore()
        ft_list = [f.strip() for f in finding_types.split(",") if f.strip()]
        findings = [{"type": ft} for ft in ft_list]
        similar  = cs.find_similar(findings, top_k=10)
        return {
            "query_finding_types": ft_list,
            "similar_cases":       similar,
            "analyzed_at":         datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"[CaseMemory] similar error: {type(e).__name__}")
        return {"status": "error", "detail": str(type(e).__name__)}


@router.post("/false-positive")
def record_false_positive(body: FalsePositiveRequest):
    """
    Record that a specific finding type produced a false positive for an entity.
    This feedback is used by WeightOptimizer to reduce the weight of
    over-firing indicators.
    """
    logger.info(f"[CaseMemory] false positive: {body.finding_type} entity={body.entity_id[:8]}")
    try:
        from ai.case_memory.case_store import CaseStore
        cs = CaseStore()
        cs.record_false_positive(
            finding_type=body.finding_type,
            entity_id=body.entity_id,
        )
        return {
            "recorded":     True,
            "finding_type": body.finding_type,
            "entity_id":    body.entity_id[:8] + "...",
            "recorded_at":  datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"[CaseMemory] false positive record error: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Failed to record feedback")
