import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import math
from datetime import datetime
from loguru import logger


BENFORD_DISTRIBUTION = {
    1: 0.30103,
    2: 0.17609,
    3: 0.12494,
    4: 0.09691,
    5: 0.07918,
    6: 0.06695,
    7: 0.05799,
    8: 0.05115,
    9: 0.04576,
}

SIGNIFICANCE_THRESHOLD = 15.507


class BenfordsAnalyzer:

    def __init__(self):
        self.benford = BENFORD_DISTRIBUTION

    def extract_numeric_values(self, text: str) -> list:
        pattern = re.compile(
            r"(?:Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*"
            r"(?:crore|lakh|cr|L|thousand)?",
            re.IGNORECASE,
        )
        values = []
        for match in pattern.finditer(text):
            raw = match.group(1).replace(",", "")
            try:
                val = float(raw)
                if val >= 1:
                    values.append(val)
            except ValueError:
                continue
        return values

    def get_first_digit(self, value: float) -> int:
        if value <= 0:
            return 0
        s = str(abs(value)).lstrip("0").replace(".", "")
        return int(s[0]) if s else 0

    def analyze(self, values: list) -> dict:
        if len(values) < 20:
            return {
                "status":           "insufficient_data",
                "sample_size":      len(values),
                "minimum_required": 20,
                "anomaly_detected": False,
                "analyzed_at":      datetime.now().isoformat(),
            }

        digit_counts = {d: 0 for d in range(1, 10)}
        for val in values:
            d = self.get_first_digit(val)
            if d in digit_counts:
                digit_counts[d] += 1

        n = sum(digit_counts.values())
        chi_squared = 0.0
        observed_dist = {}
        for digit in range(1, 10):
            observed     = digit_counts[digit]
            expected     = self.benford[digit] * n
            observed_pct = observed / n if n > 0 else 0
            observed_dist[digit] = round(observed_pct, 5)
            if expected > 0:
                chi_squared += ((observed - expected) ** 2) / expected

        anomalous_digits = []
        for digit in range(1, 10):
            observed_pct = observed_dist[digit]
            expected_pct = self.benford[digit]
            deviation    = abs(observed_pct - expected_pct)
            if deviation > 0.05:
                anomalous_digits.append({
                    "digit":        digit,
                    "observed_pct": round(observed_pct * 100, 2),
                    "expected_pct": round(expected_pct * 100, 2),
                    "deviation_pct":round(deviation * 100, 2),
                })

        anomaly_detected = chi_squared > SIGNIFICANCE_THRESHOLD

        if anomaly_detected:
            logger.warning(
                f"[Benford] ANOMALY: chi-squared={chi_squared:.2f} "
                f"(threshold={SIGNIFICANCE_THRESHOLD}) n={n}"
            )
        else:
            logger.info(
                f"[Benford] NORMAL: chi-squared={chi_squared:.2f} n={n}"
            )

        return {
            "status":              "completed",
            "sample_size":         n,
            "chi_squared":         round(chi_squared, 4),
            "significance_threshold": SIGNIFICANCE_THRESHOLD,
            "anomaly_detected":    anomaly_detected,
            "confidence":          "high" if n >= 100 else "moderate" if n >= 30 else "low",
            "observed_distribution": observed_dist,
            "expected_distribution": {d: round(v, 5) for d, v in self.benford.items()},
            "anomalous_digits":    anomalous_digits,
            "interpretation": (
                "First-digit distribution deviates significantly from Benford's Law. "
                "This is a statistical anomaly indicator warranting further review. "
                "Possible causes include rounding of declared figures, threshold avoidance, "
                "or systematic manipulation of values."
                if anomaly_detected else
                "First-digit distribution is consistent with Benford's Law. "
                "No statistical anomaly detected in this dataset."
            ),
            "analyzed_at": datetime.now().isoformat(),
        }

    def analyze_affidavit_assets(self, asset_records: list) -> dict:
        values = []
        for record in asset_records:
            raw = str(record.get("total_assets", "") or record.get("assets", ""))
            extracted = self.extract_numeric_values(raw)
            values.extend(extracted)

        logger.info(
            f"[Benford] Analyzing {len(values)} numeric values "
            f"from {len(asset_records)} affidavit records"
        )
        result = self.analyze(values)
        result["source"]      = "Election Commission of India candidate affidavits"
        result["record_count"]= len(asset_records)
        return result


if __name__ == "__main__":
    import random
    print("=" * 55)
    print("BharatGraph - Benford's Law Analyzer Test")
    print("=" * 55)

    analyzer = BenfordsAnalyzer()

    print("\n  Test 1: Naturally distributed values (should pass)")
    natural = []
    for _ in range(200):
        magnitude = random.uniform(0, 7)
        val = 10 ** magnitude
        natural.append(val)
    result1 = analyzer.analyze(natural)
    print(f"  Chi-squared: {result1['chi_squared']}")
    print(f"  Anomaly:     {result1['anomaly_detected']}")

    print("\n  Test 2: Manipulated values (clustered near thresholds)")
    manipulated = []
    for _ in range(100):
        manipulated.append(random.uniform(990000, 999999))
    for _ in range(100):
        manipulated.append(random.uniform(9800000, 9999999))
    result2 = analyzer.analyze(manipulated)
    print(f"  Chi-squared: {result2['chi_squared']}")
    print(f"  Anomaly:     {result2['anomaly_detected']}")

    print("\n  Test 3: Affidavit asset analysis")
    sample_records = [
        {"name": "Candidate A", "total_assets": "Rs 45 lakh"},
        {"name": "Candidate B", "total_assets": "Rs 1.2 crore"},
        {"name": "Candidate C", "total_assets": "Rs 99 lakh"},
    ]
    result3 = analyzer.analyze_affidavit_assets(sample_records)
    print(f"  Sample size: {result3['sample_size']}")
    print(f"  Status:      {result3['status']}")

    print("\nDone!")
