import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from api.dependencies import get_db
from ai.debate_engine import DebateEngine

router = APIRouter()
engine = DebateEngine()


@router.get("/debate/{entity_id}")
def run_debate(entity_id: str, driver=Depends(get_db)):
    logger.info(f"[Debate] Requested: {entity_id}")

    with driver.session() as s:
        row = s.run(
            "MATCH (n {id:$id}) RETURN n.name AS name, "
            "n.risk_score AS score",
            id=entity_id
        ).single()

    if not row:
        raise HTTPException(
            status_code=404, detail=f"Entity {entity_id} not found"
        )

    name = row.get("name") or entity_id

    findings = []
    try:
        from ai.risk_scorer import RiskScorer
        scorer   = RiskScorer(driver=driver)
        result   = scorer.score(entity_id, name)
        findings = result.get("findings", [])
    except Exception as e:
        logger.warning(f"[Debate] Could not load findings: {e}")

    return engine.run(entity_id, name, findings, driver=driver)
