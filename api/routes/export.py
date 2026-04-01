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
_generator = None
_hasher    = None


def get_generator() -> DossierGenerator:
    global _generator
    if _generator is None:
        _generator = DossierGenerator(driver=get_driver())
    return _generator


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

    media_type = (
        "application/pdf"
        if output_path.endswith(".pdf")
        else "text/html"
    )
    return FileResponse(
        output_path,
        media_type=media_type,
        filename=os.path.basename(output_path),
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
