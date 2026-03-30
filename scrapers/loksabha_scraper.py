import os
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from loguru import logger


class LokSabhaScraper(BaseScraper):

    BASE_URL      = "https://loksabha.nic.in"
    QUESTIONS_URL = "https://loksabha.nic.in/Questions/QResult15.aspx"

    MINISTRIES = [
        "Ministry of Finance",
        "Ministry of Home Affairs",
        "Ministry of Rural Development",
        "Ministry of Health",
    ]

    def __init__(self):
        super().__init__(name="loksabha", delay=3.0)
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
        })

    def fetch_questions(self, ministry: str = "Ministry of Finance",
                        limit: int = 20) -> list:
        logger.info(f"[LokSabha] Fetching questions for: {ministry}")
        html = self.get_html(self.QUESTIONS_URL, params={"ministry": ministry})
        if not html:
            logger.warning("[LokSabha] Could not fetch page — using sample")
            return self._get_sample_questions(ministry)
        questions = self._parse_questions(html, ministry, limit)
        if not questions:
            return self._get_sample_questions(ministry)
        return questions

    def _parse_questions(self, html: str, ministry: str, limit: int) -> list:
        soup      = BeautifulSoup(html, "lxml")
        questions = []
        for row in soup.find_all("tr")[1:limit + 1]:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue
            question = {
                "question_number": cols[0].get_text(strip=True),
                "subject":         cols[1].get_text(strip=True),
                "member_name":     cols[2].get_text(strip=True) if len(cols) > 2 else "",
                "ministry":        ministry,
                "session":         "17th Lok Sabha",
                "source":          "Lok Sabha",
                "source_url":      self.BASE_URL,
                "scraped_at":      datetime.now().isoformat(),
                "entity_type":     "parliamentary_question",
            }
            if question["subject"]:
                questions.append(question)
        logger.info(f"[LokSabha] Parsed {len(questions)} questions")
        return questions

    def _get_sample_questions(self, ministry: str) -> list:
        return [
            {
                "question_number": "Q001",
                "subject":         "Status of PM-KISAN scheme beneficiary verification",
                "member_name":     "SAMPLE MP",
                "ministry":        ministry,
                "session":         "17th Lok Sabha",
                "source":          "Lok Sabha (sample)",
                "source_url":      self.BASE_URL,
                "scraped_at":      datetime.now().isoformat(),
                "entity_type":     "parliamentary_question",
            },
            {
                "question_number": "Q002",
                "subject":         "Irregularities in MGNREGA fund disbursement",
                "member_name":     "SAMPLE MP",
                "ministry":        ministry,
                "session":         "17th Lok Sabha",
                "source":          "Lok Sabha (sample)",
                "source_url":      self.BASE_URL,
                "scraped_at":      datetime.now().isoformat(),
                "entity_type":     "parliamentary_question",
            },
        ]

    def fetch_all_ministries(self, save: bool = True) -> list:
        all_questions = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for ministry in self.MINISTRIES:
            questions = self.fetch_questions(ministry, limit=10)
            all_questions.extend(questions)
        if save and all_questions:
            filepath = f"data/samples/loksabha_questions_{timestamp}.json"
            self.save_json(all_questions, filepath)
            logger.success(f"[LokSabha] Saved {len(all_questions)} questions")
        return all_questions


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Lok Sabha Scraper")
    print("=" * 55)
    scraper   = LokSabhaScraper()
    questions = scraper.fetch_all_ministries(save=True)
    print(f"\n  Total: {len(questions)}")
    if questions:
        print(f"  Example: {questions[0]['subject'][:60]}")
    print("\nDone!")
