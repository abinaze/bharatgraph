import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, date
from loguru import logger

CONVERGENCE_WINDOWS = [
    ("election",  "contract",   90,  "Contract awarded within 90 days of election"),
    ("election",  "company",    180, "Company formed within 180 days of election"),
    ("audit",     "contract",   365, "Contract awarded within year of audit flag"),
    ("court",     "company",    180, "Company formed within 180 days of court case"),
    ("election",  "audit",      365, "Audit mention within year of election"),
]


class ConvergenceDetector:

    def detect(self, events: list[dict]) -> dict:
        logger.info(f"[ConvergenceDetector] Scanning {len(events)} events")

        convergences = []

        for i, e1 in enumerate(events):
            for e2 in events[i+1:]:
                for t1, t2, window, desc in CONVERGENCE_WINDOWS:
                    if not (e1.get("type") == t1 and e2.get("type") == t2):
                        continue
                    gap = self._day_gap(e1.get("date",""), e2.get("date",""))
                    if gap is None or gap < 0:
                        continue
                    if gap <= window:
                        severity = (
                            "HIGH"     if gap <= window // 3  else
                            "MODERATE" if gap <= window // 2  else
                            "LOW"
                        )
                        convergences.append({
                            "event_a":     e1.get("title",""),
                            "date_a":      e1.get("date",""),
                            "event_b":     e2.get("title",""),
                            "date_b":      e2.get("date",""),
                            "gap_days":    gap,
                            "window_days": window,
                            "description": desc,
                            "severity":    severity,
                            "source_a":    e1.get("source",""),
                            "source_b":    e2.get("source",""),
                        })

        convergences.sort(key=lambda x: x["gap_days"])

        logger.success(
            f"[ConvergenceDetector] {len(convergences)} temporal convergences found"
        )
        return {
            "convergence_count": len(convergences),
            "convergences":      convergences,
            "high_count":        sum(1 for c in convergences if c["severity"]=="HIGH"),
            "detected_at":       datetime.now().isoformat(),
        }

    def _day_gap(self, date_a: str, date_b: str) -> int | None:
        try:
            d1 = date.fromisoformat(date_a[:10])
            d2 = date.fromisoformat(date_b[:10])
            return abs((d2 - d1).days)
        except Exception:
            return None
