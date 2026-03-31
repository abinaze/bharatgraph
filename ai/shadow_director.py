import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from loguru import logger


class ShadowDirectorDetector:

    def __init__(self, driver=None):
        self.driver = driver

    def _fetch_company_metadata(self) -> list:
        if not self.driver:
            return []
        with self.driver.session() as session:
            return session.run(
                """
                MATCH (c:Company)
                RETURN c.id AS id, c.name AS name,
                       c.registered_address AS address,
                       c.registered_agent AS agent,
                       c.registration_date AS reg_date
                LIMIT 2000
                """
            ).data()

    def detect_address_reuse(self, companies: list) -> list:
        address_map = {}
        for co in companies:
            addr = (co.get("address") or "").strip().lower()
            if len(addr) < 10:
                continue
            if addr not in address_map:
                address_map[addr] = []
            address_map[addr].append(co)

        flags = []
        for addr, cos in address_map.items():
            if len(cos) >= 3:
                flags.append({
                    "pattern":         "address_reuse",
                    "address":         addr,
                    "company_count":   len(cos),
                    "companies":       [{"id": c["id"], "name": c["name"]}
                                        for c in cos],
                    "interpretation": (
                        f"{len(cos)} companies share the same registered address. "
                        "This structural pattern is associated with shell company "
                        "networks and nominee director arrangements."
                    ),
                    "detected_at":     datetime.now().isoformat(),
                })

        logger.info(f"[ShadowDirector] Address reuse: {len(flags)} cluster(s)")
        return flags

    def detect_high_directorship_count(self, threshold: int = 10) -> list:
        if not self.driver:
            return []
        with self.driver.session() as session:
            rows = session.run(
                """
                MATCH (p:Politician)-[:DIRECTOR_OF]->(c:Company)
                WITH p, count(c) AS co_count
                WHERE co_count >= $threshold
                RETURN p.id AS id, p.name AS name, co_count
                ORDER BY co_count DESC
                """,
                threshold=threshold
            ).data()

        results = []
        for row in rows:
            results.append({
                "pattern":           "high_directorship_count",
                "person_id":         row["id"],
                "person_name":       row["name"],
                "directorship_count":row["co_count"],
                "interpretation": (
                    f"{row['name']} is director of {row['co_count']} companies. "
                    "Individuals serving on an unusually high number of boards "
                    "are associated with nominee director arrangements where "
                    "de facto control is exercised by unlisted principals."
                ),
                "detected_at": datetime.now().isoformat(),
            })

        logger.info(
            f"[ShadowDirector] High directorship: {len(results)} person(s) "
            f"above threshold of {threshold}"
        )
        return results

    def run_full_detection(self) -> dict:
        companies     = self._fetch_company_metadata()
        address_flags = self.detect_address_reuse(companies)
        high_dir      = self.detect_high_directorship_count(threshold=10)

        total = len(address_flags) + len(high_dir)
        if total > 0:
            logger.warning(
                f"[ShadowDirector] {total} shadow director indicator(s) found"
            )
        else:
            logger.info("[ShadowDirector] No shadow director indicators found")

        return {
            "address_reuse_clusters":    address_flags,
            "high_directorship_persons": high_dir,
            "total_flags":               total,
            "analyzed_at":               datetime.now().isoformat(),
        }


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Shadow Director Detector Test")
    print("=" * 55)

    detector = ShadowDirectorDetector(driver=None)

    sample_companies = [
        {"id": "C001", "name": "Alpha Corp",
         "address": "12 MG Road, Flat 4B, Mumbai 400001"},
        {"id": "C002", "name": "Beta Ltd",
         "address": "12 MG Road, Flat 4B, Mumbai 400001"},
        {"id": "C003", "name": "Gamma Pvt",
         "address": "12 MG Road, Flat 4B, Mumbai 400001"},
        {"id": "C004", "name": "Delta Inc",
         "address": "45 Park Street, Kolkata 700016"},
        {"id": "C005", "name": "Epsilon Ltd",
         "address": "45 Park Street, Kolkata 700016"},
        {"id": "C006", "name": "Zeta Corp",
         "address": "45 Park Street, Kolkata 700016"},
        {"id": "C007", "name": "Eta Holdings",
         "address": "78 Anna Salai, Chennai 600002"},
    ]

    print("\n  Address Reuse Detection:")
    flags = detector.detect_address_reuse(sample_companies)
    print(f"  Clusters found: {len(flags)}")
    for f in flags:
        names = [c["name"] for c in f["companies"]]
        print(f"    Address: {f['address'][:40]}...")
        print(f"    Companies ({f['company_count']}): {names}")

    print("\nDone!")
