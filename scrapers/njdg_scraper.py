import os
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from loguru import logger


class NJDGScraper(BaseScraper):

    BASE_URL  = "https://njdg.ecourts.gov.in"
    STATS_URL = "https://njdg.ecourts.gov.in/njdgnew/index.php"

    def __init__(self):
        super().__init__(name="njdg", delay=2.0)
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
        })

    def fetch_pendency_stats(self, save: bool = True) -> list:
        logger.info("[NJDG] Fetching case pendency statistics...")
        html = self.get_html(self.STATS_URL)
        stats = []
        if html:
            stats = self._parse_stats(html)
        if not stats:
            logger.warning("[NJDG] Could not fetch live data — using sample")
            stats = self._get_sample_stats()
        if save and stats:
            ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/samples/njdg_stats_{ts}.json"
            self.save_json(stats, filepath)
            logger.success(f"[NJDG] Saved {len(stats)} records")
        return stats

    def _parse_stats(self, html: str) -> list:
        soup  = BeautifulSoup(html, "lxml")
        stats = []
        for row in soup.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) >= 3:
                stats.append({
                    "court_type":   cols[0].get_text(strip=True),
                    "pending_civil":cols[1].get_text(strip=True),
                    "pending_crim": cols[2].get_text(strip=True),
                    "source":       "NJDG",
                    "source_url":   self.BASE_URL,
                    "scraped_at":   datetime.now().isoformat(),
                    "entity_type":  "court_pendency_stat",
                })
        logger.info(f"[NJDG] Parsed {len(stats)} rows")
        return stats

    def _get_sample_stats(self) -> list:
        return [
            {
                "court_type":      "District and Sessions Courts",
                "total_pending":   48600000,
                "pending_civil":   12800000,
                "pending_criminal":35800000,
                "above_10_years":  4995960,
                "source":          "NJDG (sample)",
                "source_url":      self.BASE_URL,
                "scraped_at":      datetime.now().isoformat(),
                "entity_type":     "court_pendency_stat",
            },
            {
                "court_type":      "High Courts",
                "total_pending":   6100000,
                "pending_civil":   2900000,
                "pending_criminal":3200000,
                "above_10_years":  890000,
                "source":          "NJDG (sample)",
                "source_url":      self.BASE_URL,
                "scraped_at":      datetime.now().isoformat(),
                "entity_type":     "court_pendency_stat",
            },
        ]


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - NJDG Scraper")
    print("=" * 55)
    scraper = NJDGScraper()
    stats   = scraper.fetch_pendency_stats(save=True)
    print(f"\n  Records: {len(stats)}")
    if stats:
        print(f"  Example: {stats[0]['court_type']}")
    print("\nDone!")
