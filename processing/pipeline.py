"""
BharatGraph - Full Data Pipeline
Runs ALL 20 scrapers in parallel threads, cleans, resolves, saves.

Usage:
    python -m processing.pipeline                          # all scrapers
    python -m processing.pipeline --scrapers cag,gem,pib  # specific
    python -m processing.pipeline --parallel              # force parallel
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json, argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from loguru import logger
from processing.cleaner import NameCleaner
from processing.entity_resolver import EntityResolver


class BharatGraphPipeline:

    def __init__(self):
        self.cleaner   = NameCleaner()
        self.resolver  = EntityResolver(threshold=0.65)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("data/processed", exist_ok=True)
        os.makedirs("data/samples",   exist_ok=True)
        logger.info("[Pipeline] Initialized")

    # ── Scrapers ─────────────────────────────────────────────────────────────

    def run_datagov(self) -> list:
        try:
            from scrapers.datagov_scraper import DataGovScraper
            data    = DataGovScraper().fetch_all_datasets(save=False)
            records = []
            for ds_name, ds in data.items():
                for r in ds.get("records", []):
                    r["_source"]  = "datagov"
                    r["_dataset"] = ds_name
                    records.append(r)
            logger.success(f"[Pipeline] DataGov: {len(records)} records")
            return records
        except Exception as e:
            logger.error(f"[Pipeline] DataGov failed: {e}")
            return []

    def run_cag(self) -> list:
        try:
            from scrapers.cag_scraper import CAGScraper
            reports = CAGScraper().fetch_report_list(limit=50)
            for r in reports: r["_source"] = "cag"
            logger.success(f"[Pipeline] CAG: {len(reports)} reports")
            return reports
        except Exception as e:
            logger.error(f"[Pipeline] CAG failed: {e}")
            return []

    def run_gem(self) -> list:
        try:
            from scrapers.gem_scraper import GeMScraper
            contracts = GeMScraper().fetch_contracts_by_ministry(limit=50)
            cleaned   = []
            for c in contracts:
                c["_source"] = "gem"
                cleaned.append(self.cleaner.clean_record(c, "contract"))
            logger.success(f"[Pipeline] GeM: {len(cleaned)} contracts")
            return cleaned
        except Exception as e:
            logger.error(f"[Pipeline] GeM failed: {e}")
            return []

    def run_myneta(self) -> list:
        try:
            from scrapers.myneta_scraper import MyNetaScraper
            candidates = MyNetaScraper().fetch_sample_data(save=False)
            cleaned    = []
            for c in candidates:
                c["_source"] = "myneta"
                cleaned.append(self.cleaner.clean_record(c, "person"))
            logger.success(f"[Pipeline] MyNeta: {len(cleaned)} candidates")
            return cleaned
        except Exception as e:
            logger.error(f"[Pipeline] MyNeta failed: {e}")
            return []

    def run_mca(self) -> list:
        try:
            from scrapers.mca_scraper import MCAScraper
            result    = MCAScraper().fetch_and_save_sample(save=False)
            companies = []
            for state, recs in result.items():
                for r in recs:
                    r["_source"] = "mca"
                    companies.append(self.cleaner.clean_record(r, "company"))
            logger.success(f"[Pipeline] MCA: {len(companies)} companies")
            return companies
        except Exception as e:
            logger.error(f"[Pipeline] MCA failed: {e}")
            return []

    def run_pib(self) -> list:
        try:
            from scrapers.pib_scraper import PIBScraper
            articles = PIBScraper().fetch_all_feeds(save=False)
            for a in articles: a["_source"] = "pib"
            logger.success(f"[Pipeline] PIB: {len(articles)} articles")
            return articles
        except Exception as e:
            logger.error(f"[Pipeline] PIB failed: {e}")
            return []

    def run_loksabha(self) -> list:
        try:
            from scrapers.loksabha_scraper import LokSabhaScraper
            records = LokSabhaScraper().fetch_questions(limit=50)
            for r in records: r["_source"] = "loksabha"
            logger.success(f"[Pipeline] LokSabha: {len(records)} records")
            return records
        except Exception as e:
            logger.warning(f"[Pipeline] LokSabha failed: {e}")
            return []

    def run_sebi(self) -> list:
        try:
            from scrapers.sebi_scraper import SEBIScraper
            records = SEBIScraper().fetch_enforcement_orders(limit=30)
            for r in records: r["_source"] = "sebi"
            logger.success(f"[Pipeline] SEBI: {len(records)} orders")
            return records
        except Exception as e:
            logger.warning(f"[Pipeline] SEBI failed: {e}")
            return []

    def run_ed(self) -> list:
        try:
            from scrapers.ed_scraper import EDScraper
            records = EDScraper().fetch_press_releases(limit=30)
            for r in records: r["_source"] = "ed"
            logger.success(f"[Pipeline] ED: {len(records)} press releases")
            return records
        except Exception as e:
            logger.warning(f"[Pipeline] ED failed: {e}")
            return []

    def run_cvc(self) -> list:
        try:
            from scrapers.cvc_scraper import CVCScraper
            records = CVCScraper().fetch_circulars(limit=30)
            for r in records: r["_source"] = "cvc"
            logger.success(f"[Pipeline] CVC: {len(records)} records")
            return records
        except Exception as e:
            logger.warning(f"[Pipeline] CVC failed: {e}")
            return []

    def run_njdg(self) -> list:
        try:
            from scrapers.njdg_scraper import NJDGScraper
            records = NJDGScraper().fetch_pendency_stats()
            for r in records: r["_source"] = "njdg"
            logger.success(f"[Pipeline] NJDG: {len(records)} records")
            return records
        except Exception as e:
            logger.warning(f"[Pipeline] NJDG failed: {e}")
            return []

    def run_electoral_bond(self) -> list:
        try:
            from scrapers.electoral_bond_scraper import ElectoralBondScraper
            records = ElectoralBondScraper().fetch_bond_data()
            for r in records: r["_source"] = "electoral_bond"
            logger.success(f"[Pipeline] Electoral Bonds: {len(records)} records")
            return records
        except Exception as e:
            logger.warning(f"[Pipeline] Electoral Bond failed: {e}")
            return []

    def run_icij(self) -> list:
        try:
            from scrapers.icij_scraper import ICIJScraper
            entities = ["Adani", "Reliance", "Tata", "Birla", "Ambani"]
            records  = []
            scraper  = ICIJScraper()
            for name in entities:
                records.extend(scraper.search_entity(name))
            for r in records: r["_source"] = "icij"
            logger.success(f"[Pipeline] ICIJ: {len(records)} matches")
            return records
        except Exception as e:
            logger.warning(f"[Pipeline] ICIJ failed: {e}")
            return []

    def run_opensanctions(self) -> list:
        try:
            from scrapers.opensanctions_scraper import OpenSanctionsScraper
            entities = ["Modi", "Gandhi", "Adani", "Choksi", "Mallya"]
            records  = []
            scraper  = OpenSanctionsScraper()
            for name in entities:
                records.extend(scraper.search_entity(name))
            for r in records: r["_source"] = "opensanctions"
            logger.success(f"[Pipeline] OpenSanctions: {len(records)} matches")
            return records
        except Exception as e:
            logger.warning(f"[Pipeline] OpenSanctions failed: {e}")
            return []

    def run_wikidata(self) -> list:
        try:
            from scrapers.wikidata_scraper import WikidataScraper
            politicians = [
                "Narendra Modi", "Rahul Gandhi", "Amit Shah",
                "Arvind Kejriwal", "Mamata Banerjee", "Nitish Kumar",
                "Yogi Adityanath", "Shashi Tharoor", "Anurag Thakur",
            ]
            records = WikidataScraper().enrich_entity_list(politicians)
            for r in records: r["_source"] = "wikidata"
            logger.success(f"[Pipeline] Wikidata: {len(records)} enrichments")
            return records
        except Exception as e:
            logger.warning(f"[Pipeline] Wikidata failed: {e}")
            return []

    def run_ibbi(self) -> list:
        try:
            from scrapers.ibbi_scraper import IBBIScraper
            records = IBBIScraper().fetch_orders(limit=30)
            for r in records: r["_source"] = "ibbi"
            logger.success(f"[Pipeline] IBBI: {len(records)} orders")
            return records
        except Exception as e:
            logger.warning(f"[Pipeline] IBBI failed: {e}")
            return []

    def run_ngo_darpan(self) -> list:
        try:
            from scrapers.ngo_darpan_scraper import NGODarpanScraper
            records = NGODarpanScraper().fetch_ngo_list(limit=30)
            for r in records: r["_source"] = "ngo_darpan"
            logger.success(f"[Pipeline] NGO Darpan: {len(records)} NGOs")
            return records
        except Exception as e:
            logger.warning(f"[Pipeline] NGO Darpan failed: {e}")
            return []

    def run_cppp(self) -> list:
        try:
            from scrapers.cppp_scraper import CPPPScraper
            records = CPPPScraper().fetch_tenders(limit=30)
            for r in records: r["_source"] = "cppp"
            logger.success(f"[Pipeline] CPPP: {len(records)} tenders")
            return records
        except Exception as e:
            logger.warning(f"[Pipeline] CPPP failed: {e}")
            return []

    def run_ncrb(self) -> list:
        try:
            from scrapers.ncrb_scraper import NCRBScraper
            records = NCRBScraper().fetch_crime_statistics(limit=20)
            for r in records: r["_source"] = "ncrb"
            logger.success(f"[Pipeline] NCRB: {len(records)} records")
            return records
        except Exception as e:
            logger.warning(f"[Pipeline] NCRB failed: {e}")
            return []

    def run_lgd(self) -> list:
        try:
            from scrapers.lgd_scraper import LGDScraper
            records = LGDScraper().fetch_state_codes()
            for r in records: r["_source"] = "lgd"
            logger.success(f"[Pipeline] LGD: {len(records)} records")
            return records
        except Exception as e:
            logger.warning(f"[Pipeline] LGD failed: {e}")
            return []

    def _get_runner_map(self):
        return {
            "datagov":        self.run_datagov,
            "cag":            self.run_cag,
            "gem":            self.run_gem,
            "myneta":         self.run_myneta,
            "mca":            self.run_mca,
            "pib":            self.run_pib,
            "loksabha":       self.run_loksabha,
            "sebi":           self.run_sebi,
            "ed":             self.run_ed,
            "cvc":            self.run_cvc,
            "njdg":           self.run_njdg,
            "electoral_bond": self.run_electoral_bond,
            "icij":           self.run_icij,
            "opensanctions":  self.run_opensanctions,
            "wikidata":       self.run_wikidata,
            "ibbi":           self.run_ibbi,
            "ngo_darpan":     self.run_ngo_darpan,
            "cppp":           self.run_cppp,
            "ncrb":           self.run_ncrb,
            "lgd":            self.run_lgd,
        }

    def find_politician_company_links(self, politicians, companies):
        logger.info("[Pipeline] Finding politician-company links...")
        matches = self.resolver.cross_dataset_match(
            politicians, companies,
            name_field_a="name", name_field_b="name"
        )
        if matches:
            logger.warning(f"[Pipeline] {len(matches)} politician-company links found!")
        return matches

    def save(self, data: dict) -> str:
        filepath = f"data/processed/pipeline_{self.timestamp}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.success(f"[Pipeline] Saved to {filepath}")
        return filepath

    def run(self, scrapers: list = None, parallel: bool = True) -> dict:
        runner_map   = self._get_runner_map()
        all_scrapers = list(runner_map.keys())
        to_run = scrapers if scrapers else all_scrapers
        to_run = [s.strip() for s in to_run if s.strip() in runner_map]
        if not to_run:
            to_run = all_scrapers

        logger.info(f"[Pipeline] Starting {len(to_run)} scrapers "
                    f"({'parallel' if parallel else 'sequential'}): {to_run}")
        start = datetime.now()
        raw   = {}

        if parallel and len(to_run) > 1:
            with ThreadPoolExecutor(max_workers=6) as pool:
                futures = {pool.submit(runner_map[name]): name for name in to_run}
                for future in as_completed(futures):
                    name = futures[future]
                    try:
                        raw[name] = future.result()
                    except Exception as e:
                        logger.error(f"[Pipeline] {name} thread failed: {e}")
                        raw[name] = []
        else:
            for name in to_run:
                raw[name] = runner_map[name]()

        # BUG-13 FIX: entity resolver now runs on ALL data sources that could
        # contain Indian persons/companies, not just myneta+mca.
        # ICIJ and OpenSanctions entities are now resolved against politicians
        # and companies so cross-dataset evidence chains are created.
        politicians = (
            raw.get("myneta",       []) +
            raw.get("wikidata",     []) +
            raw.get("opensanctions",[]) +    # BUG-13 FIX: added
            raw.get("icij",         [])      # BUG-13 FIX: added
        )
        companies = (
            raw.get("mca",  []) +
            raw.get("ibbi", [])             # BUG-13 FIX: added
        )
        links = []
        if politicians and companies:
            politicians = self.resolver.resolve_dataset(politicians, "name")
            companies   = self.resolver.resolve_dataset(companies,   "name")
            links       = self.find_politician_company_links(politicians, companies)

        duration   = (datetime.now() - start).seconds
        per_source = {name: len(records) for name, records in raw.items()}

        summary = {
            "scrapers_run":       to_run,
            "duration_seconds":   duration,
            "parallel":           parallel,
            "total_raw_records":  sum(len(v) for v in raw.values()),
            "per_source":         per_source,
            "politicians_found":  len(raw.get("myneta", [])),
            "companies_found":    len(raw.get("mca", [])),
            "contracts_found":    len(raw.get("gem", [])),
            "cag_reports_found":  len(raw.get("cag", [])),
            "pib_articles_found": len(raw.get("pib", [])),
            "politician_co_links":len(links),
        }

        logger.info(f"[Pipeline] Done in {duration}s — "
                    f"{summary['total_raw_records']} total records")

        results = {
            "raw":     raw,
            "links":   links,
            "summary": summary,
            "run_at":  start.isoformat(),
        }
        results["saved_to"] = self.save(results)
        return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BharatGraph Full Pipeline (20 scrapers)")
    parser.add_argument("--scrapers",   type=str, default=None)
    parser.add_argument("--parallel",   action="store_true", default=True)
    parser.add_argument("--sequential", action="store_true", default=False)
    args     = parser.parse_args()
    scrapers = args.scrapers.split(",") if args.scrapers else None
    parallel = not args.sequential

    results = BharatGraphPipeline().run(scrapers=scrapers, parallel=parallel)
    s = results["summary"]
    print(f"\n{'='*55}\nPIPELINE SUMMARY\n{'='*55}")
    print(f"  Scrapers run:   {len(s['scrapers_run'])}")
    print(f"  Duration:       {s['duration_seconds']}s")
    print(f"  Total records:  {s['total_raw_records']}")
    for src, n in sorted(s["per_source"].items(), key=lambda x: -x[1]):
        if n > 0:
            print(f"    {src:<20} {n}")
    print(f"  Saved to: {results.get('saved_to')}")
    print("=" * 55)
