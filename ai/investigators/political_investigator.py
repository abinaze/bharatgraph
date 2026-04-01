import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from datetime import datetime
from loguru import logger


class PoliticalInvestigator:

    NAME   = "Political Investigator"
    FOCUS  = "Party affiliations, electoral history, parliamentary activity, political funding"
    WEIGHT = 0.10

    def investigate(self, entity_id: str, entity_name: str,
                    session) -> dict:
        logger.info(f"[Political] Investigating: {entity_name}")
        findings = []
        positive = []
        evidence = []

        try:
            row = session.run(
                """
                MATCH (p:Politician {id: $id})
                RETURN p.party AS party, p.state AS state,
                       p.criminal_cases AS cases,
                       p.total_assets AS assets,
                       p.source AS source
                """,
                id=entity_id
            ).single()

            if row:
                if row.get("cases") and int(row["cases"] or 0) > 0:
                    findings.append({
                        "type":        "declared_criminal_cases",
                        "description": (
                            f"Entity has declared {row['cases']} criminal "
                            "case(s) in their ECI election affidavit."
                        ),
                        "severity":    "MODERATE",
                        "evidence": [
                            "Source: Election Commission of India candidate affidavit"
                        ],
                    })
                    evidence.append({
                        "institution": "Election Commission of India",
                        "document":    "Candidate Affidavit (Form 26)",
                        "url":         "https://myneta.info",
                        "date":        "",
                    })

                if row.get("party"):
                    positive.append(
                        f"Party affiliation recorded: {row['party']}. "
                        "Formal party membership provides public accountability."
                    )

            pq_rows = session.run(
                """
                MATCH (q:ParliamentaryQuestion)
                WHERE toLower(q.member_name) CONTAINS toLower($name)
                RETURN count(q) AS question_count
                """,
                name=entity_name
            ).single()

            if pq_rows and pq_rows.get("question_count", 0) > 0:
                positive.append(
                    f"Entity has {pq_rows['question_count']} parliamentary "
                    "question(s) on record indicating active legislative participation."
                )

        except Exception as e:
            logger.warning(f"[Political] Neo4j query failed: {e}")

        if not findings and not positive:
            positive.append(
                "No adverse political indicators found in available official records."
            )

        return {
            "investigator": self.NAME,
            "focus":        self.FOCUS,
            "findings":     findings,
            "positive":     positive,
            "evidence":     evidence,
            "confidence":   "HIGH" if evidence else "LOW",
            "investigated_at": datetime.now().isoformat(),
        }
