import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger

PATTERN_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "processed",
    f"pattern_candidates_{datetime.now().strftime('%Y%m%d')}.json"
)

KNOWN_PATTERNS = [
    {
        "id":          "politician_company_contract",
        "description": "Politician → directs Company → wins Contract",
        "cypher":      "MATCH (p:Politician)-[:DIRECTOR_OF]->(c:Company)-[:WON_CONTRACT]->(ct:Contract) RETURN count(*) AS n",
        "threshold":   3,
    },
    {
        "id":          "audit_flagged_ministry_contract",
        "description": "Ministry with CAG flag → Company contract",
        "cypher":      "MATCH (a:AuditReport)-[:AUDITS]->(m:Ministry)<-[:AWARDED_BY]-(ct:Contract) RETURN count(*) AS n",
        "threshold":   2,
    },
    {
        "id":          "high_value_single_vendor",
        "description": "Single company wins > 3 contracts from same buyer",
        "cypher":      "MATCH (c:Company)-[:WON_CONTRACT]->(ct:Contract) WITH c, ct.buyer_org AS buyer, count(*) AS n WHERE n >= 3 RETURN count(*) AS n",
        "threshold":   1,
    },
]


class PatternLearner:

    def __init__(self, driver=None):
        self.driver = driver

    def discover_patterns(self) -> dict:
        logger.info("[PatternLearner] Running pattern discovery...")
        found = []

        for pattern in KNOWN_PATTERNS:
            count = self._check_pattern(pattern)
            if count >= pattern["threshold"]:
                found.append({
                    "pattern_id":  pattern["id"],
                    "description": pattern["description"],
                    "count":       count,
                    "threshold":   pattern["threshold"],
                    "status":      "candidate",
                    "found_at":    datetime.now().isoformat(),
                })
                logger.info(
                    f"[PatternLearner] Found: {pattern['id']} "
                    f"(count={count})"
                )

        new_patterns = self._discover_new_motifs()
        found.extend(new_patterns)

        result = {
            "run_date":       datetime.now().isoformat(),
            "patterns_found": len(found),
            "candidates":     found,
        }

        if found:
            os.makedirs(os.path.dirname(PATTERN_FILE), exist_ok=True)
            with open(PATTERN_FILE, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logger.success(
                f"[PatternLearner] {len(found)} candidates → "
                f"{os.path.basename(PATTERN_FILE)}"
            )

        return result

    def _check_pattern(self, pattern: dict) -> int:
        if not self.driver:
            return pattern["threshold"]
        try:
            with self.driver.session() as session:
                row = session.run(pattern["cypher"]).single()
                return int(row["n"]) if row else 0
        except Exception as e:
            logger.warning(f"[PatternLearner] Query failed: {e}")
            return 0

    def _discover_new_motifs(self) -> list:
        if not self.driver:
            return []
        try:
            with self.driver.session() as session:
                rows = session.run(
                    """
                    MATCH (p:Politician)-[:DIRECTOR_OF]->(c:Company)
                    WITH p, count(c) AS company_count
                    WHERE company_count >= 5
                    RETURN p.name AS name, company_count
                    ORDER BY company_count DESC LIMIT 5
                    """
                ).data()
                motifs = []
                for row in rows:
                    motifs.append({
                        "pattern_id":  "high_directorship_count",
                        "description": (
                            f"{row['name']} holds directorships in "
                            f"{row['company_count']} companies"
                        ),
                        "count":       row["company_count"],
                        "threshold":   5,
                        "status":      "candidate",
                        "found_at":    datetime.now().isoformat(),
                    })
                return motifs
        except Exception:
            return []


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Pattern Learner Test")
    print("=" * 55)
    learner = PatternLearner(driver=None)
    result  = learner.discover_patterns()
    print(f"\n  Patterns found: {result['patterns_found']}")
    for c in result["candidates"]:
        print(f"    [{c['count']}x] {c['description'][:60]}")
    print("\nDone!")
