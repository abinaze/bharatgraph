import os, sys, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger

CASE_STORE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "processed", "case_memory.json"
)


class CaseStore:

    def __init__(self):
        self._store = self._load()

    def _load(self) -> dict:
        if os.path.exists(CASE_STORE_FILE):
            try:
                return json.loads(open(CASE_STORE_FILE, encoding="utf-8").read())
            except Exception:
                pass
        return {"cases": {}, "patterns": {}, "false_positives": []}

    def _save(self):
        os.makedirs(os.path.dirname(CASE_STORE_FILE), exist_ok=True)
        with open(CASE_STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(self._store, f, indent=2, ensure_ascii=False)

    def save_case(self, entity_id: str, entity_name: str,
                   findings: list[dict], outcome: str,
                   reasoning_path: list[str]) -> str:
        case_id = hashlib.sha256(
            f"{entity_id}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        self._store["cases"][case_id] = {
            "entity_id":     entity_id,
            "entity_name":   entity_name,
            "findings":      findings,
            "outcome":       outcome,
            "reasoning_path":reasoning_path,
            "saved_at":      datetime.now().isoformat(),
        }

        for finding in findings:
            ftype = finding.get("type", "unknown")
            if ftype not in self._store["patterns"]:
                self._store["patterns"][ftype] = {
                    "count": 0, "confirmed": 0, "false_positives": 0
                }
            self._store["patterns"][ftype]["count"] += 1
            if outcome == "confirmed":
                self._store["patterns"][ftype]["confirmed"] += 1

        self._save()
        logger.info(f"[CaseStore] Saved case {case_id} for {entity_name}")
        return case_id

    def find_similar(self, findings: list[dict],
                      limit: int = 5) -> list[dict]:
        query_types = {f.get("type") for f in findings}
        similar     = []

        for case_id, case in self._store["cases"].items():
            case_types = {f.get("type") for f in case.get("findings", [])}
            overlap    = len(query_types & case_types)
            if overlap > 0:
                similar.append({
                    "case_id":     case_id,
                    "entity_name": case["entity_name"],
                    "overlap":     overlap,
                    "outcome":     case["outcome"],
                    "reasoning":   case["reasoning_path"][:3],
                })

        similar.sort(key=lambda x: -x["overlap"])
        return similar[:limit]

    def record_false_positive(self, finding_type: str,
                               reason: str) -> None:
        self._store["false_positives"].append({
            "finding_type": finding_type,
            "reason":       reason,
            "recorded_at":  datetime.now().isoformat(),
        })
        if finding_type in self._store["patterns"]:
            self._store["patterns"][finding_type]["false_positives"] += 1
        self._save()
        logger.info(f"[CaseStore] False positive recorded: {finding_type}")

    def get_pattern_stats(self) -> dict:
        return self._store["patterns"]

    def get_case_count(self) -> int:
        return len(self._store["cases"])


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Case Store Test")
    print("=" * 55)
    store = CaseStore()

    sample_findings = [
        {"type":"contract_concentration","severity":"HIGH",
         "description":"3 contracts from same ministry"},
        {"type":"ghost_company","severity":"HIGH",
         "description":"Company formed 5 days before contract"},
    ]
    cid = store.save_case(
        "test_001", "Test Politician", sample_findings,
        "confirmed", ["contract_concentration → ghost_company → HIGH risk"]
    )
    print(f"\n  Case saved: {cid}")
    print(f"  Total cases: {store.get_case_count()}")
    print(f"  Pattern stats: {store.get_pattern_stats()}")

    similar = store.find_similar([{"type":"contract_concentration"}])
    print(f"  Similar cases: {len(similar)}")
    print("\nDone!")
