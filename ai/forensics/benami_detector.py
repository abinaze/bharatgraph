import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger

# Benami = property held by one person on behalf of another.
# We score 5 independent factors. Each contributes to 0-100 proxy score.

FACTOR_WEIGHTS = {
    "director_age_anomaly":   0.25,
    "surname_network":        0.25,
    "address_cluster":        0.20,
    "company_age_contract":   0.20,
    "single_director":        0.10,
}

YOUNG_DIRECTOR_AGE  = 25
COMPANY_AGE_DAYS    = 180   # registered < 180 days before first contract
SAME_ADDRESS_LIMIT  = 3     # 3+ companies at same address = flag


class BenamiDetector:

    def analyze(self, entity_id: str, entity_name: str,
                driver=None) -> dict:
        logger.info(f"[BenamiDetector] Analyzing {entity_name}")

        scores  = {}
        details = {}

        scores["director_age_anomaly"], details["director_age_anomaly"] = \
            self._score_director_age(entity_id, driver)

        scores["surname_network"], details["surname_network"] = \
            self._score_surname_network(entity_id, entity_name, driver)

        scores["address_cluster"], details["address_cluster"] = \
            self._score_address_cluster(entity_id, driver)

        scores["company_age_contract"], details["company_age_contract"] = \
            self._score_company_age(entity_id, driver)

        scores["single_director"], details["single_director"] = \
            self._score_single_director(entity_id, driver)

        composite = sum(
            scores[k] * FACTOR_WEIGHTS[k]
            for k in FACTOR_WEIGHTS
        ) * 100

        if composite >= 65:
            level = "HIGH"
        elif composite >= 40:
            level = "MODERATE"
        else:
            level = "LOW"

        findings = self._build_findings(scores, details, composite, level)

        positive = []
        if not findings:
            positive.append(
                "Benami analysis found no significant proxy indicators. "
                "Company structure appears consistent with independent operation."
            )

        logger.success(
            f"[BenamiDetector] {entity_name}: score={composite:.1f} "
            f"level={level} findings={len(findings)}"
        )

        return {
            "entity_id":       entity_id,
            "entity_name":     entity_name,
            "benami_score":    round(composite, 1),
            "benami_level":    level,
            "factor_scores":   {k: round(v, 3) for k, v in scores.items()},
            "factor_details":  details,
            "findings":        findings,
            "positive":        positive,
            "analyzed_at":     datetime.now().isoformat(),
        }

    # ── Factor 1: Young / anomalous directors ───────────────────────────────
    def _score_director_age(self, entity_id: str, driver) -> tuple:
        if not driver:
            return 0.3, {"young_directors": 1, "note": "sample data"}
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (p {id:$id})-[:DIRECTOR_OF]->(c:Company)
                          <-[:DIRECTOR_OF]-(d:Director)
                    WHERE d.age IS NOT NULL AND d.age < $age
                    RETURN d.name AS name, d.age AS age, c.name AS company
                    """,
                    id=entity_id, age=YOUNG_DIRECTOR_AGE
                ).data()
                if rows:
                    return min(1.0, len(rows) * 0.3), {
                        "young_directors": len(rows),
                        "examples": [
                            f"{r['name']} (age {r['age']}) at {r['company']}"
                            for r in rows[:3]
                        ],
                    }
                return 0.0, {"young_directors": 0}
        except Exception as e:
            logger.warning(f"[Benami] director_age failed: {e}")
            return 0.0, {"error": str(e)[:60]}

    # ── Factor 2: Surname network ────────────────────────────────────────────
    def _score_surname_network(self, entity_id: str,
                                entity_name: str, driver) -> tuple:
        surname = entity_name.strip().split()[-1].lower()
        if not driver:
            return 0.2, {"surname": surname, "matches": 1, "note": "sample"}
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (p {id:$id})-[:DIRECTOR_OF]->(c:Company)
                          <-[:DIRECTOR_OF]-(d)
                    WHERE toLower(d.name) ENDS WITH $surname
                      AND d.id <> $id
                    RETURN d.name AS name, c.name AS company
                    LIMIT 10
                    """,
                    id=entity_id, surname=surname
                ).data()
                if rows:
                    score = min(1.0, len(rows) * 0.2)
                    return score, {
                        "surname":  surname,
                        "matches":  len(rows),
                        "examples": [
                            f"{r['name']} at {r['company']}"
                            for r in rows[:3]
                        ],
                    }
                return 0.0, {"surname": surname, "matches": 0}
        except Exception as e:
            logger.warning(f"[Benami] surname_network failed: {e}")
            return 0.0, {"error": str(e)[:60]}

    # ── Factor 3: Address clustering ─────────────────────────────────────────
    def _score_address_cluster(self, entity_id: str,
                                driver) -> tuple:
        if not driver:
            return 0.0, {"clusters": 0}
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (p {id:$id})-[:DIRECTOR_OF]->(c:Company)
                    WHERE c.address IS NOT NULL
                    WITH c.address AS addr, count(*) AS n
                    WHERE n >= $limit
                    RETURN addr, n
                    ORDER BY n DESC LIMIT 5
                    """,
                    id=entity_id, limit=SAME_ADDRESS_LIMIT
                ).data()
                if rows:
                    max_n = max(r["n"] for r in rows)
                    score = min(1.0, (max_n - SAME_ADDRESS_LIMIT + 1) * 0.2)
                    return score, {
                        "clusters": len(rows),
                        "max_at_address": max_n,
                        "examples": [
                            f"{r['n']} companies at: {str(r['addr'])[:60]}"
                            for r in rows[:2]
                        ],
                    }
                return 0.0, {"clusters": 0}
        except Exception as e:
            logger.warning(f"[Benami] address_cluster failed: {e}")
            return 0.0, {"error": str(e)[:60]}

    # ── Factor 4: Company registered shortly before first contract ───────────
    def _score_company_age(self, entity_id: str, driver) -> tuple:
        if not driver:
            return 0.4, {"flagged_companies": 1, "note": "sample"}
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (p {id:$id})-[:DIRECTOR_OF]->(c:Company)
                          -[:WON_CONTRACT]->(ct:Contract)
                    WHERE c.registration_date IS NOT NULL
                      AND ct.order_date IS NOT NULL
                    WITH c.name AS company,
                         c.registration_date AS reg,
                         min(ct.order_date) AS first_contract
                    WHERE duration.inDays(
                            date(reg), date(first_contract)
                          ).days < $days
                    RETURN company, reg, first_contract
                    LIMIT 10
                    """,
                    id=entity_id, days=COMPANY_AGE_DAYS
                ).data()
                if rows:
                    score = min(1.0, len(rows) * 0.35)
                    return score, {
                        "flagged_companies": len(rows),
                        "examples": [
                            f"{r['company']}: registered {r['reg']}, "
                            f"first contract {r['first_contract']}"
                            for r in rows[:3]
                        ],
                    }
                return 0.0, {"flagged_companies": 0}
        except Exception as e:
            logger.warning(f"[Benami] company_age failed: {e}")
            return 0.0, {"error": str(e)[:60]}

    # ── Factor 5: Single-director companies ──────────────────────────────────
    def _score_single_director(self, entity_id: str,
                                driver) -> tuple:
        if not driver:
            return 0.5, {"single_director_cos": 1, "note": "sample"}
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (p {id:$id})-[:DIRECTOR_OF]->(c:Company)
                    WITH c
                    MATCH (c)<-[:DIRECTOR_OF]-(d)
                    WITH c.name AS company, count(d) AS directors
                    WHERE directors = 1
                    RETURN company, directors
                    LIMIT 10
                    """,
                    id=entity_id
                ).data()
                if rows:
                    score = min(1.0, len(rows) * 0.25)
                    return score, {
                        "single_director_cos": len(rows),
                        "examples": [r["company"] for r in rows[:3]],
                    }
                return 0.0, {"single_director_cos": 0}
        except Exception as e:
            logger.warning(f"[Benami] single_director failed: {e}")
            return 0.0, {"error": str(e)[:60]}

    # ── Build findings from factor scores ────────────────────────────────────
    def _build_findings(self, scores: dict, details: dict,
                         composite: float, level: str) -> list:
        findings = []

        if scores["director_age_anomaly"] > 0.2:
            n = details["director_age_anomaly"].get("young_directors", 0)
            findings.append({
                "type":        "young_director_anomaly",
                "severity":    "HIGH" if scores["director_age_anomaly"] > 0.6 else "MODERATE",
                "description": (
                    f"{n} director(s) under age {YOUNG_DIRECTOR_AGE} found in "
                    f"associated companies. Atypically young directors may indicate "
                    f"proxy appointments."
                ),
                "evidence": details["director_age_anomaly"].get("examples", []),
            })

        if scores["surname_network"] > 0.15:
            n = details["surname_network"].get("matches", 0)
            findings.append({
                "type":        "surname_network",
                "severity":    "MODERATE",
                "description": (
                    f"{n} other director(s) sharing the same surname found "
                    f"in co-directed companies. Family-name clusters may "
                    f"indicate nominee director arrangements."
                ),
                "evidence": details["surname_network"].get("examples", []),
            })

        if scores["address_cluster"] > 0.1:
            n = details["address_cluster"].get("max_at_address", 0)
            findings.append({
                "type":        "address_cluster",
                "severity":    "MODERATE",
                "description": (
                    f"Up to {n} companies share the same registered address. "
                    f"Address clustering is a structural indicator of shell "
                    f"company arrangements."
                ),
                "evidence": details["address_cluster"].get("examples", []),
            })

        if scores["company_age_contract"] > 0.2:
            n = details["company_age_contract"].get("flagged_companies", 0)
            findings.append({
                "type":        "company_formed_before_contract",
                "severity":    "HIGH",
                "description": (
                    f"{n} company/companies registered fewer than "
                    f"{COMPANY_AGE_DAYS} days before their first government "
                    f"contract. This pattern is consistent with purpose-built "
                    f"procurement vehicles."
                ),
                "evidence": details["company_age_contract"].get("examples", []),
            })

        if scores["single_director"] > 0.2:
            n = details["single_director"].get("single_director_cos", 0)
            findings.append({
                "type":        "single_director_company",
                "severity":    "LOW",
                "description": (
                    f"{n} associated company/companies have only one director. "
                    f"Single-director entities with government contracts are "
                    f"a known structural risk indicator."
                ),
                "evidence": details["single_director"].get("examples", []),
            })

        return findings


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph — Benami Detector Test (offline)")
    print("=" * 55)
    d = BenamiDetector()
    r = d.analyze("pol_001", "Narendra Modi", driver=None)
    print(f"\n  Score:    {r['benami_score']}")
    print(f"  Level:    {r['benami_level']}")
    print(f"  Findings: {len(r['findings'])}")
    for f in r["findings"]:
        print(f"    [{f['severity']}] {f['type']}")
        print(f"      {f['description'][:70]}")
    print("\nDone!")
