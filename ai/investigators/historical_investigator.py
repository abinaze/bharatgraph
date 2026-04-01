import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from datetime import datetime
from loguru import logger


class HistoricalInvestigator:

    NAME   = "Historical Investigator"
    FOCUS  = "Timeline reconstruction, pattern over time, structural changes, career evolution"
    WEIGHT = 0.08

    def investigate(self, entity_id: str, entity_name: str,
                    session) -> dict:
        logger.info(f"[Historical] Investigating: {entity_name}")
        findings = []
        positive = []
        evidence = []
        timeline = []

        try:
            node_row = session.run(
                "MATCH (n {id: $id}) RETURN n.scored_at AS scored_at, "
                "labels(n)[0] AS type",
                id=entity_id
            ).single()

            entity_type = node_row["type"] if node_row else "Unknown"

            contract_rows = session.run(
                """
                MATCH (n {id: $id})-[:DIRECTOR_OF|WON_CONTRACT*1..2]->(ct:Contract)
                RETURN ct.order_date AS date, ct.amount_crore AS amount,
                       ct.buyer_org AS buyer
                ORDER BY ct.order_date
                """,
                id=entity_id
            ).data()

            for r in contract_rows:
                if r.get("date"):
                    timeline.append({
                        "date":        r["date"],
                        "event":       "Contract Awarded",
                        "detail":      f"Rs {r.get('amount')} Cr from {r.get('buyer')}",
                        "source":      "GeM",
                    })

            if len(contract_rows) >= 2:
                findings.append({
                    "type":        "recurring_contract_pattern",
                    "description": (
                        f"{len(contract_rows)} contract events found across "
                        "the entity's history indicating sustained procurement engagement."
                    ),
                    "severity":    "LOW",
                    "evidence":    [f"{len(contract_rows)} contract timeline entries"],
                })

            if timeline:
                evidence.append({
                    "institution": "BharatGraph Timeline Analysis",
                    "document":    "Reconstructed Event Timeline",
                    "url":         "",
                    "date":        datetime.now().isoformat(),
                })

            positive.append(
                f"Entity type: {entity_type}. "
                f"Timeline has {len(timeline)} recorded event(s)."
            )

        except Exception as e:
            logger.warning(f"[Historical] Neo4j query failed: {e}")

        return {
            "investigator": self.NAME,
            "focus":        self.FOCUS,
            "findings":     findings,
            "positive":     positive,
            "evidence":     evidence,
            "timeline":     timeline,
            "confidence":   "MODERATE",
            "investigated_at": datetime.now().isoformat(),
        }
