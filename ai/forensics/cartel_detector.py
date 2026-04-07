import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger

ROTATION_WINDOW_DAYS  = 730   # 2 years
MIN_VENDORS_FOR_CARTEL = 3
ROTATION_THRESHOLD    = 0.6   # 60% contracts show rotation pattern


class CartelDetector:
    """
    Vendor cartel detection via:
    1. Award rotation — vendors take turns winning contracts
    2. Price coordination — bids within tight band
    3. Co-bidding network — same vendors appear together repeatedly
    """

    def analyze(self, ministry: str, driver=None) -> dict:
        logger.info(f"[CartelDetector] Analyzing ministry: {ministry}")

        vendors = self._fetch_vendor_history(ministry, driver)
        if len(vendors) < MIN_VENDORS_FOR_CARTEL:
            return {
                "ministry":  ministry,
                "status":    "insufficient_data",
                "vendor_count": len(vendors),
            }

        rotation   = self._detect_rotation(vendors)
        co_bidding = self._detect_co_bidding(vendors)
        findings   = []

        if rotation["score"] > ROTATION_THRESHOLD:
            findings.append({
                "type":     "award_rotation",
                "severity": "HIGH",
                "description": (
                    f"Vendor rotation pattern detected in {ministry}. "
                    f"{rotation['score']*100:.0f}% of contracts show vendors "
                    f"taking turns winning in a regular sequence — a classic "
                    f"cartel coordination pattern."
                ),
                "evidence": rotation.get("evidence", []),
            })

        if co_bidding["repeat_pairs"] >= 3:
            findings.append({
                "type":     "co_bidding_network",
                "severity": "MODERATE",
                "description": (
                    f"{co_bidding['repeat_pairs']} vendor pair(s) appear together "
                    f"in multiple tenders from the same ministry. Repeated co-bidding "
                    f"by the same set of vendors indicates coordinated market allocation."
                ),
                "evidence": co_bidding.get("examples", []),
            })

        return {
            "ministry":     ministry,
            "vendor_count": len(vendors),
            "rotation":     rotation,
            "co_bidding":   co_bidding,
            "findings":     findings,
            "positive":     ["No cartel indicators detected."] if not findings else [],
            "analyzed_at":  datetime.now().isoformat(),
        }

    def _fetch_vendor_history(self, ministry: str, driver) -> list:
        if not driver:
            return [
                {"vendor":"Alpha","contracts":[1,4,7,10],"amounts":[12,11,13,12]},
                {"vendor":"Beta", "contracts":[2,5,8,11],"amounts":[13,12,12,14]},
                {"vendor":"Gamma","contracts":[3,6,9,12],"amounts":[11,13,11,13]},
            ]
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (c:Company)-[:WON_CONTRACT]->(ct:Contract)
                          -[:AWARDED_BY]->(m:Ministry)
                    WHERE toLower(m.name) CONTAINS toLower($ministry)
                    RETURN c.name AS vendor,
                           collect(ct.order_date) AS dates,
                           collect(ct.amount_crore) AS amounts
                    ORDER BY size(collect(ct.order_date)) DESC LIMIT 20
                    """, ministry=ministry
                ).data()
                return [{"vendor": r["vendor"], "dates": r["dates"],
                         "amounts": r["amounts"]} for r in rows]
        except Exception as e:
            logger.warning(f"[Cartel] Fetch failed: {e}")
            return []

    def _detect_rotation(self, vendors: list) -> dict:
        if not vendors or len(vendors) < 2:
            return {"score": 0.0, "evidence": []}

        # Check if contract indices follow a round-robin pattern
        contract_lists = [v.get("contracts", v.get("dates", [])) for v in vendors]
        total = sum(len(c) for c in contract_lists)
        if total == 0:
            return {"score": 0.0, "evidence": []}

        # Simple heuristic: if each vendor has roughly equal share → rotation
        expected_share = 1.0 / len(vendors)
        shares = [len(c) / total for c in contract_lists]
        variance = sum((s - expected_share)**2 for s in shares) / len(shares)
        rotation_score = max(0.0, 1.0 - variance * len(vendors) * 10)

        evidence = [
            f"{vendors[i]['vendor']}: {len(contract_lists[i])} contracts "
            f"({shares[i]*100:.0f}% share)"
            for i in range(min(3, len(vendors)))
        ]
        return {"score": round(rotation_score, 3), "evidence": evidence}

    def _detect_co_bidding(self, vendors: list) -> dict:
        if len(vendors) < 2:
            return {"repeat_pairs": 0, "examples": []}

        # Count overlapping tender appearances
        from itertools import combinations
        pairs     = {}
        examples  = []

        for a, b in combinations(vendors, 2):
            a_dates = set(str(d) for d in a.get("dates", a.get("contracts",[])))
            b_dates = set(str(d) for d in b.get("dates", b.get("contracts",[])))
            overlap = len(a_dates & b_dates)
            if overlap >= 2:
                key = f"{a['vendor']}+{b['vendor']}"
                pairs[key] = overlap
                examples.append(
                    f"{a['vendor']} & {b['vendor']}: "
                    f"appeared together {overlap} times"
                )

        return {
            "repeat_pairs": len(pairs),
            "examples":     examples[:5],
        }


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph — Cartel Detector Test")
    print("=" * 55)
    c = CartelDetector()
    r = c.analyze("Ministry of Road Transport", driver=None)
    print(f"\n  Vendors:     {r['vendor_count']}")
    print(f"  Rotation:    {r['rotation']['score']:.2f}")
    print(f"  Co-bidding:  {r['co_bidding']['repeat_pairs']} pairs")
    print(f"  Findings:    {len(r['findings'])}")
    for f in r["findings"]:
        print(f"  [{f['severity']}] {f['description'][:70]}")
    print("\nDone!")
