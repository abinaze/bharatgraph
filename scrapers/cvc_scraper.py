import os
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from loguru import logger


class CVCScraper(BaseScraper):

    BASE_URL    = "https://cvc.gov.in"
    ANNUAL_URL  = "https://cvc.gov.in/annual-reports"
    CIRCULARS_URL = "https://cvc.gov.in/cvc-circulars"

    def __init__(self):
        super().__init__(name="cvc", delay=2.0)
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
        })

    def fetch_circulars(self, limit: int = 20, save: bool = True) -> list:
        logger.info("[CVC] Fetching CVC circulars...")
        html      = self.get_html(self.CIRCULARS_URL)
        circulars = []
        if html:
            circulars = self._parse_links(html, "circular", limit)
        if not circulars:
            logger.warning("[CVC] Could not fetch live data — using sample")
            circulars = self._get_sample_circulars()
        if save and circulars:
            ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/samples/cvc_circulars_{ts}.json"
            self.save_json(circulars, filepath)
            logger.success(f"[CVC] Saved {len(circulars)} circulars")
        return circulars

    def _parse_links(self, html: str, keyword: str, limit: int) -> list:
        soup    = BeautifulSoup(html, "lxml")
        results = []
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            href  = link.get("href", "")
            if len(title) < 10:
                continue
            full_url = (href if href.startswith("http")
                        else self.BASE_URL + href)
            results.append({
                "title":       title,
                "url":         full_url,
                "source":      "Central Vigilance Commission",
                "source_url":  self.BASE_URL,
                "scraped_at":  datetime.now().isoformat(),
                "entity_type": f"cvc_{keyword}",
            })
            if len(results) >= limit:
                break
        logger.info(f"[CVC] Parsed {len(results)} items")
        return results

    def _get_sample_circulars(self) -> list:
        return [
            {
                "title": (
                    "Guidelines on Integrity Pact for Public Procurement — "
                    "Revised Instructions"
                ),
                "circular_number": "03/2024",
                "date":            "2024-03-15",
                "ministry":        "All Central Government Departments",
                "subject":         "Vigilance and Anti-Corruption",
                "source":          "Central Vigilance Commission (sample)",
                "source_url":      self.BASE_URL,
                "scraped_at":      datetime.now().isoformat(),
                "entity_type":     "cvc_circular",
            },
        ]


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - CVC Scraper")
    print("=" * 55)
    scraper   = CVCScraper()
    circulars = scraper.fetch_circulars(save=True)
    print(f"\n  Records: {len(circulars)}")
    if circulars:
        print(f"  Example: {circulars[0]['title'][:60]}")
    print("\nDone!")
