import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from datetime import datetime
from loguru import logger


class FinancialInvestigator:

    NAME        = "Financial Investigator"
    FOCUS       = "Money flows, contract values, asset anomalies, financial patterns"
    WEIGHT      = 0.12

    def investigate(self, entity_id: str, entity_name: str,
                    session) -> dict:
        logger.info(f"[Financial] Investigating: {entity_name}")
        findings          = []
        positive          = []
        evidence          = []

        try:
            rows = session.run(
                """
                MATCH (n {id: $id})-[:DIRECTOR_OF]->(c:Company)
                      -[:WON_CONTRACT]->(ct:Contract)
                RETURN c.name AS company, ct.order_id AS order_id,
                       ct.amount_crore AS amount, ct.buyer_org AS buyer,
                       ct.order_date AS date
                ORDER BY ct.amount_crore DESC
                """,
                id=entity_id
            ).data()

            if rows:
                total = sum(r.get("amount") or 0 for r in rows)
                findings.append({
                    "type":        "contract_financial_flow",
                    "description": (
                        f"Entity is associated with {len(rows)} contract(s) "
                        f"totalling Rs {total:.1f} Cr through directorship links."
                    ),
                    "severity":    "HIGH" if total > 100 else "MODERATE",
                    "evidence":    [
                        f"Contract {r['order_id']}: Rs {r['amount']} Cr "
                        f"from {r['buyer']}"
                        for r in rows[:5]
                    ],
                })
                for r in rows:
                    evidence.append({
                        "institution":  "Government e-Marketplace",
                        "document":     f"Contract {r['order_id']}",
                        "url":          "https://gem.gov.in",
                        "date":         r.get("date", ""),
                        "amount_crore": r.get("amount"),
                    })

            audit_rows = session.run(
                """
                MATCH (a:AuditReport)
                WHERE toLower(a.title) CONTAINS toLower($name)
                RETURN a.title AS title, a.amount_crore AS amount, a.year AS year
                ORDER BY a.amount_crore DESC
                """,
                name=entity_name
            ).data()

            if audit_rows:
                total_flagged = sum(r.get("amount") or 0 for r in audit_rows)
                findings.append({
                    "type":        "audit_financial_flag",
                    "description": (
                        f"CAG audit reports mention {len(audit_rows)} irregularity(ies) "
                        f"totalling Rs {total_flagged:.1f} Cr linked to this entity."
                    ),
                    "severity":    "HIGH" if total_flagged > 50 else "MODERATE",
                    "evidence":    [r["title"] for r in audit_rows[:3]],
                })
                for r in audit_rows:
                    evidence.append({
                        "institution": "Comptroller and Auditor General",
                        "document":    r["title"],
                        "url":         "https://cag.gov.in/en/audit-report",
                        "date":        str(r.get("year", "")),
                    })

            if not findings:
                positive.append(
                    "No significant financial anomalies detected in "
                    "available procurement and audit records."
                )

        except Exception as e:
            logger.warning(f"[Financial] Neo4j query failed: {e}")

        return {
            "investigator": self.NAME,
            "focus":        self.FOCUS,
            "findings":     findings,
            "positive":     positive,
            "evidence":     evidence,
            "confidence":   "HIGH" if len(evidence) >= 3 else "MODERATE" if evidence else "LOW",
            "investigated_at": datetime.now().isoformat(),
        }
