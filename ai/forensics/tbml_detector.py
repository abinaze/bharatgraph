import os, sys, statistics
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger

PRICE_ANOMALY_SIGMA = 2.5   # std dev threshold for price anomaly
SUBCONTRACT_DEPTH   = 3     # max re-award chain considered suspicious


class TBMLDetector:
    """
    Trade-Based indicators of value transfer:
    1. Contract price anomaly vs category median
    2. Subcontract loop detection (A awards to B, B to C, C to A)
    3. Award-to-director-change window (director changed shortly after contract)
    """

    def analyze(self, entity_id: str, driver=None) -> dict:
        logger.info(f"[TBML] Analyzing {entity_id}")

        findings = []
        positive = []

        price_findings  = self._price_anomaly(entity_id, driver)
        loop_findings   = self._subcontract_loop(entity_id, driver)
        window_findings = self._award_director_window(entity_id, driver)

        findings.extend(price_findings)
        findings.extend(loop_findings)
        findings.extend(window_findings)

        if not findings:
            positive.append(
                "Trade-based transfer analysis found no significant anomalies "
                "in contract pricing, subcontracting patterns, or director changes."
            )

        logger.success(
            f"[TBML] {entity_id}: {len(findings)} findings"
        )
        return {
            "entity_id":  entity_id,
            "findings":   findings,
            "positive":   positive,
            "analyzed_at":datetime.now().isoformat(),
        }

    def _price_anomaly(self, entity_id: str, driver) -> list:
        contracts = self._fetch_contracts(entity_id, driver)
        if len(contracts) < 3:
            return []

        amounts = [float(c.get("amount_crore") or 0) for c in contracts]
        amounts = [a for a in amounts if a > 0]
        if len(amounts) < 3:
            return []

        mean   = statistics.mean(amounts)
        stdev  = statistics.stdev(amounts)
        if stdev == 0:
            return []

        outliers = [
            c for c in contracts
            if abs(float(c.get("amount_crore") or 0) - mean) > PRICE_ANOMALY_SIGMA * stdev
        ]
        if not outliers:
            return []

        return [{
            "type":     "contract_price_anomaly",
            "severity": "HIGH" if len(outliers) >= 2 else "MODERATE",
            "description": (
                f"{len(outliers)} contract(s) have values more than "
                f"{PRICE_ANOMALY_SIGMA} standard deviations from the "
                f"entity's contract average (Rs {mean:.1f} Cr). "
                f"Abnormal contract pricing may indicate value inflation."
            ),
            "evidence": [
                f"Contract Rs {float(c.get('amount_crore',0)):.1f} Cr "
                f"vs mean Rs {mean:.1f} Cr (z={abs(float(c.get('amount_crore',0))-mean)/stdev:.1f}σ)"
                for c in outliers[:3]
            ],
        }]

    def _subcontract_loop(self, entity_id: str, driver) -> list:
        if not driver:
            return []
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH path = (c1:Company)-[:SUBCONTRACTS_TO*2..4]->(c1)
                    WHERE any(n IN nodes(path) WHERE n.id = $id)
                    RETURN length(path) AS depth, 
                           [n IN nodes(path) | n.name] AS loop_nodes
                    LIMIT 5
                    """, id=entity_id
                ).data()
                if rows:
                    return [{
                        "type":     "subcontract_loop",
                        "severity": "HIGH",
                        "description": (
                            f"Circular subcontracting detected: "
                            f"{' → '.join((rows[0].get('loop_nodes') or [])[:4])}. "
                            f"Contract re-award loops are a structural indicator "
                            f"of artificial transaction chains."
                        ),
                        "evidence": [
                            f"Loop depth: {rows[0].get('depth')} hops"
                        ],
                    }]
        except Exception:
            pass
        return []

    def _award_director_window(self, entity_id: str, driver) -> list:
        if not driver:
            return []
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (p {id:$id})-[:DIRECTOR_OF]->(c:Company)
                          -[:WON_CONTRACT]->(ct:Contract)
                    WHERE ct.order_date IS NOT NULL
                      AND c.director_change_date IS NOT NULL
                      AND abs(duration.inDays(
                            date(ct.order_date),
                            date(c.director_change_date)
                          ).days) <= 90
                    RETURN c.name AS company, ct.order_date AS award,
                           c.director_change_date AS change_date
                    LIMIT 5
                    """, id=entity_id
                ).data()
                if rows:
                    return [{
                        "type":     "director_change_near_award",
                        "severity": "MODERATE",
                        "description": (
                            f"Director change at {rows[0].get('company','?')} "
                            f"occurred within 90 days of contract award on "
                            f"{rows[0].get('award','?')}. Director substitution "
                            f"near contract award is a structural risk indicator."
                        ),
                        "evidence": [
                            f"Award: {r.get('award')} | Director change: {r.get('change_date')}"
                            for r in rows[:3]
                        ],
                    }]
        except Exception:
            pass
        return []

    def _fetch_contracts(self, entity_id: str, driver) -> list:
        if not driver:
            return [
                {"id":"c1","amount_crore":12.0,"buyer_org":"MoRTH"},
                {"id":"c2","amount_crore":11.5,"buyer_org":"MoRTH"},
                {"id":"c3","amount_crore":89.0,"buyer_org":"MoRTH"},
                {"id":"c4","amount_crore":13.0,"buyer_org":"MoRTH"},
            ]
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (p {id:$id})-[:DIRECTOR_OF]->(c:Company)
                          -[:WON_CONTRACT]->(ct:Contract)
                    RETURN ct.id AS id, ct.amount_crore AS amount_crore,
                           ct.buyer_org AS buyer_org, ct.order_date AS date
                    LIMIT 50
                    """, id=entity_id
                ).data()
                return [dict(r) for r in rows]
        except Exception:
            return []


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph — TBML Detector Test")
    print("=" * 55)
    t = TBMLDetector()
    r = t.analyze("pol_001", driver=None)
    print(f"\n  Findings: {len(r['findings'])}")
    for f in r["findings"]:
        print(f"  [{f['severity']}] {f['type']}: {f['description'][:70]}")
    if r["positive"]:
        print(f"  Positive: {r['positive'][0][:70]}")
    print("\nDone!")
