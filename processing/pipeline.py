"""
BharatGraph - Data Pipeline
Orchestrates all scrapers -> clean -> resolve -> save.

Usage:
    python -m processing.pipeline
    python -m processing.pipeline --scrapers datagov,cag,gem
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import argparse
from datetime import datetime
from loguru import logger
from .cleaner import NameCleaner
from .entity_resolver import EntityResolver


class BharatGraphPipeline:
    """Full data pipeline: scrape -> clean -> resolve -> save."""

    def __init__(self):
        self.cleaner   = NameCleaner()
        self.resolver  = EntityResolver(threshold=0.65)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("data/processed", exist_ok=True)
        os.makedirs("data/samples",   exist_ok=True)
        logger.info("[Pipeline] Initialized")

    def run_datagov(self) -> list:
        logger.info("[Pipeline] Running DataGov scraper...")
        try:
            from scrapers.datagov_scraper import DataGovScraper
            data = DataGovScraper().fetch_all_datasets(save=False)
            records = []
            for ds_name, ds in data.items():
                for r in ds.get("records", []):
                    r["_source"] = "datagov"
                    r["_dataset"] = ds_name
                    records.append(r)
            logger.success(f"[Pipeline] DataGov: {len(records)} records")
            return records
        except Exception as e:
            logger.error(f"[Pipeline] DataGov failed: {e}")
            return []

    def run_cag(self) -> list:
        logger.info("[Pipeline] Running CAG scraper...")
        try:
            from scrapers.cag_scraper import CAGScraper
            reports = CAGScraper().fetch_report_list(limit=20)
            for r in reports:
                r["_source"] = "cag"
            logger.success(f"[Pipeline] CAG: {len(reports)} reports")
            return reports
        except Exception as e:
            logger.error(f"[Pipeline] CAG failed: {e}")
            return []

    def run_gem(self) -> list:
        logger.info("[Pipeline] Running GeM scraper...")
        try:
            from scrapers.gem_scraper import GeMScraper
            contracts = GeMScraper().fetch_contracts_by_ministry(limit=20)
            cleaned = []
            for c in contracts:
                c["_source"] = "gem"
                cleaned.append(self.cleaner.clean_record(c, "contract"))
            logger.success(f"[Pipeline] GeM: {len(cleaned)} contracts")
            return cleaned
        except Exception as e:
            logger.error(f"[Pipeline] GeM failed: {e}")
            return []

    def run_myneta(self) -> list:
        logger.info("[Pipeline] Running MyNeta scraper...")
        try:
            from scrapers.myneta_scraper import MyNetaScraper
            candidates = MyNetaScraper().fetch_sample_data(save=False)
            cleaned = []
            for c in candidates:
                c["_source"] = "myneta"
                cleaned.append(self.cleaner.clean_record(c, "person"))
            logger.success(f"[Pipeline] MyNeta: {len(cleaned)} candidates")
            return cleaned
        except Exception as e:
            logger.error(f"[Pipeline] MyNeta failed: {e}")
            return []

    def run_mca(self) -> list:
        logger.info("[Pipeline] Running MCA scraper...")
        try:
            from scrapers.mca_scraper import MCAScraper
            result = MCAScraper().fetch_and_save_sample(save=False)
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
        logger.info("[Pipeline] Running PIB scraper...")
        try:
            from scrapers.pib_scraper import PIBScraper
            articles = PIBScraper().fetch_all_feeds(save=False)
            for a in articles:
                a["_source"] = "pib"
            logger.success(f"[Pipeline] PIB: {len(articles)} articles")
            return articles
        except Exception as e:
            logger.error(f"[Pipeline] PIB failed: {e}")
            return []

    def find_politician_company_links(self,
                                       politicians: list,
                                       companies: list) -> list:
        """Core analysis: find politicians who appear as company directors."""
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

    def run(self, scrapers: list = None) -> dict:
        """Run full pipeline. scrapers=None runs all."""
        all_scrapers = ["datagov", "cag", "gem", "myneta", "mca", "pib"]
        to_run = scrapers if scrapers else all_scrapers
        logger.info(f"[Pipeline] Starting: {to_run}")
        start = datetime.now()

        runner_map = {
            "datagov": self.run_datagov,
            "cag":     self.run_cag,
            "gem":     self.run_gem,
            "myneta":  self.run_myneta,
            "mca":     self.run_mca,
            "pib":     self.run_pib,
        }

        raw = {name: runner_map[name]() for name in to_run if name in runner_map}

        politicians = raw.get("myneta", [])
        companies   = raw.get("mca", [])
        links       = []
        if politicians and companies:
            politicians = self.resolver.resolve_dataset(politicians, "name")
            companies   = self.resolver.resolve_dataset(companies,   "name")
            links       = self.find_politician_company_links(politicians, companies)

        duration = (datetime.now() - start).seconds
        summary = {
            "scrapers_run":        to_run,
            "duration_seconds":    duration,
            "total_raw_records":   sum(len(v) for v in raw.values()),
            "politicians_found":   len(raw.get("myneta", [])),
            "companies_found":     len(raw.get("mca", [])),
            "contracts_found":     len(raw.get("gem", [])),
            "cag_reports_found":   len(raw.get("cag", [])),
            "pib_articles_found":  len(raw.get("pib", [])),
            "politician_co_links": len(links),
        }
        logger.info(f"[Pipeline] Done in {duration}s")

        results = {"raw": raw, "links": links,
                   "summary": summary, "run_at": start.isoformat()}
        results["saved_to"] = self.save(results)
        return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BharatGraph Pipeline")
    parser.add_argument("--scrapers", type=str, default=None,
                        help="e.g. datagov,cag,gem,myneta,mca,pib")
    args = parser.parse_args()
    scrapers = args.scrapers.split(",") if args.scrapers else None

    print("=" * 55)
    print("BharatGraph - Data Pipeline")
    print("=" * 55)

    results = BharatGraphPipeline().run(scrapers=scrapers)
    s = results["summary"]

    print(f"\n{'='*55}")
    print("PIPELINE SUMMARY")
    print(f"{'='*55}")
    print(f"  Scrapers run:   {s['scrapers_run']}")
    print(f"  Duration:       {s['duration_seconds']}s")
    print(f"  Total records:  {s['total_raw_records']}")
    print(f"  Politicians:    {s['politicians_found']}")
    print(f"  Companies:      {s['companies_found']}")
    print(f"  GeM contracts:  {s['contracts_found']}")
    print(f"  CAG reports:    {s['cag_reports_found']}")
    print(f"  PIB articles:   {s['pib_articles_found']}")
    print(f"  Politician-co:  {s['politician_co_links']}")
    print(f"  Saved to:       {results.get('saved_to')}")
    print(f"{'='*55}")
