"""
BharatGraph - MyNeta / ADR Scraper
Fetches candidate affidavit data: assets, criminal cases, education.
Source: myneta.info (run by ADR - Association for Democratic Reforms)
This data is 100% public - from Election Commission of India affidavits.
"""

import json
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from loguru import logger


class MyNetaScraper(BaseScraper):
    """
    Scrapes candidate data from MyNeta.info
    MyNeta publishes election affidavit data for every candidate:
    - Declared assets and liabilities
    - Criminal cases (self-declared)
    - Education qualifications
    - Party affiliation
    All data originally submitted to Election Commission of India.
    """

    BASE_URL = "https://myneta.info"

    # State election pages (update with current elections)
    STATE_PAGES = {
        "lok_sabha_2024": "https://myneta.info/LokSabha2024/",
        "delhi_2020":     "https://myneta.info/delhi2020/",
        "tamil_nadu_2021":"https://myneta.info/TamilNadu2021/",
    }

    def __init__(self):
        super().__init__(name="myneta", delay=3.0)  # 3s delay - be polite

    def fetch_candidates_by_state(self, state_key: str = "lok_sabha_2024",
                                   limit: int = 20) -> list:
        """
        Fetch list of candidates from a state election page.
        Returns list of candidate dicts.
        """
        url = self.STATE_PAGES.get(state_key)
        if not url:
            logger.error(f"[MyNeta] Unknown state key: {state_key}")
            return []

        logger.info(f"[MyNeta] Fetching candidates from: {state_key}")
        html = self.get_html(url)

        if not html:
            logger.error(f"[MyNeta] Could not fetch page: {url}")
            return []

        return self._parse_candidate_table(html, state_key, limit)

    def _parse_candidate_table(self, html: str, source: str,
                                limit: int = 20) -> list:
        """
        Parse candidate table from MyNeta HTML page.
        Extracts name, party, assets, liabilities, criminal cases.
        """
        soup = BeautifulSoup(html, "lxml")
        candidates = []

        # MyNeta uses standard HTML tables for candidate data
        tables = soup.find_all("table")

        for table in tables:
            rows = table.find_all("tr")
            for row in rows[1:limit + 1]:  # skip header row
                cols = row.find_all("td")
                if len(cols) < 5:
                    continue

                # Extract text safely
                def safe_text(col):
                    return col.get_text(strip=True) if col else ""

                candidate = {
                    "name":            safe_text(cols[1]) if len(cols) > 1 else "",
                    "party":           safe_text(cols[2]) if len(cols) > 2 else "",
                    "criminal_cases":  safe_text(cols[3]) if len(cols) > 3 else "0",
                    "total_assets":    safe_text(cols[4]) if len(cols) > 4 else "",
                    "liabilities":     safe_text(cols[5]) if len(cols) > 5 else "",
                    "education":       safe_text(cols[6]) if len(cols) > 6 else "",
                    "source_election": source,
                    "source_url":      self.BASE_URL,
                    "scraped_at":      datetime.now().isoformat(),
                    # Entity type for graph database
                    "entity_type":     "politician",
                }

                # Only add if name exists
                if candidate["name"]:
                    # Flag candidates with criminal cases
                    try:
                        cases = int(re.sub(r"\D", "", candidate["criminal_cases"] or "0") or "0")
                        candidate["has_criminal_cases"] = cases > 0
                        candidate["criminal_case_count"] = cases
                    except ValueError:
                        candidate["has_criminal_cases"] = False
                        candidate["criminal_case_count"] = 0

                    candidates.append(candidate)

        logger.info(f"[MyNeta] Parsed {len(candidates)} candidates")
        return candidates

    def fetch_sample_data(self, save: bool = True) -> list:
        """
        Fetch sample data from multiple elections.
        Safe to run - uses small limits.
        """
        all_candidates = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for state_key in ["lok_sabha_2024", "tamil_nadu_2021"]:
            logger.info(f"[MyNeta] Fetching: {state_key}")
            candidates = self.fetch_candidates_by_state(state_key, limit=15)
            all_candidates.extend(candidates)
            time.sleep(2)  # extra delay between pages

        if save and all_candidates:
            filepath = f"data/samples/myneta_candidates_{timestamp}.json"
            self.save_json(all_candidates, filepath)
            logger.success(f"[MyNeta] Saved {len(all_candidates)} candidates")

        return all_candidates

    def get_candidates_with_criminal_cases(self, candidates: list) -> list:
        """Filter candidates who declared criminal cases."""
        flagged = [c for c in candidates if c.get("has_criminal_cases")]
        logger.info(f"[MyNeta] Candidates with criminal cases: {len(flagged)}")
        return flagged


# ── Run directly to test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("BharatGraph - MyNeta Scraper Test")
    print("=" * 60)

    scraper = MyNetaScraper()

    print("\n[1] Fetching Lok Sabha 2024 candidates (sample)...")
    candidates = scraper.fetch_candidates_by_state("lok_sabha_2024", limit=20)
    print(f"    Total parsed: {len(candidates)}")

    if candidates:
        sample = candidates[0]
        print(f"\n    Example candidate:")
        print(f"    Name:           {sample.get('name', 'N/A')}")
        print(f"    Party:          {sample.get('party', 'N/A')}")
        print(f"    Assets:         {sample.get('total_assets', 'N/A')}")
        print(f"    Criminal Cases: {sample.get('criminal_case_count', 0)}")
        print(f"    Education:      {sample.get('education', 'N/A')}")

    print("\n[2] Flagging candidates with criminal cases...")
    flagged = scraper.get_candidates_with_criminal_cases(candidates)
    print(f"    Flagged: {len(flagged)} / {len(candidates)}")

    print("\n[3] Saving full sample...")
    all_data = scraper.fetch_sample_data(save=True)
    print(f"    Saved {len(all_data)} total candidates to data/samples/")
    print("\nDone!")
