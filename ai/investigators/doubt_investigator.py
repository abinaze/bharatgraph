import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from datetime import datetime
from loguru import logger


class DoubtInvestigator:

    NAME   = "Doubt Investigator"
    FOCUS  = "Unexplained patterns, anomalies, hypotheses, gaps that warrant further attention"
    WEIGHT = 0.08

    def investigate(self, entity_id: str, entity_name: str,
                    session) -> dict:
        logger.info(f"[Doubt] Investigating: {entity_name}")
        doubts   = []
        positive = []
        evidence = []

        try:
            row = session.run(
                """
                MATCH (n {id: $id})
                OPTIONAL MATCH (n)-[:DIRECTOR_OF]->(c:Company)
                OPTIONAL MATCH (c)-[:WON_CONTRACT]->(ct:Contract)
                OPTIONAL MATCH (a:AuditReport)-[:FLAGS]->(:Scheme)
                WHERE toLower(a.title) CONTAINS toLower($name)
                RETURN count(DISTINCT c) AS companies,
                       count(DISTINCT ct) AS contracts,
                       count(DISTINCT a) AS audit_mentions,
                       n.risk_score AS risk_score
                """,
                id=entity_id,
                name=entity_name
            ).single()

            if row:
                companies      = row.get("companies", 0) or 0
                contracts      = row.get("contracts", 0) or 0
                audit_mentions = row.get("audit_mentions", 0) or 0
                risk_score     = row.get("risk_score", 0) or 0

                if companies > 0 and contracts == 0:
                    doubts.append({
                        "hypothesis": (
                            f"Entity has {companies} company directorship(s) "
                            "but no contracts are recorded against those companies. "
                            "If contracts were awarded, they may exist in sources "
                            "not yet ingested into the graph."
                        ),
                        "gap":        "Possible data coverage gap in procurement records",
                        "action":     "Cross-reference with CPPP tender award data",
                    })

                if audit_mentions > 0 and contracts == 0:
                    doubts.append({
                        "hypothesis": (
                            f"Entity appears in {audit_mentions} CAG audit report(s) "
                            "but no corresponding contracts are in the graph. "
                            "The audit mentions may relate to schemes administered "
                            "rather than contracts directly awarded."
                        ),
                        "gap":        "Possible audit-contract linkage gap",
                        "action":     "Review CAG report full text for entity role",
                    })

                if risk_score and risk_score > 60 and audit_mentions == 0:
                    doubts.append({
                        "hypothesis": (
                            f"Risk score ({risk_score}) is elevated but "
                            "no CAG audit mentions are recorded. "
                            "The score may be driven by structural patterns "
                            "rather than documented audit findings."
                        ),
                        "gap":        "High risk score without audit confirmation",
                        "action":     "Review individual risk factors for data quality",
                    })

                if not doubts:
                    positive.append(
                        "No unexplained gaps or contradictory patterns "
                        "identified in available data."
                    )

        except Exception as e:
            logger.warning(f"[Doubt] Neo4j query failed: {e}")
            doubts.append({
                "hypothesis": "Graph database query failed — manual review recommended.",
                "gap":        "Technical gap in analysis",
                "action":     "Retry with live Neo4j connection",
            })

        return {
            "investigator": self.NAME,
            "focus":        self.FOCUS,
            "findings":     [],
            "doubts":       doubts,
            "positive":     positive,
            "evidence":     evidence,
            "confidence":   "LOW",
            "investigated_at": datetime.now().isoformat(),
        }
