import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from api.dependencies import get_db
from ai.forensics.linguistic_fingerprint import LinguisticFingerprinter

router      = APIRouter()
fingerprint = LinguisticFingerprinter()


@router.get("/linguistic/fingerprint/{entity_id}")
def linguistic_fingerprint(entity_id: str, driver=Depends(get_db)):
    logger.info(f"[Linguistic] Fingerprint requested: {entity_id}")
    with driver.session() as s:
        row = s.run(
            "MATCH (n {id:$id}) RETURN n.name AS name", id=entity_id
        ).single()
    if not row:
        raise HTTPException(status_code=404,
                            detail=f"Entity {entity_id} not found")
    return fingerprint.analyze(entity_id, [], driver=driver)
