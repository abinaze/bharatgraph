import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends
from api.dependencies import get_db

router = APIRouter()

@router.post("/admin/seed")
def seed_database(driver=Depends(get_db)):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
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
        "status":      "seeded",
        "politicians": p,
        "companies":   c,
        "contracts":   k,
        "audit_reports": a,
        "try_searching": ["Modi", "Gandhi", "Adani", "Tata", "Infosys"],
    }
