import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from api.dependencies import get_db
from ai.adversarial_engine import AdversarialEngine
from ai.risk_scorer import RiskScorer

router = APIRouter()
engine = AdversarialEngine()


@router.get("/adversarial/{entity_id}")
def adversarial_analysis(entity_id: str, driver=Depends(get_db)):
    logger.info(f"[Adversarial] Analysis requested: {entity_id}")

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

    # Pull findings from risk scorer to pass into adversarial engine
    findings = []
    try:
        # BUG-03 FIX: RiskScorer() takes no constructor args; use score_entity() not score()
        from api.routes.risk import get_risk
        risk_result = get_risk(entity_id, driver)
        findings = [
            {"name": f.name, "score": f.score, "description": f.description}
            for f in risk_result.factors
        ]
    except Exception as e:
        logger.warning(f"[Adversarial] Could not load findings from risk route: {e}")

    return engine.analyze(entity_id, name, findings, driver=driver)
