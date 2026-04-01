import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from datetime import datetime
from loguru import logger


class MediaInvestigator:

    NAME   = "Media Investigator"
    FOCUS  = "PIB mentions, press release patterns, official communication analysis"
    WEIGHT = 0.06

    def investigate(self, entity_id: str, entity_name: str,
                    session) -> dict:
        logger.info(f"[Media] Investigating: {entity_name}")
        findings = []
        positive = []
        evidence = []

        try:
            pib_rows = session.run(
                """
                MATCH (pr:PressRelease)
                WHERE toLower(pr.title) CONTAINS toLower($name)
                RETURN pr.title AS title, pr.date AS date,
                       pr.ministry AS ministry
                ORDER BY pr.date DESC
                LIMIT 10
                """,
                name=entity_name
            ).data()

            if pib_rows:
                positive.append(
                    f"Entity appears in {len(pib_rows)} PIB press release(s), "
                    "indicating official government communication activity."
                )
                evidence.append({
                    "institution": "Press Information Bureau",
                    "document":    "Official Press Releases",
                    "url":         "https://pib.gov.in",
                    "date":        pib_rows[0].get("date", ""),
                })
            else:
                findings.append({
                    "type":        "no_media_record",
                    "description": "No PIB press release mentions found for this entity.",
                    "severity":    "LOW",
                    "evidence":    [],
                })

        except Exception as e:
            logger.warning(f"[Media] Neo4j query failed: {e}")

        return {
            "investigator": self.NAME,
            "focus":        self.FOCUS,
            "findings":     findings,
            "positive":     positive,
            "evidence":     evidence,
            "confidence":   "LOW",
            "investigated_at": datetime.now().isoformat(),
        }
