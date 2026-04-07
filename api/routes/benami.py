import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from api.dependencies import get_db
from ai.forensics.benami_detector import BenamiDetector

router   = APIRouter()
detector = BenamiDetector()


@router.get("/benami/{entity_id}")
def get_benami_analysis(entity_id: str, driver=Depends(get_db)):
    logger.info(f"[Benami] Analysis requested: {entity_id}")

    with driver.session() as s:
        row = s.run(
            "MATCH (n {id:$id}) RETURN n.name AS name",
            id=entity_id
        ).single()

    if not row:
        raise HTTPException(status_code=404,
                            detail=f"Entity {entity_id} not found")

    name = row.get("name") or entity_id
    return detector.analyze(entity_id, name, driver=driver)
