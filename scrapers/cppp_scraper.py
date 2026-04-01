import os
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from loguru import logger


class CPPPScraper(BaseScraper):

    BASE_URL   = "https://eprocure.gov.in"
    TENDERS_URL = "https://eprocure.gov.in/eprocure/app"
    API_URL    = "https://api.data.gov.in/resource/40cce240-bdce-4c45-b498-e2b70ab27b3e"

    def __init__(self):
        super().__init__(name="cppp", delay=2.0)
        self.api_key = os.getenv("DATAGOV_API_KEY", "")
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
        })

    def fetch_tenders(self, save: bool = True) -> list:
        logger.info("[CPPP] Fetching central procurement tenders...")
        params = {
            "api-key": self.api_key,
            "format":  "json",
            "limit":   50,
        }
        data    = self.get_json(self.API_URL, params=params)
        tenders = []
        if data and isinstance(data, dict):
            tenders = self._parse_response(data)
        if not tenders:
            logger.warning("[CPPP] Could not fetch live data — using sample")
            tenders = self._get_sample_tenders()
        if save and tenders:
            ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/samples/cppp_tenders_{ts}.json"
            self.save_json(tenders, filepath)
            logger.success(f"[CPPP] Saved {len(tenders)} tenders")
        return tenders

    def _parse_response(self, data: dict) -> list:
        raw = (data.get("records") or data.get("data") or [])
        return [
            {**r,
             "source":      "Central Public Procurement Portal",
             "source_url":  self.BASE_URL,
             "scraped_at":  datetime.now().isoformat(),
             "entity_type": "tender"}
            for r in raw[:50]
        ]

    def _get_sample_tenders(self) -> list:
        return [
            {
                "tender_id":        "CPPP/2024/001234",
                "title":            "Construction of Rural Roads under PMGSY",
                "ministry":         "Ministry of Rural Development",
                "department":       "National Rural Roads Development Agency",
                "estimated_value":  45000000,
                "estimated_crore":  4.5,
                "tender_type":      "Open Tender",
                "bid_submission_end":"2024-08-30",
                "status":           "Awarded",
                "awarded_to":       "XYZ Infrastructure Pvt Ltd",
                "awarded_value":    42500000,
                "single_bid":       False,
                "source":           "CPPP (sample)",
                "source_url":       self.BASE_URL,
                "scraped_at":       datetime.now().isoformat(),
                "entity_type":      "tender",
            },
        ]


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - CPPP Scraper")
    print("=" * 55)
    scraper = CPPPScraper()
    tenders = scraper.fetch_tenders(save=True)
    print(f"\n  Records: {len(tenders)}")
    if tenders:
        print(f"  Example: {tenders[0].get('title', '')[:60]}")
    print("\nDone!")
