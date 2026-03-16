"""
BharatGraph - CAG (Comptroller and Auditor General) Scraper
Fetches audit reports and findings from India's supreme audit institution.
Source: cag.gov.in (official government site, 100% public)

WHY THIS MATTERS:
CAG audits expose exactly the type of fraud we want to map:
- Funds released but works not done
- Ghost beneficiaries in schemes
- Irregular contract awards
- Disproportionate spending
"""

import re
import json
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from loguru import logger


class CAGScraper(BaseScraper):
    """
    Scrapes CAG audit reports from cag.gov.in.

    CAG (Comptroller and Auditor General of India) is the
    constitutional authority that audits all government accounts.
    Their reports are gold for finding financial irregularities.

    Data includes:
    - Performance audit reports (scheme-wise)
    - State finance audit reports
    - Union government audit reports
    - Amount of irregularities found (in crores)
    - Departments/ministries flagged
    """

    BASE_URL    = "https://cag.gov.in"
    REPORTS_URL = "https://cag.gov.in/en/audit-report"

    # Keywords that indicate financial irregularities
    FRAUD_KEYWORDS = [
        "misappropriation", "irregularities", "excess payment",
        "short recovery", "loss", "avoidable expenditure",
        "fictitious", "ghost", "diversion of funds", "unspent",
        "non-utilization", "fraudulent", "collusion", "overpayment",
        "undue benefit", "unauthorized", "infructuous",
    ]

    def __init__(self):
        super().__init__(name="cag", delay=3.0)

    def fetch_report_list(self, limit: int = 20) -> list:
        """
        Fetch list of recent CAG audit reports.
        Returns list of report metadata dicts.
        """
        logger.info("[CAG] Fetching audit report list...")
        html = self.get_html(self.REPORTS_URL)

        if not html:
            logger.warning("[CAG] Could not fetch report list, using sample")
            return self._get_sample_reports()

        return self._parse_report_list(html, limit)

    def _parse_report_list(self, html: str, limit: int) -> list:
        """Parse report links and metadata from CAG website."""
        soup = BeautifulSoup(html, "lxml")
        reports = []

        # CAG site uses various link patterns for reports
        links = soup.find_all("a", href=True)

        for link in links:
            href = link.get("href", "")
            text = link.get_text(strip=True)

            # Filter for actual report links
            if not text or len(text) < 10:
                continue
            if not any(kw in href.lower() for kw in
                       ["report", "audit", "pdf", "ar-"]):
                continue

            # Build full URL
            if href.startswith("http"):
                full_url = href
            elif href.startswith("/"):
                full_url = self.BASE_URL + href
            else:
                continue

            report = {
                "title":       text,
                "url":         full_url,
                "source":      "CAG India",
                "source_url":  self.BASE_URL,
                "scraped_at":  datetime.now().isoformat(),
                "entity_type": "audit_report",
                # Flag if title mentions irregularities
                "alert_keywords": self._find_fraud_keywords(text),
            }
            reports.append(report)

            if len(reports) >= limit:
                break

        logger.info(f"[CAG] Parsed {len(reports)} report links")
        return reports if reports else self._get_sample_reports()

    def _find_fraud_keywords(self, text: str) -> list:
        """Find fraud-related keywords in report title."""
        text_lower = text.lower()
        return [kw for kw in self.FRAUD_KEYWORDS if kw in text_lower]

    def _get_sample_reports(self) -> list:
        """
        Sample CAG report structures for testing.
        Based on real CAG report formats.
        """
        return [
            {
                "title":
                    "Report on MGNREGS - Irregularities in Tamil Nadu 2023",
                "url":
                    "https://cag.gov.in/en/audit-report/details/sample-1",
                "year": "2023",
                "state": "Tamil Nadu",
                "scheme": "MGNREGS",
                "amount_crore": 112.81,
                "irregularity_type": "Misappropriation of funds",
                "finding":
                    "38,063 irregularities found. Works not executed "
                    "despite funds released.",
                "source": "CAG India (sample)",
                "scraped_at": datetime.now().isoformat(),
                "entity_type": "audit_report",
                "alert_keywords": ["irregularities", "misappropriation"],
            },
            {
                "title":
                    "Performance Audit: PM-KISAN Scheme - Assam 2024",
                "url":
                    "https://cag.gov.in/en/audit-report/details/sample-2",
                "year": "2024",
                "state": "Assam",
                "scheme": "PM-KISAN",
                "amount_crore": 768.3,
                "irregularity_type": "Ineligible beneficiaries",
                "finding":
                    "35% applicants ineligible. 1.56 million bogus entries "
                    "including govt employees and pensioners.",
                "source": "CAG India (sample)",
                "scraped_at": datetime.now().isoformat(),
                "entity_type": "audit_report",
                "alert_keywords": ["irregularities", "fictitious"],
            },
            {
                "title":
                    "Audit Report: Public Procurement Irregularities 2023",
                "url":
                    "https://cag.gov.in/en/audit-report/details/sample-3",
                "year": "2023",
                "state": "National",
                "scheme": "Public Procurement",
                "amount_crore": 450.0,
                "irregularity_type": "Bid rigging and collusion",
                "finding":
                    "Single-bid contracts awarded without competition. "
                    "Repeated winners across multiple tenders.",
                "source": "CAG India (sample)",
                "scraped_at": datetime.now().isoformat(),
                "entity_type": "audit_report",
                "alert_keywords": ["collusion", "irregularities"],
            },
        ]

    def fetch_and_save(self, save: bool = True) -> list:
        """Fetch all reports and save to disk."""
        reports = self.fetch_report_list(limit=30)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if save and reports:
            filepath = f"data/samples/cag_reports_{timestamp}.json"
            self.save_json(reports, filepath)
            logger.success(f"[CAG] Saved {len(reports)} reports to {filepath}")

        return reports

    def get_high_value_irregularities(self, reports: list,
                                       min_crore: float = 10.0) -> list:
        """
        Filter reports where amount involved >= min_crore.
        Helps prioritize large-scale fraud for investigation.
        """
        flagged = [
            r for r in reports
            if float(r.get("amount_crore", 0) or 0) >= min_crore
        ]
        logger.info(f"[CAG] Reports >= ₹{min_crore}Cr: {len(flagged)}")
        return flagged


# ── Run directly to test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("BharatGraph - CAG Audit Report Scraper Test")
    print("=" * 60)

    scraper = CAGScraper()

    print("\n[1] Fetching CAG audit report list...")
    reports = scraper.fetch_report_list(limit=20)
    print(f"    Total reports found: {len(reports)}")

    if reports:
        r = reports[0]
        print(f"\n    Example report:")
        print(f"    Title:       {r.get('title', 'N/A')[:60]}")
        print(f"    URL:         {r.get('url', 'N/A')[:60]}")
        print(f"    Alert kws:   {r.get('alert_keywords', [])}")
        if r.get("amount_crore"):
            print(f"    Amount:      ₹{r.get('amount_crore')} Crore")

    print("\n[2] Filtering high-value irregularities (>=10 Cr)...")
    big = scraper.get_high_value_irregularities(reports, min_crore=10.0)
    print(f"    High-value reports: {len(big)}")

    print("\n[3] Saving all reports...")
    all_reports = scraper.fetch_and_save(save=True)
    print(f"    Saved {len(all_reports)} reports to data/samples/")
    print("\nDone!")
