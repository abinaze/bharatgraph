import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from datetime import datetime
from loguru import logger


class CorporateInvestigator:

    NAME   = "Corporate Investigator"
    FOCUS  = "Directorships, company health, compliance history, ownership structure"
    WEIGHT = 0.10

    def investigate(self, entity_id: str, entity_name: str,
                    session) -> dict:
        logger.info(f"[Corporate] Investigating: {entity_name}")
        findings = []
        positive = []
        evidence = []

        try:
            rows = session.run(
                """
                MATCH (p {id: $id})-[:DIRECTOR_OF]->(c:Company)
                RETURN c.id AS cid, c.name AS name, c.status AS status,
                       c.state AS state, c.cin AS cin
                """,
                id=entity_id
            ).data()

            if rows:
                inactive = [r for r in rows if r.get("status") in
                            ("Strike Off", "Inactive", "Dormant")]
                if len(rows) > 5:
                    findings.append({
                        "type":        "high_directorship_count",
                        "description": (
                            f"Entity holds directorships in {len(rows)} companies. "
                            "High directorship count is associated with nominee "
                            "director arrangements."
                        ),
                        "severity":    "MODERATE",
                        "evidence":    [r["name"] for r in rows[:5]],
                    })
                if inactive:
                    findings.append({
                        "type":        "dormant_company_links",
                        "description": (
                            f"{len(inactive)} associated company(ies) have "
                            "inactive or struck-off status."
                        ),
                        "severity":    "LOW",
                        "evidence":    [r["name"] for r in inactive],
                    })
                    evidence.append({
                        "institution": "Ministry of Corporate Affairs",
                        "document":    "MCA21 Company Master Data",
                        "url":         "https://www.mca.gov.in",
                        "date":        "",
                    })

                if len(rows) <= 3 and not inactive:
                    positive.append(
                        f"Entity holds {len(rows)} directorship(s) with "
                        "no inactive or struck-off companies on record."
                    )

        except Exception as e:
            logger.warning(f"[Corporate] Neo4j query failed: {e}")

        return {
            "investigator": self.NAME,
            "focus":        self.FOCUS,
            "findings":     findings,
            "positive":     positive,
            "evidence":     evidence,
            "confidence":   "HIGH" if evidence else "LOW",
            "investigated_at": datetime.now().isoformat(),
        }
