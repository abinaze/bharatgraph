import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from fastapi import APIRouter, Depends
from loguru import logger

from api.dependencies import get_db

router = APIRouter()

SCRAPER_META = {
    "myneta":          {"name":"MyNeta / ECI",              "url":"https://myneta.info",        "data":"Politicians, assets, criminal cases"},
    "mca":             {"name":"MCA21",                     "url":"https://www.mca.gov.in",     "data":"Companies, directors, CIN"},
    "gem":             {"name":"GeM",                       "url":"https://gem.gov.in",         "data":"Government contracts"},
    "cag":             {"name":"CAG",                       "url":"https://cag.gov.in",         "data":"Audit reports, irregularities"},
    "pib":             {"name":"PIB",                       "url":"https://pib.gov.in",         "data":"Press releases"},
    "datagov":         {"name":"data.gov.in",               "url":"https://data.gov.in",        "data":"MGNREGA, PM-KISAN, open data"},
    "loksabha":        {"name":"Lok Sabha",                 "url":"https://loksabha.nic.in",    "data":"Parliamentary questions, debates"},
    "sebi":            {"name":"SEBI",                      "url":"https://www.sebi.gov.in",    "data":"Enforcement orders"},
    "electoral_bond":  {"name":"Electoral Bonds (ECI/SC)",  "url":"https://eci.gov.in",         "data":"Donor-party data"},
    "opensanctions":   {"name":"OpenSanctions",             "url":"https://opensanctions.org",  "data":"Global PEP and sanctions"},
    "icij":            {"name":"ICIJ Offshore Leaks",       "url":"https://offshoreleaks.icij.org","data":"Panama, Pandora, Paradise Papers"},
    "wikidata":        {"name":"Wikidata",                  "url":"https://www.wikidata.org",   "data":"Entity enrichment, career data"},
    "njdg":            {"name":"NJDG / eCourts",            "url":"https://njdg.ecourts.gov.in","data":"Court cases, judgments"},
    "ed":              {"name":"Enforcement Directorate",   "url":"https://enforcementdirectorate.gov.in","data":"PMLA press releases"},
    "cvc":             {"name":"CVC",                       "url":"https://cvc.gov.in",         "data":"Vigilance advisories"},
    "ncrb":            {"name":"NCRB",                      "url":"https://ncrb.gov.in",        "data":"Crime statistics"},
    "lgd":             {"name":"LGD / Panchayati Raj",      "url":"https://lgdirectory.gov.in", "data":"Local government data"},
    "ibbi":            {"name":"IBBI",                      "url":"https://ibbi.gov.in",        "data":"Corporate insolvency records"},
    "ngo_darpan":      {"name":"NGO Darpan / NITI Aayog",   "url":"https://ngodarpan.gov.in",   "data":"NGO registration and funding"},
    "cppp":            {"name":"CPPP",                      "url":"https://eprocure.gov.in",    "data":"Procurement transparency"},
}


@router.get("/sources")
def sources_summary(driver=Depends(get_db)):
    """Returns count of nodes per source dataset loaded in Neo4j."""
    logger.info("[Sources] Summary requested")

    db_counts = {}
    try:
        with driver.session() as s:
            rows = s.run(
                """
                MATCH (n)
                WHERE n.source IS NOT NULL
                RETURN n.source AS source, count(*) AS total
                ORDER BY total DESC
                """
            ).data()
            db_counts = {r["source"]: r["total"] for r in rows}
    except Exception as e:
        logger.warning(f"[Sources] DB query failed: {e}")

    label_counts = {}
    try:
        with driver.session() as s:
            rows = s.run(
                """
                MATCH (n)
                RETURN labels(n)[0] AS label, count(*) AS total
                ORDER BY total DESC
                """
            ).data()
            label_counts = {r["label"]: r["total"] for r in rows if r.get("label")}
    except Exception as e:
        logger.warning(f"[Sources] Label count failed: {e}")

    sources = []
    for key, meta in SCRAPER_META.items():
        count = db_counts.get(key, 0)
        sources.append({
            "dataset":      key,
            "name":         meta["name"],
            "url":          meta["url"],
            "data_type":    meta["data"],
            "records_in_db": count,
            "status":       "loaded" if count > 0 else "pending",
        })

    sources.sort(key=lambda x: -x["records_in_db"])

    total_records = sum(label_counts.values()) if label_counts else 0

    return {
        "total_records":  total_records,
        "label_counts":   label_counts,
        "source_count":   len(SCRAPER_META),
        "loaded_sources": sum(1 for s in sources if s["status"] == "loaded"),
        "sources":        sources,
        "generated_at":   datetime.now().isoformat(),
    }


@router.get("/sources/{dataset}")
def source_detail(dataset: str, driver=Depends(get_db)):
    """Returns sample records from a specific dataset."""
    logger.info(f"[Sources] Detail for {dataset}")

    meta = SCRAPER_META.get(dataset)
    if not meta:
        return {"error": f"Unknown dataset: {dataset}",
                "available": list(SCRAPER_META.keys())}

    records = []
    try:
        with driver.session() as s:
            rows = s.run(
                """
                MATCH (n)
                WHERE n.source = $src
                RETURN n.id AS id, labels(n)[0] AS label,
                       coalesce(n.name, n.title) AS name,
                       n.state AS state, n.scraped_at AS scraped_at
                LIMIT 20
                """,
                src=dataset
            ).data()
            records = [dict(r) for r in rows]
    except Exception as e:
        logger.warning(f"[Sources] Detail query failed: {e}")

    return {
        "dataset":      dataset,
        "name":         meta["name"],
        "url":          meta["url"],
        "data_type":    meta["data"],
        "sample_count": len(records),
        "records":      records,
    }
