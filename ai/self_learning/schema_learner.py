import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger

KNOWN_POLITICIAN_FIELDS = {
    "id","name","state","party","constituency","criminal_cases",
    "total_assets_crore","movable_assets_crore","education","year",
    "risk_score","risk_level","betweenness_centrality","pagerank",
}
KNOWN_COMPANY_FIELDS = {
    "id","name","state","cin","status","paid_up_capital_crore",
    "industry","registration_date","director_count",
}
KNOWN_CONTRACT_FIELDS = {
    "id","order_id","item_desc","amount_crore","buyer_org",
    "order_date","company_id","ministry","category",
}

PENDING_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "processed", "pending_schema_additions.json"
)

NODE_SCHEMAS = {
    "Politician": KNOWN_POLITICIAN_FIELDS,
    "Company":    KNOWN_COMPANY_FIELDS,
    "Contract":   KNOWN_CONTRACT_FIELDS,
}


class SchemaLearner:

    def detect_new_fields(self, records: list[dict],
                           node_type: str) -> dict:
        known     = NODE_SCHEMAS.get(node_type, set())
        new_found = {}

        for record in records:
            for field, value in record.items():
                if field not in known and field not in new_found:
                    new_found[field] = {
                        "sample_value": str(value)[:100],
                        "node_type":    node_type,
                        "detected_at":  datetime.now().isoformat(),
                        "status":       "pending_review",
                    }

        if new_found:
            logger.info(
                f"[SchemaLearner] {len(new_found)} new fields in {node_type}: "
                f"{list(new_found.keys())}"
            )
            self._write_pending(new_found)

        return new_found

    def _write_pending(self, new_fields: dict):
        existing = {}
        if os.path.exists(PENDING_FILE):
            try:
                existing = json.loads(open(PENDING_FILE,
                                           encoding="utf-8").read())
            except Exception:
                existing = {}

        existing.update(new_fields)
        os.makedirs(os.path.dirname(PENDING_FILE), exist_ok=True)
        with open(PENDING_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        logger.success(
            f"[SchemaLearner] Pending additions written → "
            f"data/processed/pending_schema_additions.json"
        )

    def get_pending(self) -> dict:
        if not os.path.exists(PENDING_FILE):
            return {}
        try:
            return json.loads(open(PENDING_FILE, encoding="utf-8").read())
        except Exception:
            return {}


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Schema Learner Test")
    print("=" * 55)
    learner  = SchemaLearner()
    sample   = [
        {"id": "p001", "name": "Test Politician",
         "state": "Maharashtra", "party": "Test Party",
         "new_field_tax_returns": "filed",
         "foreign_assets_crore": 12.5,
         "spouse_income_crore": 3.2},
    ]
    new = learner.detect_new_fields(sample, "Politician")
    print(f"\n  New fields found: {len(new)}")
    for k, v in new.items():
        print(f"    {k}: {v['sample_value']}")
    print(f"\n  Pending file: {PENDING_FILE}")
    print("\nDone!")
