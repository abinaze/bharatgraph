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
    """Load sample nodes AND relationships into Neo4j for demonstration."""
    from graph.seed import (
        SAMPLE_POLITICIANS, SAMPLE_COMPANIES,
        SAMPLE_CONTRACTS, SAMPLE_AUDIT_REPORTS,
        SAMPLE_DIRECTOR_LINKS,
    )
    from graph.loader import GraphLoader

    # BUG-21 FIX: pass the existing driver so GraphLoader doesn't open a
    # second connection (GraphLoader.__init__ now accepts driver= kwarg).
    loader = GraphLoader(driver=driver)
    p = loader.load_politicians(SAMPLE_POLITICIANS)
    c = loader.load_companies(SAMPLE_COMPANIES)
    k = loader.load_contracts(SAMPLE_CONTRACTS)
    a = loader.load_audit_reports(SAMPLE_AUDIT_REPORTS)
    d = loader.load_politician_company_links(SAMPLE_DIRECTOR_LINKS)

    return {
        "status":        "seeded",
        "politicians":   p,
        "companies":     c,
        "contracts":     k,
        "audit_reports": a,
        "director_links":d,
        "try_searching": [
            "Modi", "Gandhi", "Adani", "Tata", "Infosys",
            "Amit Shah", "Anurag Thakur", "road construction", "audit Maharashtra"
        ],
        "note": (
            "Sample data loaded with DIRECTOR_OF and WON_CONTRACT relationships. "
            "Search any name above to see the investigation graph."
        ),
        "next": "POST /admin/pipeline to ingest all 21 live government sources",
    }


@router.post("/admin/pipeline")
def trigger_pipeline(
    background_tasks: BackgroundTasks,
    scrapers: str = "all",
    driver=Depends(get_db),
):
    """Trigger full pipeline in background. scrapers: comma-separated or 'all'."""
    if _pipeline_status["running"]:
        return {
            "status":  "already_running",
            "started": _pipeline_status["last_run"],
            "message": "Pipeline is already running. Check /admin/pipeline/status",
        }

    scraper_list = None if scrapers == "all" else scrapers.split(",")
    background_tasks.add_task(_run_pipeline_background, scraper_list, driver)
    _pipeline_status["running"]  = True
    _pipeline_status["last_run"] = datetime.now().isoformat()

    return {
        "status":  "started",
        "scrapers":scrapers,
        "message": "Pipeline running in background. Check /admin/pipeline/status",
        "note":    "Full run takes 3-8 minutes depending on network.",
    }


@router.get("/admin/pipeline/status")
def pipeline_status():
    return {
        "running":      _pipeline_status["running"],
        "last_run":     _pipeline_status["last_run"],
        "last_summary": _pipeline_status["last_summary"],
        "last_error":   _pipeline_status["last_error"],
    }


def _run_pipeline_background(scraper_list, driver):
    """
    Background task — runs pipeline then loads ALL scraped data into Neo4j.

    BUG-21 FIX: GraphLoader now receives the existing driver instead of
    creating a second Neo4j connection (which would exceed the free-tier limit).

    BUG-22 FIX: key was "electoral_bonds" (wrong) — corrected to "electoral_bond"
    to match the scraper output key set by run_electoral_bond() in pipeline.py.

    BUG-30 FIX: added the 7 missing scrapers: icij, opensanctions, njdg, lgd,
    ncrb, wikidata, datagov — these were scraped but their loader methods were
    never registered in SCRAPER_TO_LOADER so they were silently dropped.
    """
    try:
        logger.info("[Admin] Background pipeline started")
        from processing.pipeline import BharatGraphPipeline
        from graph.loader import GraphLoader

        results = BharatGraphPipeline().run(scrapers=scraper_list, parallel=True)
        summary = results["summary"]
        raw     = results.get("raw", {})

        logger.info("[Admin] Pipeline done — loading into Neo4j...")
        # BUG-21 FIX: reuse the existing driver, don't open a second connection
        loader = GraphLoader(driver=driver)

        # Complete mapping of all 20 scrapers to their loader methods.
        # BUG-22 FIX: was "electoral_bonds" → corrected to "electoral_bond"
        # BUG-30 FIX: added 7 previously missing scrapers
        SCRAPER_TO_LOADER = {
            "myneta":         "load_politicians",
            "mca":            "load_companies",
            "gem":            "load_contracts",
            "cag":            "load_audit_reports",
            "pib":            "load_press_releases",
            "sebi":           "load_regulatory_orders",
            "ed":             "load_enforcement_actions",
            "electoral_bond": "load_electoral_bonds",       # BUG-22 FIX: was "electoral_bonds"
            "ibbi":           "load_insolvency_orders",
            "ngo_darpan":     "load_ngos",
            "cppp":           "load_tenders",
            "loksabha":       "load_parliament_questions",
            "cvc":            "load_vigilance_circulars",
            # BUG-30 FIX: 7 new scrapers added below
            "icij":           "load_icij_entities",
            "opensanctions":  "load_sanctioned_entities",
            "njdg":           "load_court_cases",
            "lgd":            "load_local_bodies",
            "ncrb":           "load_crime_reports",
            "wikidata":       "load_wikidata_enrichments",
            "datagov":        "load_datagov_documents",
        }

        loaded = {}
        for scraper_key, method_name in SCRAPER_TO_LOADER.items():
            records = raw.get(scraper_key, [])
            if not records:
                logger.debug(f"[Admin] No records for {scraper_key}, skipping")
                continue
            method = getattr(loader, method_name, None)
            if method is None:
                logger.warning(f"[Admin] loader.{method_name}() not found — skipping {scraper_key}")
                continue
            try:
                n = method(records)
                loaded[scraper_key] = n
                logger.info(f"[Admin] Loaded {n} {scraper_key} records via {method_name}()")
            except Exception as load_err:
                logger.error(f"[Admin] Failed loading {scraper_key}: {load_err}")
                loaded[scraper_key] = 0

        total_loaded = sum(loaded.values())
        _pipeline_status["last_summary"] = {
            **summary,
            "loaded":       loaded,
            "total_loaded": total_loaded,
            "completed_at": datetime.now().isoformat(),
        }
        logger.success(
            f"[Admin] Pipeline complete — "
            f"{total_loaded} total records loaded across {len(loaded)} datasets"
        )

    except Exception as e:
        logger.error(f"[Admin] Pipeline failed: {e}")
        _pipeline_status["last_error"] = str(e)
    finally:
        _pipeline_status["running"] = False
