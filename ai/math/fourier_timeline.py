import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger


class FourierTimelineAnalyzer:

    def __init__(self):
        self._np = None
        try:
            import numpy as np
            self._np = np
            logger.success("[Fourier] NumPy loaded")
        except ImportError as e:
            logger.warning(f"[Fourier] NumPy not available: {e}")

    def analyze(self, entity_id: str, contract_events: list[dict]) -> dict:
        logger.info(f"[Fourier] Analyzing {len(contract_events)} events for {entity_id}")

        if self._np is None:
            return {"entity_id": entity_id, "status": "unavailable"}

        if len(contract_events) < 4:
            return {"entity_id": entity_id, "status": "insufficient_data",
                    "event_count": len(contract_events)}

        np     = self._np
        events = sorted(contract_events, key=lambda e: e.get("date", ""))
        amounts = np.array([float(e.get("amount_crore", 0)) for e in events])

        fft_result  = np.fft.rfft(amounts)
        power       = np.abs(fft_result) ** 2
        n           = len(amounts)
        frequencies = np.fft.rfftfreq(n)

        dominant_idx   = int(np.argmax(power[1:]) + 1)
        dominant_freq  = float(frequencies[dominant_idx])
        dominant_power = float(power[dominant_idx])
        total_power    = float(np.sum(power[1:]))
        concentration  = dominant_power / total_power if total_power > 0 else 0.0

        if concentration > 0.6:
            pattern = "HIGHLY_PERIODIC"
            severity = "HIGH"
        elif concentration > 0.3:
            pattern = "MODERATELY_PERIODIC"
            severity = "MODERATE"
        else:
            pattern = "RANDOM"
            severity = "LOW"

        if dominant_freq > 0:
            period_events = round(1.0 / dominant_freq)
        else:
            period_events = 0

        findings = []
        if pattern in ("HIGHLY_PERIODIC", "MODERATELY_PERIODIC"):
            findings.append({
                "type":        "periodic_contract_pattern",
                "severity":    severity,
                "description": (
                    f"Fourier analysis of {n} contract events reveals a {pattern} "
                    f"pattern. Dominant frequency at every ~{period_events} events "
                    f"with {concentration*100:.1f}% power concentration. "
                    "Regular periodicity in contract awards may indicate a scheduled "
                    "arrangement rather than competitive procurement."
                ),
                "evidence": [
                    f"Dominant frequency: {dominant_freq:.4f} cycles/event",
                    f"Power concentration: {concentration*100:.1f}%",
                    f"Pattern period: ~{period_events} contract events",
                ],
            })

        fiscal_spike = self._detect_fiscal_year_spike(events)
        if fiscal_spike:
            findings.append(fiscal_spike)

        logger.success(
            f"[Fourier] {entity_id}: pattern={pattern} "
            f"concentration={concentration:.2f} findings={len(findings)}"
        )

        return {
            "entity_id":        entity_id,
            "event_count":      n,
            "pattern":          pattern,
            "dominant_freq":    round(dominant_freq, 6),
            "power_concentration": round(concentration, 4),
            "period_events":    period_events,
            "findings":         findings,
            "analyzed_at":      datetime.now().isoformat(),
        }

    def _detect_fiscal_year_spike(self, events: list[dict]) -> dict | None:
        march_events = [e for e in events if e.get("date","")[-5:] in
                        ("02-28","02-29","03-01","03-15","03-31","03-30")]
        if len(march_events) >= 2 and len(march_events) / len(events) > 0.3:
            return {
                "type":        "fiscal_year_end_spike",
                "severity":    "MODERATE",
                "description": (
                    f"{len(march_events)} of {len(events)} contracts awarded in "
                    "February/March (fiscal year end). Concentrated fiscal-year-end "
                    "spending may indicate budget utilisation pressure rather than "
                    "genuine procurement need."
                ),
                "evidence": [f"Fiscal year-end contracts: {len(march_events)}/{len(events)}"],
            }
        return None


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Fourier Timeline Analyzer Test")
    print("=" * 55)
    import math
    a = FourierTimelineAnalyzer()

    periodic_events = [
        {"date": f"2022-{(i*3)%12+1:02d}-15", "amount_crore": 10 + 5*math.sin(i*math.pi/3)}
        for i in range(12)
    ]
    r = a.analyze("test_entity_001", periodic_events)
    print(f"\n  Events:       {r['event_count']}")
    print(f"  Pattern:      {r['pattern']}")
    print(f"  Concentration:{r['power_concentration']:.2f}")
    print(f"  Period:       ~{r['period_events']} events")
    print(f"  Findings:     {len(r['findings'])}")
    for f in r['findings']:
        print(f"    [{f['severity']}] {f['description'][:70]}")
    print("\nDone!")
