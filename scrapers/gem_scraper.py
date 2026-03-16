"""
BharatGraph - GeM (Government e-Marketplace) Scraper
Fetches government contract and procurement data.
Source: gem.gov.in + data.gov.in GeM datasets (public)

WHY THIS IS THE MOST IMPORTANT SCRAPER:
GeM is where the government buys everything.
If a politician's relative's company wins contracts here,
that's exactly the pattern BharatGraph needs to flag.

Pattern we're looking for:
Politician → (relative/director) → Company → GeM Contract Won
"""

import json
import re
from datetime import datetime
from scrapers.base_scraper import BaseScraper
from loguru import logger


class GeMScraper(BaseScraper):
    """
    Scrapes procurement contract data from Government e-Marketplace (GeM).

    GeM is India's official online procurement portal.
    All government purchases through GeM are public record.

    Data includes:
    - Contract/order details
    - Buyer (government department)
    - Seller (company that won)
    - Contract value in INR
    - Product/service category
    - Order date

    This is critical for finding:
    - Repeated contract winners
    - Companies linked to politicians winning contracts
    - Unusual concentration of contracts
    """

    # GeM public stats API
    GEM_STATS_URL = "https://mkp.gem.gov.in/api/v2/public/stats"

    # GeM data on data.gov.in
    DATAGOV_BASE   = "https://api.data.gov.in/resource/"
    DATAGOV_APIKEY = os.getenv("DATAGOV_API_KEY", "")

    # GeM dataset resource IDs on data.gov.in
    GEM_DATASETS = {
        "gem_orders": "0a4b1e09-c3e0-4f0a-8f06-4f62a6d08e4e",
    }

    def __init__(self):
        super().__init__(name="gem", delay=2.0)

    def fetch_gem_stats(self) -> dict:
        """
        Fetch public GeM platform statistics.
        Returns total orders, GMV, sellers, buyers count.
        """
        logger.info("[GeM] Fetching platform statistics...")
        data = self.get_json(self.GEM_STATS_URL)

        if data:
            logger.success("[GeM] Stats fetched successfully")
            return {
                "source": "GeM Public Stats",
                "scraped_at": datetime.now().isoformat(),
                "stats": data,
            }

        logger.warning("[GeM] Could not fetch stats, using sample")
        return self._get_sample_stats()

    def fetch_contracts_by_ministry(self, ministry: str = "all",
                                     limit: int = 50) -> list:
        """
        Fetch procurement contracts, optionally filtered by ministry.
        Uses data.gov.in GeM dataset.
        """
        import os
        api_key = os.getenv("DATAGOV_API_KEY", self.DATAGOV_APIKEY)
        logger.info(f"[GeM] Fetching contracts for ministry: {ministry}")

        url = f"{self.DATAGOV_BASE}{self.GEM_DATASETS['gem_orders']}"
        params = {
            "api-key": api_key,
            "format":  "json",
            "limit":   limit,
        }
        if ministry != "all":
            params["filters[ministry_name]"] = ministry

        data = self.get_json(url, params=params)

        if data and "records" in data:
            contracts = self._normalize_contracts(data["records"])
            logger.success(f"[GeM] Got {len(contracts)} contracts")
            return contracts

        logger.warning("[GeM] API unavailable, using sample data")
        return self._get_sample_contracts()

    def _normalize_contracts(self, records: list) -> list:
        """Normalize GeM contract records."""
        contracts = []
        for rec in records:
            contract = {
                "order_id":      rec.get("order_id", rec.get("id", "")),
                "buyer_org":     rec.get("buyer_organisation",
                                         rec.get("ministry", "")),
                "seller_name":   rec.get("seller_name",
                                         rec.get("company_name", "")),
                "seller_gstin":  rec.get("gstin", ""),
                "product":       rec.get("product_name",
                                         rec.get("category", "")),
                "amount_inr":    rec.get("order_value",
                                         rec.get("amount", 0)),
                "order_date":    rec.get("order_date",
                                         rec.get("date", "")),
                "state":         rec.get("buyer_state", ""),
                "source":        "GeM / data.gov.in",
                "scraped_at":    datetime.now().isoformat(),
                "entity_type":   "contract",
            }
            if contract["seller_name"] or contract["order_id"]:
                contracts.append(contract)
        return contracts

    def _get_sample_stats(self) -> dict:
        """Sample GeM statistics for testing."""
        return {
            "source": "GeM Sample Data",
            "scraped_at": datetime.now().isoformat(),
            "stats": {
                "total_orders": 6200000,
                "total_gmv_crore": 285000,
                "total_sellers": 680000,
                "total_buyers": 75000,
                "note": "SAMPLE DATA - real stats at gem.gov.in/statistics",
            },
        }

    def _get_sample_contracts(self) -> list:
        """
        Sample contract structures for graph testing.
        Shows the type of data we'll eventually link to politicians.
        """
        return [
            {
                "order_id":    "GEM/2024/B/12345",
                "buyer_org":   "Ministry of Rural Development",
                "seller_name": "SAMPLE INFRASTRUCTURE PVT LTD",
                "seller_gstin":"33AABCS1234A1Z5",
                "product":     "Construction Services",
                "amount_inr":  15000000,
                "amount_crore": 1.5,
                "order_date":  "2024-03-15",
                "state":       "Tamil Nadu",
                "source":      "GeM (sample)",
                "scraped_at":  datetime.now().isoformat(),
                "entity_type": "contract",
                "note":        "SAMPLE - replace with real GeM fetch",
            },
            {
                "order_id":    "GEM/2024/B/67890",
                "buyer_org":   "Ministry of Health",
                "seller_name": "SAMPLE MEDICAL SUPPLIES LTD",
                "seller_gstin":"27AABCM5678B1Z3",
                "product":     "Medical Equipment",
                "amount_inr":  50000000,
                "amount_crore": 5.0,
                "order_date":  "2024-06-10",
                "state":       "Maharashtra",
                "source":      "GeM (sample)",
                "scraped_at":  datetime.now().isoformat(),
                "entity_type": "contract",
                "note":        "SAMPLE - replace with real GeM fetch",
            },
            {
                "order_id":    "GEM/2024/B/11111",
                "buyer_org":   "Ministry of Rural Development",
                "seller_name": "SAMPLE INFRASTRUCTURE PVT LTD",
                "seller_gstin":"33AABCS1234A1Z5",
                "product":     "Road Construction",
                "amount_inr":  80000000,
                "amount_crore": 8.0,
                "order_date":  "2024-09-20",
                "state":       "Tamil Nadu",
                "source":      "GeM (sample)",
                "scraped_at":  datetime.now().isoformat(),
                "entity_type": "contract",
                "note":        "SAMPLE - same company, 2nd contract (pattern!)",
            },
        ]

    def find_repeated_winners(self, contracts: list) -> dict:
        """
        Find companies that won multiple contracts.
        This is a KEY risk indicator - contract concentration.

        Returns dict of {seller_name: [list of contracts]}
        """
        from collections import defaultdict
        winners = defaultdict(list)

        for c in contracts:
            seller = c.get("seller_name", "").strip()
            if seller:
                winners[seller].append(c)

        # Only return sellers with 2+ contracts
        repeated = {k: v for k, v in winners.items() if len(v) >= 2}

        logger.info(f"[GeM] Repeated contract winners: {len(repeated)}")
        for seller, contracts_list in repeated.items():
            total = sum(float(c.get("amount_crore", 0) or 0)
                       for c in contracts_list)
            logger.info(
                f"  → {seller}: {len(contracts_list)} contracts, "
                f"₹{total:.2f} Cr total"
            )
        return repeated

    def fetch_and_save(self, save: bool = True) -> dict:
        """Fetch contracts + stats and save to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        stats     = self.fetch_gem_stats()
        contracts = self.fetch_contracts_by_ministry(limit=30)
        repeated  = self.find_repeated_winners(contracts)

        result = {
            "stats":            stats,
            "contracts":        contracts,
            "repeated_winners": {
                k: v for k, v in repeated.items()
            },
            "scraped_at": datetime.now().isoformat(),
        }

        if save:
            filepath = f"data/samples/gem_contracts_{timestamp}.json"
            self.save_json(result, filepath)
            logger.success(f"[GeM] Saved to {filepath}")

        return result


# ── Run directly to test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("BharatGraph - GeM Contracts Scraper Test")
    print("=" * 60)

    scraper = GeMScraper()

    print("\n[1] Fetching GeM platform stats...")
    stats = scraper.fetch_gem_stats()
    s = stats.get("stats", {})
    print(f"    Total orders:  {s.get('total_orders', 'N/A'):,}")
    print(f"    Total GMV:     ₹{s.get('total_gmv_crore', 'N/A'):,} Cr")
    print(f"    Total sellers: {s.get('total_sellers', 'N/A'):,}")

    print("\n[2] Fetching contracts...")
    contracts = scraper.fetch_contracts_by_ministry(limit=20)
    print(f"    Total contracts: {len(contracts)}")

    if contracts:
        c = contracts[0]
        print(f"\n    Example contract:")
        print(f"    Order ID:    {c.get('order_id')}")
        print(f"    Buyer:       {c.get('buyer_org')}")
        print(f"    Seller:      {c.get('seller_name')}")
        print(f"    Amount:      ₹{c.get('amount_crore')} Cr")
        print(f"    Date:        {c.get('order_date')}")

    print("\n[3] Finding repeated contract winners (risk indicator)...")
    repeated = scraper.find_repeated_winners(contracts)
    if repeated:
        print(f"    ⚠️  {len(repeated)} companies won multiple contracts!")
    else:
        print("    No repeated winners found in sample")

    print("\n[4] Saving full data...")
    result = scraper.fetch_and_save(save=True)
    print(f"    Contracts saved: {len(result['contracts'])}")
    print(f"    Repeated winners: {len(result['repeated_winners'])}")
    print("\nDone! Check data/samples/ folder.")
