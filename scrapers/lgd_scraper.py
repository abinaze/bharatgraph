import os
from datetime import datetime
from scrapers.base_scraper import BaseScraper
from loguru import logger


class LGDScraper(BaseScraper):

    BASE_URL   = "https://lgdirectory.gov.in"
    STATES_URL = "https://lgdirectory.gov.in/lgdStateWiseDetail.do"
    API_URL    = "https://api.data.gov.in/resource/6176ee09-3d56-4a3b-8115-21841576787d"

    def __init__(self):
        super().__init__(name="lgd", delay=1.5)
        self.api_key = os.getenv("DATAGOV_API_KEY", "")

    def fetch_state_codes(self, save: bool = True) -> list:
        logger.info("[LGD] Fetching state and district codes...")
        params = {
            "api-key": self.api_key,
            "format":  "json",
            "limit":   100,
        }
        data    = self.get_json(self.API_URL, params=params)
        records = []
        if data and isinstance(data, dict):
            records = self._parse_api_response(data)
        if not records:
            logger.warning("[LGD] Could not fetch live data — using sample")
            records = self._get_sample_codes()
        if save and records:
            ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/samples/lgd_codes_{ts}.json"
            self.save_json(records, filepath)
            logger.success(f"[LGD] Saved {len(records)} codes")
        return records

    def _parse_api_response(self, data: dict) -> list:
        raw = (data.get("records") or data.get("data") or
               data.get("items") or [])
        return [
            {**r,
             "source":      "Local Government Directory",
             "source_url":  self.BASE_URL,
             "scraped_at":  datetime.now().isoformat(),
             "entity_type": "administrative_unit"}
            for r in raw[:100]
        ]

    def _get_sample_codes(self) -> list:
        return [
            {
                "lgd_state_code":    33,
                "state_name":        "Tamil Nadu",
                "lgd_district_code": 601,
                "district_name":     "Chennai",
                "total_villages":    2789,
                "gram_panchayats":   12524,
                "source":            "Local Government Directory (sample)",
                "source_url":        self.BASE_URL,
                "scraped_at":        datetime.now().isoformat(),
                "entity_type":       "administrative_unit",
            },
            {
                "lgd_state_code":    27,
                "state_name":        "Maharashtra",
                "lgd_district_code": 527,
                "district_name":     "Mumbai",
                "total_villages":    1247,
                "gram_panchayats":   2891,
                "source":            "Local Government Directory (sample)",
                "source_url":        self.BASE_URL,
                "scraped_at":        datetime.now().isoformat(),
                "entity_type":       "administrative_unit",
            },
        ]


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - LGD Scraper")
    print("=" * 55)
    scraper = LGDScraper()
    codes   = scraper.fetch_state_codes(save=True)
    print(f"\n  Records: {len(codes)}")
    if codes:
        print(f"  Example: {codes[0].get('state_name')} — "
              f"District: {codes[0].get('district_name')}")
    print("\nDone!")
