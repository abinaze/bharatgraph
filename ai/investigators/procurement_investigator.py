import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from datetime import datetime
from loguru import logger


class ProcurementInvestigator:

    NAME   = "Procurement Investigator"
    FOCUS  = "Tender patterns, bid concentration, single bids, ministry relationships"
    WEIGHT = 0.12

    def investigate(self, entity_id: str, entity_name: str,
                    session) -> dict:
        logger.info(f"[Procurement] Investigating: {entity_name}")
        findings = []
        positive = []
        evidence = []

        try:
            rows = session.run(
                """
                MATCH (c {id: $id})-[:WON_CONTRACT]->(ct:Contract)
                RETURN ct.buyer_org AS buyer, count(ct) AS cnt,
                       sum(ct.amount_crore) AS total
                ORDER BY cnt DESC
                """,
                id=entity_id
            ).data()

            if rows:
                top_buyer      = rows[0]
                total_buyers   = len(rows)
                total_contracts= sum(r["cnt"] for r in rows)

                if total_buyers == 1 and total_contracts >= 3:
                    findings.append({
                        "type":        "single_buyer_concentration",
                        "description": (
                            f"All {total_contracts} contract(s) awarded by "
                            f"a single buyer: {top_buyer['buyer']}. "
                            "High concentration in a single procuring entity "
                            "is a structural risk indicator."
                        ),
                        "severity":    "HIGH",
                        "evidence":    [
                            f"{top_buyer['buyer']}: {top_buyer['cnt']} contracts, "
                            f"Rs {top_buyer['total']:.1f} Cr"
                        ],
                    })

                evidence.append({
                    "institution": "Government e-Marketplace",
                    "document":    "Procurement Order Records",
                    "url":         "https://gem.gov.in",
                    "date":        "",
                })

                if total_buyers >= 3 and total_contracts >= 5:
                    positive.append(
                        f"Entity has won contracts from {total_buyers} different "
                        "procuring organisations indicating competitive participation."
                    )

        except Exception as e:
            logger.warning(f"[Procurement] Neo4j query failed: {e}")

        return {
            "investigator": self.NAME,
            "focus":        self.FOCUS,
            "findings":     findings,
            "positive":     positive,
            "evidence":     evidence,
            "confidence":   "HIGH" if evidence else "LOW",
            "investigated_at": datetime.now().isoformat(),
        }
