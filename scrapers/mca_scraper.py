"""
BharatGraph - MCA (Ministry of Corporate Affairs) Scraper
Fetches company and director data from India's corporate registry.
Sources:
  - data.gov.in (MCA company master dataset - free, public)
  - MCA21 portal snapshots
This links politicians → companies → contracts in the graph.
"""

import json
import re
from datetime import datetime
from scrapers.base_scraper import BaseScraper
from loguru import logger


class MCAScraper(BaseScraper):
    """
    Scrapes company and director data from MCA (Ministry of Corporate Affairs).

    Why this matters for BharatGraph:
    If a politician or their relative is a director of a company
    that wins government contracts, that is a key relationship to map.

    Data from data.gov.in MCA snapshots (public, legal, free).
    """

    # MCA company master data on data.gov.in (public snapshot)
    # This resource ID gives: CIN, company name, status, state, directors
    MCA_RESOURCE_IDS = {
        "company_master": "9ef84268-d588-465a-a308-a864a43d0070",
        # Note: We use the DataGov API to access MCA snapshots
    }

    DATAGOV_API_KEY =os.getenv("DATAGOV_API_KEY", "")
    DATAGOV_BASE = "https://api.data.gov.in/resource/"

    # Company status types we care about
    ACTIVE_STATUSES = ["Active", "ACTIVE", "active"]

    def __init__(self):
        super().__init__(name="mca", delay=2.0)

    def fetch_companies_by_state(self, state: str = "Tamil Nadu",
                                  limit: int = 50) -> list:
        """
        Fetch companies registered in a given state.
        Uses data.gov.in public API.
        """
        logger.info(f"[MCA] Fetching companies in: {state}")

        # Try fetching from data.gov.in
        url = f"{self.DATAGOV_BASE}9ef84268-d588-465a-a308-a864a43d0070"
        params = {
            "api-key": self.DATAGOV_API_KEY,
            "format":  "json",
            "limit":   limit,
            "filters[state_name]": state,
        }

        data = self.get_json(url, params=params)

        if data and "records" in data:
            companies = self._normalize_companies(data["records"], state)
            logger.success(f"[MCA] Got {len(companies)} companies from {state}")
            return companies

        logger.warning(f"[MCA] No data from API, using sample data")
        return self._get_sample_companies()

    def _normalize_companies(self, records: list, state: str) -> list:
        """
        Normalize raw MCA records into standard format.
        """
        companies = []
        for rec in records:
            company = {
                # Standard fields across MCA datasets
                "cin":           rec.get("corporate_identification_number", 
                                         rec.get("cin", "")),
                "name":          rec.get("company_name", 
                                         rec.get("name", "")),
                "status":        rec.get("company_status", 
                                         rec.get("status", "")),
                "state":         rec.get("state_name", state),
                "registration_date": rec.get("date_of_registration", ""),
                "company_class": rec.get("class_of_company", ""),
                "company_type":  rec.get("type_of_company", ""),
                "registered_office": rec.get("registered_office_address", ""),
                "source":        "MCA/data.gov.in",
                "scraped_at":    datetime.now().isoformat(),
                "entity_type":   "company",
            }
            if company["name"]:
                companies.append(company)
        return companies

    def _get_sample_companies(self) -> list:
        """
        Returns hardcoded sample data for testing when API is unavailable.
        These are example company structures only - not real sensitive data.
        """
        return [
            {
                "cin": "U45200TN2010PTC000001",
                "name": "SAMPLE CONSTRUCTION PRIVATE LIMITED",
                "status": "Active",
                "state": "Tamil Nadu",
                "registration_date": "2010-01-15",
                "company_class": "Private",
                "company_type": "Company limited by Shares",
                "source": "sample_data",
                "scraped_at": datetime.now().isoformat(),
                "entity_type": "company",
                "note": "SAMPLE DATA - replace with real MCA fetch",
            },
            {
                "cin": "U74999DL2015PTC000002",
                "name": "SAMPLE INFRASTRUCTURE LIMITED",
                "status": "Active",
                "state": "Delhi",
                "registration_date": "2015-03-20",
                "company_class": "Public",
                "company_type": "Company limited by Shares",
                "source": "sample_data",
                "scraped_at": datetime.now().isoformat(),
                "entity_type": "company",
                "note": "SAMPLE DATA - replace with real MCA fetch",
            },
        ]

    def search_company_by_name(self, name: str) -> list:
        """
        Search for a company by name fragment.
        Useful for finding if a politician's family name appears in company names.
        """
        logger.info(f"[MCA] Searching for company: {name}")
        url = f"{self.DATAGOV_BASE}9ef84268-d588-465a-a308-a864a43d0070"
        params = {
            "api-key": self.DATAGOV_API_KEY,
            "format":  "json",
            "limit":   20,
            "filters[company_name]": name.upper(),
        }
        data = self.get_json(url, params=params)
        if data and "records" in data:
            return self._normalize_companies(data["records"], "unknown")
        return []

    def fetch_and_save_sample(self, save: bool = True) -> dict:
        """
        Fetch sample company data from multiple states and save.
        """
        results = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        states = ["Tamil Nadu", "Maharashtra", "Delhi"]

        for state in states:
            companies = self.fetch_companies_by_state(state, limit=20)
            results[state] = companies
            logger.info(f"[MCA] {state}: {len(companies)} companies")

        if save:
            filepath = f"data/samples/mca_companies_{timestamp}.json"
            self.save_json(results, filepath)
            logger.success(f"[MCA] Saved to {filepath}")

        return results


# ── Run directly to test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("BharatGraph - MCA Scraper Test")
    print("=" * 60)

    scraper = MCAScraper()

    print("\n[1] Fetching companies from Tamil Nadu...")
    companies = scraper.fetch_companies_by_state("Tamil Nadu", limit=10)
    print(f"    Total: {len(companies)} companies")

    if companies:
        sample = companies[0]
        print(f"\n    Example company:")
        print(f"    CIN:    {sample.get('cin', 'N/A')}")
        print(f"    Name:   {sample.get('name', 'N/A')}")
        print(f"    Status: {sample.get('status', 'N/A')}")
        print(f"    State:  {sample.get('state', 'N/A')}")

    print("\n[2] Fetching and saving multi-state sample...")
    all_data = scraper.fetch_and_save_sample(save=True)
    total = sum(len(v) for v in all_data.values())
    print(f"    Total companies saved: {total}")
    print("\nDone! Check data/samples/ folder.")
