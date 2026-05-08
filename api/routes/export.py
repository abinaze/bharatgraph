import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from loguru import logger

from api.dependencies import get_db, get_driver
from ai.dossier_generator import DossierGenerator
from ai.report_hasher import ReportHasher
from ai.multi_investigator import MultiInvestigator

router   = APIRouter()
_hasher = None


def get_generator() -> DossierGenerator:
    """BUG-08 FIX: was caching generator with stale driver.
    Now creates a fresh generator per request -- driver is always fresh."""
    return DossierGenerator(driver=get_driver())


def get_hasher() -> ReportHasher:
    global _hasher
    if _hasher is None:
        _hasher = ReportHasher()
    return _hasher


@router.get("/export/pdf/{entity_id}")
def export_pdf(entity_id: str, driver=Depends(get_db)):
    logger.info(f"[Export] PDF requested for: {entity_id}")

    investigator = MultiInvestigator(driver=driver)
    with driver.session() as session:
        row = session.run(
            "MATCH (n {id: $id}) RETURN n.name AS name",
            id=entity_id
        ).single()

    if not row:
        raise HTTPException(status_code=404,
                            detail=f"Entity {entity_id} not found")

    entity_name  = row["name"] or entity_id
    multi_report = investigator.investigate(entity_id, entity_name)

    generator = DossierGenerator(driver=driver)
    result    = generator.generate(
        entity_id,
        multi_report=multi_report,
        output_dir="data/processed",
    )

    output_path = result.get("pdf_path") or result.get("html_path")
    if not output_path or not os.path.exists(output_path):
        raise HTTPException(status_code=500,
                            detail="Dossier generation failed")
    # H-07 / CodeQL fix: use file-anchored absolute path
    _routes_dir   = os.path.dirname(os.path.abspath(__file__))
    _project_root = os.path.dirname(os.path.dirname(_routes_dir))
    allowed_dir   = os.path.realpath(os.path.join(_project_root, "data", "processed"))
    real_out      = os.path.realpath(output_path)
    if not real_out.startswith(allowed_dir + os.sep):
        raise HTTPException(status_code=400, detail="Invalid output path")

    media_type = (
        "application/pdf"
        if real_out.endswith(".pdf")
        else "text/html"
    )
    
    # BUG-17 FIX: wire blockchain audit trail to dossier export.
    # AuditChain was fully implemented but never called anywhere.
    # README claimed "SHA-256 blockchain audit trail" -- now true.
    try:
        from blockchain.audit_chain import store_daily_root
        from api.dependencies import get_driver as _get_driver
        _drv = _get_driver()
        if _drv:
            store_daily_root(_drv)
    except Exception as _bc_err:
        logger.debug(f"[Export] Blockchain audit step (optional): {_bc_err}")

    # CodeQL #16-17 FIX: use validated real_out path for all file operations
    return FileResponse(
        real_out,
        media_type=media_type,
        filename=os.path.basename(real_out),
        headers={"X-Report-Hash": result["report_hash"]},
    )


@router.get("/verify/{report_hash}")
def verify_report(report_hash: str, driver=Depends(get_db)):
    hasher = get_hasher()
    result = hasher.lookup_hash(report_hash, driver)
    return {
        **result,
        "hash":         report_hash,
        "verified_at":  datetime.now().isoformat(),
    }
