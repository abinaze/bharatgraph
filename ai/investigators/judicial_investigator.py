import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from datetime import datetime
from loguru import logger


class JudicialInvestigator:

    NAME   = "Judicial Investigator"
    FOCUS  = "Court cases, pending litigation, judicial history, compliance with court orders"
    WEIGHT = 0.08

    def investigate(self, entity_id: str, entity_name: str,
                    session) -> dict:
        logger.info(f"[Judicial] Investigating: {entity_name}")
        findings = []
        positive = []
        evidence = []

        try:
            rows = session.run(
                """
                MATCH (c:CourtCase)-[:INVOLVES]->(n {id: $id})
                RETURN c.case_number AS case_num, c.court AS court,
                       c.case_type AS type, c.status AS status,
                       c.filing_date AS filed
                """,
                id=entity_id
            ).data()

            if rows:
                pending = [r for r in rows if r.get("status") == "Pending"]
                findings.append({
                    "type":        "court_cases_found",
                    "description": (
                        f"{len(rows)} court case(s) found involving this entity. "
                        f"{len(pending)} are currently pending."
                    ),
                    "severity":    "HIGH" if len(rows) >= 3 else "MODERATE",
                    "evidence":    [
                        f"{r['case_num']} at {r['court']} ({r['status']})"
                        for r in rows[:5]
                    ],
                })
                evidence.append({
                    "institution": "National Judicial Data Grid",
                    "document":    "Case Status Records",
                    "url":         "https://njdg.ecourts.gov.in",
                    "date":        "",
                })
            else:
                positive.append(
                    "No court cases found against this entity in the "
                    "National Judicial Data Grid records."
                )

        except Exception as e:
            logger.warning(f"[Judicial] Neo4j query failed: {e}")

        return {
            "investigator": self.NAME,
            "focus":        self.FOCUS,
            "findings":     findings,
            "positive":     positive,
            "evidence":     evidence,
            "confidence":   "MODERATE",
            "investigated_at": datetime.now().isoformat(),
        }
