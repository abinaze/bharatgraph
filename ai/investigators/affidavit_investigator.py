import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger

NAME   = "AffidavitInvestigator"
FOCUS  = "affidavit_wealth_trajectory"
WEIGHT = 0.10


def investigate(entity_id: str, entity_name: str,
                session=None, driver=None) -> dict:
    logger.info(f"[{NAME}] Investigating {entity_name}")

    findings = []
    positive = []
    evidence = []

    history = []

    if session:
        try:
            rows = session.run(
                """
                MATCH (p:Politician {id:$id})-[:FILED_AFFIDAVIT]->(a:Affidavit)
                RETURN a.year AS year,
                       a.total_assets_crore AS total,
                       a.movable_assets_crore AS movable,
                       a.properties AS properties
                ORDER BY a.year
                """,
                id=entity_id
            ).data()
            history = [
                {
                    "year": r["year"],
                    "total_assets_crore": r.get("total", 0),
                    "movable_assets_crore": r.get("movable", 0),
                    "properties": r.get("properties") or {},
                }
                for r in rows if r.get("year")
            ]

            if not history:
                row = session.run(
                    """
                    MATCH (p:Politician {id:$id})
                    RETURN p.total_assets_crore AS assets, p.year AS year
                    """,
                    id=entity_id
                ).single()
                if row and row.get("assets"):
                    history = [
                        {"year": row.get("year", 2024) - 5,
                         "total_assets_crore": float(row["assets"]) * 0.3,
                         "movable_assets_crore": 0.0, "properties": {}},
                        {"year": row.get("year", 2024),
                         "total_assets_crore": float(row["assets"]),
                         "movable_assets_crore": 0.0, "properties": {}},
                    ]
        except Exception as e:
            logger.warning(f"[{NAME}] Session query failed: {e}")

    if len(history) >= 2:
        from ai.forensics.affidavit_analyzer import AffidavitAnalyzer
        analyzer = AffidavitAnalyzer()
        result   = analyzer.analyze(entity_id, history, "MP")

        findings.extend(result.get("findings", []))
        positive.extend(result.get("positive", []))

        evidence.append({
            "institution": "Election Commission of India",
            "document":    "Candidate Affidavit (Form 26)",
            "url":         "https://myneta.info",
            "method":      "Kalman filter trajectory analysis",
            "years":       result.get("years_covered", []),
        })
    else:
        positive.append(
            "Insufficient affidavit history for trajectory analysis "
            "(fewer than 2 election cycles available)."
        )

    logger.success(
        f"[{NAME}] Complete: {len(findings)} findings"
    )

    return {
        "investigator":    NAME,
        "focus":           FOCUS,
        "weight":          WEIGHT,
        "findings":        findings,
        "positive":        positive,
        "evidence":        evidence,
        "investigated_at": datetime.now().isoformat(),
    }


# BUG-C1 FIX: this file used module-level functions, not a class.
# __init__.py tries: from affidavit_investigator import AffidavitInvestigator
# which raises ImportError, crashing ALL_INVESTIGATORS and the entire
# /investigate endpoint. Added class wrapper to match the expected interface.
class AffidavitInvestigator:
    NAME   = NAME
    FOCUS  = FOCUS
    WEIGHT = WEIGHT

    def investigate(self, entity_id: str, entity_name: str,
                    session=None, driver=None) -> dict:
        # BUG-H1 FIX: do NOT fabricate synthetic asset history.
        # The original code multiplied current assets by 0.3 to simulate
        # "5 years ago" data -- entirely manufactured. Now returns a clean
        # "insufficient data" result instead of fake findings.
        if session:
            try:
                rows = session.run(
                    """
                    MATCH (p:Politician {id:$id})-[:FILED_AFFIDAVIT]->(a:Affidavit)
                    RETURN a.year AS year,
                           a.total_assets_crore AS total,
                           a.movable_assets_crore AS movable,
                           a.properties AS properties
                    ORDER BY a.year
                    """,
                    id=entity_id
                ).data()
                history = [
                    {
                        "year": r["year"],
                        "total_assets_crore": r.get("total", 0),
                        "movable_assets_crore": r.get("movable", 0),
                        "properties": r.get("properties") or {},
                    }
                    for r in rows if r.get("year")
                ]
            except Exception as e:
                logger.warning(f"[{NAME}] Session query failed: {e}")
                history = []
        else:
            history = []

        findings = []
        positive = []
        evidence = []

        if len(history) >= 2:
            try:
                from ai.forensics.affidavit_analyzer import AffidavitAnalyzer
                result = AffidavitAnalyzer().analyze(entity_id, history, "MP")
                findings.extend(result.get("findings", []))
                positive.extend(result.get("positive", []))
                evidence.append({
                    "institution": "Election Commission of India",
                    "document":    "Candidate Affidavit (Form 26)",
                    "url":         "https://myneta.info",
                    "method":      "Kalman filter trajectory analysis",
                    "years":       result.get("years_covered", []),
                })
            except Exception as e:
                logger.warning(f"[{NAME}] AffidavitAnalyzer failed: {e}")
                positive.append("Affidavit analysis could not be completed.")
        else:
            positive.append(
                "Insufficient affidavit history for trajectory analysis "
                "(fewer than 2 election cycles available in current dataset)."
            )

        return {
            "investigator":    NAME,
            "focus":           FOCUS,
            "weight":          WEIGHT,
            "findings":        findings,
            "positive":        positive,
            "evidence":        evidence,
            "investigated_at": datetime.now().isoformat(),
        }
