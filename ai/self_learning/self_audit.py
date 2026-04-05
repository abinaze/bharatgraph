import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger

AUDIT_RESULTS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "processed", "scraper_health.json"
)

SCRAPERS = [
    "datagov_scraper", "pib_scraper", "myneta_scraper", "mca_scraper",
    "cag_scraper", "gem_scraper", "icij_scraper", "loksabha_scraper",
    "sebi_scraper", "electoral_bond_scraper", "opensanctions_scraper",
    "wikidata_scraper", "njdg_scraper", "ed_scraper", "cvc_scraper",
    "ncrb_scraper", "lgd_scraper", "ibbi_scraper", "ngo_darpan_scraper",
    "cppp_scraper",
]


class SelfAudit:

    def run(self, timeout_secs: int = 30) -> dict:
        logger.info(f"[SelfAudit] Running health check on {len(SCRAPERS)} scrapers")
        results   = {}
        alerts    = []
        passed    = 0
        failed    = 0

        for scraper_name in SCRAPERS:
            result = self._test_scraper(scraper_name, timeout_secs)
            results[scraper_name] = result
            if result["status"] == "pass":
                passed += 1
            else:
                failed += 1
                alerts.append({
                    "scraper": scraper_name,
                    "issue":   result["issue"],
                    "status":  result["status"],
                })
                logger.warning(
                    f"[SelfAudit] ALERT: {scraper_name} — {result['issue']}"
                )

        summary = {
            "run_date":      datetime.now().isoformat(),
            "total":         len(SCRAPERS),
            "passed":        passed,
            "failed":        failed,
            "alerts":        alerts,
            "scraper_results": results,
        }

        os.makedirs(os.path.dirname(AUDIT_RESULTS_FILE), exist_ok=True)
        with open(AUDIT_RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        if alerts:
            logger.warning(
                f"[SelfAudit] {len(alerts)} scrapers need attention. "
                f"See {AUDIT_RESULTS_FILE}"
            )
        else:
            logger.success("[SelfAudit] All scrapers healthy")

        return summary

    def _test_scraper(self, name: str, timeout: int) -> dict:
        module_path = f"scrapers.{name}"
        start       = time.time()
        try:
            import importlib
            mod = importlib.import_module(module_path)
            elapsed = round(time.time() - start, 2)

            class_map = {
                "datagov_scraper":         "DataGovScraper",
                "pib_scraper":             "PIBScraper",
                "myneta_scraper":          "MyNetaScraper",
                "mca_scraper":             "MCAScraper",
                "cag_scraper":             "CAGScraper",
                "gem_scraper":             "GeMScraper",
                "wikidata_scraper":        "WikidataScraper",
                "njdg_scraper":            "NJDGScraper",
                "ed_scraper":              "EDScraper",
                "cvc_scraper":             "CVCScraper",
                "ncrb_scraper":            "NCRBScraper",
                "lgd_scraper":             "LGDScraper",
                "ibbi_scraper":            "IBBIScraper",
                "ngo_darpan_scraper":      "NGODarpanScraper",
                "cppp_scraper":            "CPPPScraper",
                "icij_scraper":            "ICIJScraper",
                "loksabha_scraper":        "LokSabhaScraper",
                "sebi_scraper":            "SEBIScraper",
                "electoral_bond_scraper":  "ElectoralBondScraper",
                "opensanctions_scraper":   "OpenSanctionsScraper",
            }

            cls_name = class_map.get(name)
            if cls_name and hasattr(mod, cls_name):
                return {"status":"pass","elapsed_s":elapsed,"issue":None}
            return {"status":"warn","elapsed_s":elapsed,
                    "issue":"Class not found in module"}
        except Exception as e:
            elapsed = round(time.time() - start, 2)
            return {"status":"fail","elapsed_s":elapsed,"issue":str(e)[:120]}


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Self Audit Test")
    print("=" * 55)
    audit  = SelfAudit()
    result = audit.run(timeout_secs=10)
    print(f"\n  Total:   {result['total']}")
    print(f"  Passed:  {result['passed']}")
    print(f"  Failed:  {result['failed']}")
    if result["alerts"]:
        print(f"\n  Alerts:")
        for a in result["alerts"][:5]:
            print(f"    [{a['status']}] {a['scraper']}: {a['issue'][:60]}")
    print("\nDone!")
