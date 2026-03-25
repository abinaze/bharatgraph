"""
BharatGraph - PIB (Press Information Bureau) Scraper
Fetches official government press releases.
Source: pib.gov.in

NOTE: PIB RSS feeds return empty XML (server blocks feedparser).
Fix: Scrape pib.gov.in/allRel.aspx HTML page directly.
"""

import os
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from loguru import logger


class PIBScraper(BaseScraper):
    """
    Scrapes press releases from PIB using direct HTML scraping.
    RSS mode was abandoned - PIB server blocks feedparser.
    """

    PIB_RELEASES_URL = "https://pib.gov.in/allRel.aspx"
    PIB_BASE_URL     = "https://pib.gov.in"

    ALERT_KEYWORDS = [
        "scheme", "crore", "lakh", "contract", "tender", "allocation",
        "fund", "grant", "subsidy", "project", "award", "procurement",
        "budget", "expenditure", "beneficiary", "disburse", "inaugurate",
        "launch", "approve", "sanction", "release",
    ]

    def __init__(self):
        super().__init__(name="pib", delay=2.0)
        # Browser User-Agent so PIB doesn't block the request
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

    def fetch_releases(self, limit: int = 30) -> list:
        """Fetch press releases by scraping pib.gov.in/allRel.aspx"""
        logger.info(f"[PIB] Fetching from: {self.PIB_RELEASES_URL}")
        html = self.get_html(self.PIB_RELEASES_URL)

        if not html:
            logger.error("[PIB] Could not fetch page")
            return self._get_sample_articles()

        articles = self._parse_releases_page(html, limit)

        if not articles:
            logger.warning("[PIB] No articles parsed — using sample data")
            return self._get_sample_articles()

        return articles

    def _parse_releases_page(self, html: str, limit: int) -> list:
        """Parse press release links from PIB HTML page."""
        soup = BeautifulSoup(html, "lxml")
        articles = []

        for link in soup.find_all("a", href=True):
            href  = link.get("href", "")
            title = link.get_text(strip=True)

            if not title or len(title) < 15:
                continue
            if not any(kw in href.lower() for kw in
                       ["prid=", "pressrelease", "pressrelaseid", "newsite"]):
                continue

            if href.startswith("http"):
                full_url = href
            elif href.startswith("/"):
                full_url = self.PIB_BASE_URL + href
            else:
                full_url = self.PIB_BASE_URL + "/" + href

            articles.append({
                "title":          title,
                "link":           full_url,
                "published":      "",
                "source":         "PIB",
                "scraped_at":     datetime.now().isoformat(),
                "entity_type":    "press_release",
                "alert_keywords": self._find_keywords(title),
            })

            if len(articles) >= limit:
                break

        logger.info(f"[PIB] Parsed {len(articles)} press releases")
        return articles

    def _find_keywords(self, text: str) -> list:
        """Find alert keywords in article title."""
        return [kw for kw in self.ALERT_KEYWORDS if kw in text.lower()]

    def fetch_all_feeds(self, save: bool = True) -> list:
        """Main method used by pipeline — fetch all releases."""
        articles = self.fetch_releases(limit=50)

        if save and articles:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath  = f"data/samples/pib_articles_{timestamp}.json"
            self.save_json(articles, filepath)
            logger.success(f"[PIB] Saved {len(articles)} articles to {filepath}")

        return articles

    def get_high_alert_articles(self, articles: list = None) -> list:
        """Filter articles with 2+ alert keywords."""
        if articles is None:
            articles = self.fetch_all_feeds(save=False)
        high_alert = [a for a in articles if len(a.get("alert_keywords", [])) >= 2]
        logger.info(f"[PIB] High-alert: {len(high_alert)}/{len(articles)}")
        return high_alert

    def _get_sample_articles(self) -> list:
        """Sample data used when site is unreachable."""
        return [
            {
                "title":          "PM launches new rural infrastructure fund allocation scheme",
                "link":           "https://pib.gov.in/PressReleasePage.aspx?PRID=1000001",
                "published":      datetime.now().isoformat(),
                "source":         "PIB (sample)",
                "scraped_at":     datetime.now().isoformat(),
                "entity_type":    "press_release",
                "alert_keywords": ["scheme", "fund", "allocation"],
                "note":           "SAMPLE - real PIB fetch failed",
            },
            {
                "title":          "Cabinet approves procurement of medical equipment worth 500 crore",
                "link":           "https://pib.gov.in/PressReleasePage.aspx?PRID=1000002",
                "published":      datetime.now().isoformat(),
                "source":         "PIB (sample)",
                "scraped_at":     datetime.now().isoformat(),
                "entity_type":    "press_release",
                "alert_keywords": ["procurement", "crore", "approve"],
                "note":           "SAMPLE - real PIB fetch failed",
            },
        ]


# ── Run directly to test ─────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("BharatGraph - PIB Scraper Test (HTML mode)")
    print("=" * 60)

    scraper = PIBScraper()

    print("\n[1] Fetching PIB press releases...")
    articles = scraper.fetch_all_feeds(save=True)
    print(f"    Total: {len(articles)}")

    if articles:
        print(f"\n    Example:")
        print(f"    Title:    {articles[0]['title'][:70]}")
        print(f"    Keywords: {articles[0]['alert_keywords']}")

    print("\n[2] High-alert articles (2+ keywords)...")
    high = scraper.get_high_alert_articles(articles)
    print(f"    High-alert: {len(high)}")
    print("\nDone!")
