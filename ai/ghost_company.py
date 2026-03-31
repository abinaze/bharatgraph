import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from loguru import logger


GHOST_FLAGS = {
    "recent_registration":  30,
    "no_prior_record":      20,
    "single_director":      20,
    "capital_anomaly":      20,
    "no_contract_history":  10,
}

GHOST_THRESHOLD = 60


class GhostCompanyDetector:

    def __init__(self, driver=None):
        self.driver = driver

    def _fetch_companies_with_contracts(self) -> list:
        if not self.driver:
            return []
        with self.driver.session() as session:
            return session.run(
                """
                MATCH (c:Company)-[:WON_CONTRACT]->(ct:Contract)
                WITH c, min(ct.order_date) AS first_contract,
                     count(ct) AS contract_count,
                     sum(ct.amount_crore) AS total_value
                RETURN c.id AS id, c.name AS name,
                       c.registration_date AS reg_date,
                       c.paid_up_capital AS capital,
                       c.director_count AS directors,
                       c.cag_mentions AS cag_mentions,
                       c.sebi_mentions AS sebi_mentions,
                       first_contract, contract_count, total_value
                """
            ).data()

    def score_company(self, company: dict) -> dict:
        score  = 0
        flags  = []

        reg_date_str    = company.get("reg_date", "")
        first_contract  = company.get("first_contract", "")

        if reg_date_str and first_contract:
            try:
                if isinstance(reg_date_str, str):
                    reg_date = datetime.fromisoformat(reg_date_str[:10])
                else:
                    reg_date = datetime(reg_date_str.year,
                                        reg_date_str.month,
                                        reg_date_str.day)

                if isinstance(first_contract, str):
                    contract_date = datetime.fromisoformat(first_contract[:10])
                else:
                    contract_date = datetime(first_contract.year,
                                             first_contract.month,
                                             first_contract.day)

                days_diff = (contract_date - reg_date).days
                if 0 <= days_diff <= 90:
                    score += GHOST_FLAGS["recent_registration"]
                    flags.append({
                        "flag": "recent_registration",
                        "detail": (
                            f"Company registered {days_diff} days before "
                            "first contract award"
                        ),
                        "score": GHOST_FLAGS["recent_registration"],
                    })
            except (ValueError, TypeError, AttributeError):
                pass

        cag_mentions  = int(company.get("cag_mentions", 0) or 0)
        sebi_mentions = int(company.get("sebi_mentions", 0) or 0)
        if cag_mentions == 0 and sebi_mentions == 0:
            score += GHOST_FLAGS["no_prior_record"]
            flags.append({
                "flag": "no_prior_record",
                "detail": "No mentions in CAG audit reports or SEBI filings",
                "score": GHOST_FLAGS["no_prior_record"],
            })

        directors = int(company.get("directors", 1) or 1)
        if directors == 1:
            score += GHOST_FLAGS["single_director"]
            flags.append({
                "flag": "single_director",
                "detail": "Company has only one registered director",
                "score": GHOST_FLAGS["single_director"],
            })

        capital     = float(company.get("capital", 0) or 0)
        total_value = float(company.get("total_value", 0) or 0)
        if capital > 0 and total_value > capital * 10:
            ratio = round(total_value / capital, 1)
            score += GHOST_FLAGS["capital_anomaly"]
            flags.append({
                "flag": "capital_anomaly",
                "detail": (
                    f"Contract value (Rs {total_value:.1f} Cr) is {ratio}x "
                    f"the paid-up capital (Rs {capital:.1f} Cr)"
                ),
                "score": GHOST_FLAGS["capital_anomaly"],
            })

        contract_count = int(company.get("contract_count", 0) or 0)
        if contract_count == 1:
            score += GHOST_FLAGS["no_contract_history"]
            flags.append({
                "flag": "no_contract_history",
                "detail": "Only one contract on record — no prior procurement history",
                "score": GHOST_FLAGS["no_contract_history"],
            })

        is_ghost = score >= GHOST_THRESHOLD

        return {
            "company_id":    company.get("id", ""),
            "company_name":  company.get("name", ""),
            "ghost_score":   score,
            "ghost_threshold": GHOST_THRESHOLD,
            "is_flagged":    is_ghost,
            "flags":         flags,
            "flag_count":    len(flags),
            "interpretation": (
                f"Company exhibits {len(flags)} ghost company indicator(s) "
                f"with a structural risk score of {score}/100. "
                "This combination of patterns is associated with shell entities "
                "created specifically for a government procurement event. "
                "This is an analytical indicator, not a legal finding."
                if is_ghost else
                f"Score {score}/100 — below ghost company threshold of {GHOST_THRESHOLD}."
            ),
            "analyzed_at": datetime.now().isoformat(),
        }

    def run_detection(self, companies: list = None) -> list:
        if companies is None:
            companies = self._fetch_companies_with_contracts()

        results = []
        for company in companies:
            result = self.score_company(company)
            if result["is_flagged"]:
                results.append(result)
                logger.warning(
                    f"[GhostCompany] FLAGGED: {result['company_name']} "
                    f"score={result['ghost_score']} flags={result['flag_count']}"
                )

        logger.info(
            f"[GhostCompany] Analysed {len(companies)} companies. "
            f"Flagged: {len(results)}"
        )
        return results


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Ghost Company Detector Test")
    print("=" * 55)

    detector = GhostCompanyDetector(driver=None)

    today = datetime.now()

    test_companies = [
        {
            "id": "C001", "name": "Quick Win Pvt Ltd",
            "reg_date":      (today - timedelta(days=45)).strftime("%Y-%m-%d"),
            "first_contract":(today - timedelta(days=15)).strftime("%Y-%m-%d"),
            "capital": 2.0, "directors": 1,
            "cag_mentions": 0, "sebi_mentions": 0,
            "contract_count": 1, "total_value": 50.0,
        },
        {
            "id": "C002", "name": "Established Builders Ltd",
            "reg_date":      (today - timedelta(days=3650)).strftime("%Y-%m-%d"),
            "first_contract":(today - timedelta(days=500)).strftime("%Y-%m-%d"),
            "capital": 100.0, "directors": 5,
            "cag_mentions": 2, "sebi_mentions": 1,
            "contract_count": 15, "total_value": 450.0,
        },
        {
            "id": "C003", "name": "Shadow Holdings",
            "reg_date":      (today - timedelta(days=30)).strftime("%Y-%m-%d"),
            "first_contract":(today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "capital": 1.0, "directors": 1,
            "cag_mentions": 0, "sebi_mentions": 0,
            "contract_count": 1, "total_value": 25.0,
        },
    ]

    print("\n  Running detection on 3 test companies...")
    results = detector.run_detection(test_companies)

    print(f"\n  Flagged: {len(results)} of {len(test_companies)}")
    for r in results:
        print(f"\n  Company: {r['company_name']}")
        print(f"  Score:   {r['ghost_score']}/100")
        for f in r["flags"]:
            print(f"    [{f['flag']}] {f['detail']}")

    print("\nDone!")
