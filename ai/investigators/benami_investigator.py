import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger

NAME   = "BenamiInvestigator"
FOCUS  = "benami_proxy_detection"
WEIGHT = 0.09


def investigate(entity_id: str, entity_name: str,
                session=None, driver=None) -> dict:
    logger.info(f"[{NAME}] Investigating {entity_name}")

    findings = []
    positive = []
    evidence = []

    try:
        from ai.forensics.benami_detector import BenamiDetector
        detector = BenamiDetector()
        result   = detector.analyze(entity_id, entity_name, driver=driver)

        findings.extend(result.get("findings", []))
        positive.extend(result.get("positive", []))

        evidence.append({
            "institution": "Ministry of Corporate Affairs",
            "document":    "MCA21 Director and Company Records",
            "url":         "https://www.mca.gov.in",
            "method":      "5-factor benami proxy scoring",
            "score":       result.get("benami_score", 0),
            "level":       result.get("benami_level", "LOW"),
        })

    except Exception as e:
        logger.warning(f"[{NAME}] Analysis failed: {e}")
        positive.append("Benami analysis could not be completed.")

    logger.success(f"[{NAME}] Complete: {len(findings)} findings")

    return {
        "investigator":    NAME,
        "focus":           FOCUS,
        "weight":          WEIGHT,
        "findings":        findings,
        "positive":        positive,
        "evidence":        evidence,
        "investigated_at": datetime.now().isoformat(),
    }
