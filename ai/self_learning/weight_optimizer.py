import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger

WEIGHTS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "processed", "indicator_weights.json"
)

DEFAULT_WEIGHTS = {
    "politician_company_overlap": 0.35,
    "contract_concentration":     0.25,
    "audit_mention_frequency":    0.20,
    "asset_growth_anomaly":       0.15,
    "criminal_case_presence":     0.05,
}

MIN_CONFIRMATIONS = 3
DELTA_INCREASE    = 0.01
DELTA_DECREASE    = 0.005


class WeightOptimizer:

    def __init__(self):
        self.weights      = self._load_weights()
        self.outcomes     = self._load_outcomes()

    def _load_weights(self) -> dict:
        if os.path.exists(WEIGHTS_FILE):
            try:
                data = json.loads(open(WEIGHTS_FILE, encoding="utf-8").read())
                return data.get("weights", DEFAULT_WEIGHTS.copy())
            except Exception:
                pass
        return DEFAULT_WEIGHTS.copy()

    def _load_outcomes(self) -> list:
        if os.path.exists(WEIGHTS_FILE):
            try:
                data = json.loads(open(WEIGHTS_FILE, encoding="utf-8").read())
                return data.get("outcomes", [])
            except Exception:
                pass
        return []

    def record_outcome(self, entity_id: str, indicator_fired: list[str],
                        confirmed: bool) -> None:
        self.outcomes.append({
            "entity_id":      entity_id,
            "indicator_fired":indicator_fired,
            "confirmed":      confirmed,
            "recorded_at":    datetime.now().isoformat(),
        })
        self._save()
        logger.info(
            f"[WeightOptimizer] Outcome recorded: {entity_id} "
            f"confirmed={confirmed} indicators={indicator_fired}"
        )

    def optimize(self) -> dict:
        confirmed   = [o for o in self.outcomes if o["confirmed"]]
        unconfirmed = [o for o in self.outcomes if not o["confirmed"]]

        if len(confirmed) < MIN_CONFIRMATIONS:
            logger.info(
                f"[WeightOptimizer] Only {len(confirmed)} confirmed outcomes. "
                f"Need {MIN_CONFIRMATIONS} before adjusting weights."
            )
            return {"adjusted": False, "reason": "insufficient_confirmations",
                    "confirmed_count": len(confirmed)}

        changes = {}
        for indicator in DEFAULT_WEIGHTS:
            fired_confirmed   = sum(1 for o in confirmed
                                    if indicator in o.get("indicator_fired", []))
            fired_unconfirmed = sum(1 for o in unconfirmed
                                    if indicator in o.get("indicator_fired", []))

            old_weight = self.weights.get(indicator, DEFAULT_WEIGHTS[indicator])

            if fired_confirmed > fired_unconfirmed:
                new_weight = min(0.50, old_weight + DELTA_INCREASE)
            elif fired_unconfirmed > fired_confirmed:
                new_weight = max(0.01, old_weight - DELTA_DECREASE)
            else:
                new_weight = old_weight

            if abs(new_weight - old_weight) > 0.0001:
                changes[indicator] = {
                    "old": round(old_weight, 4),
                    "new": round(new_weight, 4),
                    "delta": round(new_weight - old_weight, 4),
                }
                self.weights[indicator] = new_weight

        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: round(v/total, 4) for k,v in self.weights.items()}

        self._save()
        logger.success(
            f"[WeightOptimizer] Weights adjusted: {len(changes)} changes. "
            f"Pending human approval."
        )

        return {
            "adjusted":         len(changes) > 0,
            "changes":          changes,
            "new_weights":      self.weights,
            "confirmed_cases":  len(confirmed),
            "optimized_at":     datetime.now().isoformat(),
            "note":             "Changes require human approval before deployment.",
        }

    def _save(self):
        os.makedirs(os.path.dirname(WEIGHTS_FILE), exist_ok=True)
        with open(WEIGHTS_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "weights":      self.weights,
                "outcomes":     self.outcomes,
                "last_updated": datetime.now().isoformat(),
            }, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Weight Optimizer Test")
    print("=" * 55)
    opt = WeightOptimizer()
    print(f"\n  Current weights:")
    for k, v in opt.weights.items():
        print(f"    {k}: {v}")

    for i in range(4):
        opt.record_outcome(
            f"test_entity_{i:03d}",
            ["politician_company_overlap", "contract_concentration"],
            confirmed=True
        )
    opt.record_outcome("test_entity_004",
                       ["asset_growth_anomaly"], confirmed=False)

    result = opt.optimize()
    print(f"\n  Adjusted: {result['adjusted']}")
    print(f"  Confirmed cases: {result['confirmed_cases']}")
    if result.get("changes"):
        for k, v in result["changes"].items():
            print(f"  {k}: {v['old']} → {v['new']} ({v['delta']:+.4f})")
    print("\nDone!")
