import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger

SALARY_CRORE_PER_YEAR = {
    "MP": 0.24, "MLA": 0.12, "CM": 0.18,
    "Minister": 0.15, "Unknown": 0.10,
}
INVESTMENT_RETURN_RATE = 0.08
ELECTION_YEARS         = {2004, 2009, 2014, 2019, 2024}


class AffidavitAnalyzer:

    def __init__(self):
        self._Q = 0.001
        self._R = 0.01

    def analyze(self, entity_id: str, history: list[dict],
                 role: str = "Unknown") -> dict:
        logger.info(
            f"[AffidavitAnalyzer] {entity_id}: "
            f"{len(history)} affidavits role={role}"
        )

        if len(history) < 2:
            return {
                "entity_id":   entity_id,
                "status":      "insufficient_data",
                "count":       len(history),
            }

        sorted_h = sorted(history, key=lambda x: x.get("year", 0))
        assets   = [float(a.get("total_assets_crore", 0)) for a in sorted_h]
        years    = [a.get("year", 2024) for a in sorted_h]

        kalman     = self._kalman_filter(assets)
        annual_inc = SALARY_CRORE_PER_YEAR.get(role, 0.10)
        duration   = max(1, years[-1] - years[0])
        expected   = self._expected_growth(assets[0], duration, annual_inc)
        residual   = assets[-1] - expected
        ratio      = residual / expected if expected > 0 else 0.0

        if ratio > 5:
            level = "VERY_HIGH"
        elif ratio > 2:
            level = "HIGH"
        elif ratio > 0.5:
            level = "MODERATE"
        else:
            level = "LOW"

        disappeared = self._find_disappeared(sorted_h)
        surge       = self._election_surge(sorted_h, years)

        findings = []

        if kalman["anomaly_years"]:
            findings.append({
                "type":     "kalman_wealth_anomaly",
                "severity": kalman["anomaly_years"][0]["severity"],
                "description": (
                    f"Kalman filter detected "
                    f"{len(kalman['anomaly_years'])} anomalous jump(s) in "
                    f"declared assets exceeding 3-sigma threshold."
                ),
                "evidence": [
                    f"Step {a['step']}: innovation "
                    f"Rs {a['innovation']:.2f} Cr "
                    f"(threshold Rs {a['threshold']:.2f} Cr)"
                    for a in kalman["anomaly_years"][:3]
                ],
            })

        if level in ("HIGH", "VERY_HIGH"):
            findings.append({
                "type":     "unexplained_wealth",
                "severity": level,
                "description": (
                    f"Asset growth of Rs {assets[-1]-assets[0]:.1f} Cr "
                    f"over {duration} years is {ratio:.1f}x the amount "
                    f"expected from declared income of "
                    f"Rs {annual_inc:.2f} Cr/year."
                ),
                "evidence": [
                    f"Initial assets: Rs {assets[0]:.2f} Cr",
                    f"Final assets:   Rs {assets[-1]:.2f} Cr",
                    f"Expected:       Rs {expected:.2f} Cr",
                    f"Unexplained:    Rs {residual:.2f} Cr",
                ],
            })

        if disappeared:
            findings.append({
                "type":     "asset_disappearance",
                "severity": "MODERATE",
                "description": (
                    f"{len(disappeared)} asset(s) declared in earlier "
                    f"affidavits not found in later filings without "
                    f"documented sale or transfer."
                ),
                "evidence": disappeared[:3],
            })

        if surge:
            findings.append({
                "type":     "pre_election_surge",
                "severity": "HIGH",
                "description": (
                    "Movable assets (cash, jewellery) show a significant "
                    "increase in the affidavit filed immediately before "
                    "an election."
                ),
                "evidence": surge,
            })

        positive = []
        if not findings:
            positive.append(
                "Affidavit trajectory analysis found no anomalies. "
                "Asset growth is consistent with declared income sources."
            )
        elif level == "LOW":
            positive.append(
                "Asset growth is within expected range for declared salary "
                "and investment returns."
            )

        logger.success(
            f"[AffidavitAnalyzer] {entity_id}: level={level} "
            f"residual=Rs {residual:.1f} Cr findings={len(findings)}"
        )

        return {
            "entity_id":         entity_id,
            "affidavit_count":   len(history),
            "years_covered":     years,
            "asset_series":      [round(a, 2) for a in assets],
            "kalman_result":     kalman,
            "expected_crore":    round(expected, 2),
            "actual_growth":     round(assets[-1] - assets[0], 2),
            "residual_crore":    round(residual, 2),
            "residual_ratio":    round(ratio, 2),
            "unexplained_level": level,
            "findings":          findings,
            "positive":          positive,
            "analyzed_at":       datetime.now().isoformat(),
        }

    def _expected_growth(self, initial: float,
                          years: int, annual: float) -> float:
        returns  = initial * ((1 + INVESTMENT_RETURN_RATE) ** years - 1)
        savings  = annual * years * 0.6
        return initial + returns + savings

    def _kalman_filter(self, observations: list[float]) -> dict:
        if len(observations) < 2:
            return {"innovations": [], "anomaly_years": []}

        x_hat = observations[0]
        P     = 1.0
        Q     = self._Q
        R     = self._R

        innovations   = []
        anomaly_years = []

        for k, z in enumerate(observations[1:], 1):
            x_pred = x_hat
            P_pred = P + Q
            S      = P_pred + R
            K      = P_pred / S
            innov  = z - x_pred
            x_hat  = x_pred + K * innov
            P      = (1 - K) * P_pred

            innovations.append(round(innov, 4))
            thresh = 3 * math.sqrt(abs(S))
            if abs(innov) > thresh:
                anomaly_years.append({
                    "step":       k,
                    "innovation": round(innov, 2),
                    "threshold":  round(thresh, 2),
                    "severity":   (
                        "VERY_HIGH" if abs(innov) > 5 * thresh
                        else "HIGH"
                    ),
                })

        return {"innovations": innovations, "anomaly_years": anomaly_years}

    def _find_disappeared(self, history: list[dict]) -> list[str]:
        if len(history) < 2:
            return []
        first = set(history[0].get("properties", {}).keys())
        last  = set(history[-1].get("properties", {}).keys())
        gone  = first - last
        return [
            f"Property '{p}' declared in {history[0].get('year')} "
            f"absent in {history[-1].get('year')}"
            for p in list(gone)[:5]
        ]

    def _election_surge(self, history: list[dict],
                         years: list[int]) -> list[str]:
        surges = []
        for i, a in enumerate(history):
            if a.get("year") in ELECTION_YEARS and i > 0:
                prev = float(history[i-1].get("movable_assets_crore", 0))
                curr = float(a.get("movable_assets_crore", 0))
                if prev > 0 and curr > prev * 1.5:
                    pct = (curr / prev - 1) * 100
                    surges.append(
                        f"Movable: Rs {prev:.2f} Cr → Rs {curr:.2f} Cr "
                        f"(+{pct:.0f}%) before {a.get('year')} election"
                    )
        return surges


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Affidavit Analyzer Test")
    print("=" * 55)
    a = AffidavitAnalyzer()
    sample = [
        {"year":2009,"total_assets_crore":1.2,"movable_assets_crore":0.3,
         "properties":{"plotA":"Plot A, Sector 5"}},
        {"year":2014,"total_assets_crore":8.5,"movable_assets_crore":2.1,
         "properties":{"plotA":"Plot A"}},
        {"year":2019,"total_assets_crore":22.4,"movable_assets_crore":6.8,
         "properties":{}},
        {"year":2024,"total_assets_crore":48.7,"movable_assets_crore":12.3,
         "properties":{}},
    ]
    r = a.analyze("pol_test", sample, "MP")
    print(f"\n  Years:         {r['years_covered']}")
    print(f"  Asset series:  {r['asset_series']}")
    print(f"  Expected:      Rs {r['expected_crore']} Cr")
    print(f"  Residual:      Rs {r['residual_crore']} Cr ({r['residual_ratio']}x)")
    print(f"  Level:         {r['unexplained_level']}")
    print(f"  Kalman anomaly:{len(r['kalman_result']['anomaly_years'])}")
    print(f"  Findings:      {len(r['findings'])}")
    for f in r["findings"]:
        print(f"    [{f['severity']}] {f['type']}: {f['description'][:65]}")
    print("\nDone!")
