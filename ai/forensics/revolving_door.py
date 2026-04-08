import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, date
from loguru import logger

COOLING_OFF_DAYS = 365   # 1 year minimum expected gap
BENEFIT_WINDOW   = 730   # 2 years pre-appointment benefit window


class RevolvingDoorDetector:
    """
    Detects career transitions from regulatory/government roles
    to private-sector boards and companies that were regulated
    or benefited from the official's decisions.
    """

    def analyze(self, entity_id: str, entity_name: str,
                driver=None) -> dict:
        logger.info(f"[RevolvingDoor] Analyzing {entity_name}")

        transitions = self._fetch_transitions(entity_id, driver)
        findings    = []
        positive    = []

        for t in transitions:
            gap_days = self._day_gap(
                t.get("left_date",""), t.get("joined_date","")
            )
            if gap_days is None:
                continue

            if gap_days < COOLING_OFF_DAYS:
                findings.append({
                    "type":     "cooling_off_violation",
                    "severity": "HIGH" if gap_days < 180 else "MODERATE",
                    "description": (
                        f"{entity_name} moved from {t.get('from_role','?')} "
                        f"at {t.get('from_org','?')} to {t.get('to_role','?')} "
                        f"at {t.get('to_org','?')} in {gap_days} days — "
                        f"below the expected {COOLING_OFF_DAYS}-day cooling-off period."
                    ),
                    "evidence": [
                        f"Left: {t.get('from_org')} on {t.get('left_date')}",
                        f"Joined: {t.get('to_org')} on {t.get('joined_date')}",
                        f"Gap: {gap_days} days",
                    ],
                })

            pre_benefit = self._check_pre_employment_benefit(
                t, entity_id, driver
            )
            if pre_benefit:
                findings.append(pre_benefit)

        if not findings:
            positive.append(
                "No cooling-off violations or pre-employment benefit patterns "
                "detected in available career transition data."
            )

        logger.success(
            f"[RevolvingDoor] {entity_name}: "
            f"{len(transitions)} transitions, {len(findings)} findings"
        )
        return {
            "entity_id":         entity_id,
            "entity_name":       entity_name,
            "transitions_found": len(transitions),
            "findings":          findings,
            "positive":          positive,
            "analyzed_at":       datetime.now().isoformat(),
        }

    def _fetch_transitions(self, entity_id: str, driver) -> list:
        if not driver:
            return [
                {
                    "from_org":    "Ministry of Finance",
                    "from_role":   "Joint Secretary",
                    "left_date":   "2021-03-31",
                    "to_org":      "HDFC Bank",
                    "to_role":     "Independent Director",
                    "joined_date": "2021-07-15",
                    "entity_type": "regulator_to_private",
                },
            ]
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (p {id:$id})-[:WORKED_AT]->(org)
                    RETURN org.name AS from_org, org.role AS from_role,
                           org.left_date AS left_date, org.type AS org_type
                    LIMIT 20
                    """, id=entity_id
                ).data()
                return [dict(r) for r in rows]
        except Exception:
            return []

    def _check_pre_employment_benefit(self, transition: dict,
                                       entity_id: str, driver) -> dict | None:
        if not driver:
            return None
        try:
            to_org = transition.get("to_org","")
            with driver.session() as s:
                row = s.run(
                    """
                    MATCH (c:Company {name:$name})-[:WON_CONTRACT]->(ct:Contract)
                    WHERE ct.order_date >= $start AND ct.order_date <= $end
                    RETURN count(ct) AS n, sum(ct.amount_crore) AS total
                    """,
                    name=to_org,
                    start=transition.get("left_date","2000-01-01"),
                    end=transition.get("joined_date","2099-01-01"),
                ).single()
                if row and row.get("n",0) >= 2:
                    return {
                        "type":     "pre_employment_benefit",
                        "severity": "HIGH",
                        "description": (
                            f"{to_org} received {row['n']} government contracts "
                            f"worth Rs {row.get('total',0):.1f} Cr during the "
                            f"period between the official's departure and board appointment."
                        ),
                        "evidence": [
                            f"Contracts: {row['n']}",
                            f"Total: Rs {row.get('total',0):.1f} Cr",
                            f"Window: {transition.get('left_date')} → {transition.get('joined_date')}",
                        ],
                    }
        except Exception:
            pass
        return None

    def _day_gap(self, date_a: str, date_b: str):
        try:
            d1 = date.fromisoformat(date_a[:10])
            d2 = date.fromisoformat(date_b[:10])
            return abs((d2 - d1).days)
        except Exception:
            return None


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph — Revolving Door Test")
    print("=" * 55)
    r = RevolvingDoorDetector()
    result = r.analyze("pol_001", "Test Official", driver=None)
    print(f"\n  Transitions: {result['transitions_found']}")
    print(f"  Findings:    {len(result['findings'])}")
    for f in result["findings"]:
        print(f"  [{f['severity']}] {f['type']}: {f['description'][:70]}")
    print("\nDone!")
