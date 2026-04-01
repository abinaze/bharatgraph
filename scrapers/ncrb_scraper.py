import os
from datetime import datetime
from scrapers.base_scraper import BaseScraper
from loguru import logger


class NCRBScraper(BaseScraper):

    BASE_URL = "https://ncrb.gov.in"
    DATA_URL = "https://ncrb.gov.in/crime-in-india"
    OPENCITY_URL = "https://data.opencity.in/dataset/crime-in-india-2023"

    def __init__(self):
        super().__init__(name="ncrb", delay=2.0)

    def fetch_crime_statistics(self, save: bool = True) -> list:
        logger.info("[NCRB] Fetching Crime in India statistics...")
        data = self.get_json(self.OPENCITY_URL)
        stats = []
        if data:
            stats = self._parse_opencity(data)
        if not stats:
            logger.warning("[NCRB] Could not fetch live data — using sample")
            stats = self._get_sample_stats()
        if save and stats:
            ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/samples/ncrb_stats_{ts}.json"
            self.save_json(stats, filepath)
            logger.success(f"[NCRB] Saved {len(stats)} records")
        return stats

    def _parse_opencity(self, data: dict) -> list:
        if isinstance(data, list):
            return [
                {**record,
                 "source":      "NCRB Crime in India",
                 "source_url":  self.BASE_URL,
                 "scraped_at":  datetime.now().isoformat(),
                 "entity_type": "crime_statistic"}
                for record in data[:50]
            ]
        return []

    def _get_sample_stats(self) -> list:
        return [
            {
                "state":                "Tamil Nadu",
                "year":                 2023,
                "ipc_crimes_total":     183421,
                "economic_offences":    12847,
                "crimes_by_officials":  234,
                "cyber_crimes":         8932,
                "source":               "NCRB Crime in India 2023 (sample)",
                "source_url":           self.BASE_URL,
                "scraped_at":           datetime.now().isoformat(),
                "entity_type":          "crime_statistic",
            },
            {
                "state":                "Maharashtra",
                "year":                 2023,
                "ipc_crimes_total":     412893,
                "economic_offences":    28341,
                "crimes_by_officials":  567,
                "cyber_crimes":         19234,
                "source":               "NCRB Crime in India 2023 (sample)",
                "source_url":           self.BASE_URL,
                "scraped_at":           datetime.now().isoformat(),
                "entity_type":          "crime_statistic",
            },
        ]


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - NCRB Scraper")
    print("=" * 55)
    scraper = NCRBScraper()
    stats   = scraper.fetch_crime_statistics(save=True)
    print(f"\n  Records: {len(stats)}")
    if stats:
        print(f"  Example: {stats[0].get('state')} — "
              f"{stats[0].get('ipc_crimes_total')} IPC crimes")
    print("\nDone!")
