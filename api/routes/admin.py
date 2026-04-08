import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from fastapi import APIRouter, Depends, BackgroundTasks
from loguru import logger
from api.dependencies import get_db

router = APIRouter()

_pipeline_status = {
    "running": False, "last_run": None,
    "last_summary": None, "last_error": None,
}


@router.post("/admin/seed")
def seed_database(driver=Depends(get_db)):
    """Load sample data into Neo4j — use when pipeline has not run yet."""
    from graph.seed import (
        SAMPLE_POLITICIANS, SAMPLE_COMPANIES,
        SAMPLE_CONTRACTS, SAMPLE_AUDIT_REPORTS
    )
    from graph.loader import GraphLoader

    loader = GraphLoader()
    p = loader.load_politicians(SAMPLE_POLITICIANS)
    c = loader.load_companies(SAMPLE_COMPANIES)
    k = loader.load_contracts(SAMPLE_CONTRACTS)
    a = loader.load_audit_reports(SAMPLE_AUDIT_REPORTS)

    return {
        "status":        "seeded",
        "politicians":   p,
        "companies":     c,
        "contracts":     k,
        "audit_reports": a,
        "try_searching": ["Modi", "Gandhi", "Adani", "Tata", "Infosys",
                          "road construction", "audit Maharashtra"],
        "next":          "POST /admin/pipeline to run all 20 live scrapers",
    }


@router.post("/admin/pipeline")
def trigger_pipeline(
    background_tasks: BackgroundTasks,
    scrapers: str = "all",
    driver=Depends(get_db),
):
    """
    Trigger full 20-scraper pipeline in background.
    scrapers: comma-separated list or 'all'
    e.g. POST /admin/pipeline?scrapers=cag,gem,pib,myneta,wikidata
    """
    if _pipeline_status["running"]:
        return {
            "status":   "already_running",
            "started":  _pipeline_status["last_run"],
            "message":  "Pipeline is already running. Check /admin/pipeline/status",
        }

    scraper_list = None if scrapers == "all" else scrapers.split(",")

    background_tasks.add_task(
        _run_pipeline_background, scraper_list, driver
    )

    _pipeline_status["running"]  = True
    _pipeline_status["last_run"] = datetime.now().isoformat()

    return {
        "status":   "started",
        "scrapers": scrapers,
        "message":  "Pipeline running in background. Check /admin/pipeline/status",
        "note":     "Full run takes 3-8 minutes depending on network.",
    }


@router.get("/admin/pipeline/status")
def pipeline_status():
    """Check if pipeline is running and see last result."""
    return {
        "running":      _pipeline_status["running"],
        "last_run":     _pipeline_status["last_run"],
        "last_summary": _pipeline_status["last_summary"],
        "last_error":   _pipeline_status["last_error"],
    }


def _run_pipeline_background(scraper_list, driver):
    """Background task — runs pipeline then loads results into Neo4j."""
    try:
        logger.info("[Admin] Background pipeline started")
        from processing.pipeline import BharatGraphPipeline
        from graph.loader import GraphLoader

        results = BharatGraphPipeline().run(
            scrapers=scraper_list, parallel=True
        )
        summary = results["summary"]
        raw     = results.get("raw", {})

        logger.info("[Admin] Pipeline done — loading into Neo4j...")
        loader = GraphLoader()

        loaded = {
            "politicians":    loader.load_politicians(raw.get("myneta", [])),
            "companies":      loader.load_companies(raw.get("mca", [])),
            "contracts":      loader.load_contracts(raw.get("gem", [])),
            "audit_reports":  loader.load_audit_reports(raw.get("cag", [])),
            "press_releases": loader.load_press_releases(raw.get("pib", [])),
        }

        _pipeline_status["last_summary"] = {
            **summary,
            "loaded": loaded,
            "completed_at": datetime.now().isoformat(),
        }
        logger.success(
            f"[Admin] Pipeline complete — "
            f"{summary['total_raw_records']} records loaded"
        )

    except Exception as e:
        logger.error(f"[Admin] Pipeline failed: {e}")
        _pipeline_status["last_error"] = str(e)
    finally:
        _pipeline_status["running"] = False
