import os
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from loguru import logger


class ICIJScraper(BaseScraper):

    SEARCH_URL = "https://offshoreleaks.icij.org/search"

    DATASETS = [
        "panama-papers",
        "pandora-papers",
        "paradise-papers",
        "offshore-leaks",
    ]

    def __init__(self):
        super().__init__(name="icij", delay=2.0)
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })

    def search_entity(self, name: str) -> list:
        logger.info(f"[ICIJ] Searching Offshore Leaks: '{name}'")
        html = self.get_html(self.SEARCH_URL, params={"q": name})
        if not html:
            logger.warning(f"[ICIJ] No response for '{name}'")
            return []
        return self._parse_results(html, name)

    def _parse_results(self, html: str, name: str) -> list:
        soup    = BeautifulSoup(html, "lxml")
        results = []

        rows = soup.find_all("tr")
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue
            entity_name  = cols[0].get_text(strip=True)
            jurisdiction = cols[1].get_text(strip=True) if len(cols) > 1 else ""
            dataset      = cols[2].get_text(strip=True) if len(cols) > 2 else ""
            link_tag     = cols[0].find("a")
            url          = ("https://offshoreleaks.icij.org" + link_tag["href"]
                           if link_tag and link_tag.get("href") else "")
            if entity_name:
                results.append({
                    "entity_id":    url.split("/")[-1] if url else "",
                    "name":         entity_name,
                    "jurisdiction": jurisdiction,
                    "dataset":      dataset,
                    "url":          url,
                    "search_term":  name,
                    "source":       "ICIJ Offshore Leaks",
                    "source_url":   self.SEARCH_URL,
                    "scraped_at":   datetime.now().isoformat(),
                    "entity_type":  "offshore_entity",
                })

        if not results and "No results" not in html and len(html) > 500:
            logger.info(f"[ICIJ] Site reachable but table parse found 0 rows for '{name}'")

        logger.info(f"[ICIJ] Found {len(results)} offshore entities for '{name}'")
        return results

    def screen_entities(self, names: list, save: bool = True) -> dict:
        flagged = {}
        for name in names:
            matches = self.search_entity(name)
            if matches:
                flagged[name] = matches
                logger.warning(f"[ICIJ] OFFSHORE MATCH: '{name}' found in leaked data")
            else:
                logger.info(f"[ICIJ] CLEAR: '{name}' not found in offshore data")
        if save and flagged:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath  = f"data/samples/icij_matches_{timestamp}.json"
            self.save_json(flagged, filepath)
            logger.success(f"[ICIJ] Saved {len(flagged)} offshore matches")
        return flagged


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - ICIJ Offshore Leaks Scraper Test")
    print("=" * 55)
    scraper    = ICIJScraper()
    test_names = ["Sample Corporation", "Test Holdings"]
    print(f"\n  Searching {len(test_names)} entities in Offshore Leaks...")
    results = scraper.screen_entities(test_names, save=True)
    print(f"  Found in offshore leak data: {len(results)}")
    print("\nDone!")
