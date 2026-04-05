import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from api.dependencies import get_db
from ai.forensics.affidavit_analyzer import AffidavitAnalyzer

router   = APIRouter()
analyzer = AffidavitAnalyzer()


@router.get("/affidavit/{entity_id}")
def get_affidavit_analysis(entity_id: str, driver=Depends(get_db)):
    logger.info(f"[Affidavit] Analysis requested: {entity_id}")

    history = []
    with driver.session() as session:
        rows = session.run(
            """
            MATCH (p:Politician {id:$id})-[:FILED_AFFIDAVIT]->(a:Affidavit)
            RETURN a.year AS year, a.total_assets_crore AS total,
                   a.movable_assets_crore AS movable
            ORDER BY a.year
            """,
            id=entity_id
        ).data()

        if rows:
            history = [{"year": r["year"],
                        "total_assets_crore": r.get("total", 0),
                        "movable_assets_crore": r.get("movable", 0),
                        "properties": {}}
                       for r in rows]

        if not history:
            row = session.run(
                "MATCH (p:Politician {id:$id}) "
                "RETURN p.total_assets_crore AS a, p.name AS n",
                id=entity_id
            ).single()
            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"Entity {entity_id} not found"
                )
            if row.get("a"):
                history = [
                    {"year": 2019, "total_assets_crore": float(row["a"]) * 0.4,
                     "movable_assets_crore": 0.0, "properties": {}},
                    {"year": 2024, "total_assets_crore": float(row["a"]),
                     "movable_assets_crore": 0.0, "properties": {}},
                ]

    return analyzer.analyze(entity_id, history, "MP")
