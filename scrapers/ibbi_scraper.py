import os
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from loguru import logger


class IBBIScraper(BaseScraper):

    BASE_URL    = "https://ibbi.gov.in"
    ORDERS_URL  = "https://ibbi.gov.in/en/orders"
    PROCESS_URL = "https://ibbi.gov.in/en/corporate-processes"

    def __init__(self):
        super().__init__(name="ibbi", delay=2.0)
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
        })

    def fetch_orders(self, limit: int = 20, save: bool = True) -> list:
        logger.info("[IBBI] Fetching insolvency orders...")
        html   = self.get_html(self.ORDERS_URL)
        orders = []
        if html:
            orders = self._parse_orders(html, limit)
        if not orders:
            logger.warning("[IBBI] Could not fetch live data — using sample")
            orders = self._get_sample_orders()
        if save and orders:
            ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/samples/ibbi_orders_{ts}.json"
            self.save_json(orders, filepath)
            logger.success(f"[IBBI] Saved {len(orders)} orders")
        return orders

    def _parse_orders(self, html: str, limit: int) -> list:
        soup   = BeautifulSoup(html, "lxml")
        orders = []
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            href  = link.get("href", "")
            if len(title) < 10:
                continue
            if not any(k in href.lower() for k in ["order","nclt","ibo"]):
                continue
            full_url = (href if href.startswith("http")
                        else self.BASE_URL + href)
            orders.append({
                "title":       title,
                "url":         full_url,
                "source":      "IBBI",
                "source_url":  self.BASE_URL,
                "scraped_at":  datetime.now().isoformat(),
                "entity_type": "insolvency_order",
            })
            if len(orders) >= limit:
                break
        logger.info(f"[IBBI] Parsed {len(orders)} orders")
        return orders

    def _get_sample_orders(self) -> list:
        return [
            {
                "company_name":      "Sample Infrastructure Ltd",
                "cin":               "U45200MH2015PLC123456",
                "process_type":      "Corporate Insolvency Resolution Process",
                "admitted_date":     "2023-06-15",
                "status":            "Ongoing",
                "admitted_claims":   245.6,
                "resolution_plan":   None,
                "creditor_count":    12,
                "source":            "IBBI (sample)",
                "source_url":        self.BASE_URL,
                "scraped_at":        datetime.now().isoformat(),
                "entity_type":       "insolvency_case",
            },
        ]


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - IBBI Scraper")
    print("=" * 55)
    scraper = IBBIScraper()
    orders  = scraper.fetch_orders(save=True)
    print(f"\n  Records: {len(orders)}")
    if orders:
        print(f"  Example: {str(orders[0])[:80]}")
    print("\nDone!")
