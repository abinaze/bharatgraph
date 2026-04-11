import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from api.dependencies import get_db
from ai.forensics.policy_benefit_analyzer import PolicyBenefitAnalyzer

router   = APIRouter()
analyzer = PolicyBenefitAnalyzer()


@router.get("/policy/causal/{entity_id}")
def policy_causal_analysis(entity_id: str, driver=Depends(get_db)):
    logger.info(f"[Policy] Causal analysis requested: {entity_id}")
    with driver.session() as s:
        row = s.run(
            "MATCH (n {id:$id}) RETURN n.name AS name", id=entity_id
        ).single()
    if not row:
        raise HTTPException(
            status_code=404, detail=f"Entity {entity_id} not found"
        )
    name = row.get("name") or entity_id
    return analyzer.analyze(entity_id, name, driver=driver)
