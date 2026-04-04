import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from loguru import logger

from api.dependencies import get_db
from ai.deep_investigator import DeepInvestigator
from ai.connection_mapper import ConnectionMapper

router = APIRouter()


@router.get("/investigate/{entity_id}")
def deep_investigate(entity_id: str, driver=Depends(get_db)):
    logger.info(f"[Investigation] Deep investigate: {entity_id}")
    investigator = DeepInvestigator(driver=driver)
    with driver.session() as session:
        row = session.run(
            "MATCH (n {id:$id}) RETURN n.name AS name",
            id=entity_id
        ).single()
    name = (row["name"] if row else entity_id) or entity_id
    return investigator.investigate(entity_id, name)


@router.get("/connection-map")
def connection_map(
    a: str = Query(..., description="Entity A ID"),
    b: str = Query(..., description="Entity B ID"),
    driver=Depends(get_db),
):
    logger.info(f"[Investigation] Connection map: {a} → {b}")
    mapper = ConnectionMapper(driver=driver)
    return mapper.find_paths(a, b)


@router.get("/node-evidence/{entity_id}")
def node_evidence(entity_id: str, driver=Depends(get_db)):
    logger.info(f"[Investigation] Node evidence: {entity_id}")
    mapper = ConnectionMapper(driver=driver)
    return mapper.get_node_evidence(entity_id)
