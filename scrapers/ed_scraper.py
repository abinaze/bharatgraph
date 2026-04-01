import os
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from loguru import logger


class EDScraper(BaseScraper):

    BASE_URL      = "https://enforcementdirectorate.gov.in"
    PRESS_URL     = "https://enforcementdirectorate.gov.in/press-release"
    STATS_URL     = "https://enforcementdirectorate.gov.in/statistics"

    def __init__(self):
        super().__init__(name="ed", delay=2.0)
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
        })

    def fetch_press_releases(self, limit: int = 20,
                              save: bool = True) -> list:
        logger.info("[ED] Fetching press releases...")
        html     = self.get_html(self.PRESS_URL)
        releases = []
        if html:
            releases = self._parse_press_releases(html, limit)
        if not releases:
            logger.warning("[ED] Could not fetch live data — using sample")
            releases = self._get_sample_releases()
        if save and releases:
            ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/samples/ed_releases_{ts}.json"
            self.save_json(releases, filepath)
            logger.success(f"[ED] Saved {len(releases)} releases")
        return releases

    def _parse_press_releases(self, html: str, limit: int) -> list:
        soup     = BeautifulSoup(html, "lxml")
        releases = []
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            href  = link.get("href", "")
            if len(title) < 15:
                continue
            if not any(k in title.lower() for k in
                       ["attach","arrest","pmla","fema","crore","case"]):
                continue
            full_url = (href if href.startswith("http")
                        else self.BASE_URL + href)
            releases.append({
                "title":       title,
                "url":         full_url,
                "source":      "Enforcement Directorate",
                "source_url":  self.BASE_URL,
                "scraped_at":  datetime.now().isoformat(),
                "entity_type": "ed_press_release",
            })
            if len(releases) >= limit:
                break
        logger.info(f"[ED] Parsed {len(releases)} press releases")
        return releases

    def _get_sample_releases(self) -> list:
        return [
            {
                "title": (
                    "ED Attaches Properties Worth Rs 10021.46 Crore "
                    "in PACL Money Laundering Case"
                ),
                "date":        "2026-02-18",
                "amount_crore":10021.46,
                "case_type":   "PMLA",
                "accused":     "PACL India Limited",
                "url": (
                    "https://enforcementdirectorate.gov.in/"
                    "press-release/2026/feb/pacl"
                ),
                "source":      "Enforcement Directorate (sample)",
                "source_url":  self.BASE_URL,
                "scraped_at":  datetime.now().isoformat(),
                "entity_type": "ed_press_release",
            },
        ]


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - ED Scraper")
    print("=" * 55)
    scraper  = EDScraper()
    releases = scraper.fetch_press_releases(save=True)
    print(f"\n  Records: {len(releases)}")
    if releases:
        print(f"  Example: {releases[0]['title'][:60]}")
    print("\nDone!")
