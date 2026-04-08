import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from api.dependencies import get_db
from ai.forensics.revolving_door import RevolvingDoorDetector
from ai.forensics.tbml_detector  import TBMLDetector

router    = APIRouter()
rev_door  = RevolvingDoorDetector()
tbml      = TBMLDetector()


@router.get("/conflict/revolving-door/{entity_id}")
def revolving_door(entity_id: str, driver=Depends(get_db)):
    with driver.session() as s:
        row = s.run(
            "MATCH (n {id:$id}) RETURN n.name AS name", id=entity_id
        ).single()
    if not row:
        raise HTTPException(status_code=404,
                            detail=f"Entity {entity_id} not found")
    name = row.get("name") or entity_id
    return rev_door.analyze(entity_id, name, driver=driver)


@router.get("/conflict/tbml/{entity_id}")
def tbml_analysis(entity_id: str, driver=Depends(get_db)):
    return tbml.analyze(entity_id, driver=driver)
