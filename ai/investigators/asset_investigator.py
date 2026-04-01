import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from datetime import datetime
from loguru import logger


class AssetInvestigator:

    NAME   = "Asset Investigator"
    FOCUS  = "Declared assets, liabilities, growth across election cycles, property records"
    WEIGHT = 0.10

    def investigate(self, entity_id: str, entity_name: str,
                    session) -> dict:
        logger.info(f"[Asset] Investigating: {entity_name}")
        findings = []
        positive = []
        evidence = []

        try:
            row = session.run(
                """
                MATCH (p:Politician {id: $id})
                RETURN p.total_assets AS assets,
                       p.total_liabilities AS liabilities,
                       p.education AS education
                """,
                id=entity_id
            ).single()

            if row:
                assets_str = str(row.get("assets") or "")
                liab_str   = str(row.get("liabilities") or "")

                if assets_str and any(c.isdigit() for c in assets_str):
                    evidence.append({
                        "institution": "Election Commission of India",
                        "document":    "Candidate Affidavit — Asset Declaration",
                        "url":         "https://myneta.info",
                        "date":        "",
                    })
                    positive.append(
                        f"Asset declaration available from ECI affidavit: "
                        f"{assets_str}. Multi-cycle comparison requires "
                        "data from consecutive election affidavits."
                    )

                if row.get("education"):
                    positive.append(
                        f"Educational qualification declared: {row['education']}."
                    )

        except Exception as e:
            logger.warning(f"[Asset] Neo4j query failed: {e}")

        if not findings and not positive:
            findings.append({
                "type":        "insufficient_asset_data",
                "description": "Asset declaration data not available for this entity.",
                "severity":    "LOW",
                "evidence":    [],
            })

        return {
            "investigator": self.NAME,
            "focus":        self.FOCUS,
            "findings":     findings,
            "positive":     positive,
            "evidence":     evidence,
            "confidence":   "MODERATE" if evidence else "LOW",
            "investigated_at": datetime.now().isoformat(),
        }
