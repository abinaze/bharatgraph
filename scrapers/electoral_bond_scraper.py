import os
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from loguru import logger


class ElectoralBondScraper(BaseScraper):

    ECI_URL = "https://www.eci.gov.in/electoral-bonds"

    def __init__(self):
        super().__init__(name="electoral_bond", delay=2.0)

    def fetch_bond_data(self, save: bool = True) -> list:
        logger.info("[ElectoralBond] Fetching bond disclosure data...")
        html  = self.get_html(self.ECI_URL)
        bonds = []
        if html:
            bonds = self._parse_bond_page(html)
        if not bonds:
            logger.warning("[ElectoralBond] Live page returned no data — using sample")
            bonds = self._get_sample_bonds()
        if save and bonds:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath  = f"data/samples/electoral_bonds_{timestamp}.json"
            self.save_json(bonds, filepath)
            logger.success(f"[ElectoralBond] Saved {len(bonds)} records")
        return bonds

    def _parse_bond_page(self, html: str) -> list:
        soup  = BeautifulSoup(html, "lxml")
        bonds = []
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            href  = link.get("href", "")
            if any(kw in title.lower() for kw in ["bond","donor","purchase","redemption"]):
                bonds.append({
                    "title":       title,
                    "url":         href if href.startswith("http") else self.ECI_URL,
                    "source":      "Election Commission of India",
                    "source_url":  self.ECI_URL,
                    "scraped_at":  datetime.now().isoformat(),
                    "entity_type": "electoral_bond_disclosure",
                })
        return bonds

    def _get_sample_bonds(self) -> list:
        return [
            {
                "bond_number":      "EB001",
                "purchaser_name":   "SAMPLE CORPORATION LTD",
                "denomination_crore": 1.0,
                "purchase_date":    "2023-04-05",
                "redemption_date":  "2023-04-12",
                "redeemed_by":      "SAMPLE POLITICAL PARTY",
                "source":           "Supreme Court ordered ECI disclosure (sample)",
                "source_url":       self.ECI_URL,
                "scraped_at":       datetime.now().isoformat(),
                "entity_type":      "electoral_bond",
            },
        ]


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Electoral Bond Scraper")
    print("=" * 55)
    scraper = ElectoralBondScraper()
    bonds   = scraper.fetch_bond_data(save=True)
    print(f"\n  Total records: {len(bonds)}")
    print("\nDone!")
