import os
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from loguru import logger


class NGODarpanScraper(BaseScraper):

    BASE_URL   = "https://ngodarpan.gov.in"
    SEARCH_URL = "https://ngodarpan.gov.in/index.php/search"
    API_URL    = "https://api.data.gov.in/resource/2b0ce19b-4807-4f79-abde-cbc37d0c9d71"

    def __init__(self):
        super().__init__(name="ngo_darpan", delay=2.0)
        self.api_key = os.getenv("DATAGOV_API_KEY", "")

    def fetch_ngo_list(self, state: str = "Tamil Nadu",
                        save: bool = True) -> list:
        logger.info(f"[NGODarpan] Fetching NGOs in {state}...")
        params = {
            "api-key": self.api_key,
            "format":  "json",
            "limit":   50,
            "filters[state]": state,
        }
        data = self.get_json(self.API_URL, params=params)
        ngos = []
        if data and isinstance(data, dict):
            ngos = self._parse_response(data)
        if not ngos:
            logger.warning("[NGODarpan] Could not fetch live data — using sample")
            ngos = self._get_sample_ngos(state)
        if save and ngos:
            ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/samples/ngo_darpan_{ts}.json"
            self.save_json(ngos, filepath)
            logger.success(f"[NGODarpan] Saved {len(ngos)} NGOs")
        return ngos

    def _parse_response(self, data: dict) -> list:
        raw = (data.get("records") or data.get("data") or [])
        return [
            {**r,
             "source":      "NGO Darpan, NITI Aayog",
             "source_url":  self.BASE_URL,
             "scraped_at":  datetime.now().isoformat(),
             "entity_type": "ngo"}
            for r in raw[:50]
        ]

    def _get_sample_ngos(self, state: str) -> list:
        return [
            {
                "darpan_id":     "TN/2018/0123456",
                "ngo_name":      "Sample Rural Development Trust",
                "state":         state,
                "district":      "Chennai",
                "registration_type": "Trust",
                "year_of_reg":   2018,
                "key_issues":    "Rural Development, Education",
                "csr_receipts":  1250000,
                "govt_grants":   3400000,
                "source":        "NGO Darpan (sample)",
                "source_url":    self.BASE_URL,
                "scraped_at":    datetime.now().isoformat(),
                "entity_type":   "ngo",
            },
        ]


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - NGO Darpan Scraper")
    print("=" * 55)
    scraper = NGODarpanScraper()
    ngos    = scraper.fetch_ngo_list(state="Tamil Nadu", save=True)
    print(f"\n  Records: {len(ngos)}")
    if ngos:
        print(f"  Example: {ngos[0].get('ngo_name')}")
    print("\nDone!")
