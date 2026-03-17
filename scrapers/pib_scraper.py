"""
BharatGraph - PIB (Press Information Bureau) Scraper
Fetches official government press releases and cabinet decisions.
Source: pib.gov.in (India's official govt press body)
These are 100% public and legal to use.
"""

import feedparser
import json
import os
from datetime import datetime
from scrapers.base_scraper import BaseScraper
from loguru import logger


class PIBScraper(BaseScraper):
    """
    Scrapes official press releases from Press Information Bureau (PIB).
    PIB is the nodal agency of the Government of India
    for disseminating information to print and electronic media.

    Data includes:
    - Cabinet decisions
    - Ministry press releases
    - Policy announcements
    - Scheme launches
    """

    # PIB RSS feeds (verified March 2026)
    RSS_FEEDS = {
        "pib_all":     "https://pib.gov.in/Rss.aspx",
        "pib_release": "https://pib.gov.in/RssMain.aspx",
        "pib_hindi":   "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=2&Regid=3",
    }

    # Keywords that flag articles about money, schemes, contracts
    ALERT_KEYWORDS = [
        "scheme", "crore", "lakh", "contract", "tender", "allocation",
        "fund", "grant", "subsidy", "project", "award", "procurement",
        "budget", "expenditure", "beneficiary", "disburse",
    ]

    def __init__(self):
        super().__init__(name="pib", delay=2.0)

    def fetch_feed(self, feed_name: str = "pib_all") -> list:
        """
        Fetch latest press releases from a PIB RSS feed.
        Returns list of article dicts.
        """
        # Default to pib_all if feed_name not found
        url = self.RSS_FEEDS.get(feed_name, self.RSS_FEEDS["pib_all"])
        logger.info(f"[PIB] Fetching feed: {feed_name} -> {url}")

        try:
            feed = feedparser.parse(url)

            # Handle empty RSS
            if not feed.entries:
                logger.warning(f"[PIB] RSS empty for: {feed_name}")
                # Try raw HTML fetch to check if site is reachable
                html = self.get_html(url)
                if html and len(html) > 500:
                    logger.info(
                        f"[PIB] Site reachable ({len(html)} chars) "
                        f"but RSS has no entries - may need login/cookies"
                    )
                else:
                    logger.error(f"[PIB] Site unreachable: {url}")
                return []

            # Parse entries
            articles = []
            for entry in feed.entries:
                article = {
                    "title":      entry.get("title", ""),
                    "link":       entry.get("link", ""),
                    "published":  entry.get("published", ""),
                    "summary":    entry.get("summary", ""),
                    "source":     "PIB",
                    "feed_name":  feed_name,
                    "scraped_at": datetime.now().isoformat(),
                    "alert_keywords": self._find_keywords(
                        entry.get("title", "") + " " + entry.get("summary", "")
                    ),
                }
                articles.append(article)

            logger.success(f"[PIB] Got {len(articles)} articles from: {feed_name}")
            return articles

        except Exception as e:
            logger.error(f"[PIB] Error fetching feed {feed_name}: {e}")
            return []

    def _find_keywords(self, text: str) -> list:
        """Find alert keywords in article text."""
        text_lower = text.lower()
        return [kw for kw in self.ALERT_KEYWORDS if kw in text_lower]

    def fetch_all_feeds(self, save: bool = True) -> list:
        """Fetch all configured feeds and combine results."""
        all_articles = []
        seen_links = set()

        for feed_name in self.RSS_FEEDS:
            articles = self.fetch_feed(feed_name)
            for article in articles:
                if article["link"] not in seen_links:
                    all_articles.append(article)
                    seen_links.add(article["link"])

        # Sort by date (newest first)
        all_articles.sort(
            key=lambda x: x.get("published", ""), reverse=True
        )

        if save and all_articles:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/samples/pib_articles_{timestamp}.json"
            self.save_json(all_articles, filepath)
            logger.success(
                f"[PIB] Saved {len(all_articles)} articles to {filepath}"
            )

        return all_articles

    def get_high_alert_articles(self, articles: list = None) -> list:
        """
        Filter articles that contain 3+ alert keywords.
        These are most likely about money flows or schemes.
        """
        if articles is None:
            articles = self.fetch_all_feeds(save=False)

        high_alert = [
            a for a in articles
            if len(a.get("alert_keywords", [])) >= 3
        ]
        logger.info(
            f"[PIB] High-alert articles: {len(high_alert)}/{len(articles)}"
        )
        return high_alert


# ── Run directly to test ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("BharatGraph - PIB Scraper Test")
    print("=" * 60)

    scraper = PIBScraper()

    print("\n[1] Fetching all PIB feeds...")
    articles = scraper.fetch_all_feeds(save=True)
    print(f"    Total articles: {len(articles)}")

    if articles:
        print(f"\n    Latest: {articles[0]['title'][:70]}...")
        print(f"    Published: {articles[0]['published']}")
        print(f"    Alert keywords: {articles[0]['alert_keywords']}")
    else:
        print("    No articles (PIB RSS may require browser cookies)")
        print("    Alternative: https://pib.gov.in/newsite/erelease.aspx")

    print("\n[2] High-alert articles (3+ keywords)...")
    high_alert = scraper.get_high_alert_articles(articles)
    print(f"    High-alert: {len(high_alert)}")

    print("\nDone!")
