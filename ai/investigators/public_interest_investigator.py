import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from datetime import datetime
from loguru import logger


class PublicInterestInvestigator:

    NAME   = "Public Interest Investigator"
    FOCUS  = "Scheme implementation, beneficiary data, development indicators, governance quality"
    WEIGHT = 0.08

    def investigate(self, entity_id: str, entity_name: str,
                    session) -> dict:
        logger.info(f"[PublicInterest] Investigating: {entity_name}")
        findings = []
        positive = []
        evidence = []

        try:
            scheme_rows = session.run(
                """
                MATCH (s:Scheme)<-[:FLAGS]-(a:AuditReport)
                WHERE toLower(s.name) CONTAINS toLower($name)
                   OR toLower(a.title) CONTAINS toLower($name)
                RETURN s.name AS scheme, count(a) AS audit_count,
                       sum(a.amount_crore) AS flagged_amount
                ORDER BY flagged_amount DESC
                LIMIT 5
                """,
                name=entity_name
            ).data()

            if scheme_rows:
                for scheme in scheme_rows:
                    if scheme.get("flagged_amount") and scheme["flagged_amount"] > 0:
                        findings.append({
                            "type":        "scheme_audit_flag",
                            "description": (
                                f"Scheme '{scheme['scheme']}' linked to entity "
                                f"has {scheme['audit_count']} CAG audit flag(s) "
                                f"totalling Rs {scheme['flagged_amount']:.1f} Cr. "
                                "This may impact public welfare delivery."
                            ),
                            "severity":    "HIGH",
                            "evidence":    [
                                f"CAG flagged Rs {scheme['flagged_amount']:.1f} Cr "
                                f"in {scheme['scheme']}"
                            ],
                        })
                        evidence.append({
                            "institution": "CAG of India",
                            "document":    "Scheme Performance Audit",
                            "url":         "https://cag.gov.in/en/audit-report",
                            "date":        "",
                        })
            else:
                positive.append(
                    "No adverse scheme audit findings linked to this entity "
                    "in available CAG audit records."
                )

        except Exception as e:
            logger.warning(f"[PublicInterest] Neo4j query failed: {e}")

        return {
            "investigator": self.NAME,
            "focus":        self.FOCUS,
            "findings":     findings,
            "positive":     positive,
            "evidence":     evidence,
            "confidence":   "MODERATE",
            "investigated_at": datetime.now().isoformat(),
        }
