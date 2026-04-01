import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from datetime import datetime
from loguru import logger


class NetworkInvestigator:

    NAME   = "Network Investigator"
    FOCUS  = "Graph centrality, community membership, key connections, bridge entities"
    WEIGHT = 0.08

    def investigate(self, entity_id: str, entity_name: str,
                    session) -> dict:
        logger.info(f"[Network] Investigating: {entity_name}")
        findings = []
        positive = []
        evidence = []

        try:
            row = session.run(
                """
                MATCH (n {id: $id})
                RETURN n.betweenness_centrality AS bc,
                       n.pagerank AS pr,
                       n.risk_score AS rs
                """,
                id=entity_id
            ).single()

            if row:
                bc = row.get("bc") or 0
                pr = row.get("pr") or 0

                if bc > 0.1:
                    findings.append({
                        "type":        "high_betweenness_centrality",
                        "description": (
                            f"Entity has betweenness centrality of {bc:.4f}, "
                            "indicating it acts as a significant bridge "
                            "between institutional networks."
                        ),
                        "severity":    "MODERATE",
                        "evidence":    [f"Betweenness: {bc:.4f}"],
                    })
                elif bc > 0:
                    positive.append(
                        f"Betweenness centrality ({bc:.4f}) is within "
                        "normal range — entity is not a network gatekeeper."
                    )

            neighbour_rows = session.run(
                """
                MATCH (n {id: $id})-[r]-(neighbour)
                RETURN labels(neighbour)[0] AS type, count(neighbour) AS cnt
                ORDER BY cnt DESC
                """,
                id=entity_id
            ).data()

            if neighbour_rows:
                total_connections = sum(r["cnt"] for r in neighbour_rows)
                conn_summary = ", ".join(
                    f"{r['cnt']} {r['type']}(s)" for r in neighbour_rows[:4]
                )
                findings.append({
                    "type":        "network_connectivity",
                    "description": (
                        f"Entity has {total_connections} direct connections: "
                        f"{conn_summary}."
                    ),
                    "severity":    "LOW",
                    "evidence":    [conn_summary],
                })

        except Exception as e:
            logger.warning(f"[Network] Neo4j query failed: {e}")

        return {
            "investigator": self.NAME,
            "focus":        self.FOCUS,
            "findings":     findings,
            "positive":     positive,
            "evidence":     evidence,
            "confidence":   "MODERATE",
            "investigated_at": datetime.now().isoformat(),
        }
