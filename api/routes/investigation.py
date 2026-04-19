import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from loguru import logger

from api.dependencies import get_db
from ai.deep_investigator import DeepInvestigator
from ai.connection_mapper import ConnectionMapper

router = APIRouter()


@router.get("/investigate/{entity_id}")
def deep_investigate(entity_id: str, driver=Depends(get_db)):
    """BUG-04 FIX: was no try/except — any exception became a raw 500."""
    logger.info(f"[Investigation] Deep investigate: {entity_id}")
    try:
        investigator = DeepInvestigator(driver=driver)
        name = entity_id
        try:
            with driver.session() as session:
                row = session.run(
                    "MATCH (n {id:$id}) RETURN n.name AS name", id=entity_id
                ).single()
            name = (row["name"] if row else entity_id) or entity_id
        except Exception as name_err:
            logger.debug(f"[Investigation] Name lookup failed: {name_err}")

        return investigator.investigate(entity_id, name)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Investigation] Error for {entity_id}: {type(e).__name__}: {e}")
        return {
            "entity_id":   entity_id,
            "entity_name": entity_id,
            "status":      "error",
            "error":       "Investigation failed — please retry",
            "total_items": 0,
            "layers":      [],
            "confidence":  0,
            "investigated_at": datetime.now().isoformat(),
        }


@router.get("/connection-map")
def connection_map(
    a: str = Query(..., description="Entity A ID"),
    b: str = Query(..., description="Entity B ID"),
    driver=Depends(get_db),
):
    """BUG-04 FIX: wrapped with try/except."""
    logger.info(f"[Investigation] Connection map: {a} <-> {b}")
    try:
        mapper = ConnectionMapper(driver=driver)
        return mapper.find_paths(a, b)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Investigation] Connection map error: {e}")
        raise HTTPException(status_code=500, detail="Connection map failed — please retry")


@router.get("/node-evidence/{entity_id}")
def node_evidence(entity_id: str, driver=Depends(get_db)):
    """BUG-04 FIX: wrapped with try/except."""
    logger.info(f"[Investigation] Node evidence: {entity_id}")
    try:
        with driver.session() as s:
            row = s.run("MATCH (n {id:$id}) RETURN n.id AS id", id=entity_id).single()
        if not row:
            raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
        mapper = ConnectionMapper(driver=driver)
        return mapper.get_node_evidence(entity_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Investigation] Node evidence error for {entity_id}: {e}")
        raise HTTPException(status_code=500, detail="Evidence fetch failed — please retry")
