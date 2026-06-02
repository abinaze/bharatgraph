"""
BharatGraph - Phase 34: Forensic Intelligence API
GET /forensics/circular-ownership       -- detect shell company ownership rings
GET /forensics/ghost-companies          -- companies with contracts but no activity
GET /forensics/shadow-directors         -- directors of 10+ companies / shared addresses
GET /forensics/benfords/{entity_id}     -- Benford Law analysis on asset declarations
GET /forensics/shadow-draft             -- policy text similarity to lobbying documents

Pure ASCII. All detectors built in ai/ -- this file just exposes them.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from fastapi import APIRouter, Depends, Query
from loguru import logger

from api.dependencies import get_db

router = APIRouter(prefix="/forensics", tags=["Forensics"])


@router.get("/circular-ownership")
def circular_ownership(
    max_cycle_length: int = Query(6, ge=3, le=10),
    driver=Depends(get_db),
):
    """
    Detect shell company ownership cycles in the full graph.
    A cycle A -> B -> C -> A indicates potential circular ownership
    used to obscure beneficial ownership.
    """
    logger.info("[Forensics] circular ownership scan")
    try:
        from ai.circular_ownership import CircularOwnershipDetector
        det    = CircularOwnershipDetector(driver=driver)
        cycles = det.detect_cycles()
        filtered = [c for c in cycles if len(c.get("cycle", [])) <= max_cycle_length]
        return {
            "total_cycles_detected": len(cycles),
            "shown":                  len(filtered),
            "max_cycle_length":       max_cycle_length,
            "cycles":                 filtered,
            "analyzed_at":            datetime.now().isoformat(),
            "note": (
                "Circular ownership often indicates shell company structures "
"                used to obscure beneficial ownership or inflate valuations."
            ),
        }
    except Exception as e:
        logger.error(f"[Forensics] circular ownership error: {type(e).__name__}")
        return {"status": "error", "detail": str(type(e).__name__),
                "analyzed_at": datetime.now().isoformat()}


@router.get("/ghost-companies")
def ghost_companies(
    min_score: int = Query(70, ge=0, le=100),
    limit:     int = Query(50, ge=1, le=200),
    driver=Depends(get_db),
):
    """
    Score every company in the graph for ghost company indicators:
    - No declared employees
    - Minimal registered capital
    - High government contract volume
    - No web presence or filings

    Returns companies with ghost_score >= min_score (default 70).
    """
    logger.info(f"[Forensics] ghost company scan min_score={min_score}")
    try:
        from ai.ghost_company import GhostCompanyDetector
        det     = GhostCompanyDetector(driver=driver)
        results = det.run_detection()
        flagged = [r for r in results if r.get("ghost_score", 0) >= min_score]
        flagged.sort(key=lambda x: x.get("ghost_score", 0), reverse=True)
        return {
            "total_scanned":  len(results),
            "flagged_count":  len(flagged),
            "min_score":      min_score,
            "companies":      flagged[:limit],
            "analyzed_at":    datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"[Forensics] ghost companies error: {type(e).__name__}")
        return {"status": "error", "detail": str(type(e).__name__),
                "analyzed_at": datetime.now().isoformat()}


@router.get("/shadow-directors")
def shadow_directors(
    min_company_count: int = Query(10, ge=3, le=100),
    driver=Depends(get_db),
):
    """
    Detect shadow director patterns:
    1. Individuals who are director of 10+ companies
    2. Multiple companies sharing the same registered address
       (indicates a registration agent acting as nominee director)
    """
    logger.info("[Forensics] shadow director scan")
    try:
        from ai.shadow_director import ShadowDirectorDetector
        det    = ShadowDirectorDetector(driver=driver)
        result = det.run_full_detection()
        high_count = [
            r for r in result.get("high_directorship_count", [])
            if r.get("company_count", 0) >= min_company_count
        ]
        return {
            "address_reuse_clusters":    result.get("address_reuse", []),
            "high_directorship_entities": high_count,
            "min_company_count":         min_company_count,
            "analyzed_at":               datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"[Forensics] shadow directors error: {type(e).__name__}")
        return {"status": "error", "detail": str(type(e).__name__),
                "analyzed_at": datetime.now().isoformat()}


@router.get("/benfords/{entity_id}")
def benfords_analysis(entity_id: str, driver=Depends(get_db)):
    """
    Run Benford Law analysis on all affidavit asset values declared
    by this entity. Significant deviation (chi2 > 15.5) suggests
    fabricated or heavily rounded financial figures.
    """
    logger.info(f"[Forensics] Benford analysis entity={entity_id[:8]}")
    try:
        from ai.benfords_analyzer import BenfordsAnalyzer
        ba = BenfordsAnalyzer()
        with driver.session() as s:
            rows = s.run(
                "MATCH (n {id:})-[:FILED_AFFIDAVIT]->(a:Affidavit)"
"                RETURN a.total_assets_crore    AS total,"
"                       a.movable_assets_crore AS movable,"
"                       a.liabilities_crore    AS liabilities,"
"                       a.year                 AS year",
                id=entity_id
            ).data()
        if not rows:
            return {
                "entity_id": entity_id,
                "status":    "no_data",
                "note":      "No affidavit records found for this entity",
            }
        values = []
        for r in rows:
            for k in ("total", "movable", "liabilities"):
                if r.get(k): values.append(float(r[k]))
        if len(values) < 5:
            return {
                "entity_id":    entity_id,
                "status":       "insufficient_data",
                "value_count":  len(values),
                "note":         "Fewer than 5 numeric values -- Benford analysis unreliable",
            }
        result = ba.analyze(values)
        result["entity_id"]  = entity_id
        result["value_count"] = len(values)
        result["analyzed_at"] = datetime.now().isoformat()
        return result
    except Exception as e:
        logger.error(f"[Forensics] Benford error entity={entity_id[:8]}: {type(e).__name__}")
        return {"status": "error", "detail": str(type(e).__name__)}


@router.get("/shadow-draft")
def shadow_draft_check(
    submission_id: str = Query(..., description="Node ID of submitted policy/bill text"),
    bill_id:       str = Query(..., description="Node ID of reference bill text"),
    driver=Depends(get_db),
):
    """
    Compare two policy/bill texts for shadow drafting (text copied from
    lobbying documents or industry submissions into government bills).
    Returns similarity score and matched sections.
    """
    logger.info(f"[Forensics] shadow draft check {submission_id[:8]} vs {bill_id[:8]}")
    try:
        from ai.shadow_draft_detector import ShadowDraftDetector
        det = ShadowDraftDetector()
        with driver.session() as s:
            sub = s.run(
                "MATCH (n {id:}) RETURN coalesce(n.text,n.content,n.summary) AS t",
                id=submission_id
            ).single()
            bill = s.run(
                "MATCH (n {id:}) RETURN coalesce(n.text,n.content,n.summary) AS t",
                id=bill_id
            ).single()
        if not sub or not bill:
            return {"status": "node_not_found",
                    "found_submission": sub is not None,
                    "found_bill": bill is not None}
        result = det.compare(sub["t"] or "", bill["t"] or "")
        result["submission_id"] = submission_id
        result["bill_id"]       = bill_id
        result["analyzed_at"]   = datetime.now().isoformat()
        return result
    except Exception as e:
        logger.error(f"[Forensics] shadow draft error: {type(e).__name__}")
        return {"status": "error", "detail": str(type(e).__name__)}
