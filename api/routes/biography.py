import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from api.dependencies import get_db
from ai.biography.timeline_builder    import TimelineBuilder
from ai.biography.convergence_detector import ConvergenceDetector
from ai.biography.biography_generator  import BiographyGenerator

router    = APIRouter()
builder   = TimelineBuilder()
detector  = ConvergenceDetector()
generator = BiographyGenerator()


@router.get("/biography/{entity_id}")
def get_biography(entity_id: str, driver=Depends(get_db)):
    logger.info(f"[Biography] Requested: {entity_id}")

    with driver.session() as s:
        row = s.run(
            "MATCH (n {id:$id}) RETURN n.name AS name, n.risk_score AS rs",
            id=entity_id
        ).single()

    if not row:
        raise HTTPException(status_code=404,
                            detail=f"Entity {entity_id} not found")

    name       = row.get("name") or entity_id
    risk_score = int(row.get("rs") or 0)

    timeline     = builder.build(entity_id, name, driver)
    convergences = detector.detect(timeline["events"])
    biography    = generator.generate(name, timeline, convergences, risk_score)

    return {
        "entity_id":   entity_id,
        "entity_name": name,
        "timeline":    timeline,
        "convergences": convergences,
        "biography":   biography,
    }
