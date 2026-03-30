import os
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from loguru import logger


class SEBIScraper(BaseScraper):

    BASE_URL   = "https://www.sebi.gov.in"
    ORDERS_URL = "https://www.sebi.gov.in/enforcement/orders"

    def __init__(self):
        super().__init__(name="sebi", delay=2.0)
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
        })

    def fetch_enforcement_orders(self, limit: int = 20) -> list:
        logger.info("[SEBI] Fetching enforcement orders...")
        html = self.get_html(self.ORDERS_URL)
        if not html:
            logger.warning("[SEBI] Could not fetch page — using sample")
            return self._get_sample_orders()
        orders = self._parse_orders(html, limit)
        if not orders:
            return self._get_sample_orders()
        return orders

    def _parse_orders(self, html: str, limit: int) -> list:
        soup   = BeautifulSoup(html, "lxml")
        orders = []
        for link in soup.find_all("a", href=True):
            href  = link.get("href", "")
            title = link.get_text(strip=True)
            if not title or len(title) < 10:
                continue
            if not any(kw in href.lower() for kw in ["order","adjudication","settlement"]):
                continue
            full_url = href if href.startswith("http") else self.BASE_URL + href
            orders.append({
                "title":       title,
                "url":         full_url,
                "order_type":  "Enforcement Order",
                "source":      "SEBI",
                "source_url":  self.BASE_URL,
                "scraped_at":  datetime.now().isoformat(),
                "entity_type": "regulatory_order",
            })
            if len(orders) >= limit:
                break
        logger.info(f"[SEBI] Parsed {len(orders)} orders")
        return orders

    def _get_sample_orders(self) -> list:
        return [
            {
                "title":       "Adjudication Order against Director for insider trading",
                "url":         "https://www.sebi.gov.in/enforcement/orders/sample-1",
                "order_type":  "Adjudication Order",
                "violation":   "Insider trading under SEBI (PIT) Regulations 2015",
                "source":      "SEBI (sample)",
                "source_url":  self.BASE_URL,
                "scraped_at":  datetime.now().isoformat(),
                "entity_type": "regulatory_order",
            },
        ]

    def fetch_and_save(self, save: bool = True) -> list:
        orders = self.fetch_enforcement_orders(limit=30)
        if save and orders:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath  = f"data/samples/sebi_orders_{timestamp}.json"
            self.save_json(orders, filepath)
            logger.success(f"[SEBI] Saved {len(orders)} orders")
        return orders


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - SEBI Scraper")
    print("=" * 55)
    scraper = SEBIScraper()
    orders  = scraper.fetch_and_save(save=True)
    print(f"\n  Total orders: {len(orders)}")
    if orders:
        print(f"  Example: {orders[0]['title'][:60]}")
    print("\nDone!")
