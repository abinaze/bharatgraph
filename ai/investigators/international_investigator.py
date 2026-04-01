import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from datetime import datetime
from loguru import logger


class InternationalInvestigator:

    NAME   = "International Investigator"
    FOCUS  = "Offshore entities, sanctions, ICIJ leaks, cross-border connections, PEP status"
    WEIGHT = 0.10

    def investigate(self, entity_id: str, entity_name: str,
                    session) -> dict:
        logger.info(f"[International] Investigating: {entity_name}")
        findings = []
        positive = []
        evidence = []

        try:
            offshore_rows = session.run(
                """
                MATCH (o:OffshoreEntity)-[:LINKED_TO]->(n {id: $id})
                RETURN o.name AS name, o.dataset AS dataset,
                       o.jurisdiction AS jurisdiction
                """,
                id=entity_id
            ).data()

            if offshore_rows:
                findings.append({
                    "type":        "offshore_entity_link",
                    "description": (
                        f"Entity is linked to {len(offshore_rows)} offshore "
                        "entity(ies) in ICIJ Offshore Leaks data "
                        "(Panama, Pandora, or Paradise Papers)."
                    ),
                    "severity":    "HIGH",
                    "evidence":    [
                        f"{r['name']} in {r['jurisdiction']} ({r['dataset']})"
                        for r in offshore_rows[:5]
                    ],
                })
                evidence.append({
                    "institution": "ICIJ Offshore Leaks",
                    "document":    "Offshore Leaks Database",
                    "url":         "https://offshoreleaks.icij.org",
                    "date":        "",
                })

            sanctions_rows = session.run(
                """
                MATCH (s:SanctionedEntity)-[:IS_SANCTIONED]->(n {id: $id})
                RETURN s.datasets AS datasets
                """,
                id=entity_id
            ).data()

            if sanctions_rows:
                findings.append({
                    "type":        "sanctions_pep_match",
                    "description": (
                        "Entity appears in OpenSanctions PEP or "
                        "sanctions dataset."
                    ),
                    "severity":    "VERY_HIGH",
                    "evidence":    ["Source: OpenSanctions.org"],
                })

            if not offshore_rows and not sanctions_rows:
                positive.append(
                    "No matches found in ICIJ Offshore Leaks database "
                    "or OpenSanctions PEP and sanctions lists."
                )

        except Exception as e:
            logger.warning(f"[International] Neo4j query failed: {e}")

        return {
            "investigator": self.NAME,
            "focus":        self.FOCUS,
            "findings":     findings,
            "positive":     positive,
            "evidence":     evidence,
            "confidence":   "HIGH" if findings else "MODERATE",
            "investigated_at": datetime.now().isoformat(),
        }
