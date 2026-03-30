import os
from datetime import datetime
from scrapers.base_scraper import BaseScraper
from loguru import logger


class OpenSanctionsScraper(BaseScraper):

    API_URL = "https://api.opensanctions.org/search/default"

    def __init__(self):
        super().__init__(name="opensanctions", delay=1.5)
        self.api_key = os.getenv("OPENSANCTIONS_API_KEY", "")
        if self.api_key:
            self.session.headers.update({"Authorization": f"ApiKey {self.api_key}"})
        else:
            logger.warning("[OpenSanctions] No API key — add OPENSANCTIONS_API_KEY to .env")

    def search_entity(self, name: str, schema: str = "Person") -> list:
        logger.info(f"[OpenSanctions] Searching: '{name}'")
        params = {"q": name, "schema": schema, "limit": 10}
        data   = self.get_json(self.API_URL, params=params)
        if not data or "results" not in data:
            return []
        results = []
        for r in data["results"]:
            props = r.get("properties", {})
            results.append({
                "entity_id":    r.get("id", ""),
                "name":         r.get("caption", name),
                "schema":       r.get("schema", schema),
                "datasets":     r.get("datasets", []),
                "is_pep":       "pep" in str(r.get("datasets", [])).lower(),
                "is_sanctioned":any(d in ["us_ofac_sdn","un_sc_sanctions","eu_fsf"]
                                    for d in r.get("datasets", [])),
                "countries":    props.get("country", []),
                "positions":    props.get("position", []),
                "source":       "OpenSanctions",
                "source_url":   "https://opensanctions.org",
                "scraped_at":   datetime.now().isoformat(),
                "entity_type":  "sanctions_check",
            })
        logger.success(f"[OpenSanctions] Found {len(results)} matches for '{name}'")
        return results

    def screen_entity_list(self, names: list) -> dict:
        results = {}
        for name in names:
            matches = self.search_entity(name)
            if any(m["is_sanctioned"] or m["is_pep"] for m in matches):
                results[name] = matches
                logger.warning(f"[OpenSanctions] FLAG: '{name}' in sanctions/PEP data")
            else:
                logger.info(f"[OpenSanctions] CLEAR: '{name}'")
        return results

    def fetch_and_save(self, names: list, save: bool = True) -> dict:
        results = self.screen_entity_list(names)
        if save and results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.save_json(results, f"data/samples/opensanctions_{timestamp}.json")
        return results


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - OpenSanctions Scraper")
    print("=" * 55)
    scraper = OpenSanctionsScraper()
    results = scraper.fetch_and_save(["Sample Person", "Test Corporation"], save=True)
    print(f"\n  Flagged: {len(results)}")
    print("\nDone!")
