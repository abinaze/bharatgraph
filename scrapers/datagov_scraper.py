"""
BharatGraph - Data.gov.in Scraper
Fetches public datasets from India's Open Government Data portal.
Free API key already included (public key).
"""

import json
import os
from datetime import datetime
from scrapers.base_scraper import BaseScraper
from loguru import logger


class DataGovScraper(BaseScraper):
    """
    Scrapes data from data.gov.in - India's official open data portal.
    Datasets: government schemes, beneficiary lists, budget data.
    """

    # Public datasets we want (resource IDs from data.gov.in)
    DATASETS = {
        "mgnrega_states": "9ef84268-d588-465a-a308-a864a43d0070",
        "pm_kisan_states": "c1e45527-0de1-4afe-90c0-8e70c9f9dd9d",
    }

    def __init__(self):
        super().__init__(name="datagov", delay=2.0)
        self.base_url = "https://api.data.gov.in/resource/"
        # This is a public key from data.gov.in - works for basic access
        self.api_key = "579b464db66ec23d9960025070515804"

    def fetch_dataset(self, resource_id: str, limit: int = 100) -> dict:
        """
        Fetch a dataset from data.gov.in by resource ID.
        Returns raw JSON data.
        """
        url = f"{self.base_url}{resource_id}"
        params = {
            "api-key": self.api_key,
            "format": "json",
            "limit": limit,
            "offset": 0,
        }

        logger.info(f"[DataGov] Fetching dataset: {resource_id}")
        data = self.get_json(url, params=params)

        if data:
            logger.info(f"[DataGov] Got {data.get('total', '?')} total records")
        return data

    def fetch_all_datasets(self, save: bool = True) -> dict:
        """
        Fetch all configured datasets and optionally save to disk.
        Returns dict of {name: data}.
        """
        results = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for name, resource_id in self.DATASETS.items():
            logger.info(f"[DataGov] Processing: {name}")
            data = self.fetch_dataset(resource_id, limit=50)

            if data:
                results[name] = data

                if save:
                    filepath = f"data/samples/datagov_{name}_{timestamp}.json"
                    self.save_json(data, filepath)
                    logger.success(f"[DataGov] Saved: {filepath}")
            else:
                logger.warning(f"[DataGov] Failed to fetch: {name}")

        return results

    def get_dataset_info(self, resource_id: str) -> dict:
        """
        Get metadata/info about a dataset.
        """
        url = f"https://api.data.gov.in/resource/{resource_id}"
        params = {
            "api-key": self.api_key,
            "format": "json",
            "limit": 1,
        }
        return self.get_json(url, params=params)


# ── Run directly to test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("BharatGraph - DataGov Scraper Test")
    print("=" * 60)

    scraper = DataGovScraper()

    print("\n[1] Fetching MGNREGA dataset (50 records)...")
    data = scraper.fetch_dataset(
        "9ef84268-d588-465a-a308-a864a43d0070", limit=10
    )

    if data:
        print(f"    ✅ Success! Total records available: {data.get('total', '?')}")
        print(f"    Fields: {list(data.get('fields', [{}])[0].keys()) if data.get('fields') else 'N/A'}")
    else:
        print("    ❌ Failed (check internet connection)")

    print("\n[2] Fetching all configured datasets...")
    all_data = scraper.fetch_all_datasets(save=True)
    print(f"    ✅ Fetched {len(all_data)} datasets")
    print("\nDone! Check data/samples/ folder for output files.")
