import os
from datetime import datetime
from scrapers.base_scraper import BaseScraper
from loguru import logger


class WikidataScraper(BaseScraper):

    SPARQL_URL = "https://query.wikidata.org/sparql"

    def __init__(self):
        super().__init__(name="wikidata", delay=1.0)
        self.session.headers.update({
            "Accept":     "application/sparql-results+json",
            "User-Agent": "BharatGraph/0.1 (civic-transparency-platform)",
        })

    def enrich_politician(self, name: str) -> dict:
        logger.info(f"[Wikidata] Enriching: '{name}'")
        query = f"""
        SELECT ?person ?birthDate ?educationLabel ?positionLabel ?partyLabel WHERE {{
          ?person wdt:P31 wd:Q5 .
          ?person rdfs:label "{name}"@en .
          OPTIONAL {{ ?person wdt:P569 ?birthDate }}
          OPTIONAL {{ ?person wdt:P69 ?education }}
          OPTIONAL {{ ?person wdt:P39 ?position }}
          OPTIONAL {{ ?person wdt:P102 ?party }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
        }}
        LIMIT 5
        """
        data     = self.get_json(self.SPARQL_URL, params={"query": query, "format": "json"})
        bindings = data.get("results",{}).get("bindings",[]) if data else []
        if not bindings:
            return self._empty_enrichment(name)
        return {
            "name":       name,
            "wikidata_id":bindings[0].get("person",{}).get("value","").split("/")[-1],
            "birth_date": bindings[0].get("birthDate",{}).get("value",""),
            "education":  list({b.get("educationLabel",{}).get("value","")
                                for b in bindings if b.get("educationLabel")}),
            "positions":  list({b.get("positionLabel",{}).get("value","")
                                for b in bindings if b.get("positionLabel")}),
            "party":      bindings[0].get("partyLabel",{}).get("value",""),
            "source":     "Wikidata",
            "source_url": "https://www.wikidata.org",
            "scraped_at": datetime.now().isoformat(),
        }

    def _empty_enrichment(self, name: str) -> dict:
        return {"name": name, "wikidata_id": "", "birth_date": "",
                "education": [], "positions": [], "party": "",
                "source": "Wikidata", "source_url": "https://www.wikidata.org",
                "scraped_at": datetime.now().isoformat()}

    def enrich_entity_list(self, names: list, save: bool = True) -> list:
        results = [self.enrich_politician(n) for n in names]
        if save and results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.save_json(results, f"data/samples/wikidata_enrichment_{timestamp}.json")
            logger.success(f"[Wikidata] Saved enrichment for {len(results)} entities")
        return results


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Wikidata Scraper")
    print("=" * 55)
    scraper = WikidataScraper()
    results = scraper.enrich_entity_list(["Narendra Modi", "Rahul Gandhi"], save=True)
    for r in results:
        print(f"\n  {r['name']}: ID={r['wikidata_id']} party={r['party']}")
        print(f"  positions={r['positions'][:2]}")
    print("\nDone!")
