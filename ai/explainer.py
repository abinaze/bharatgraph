import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


RISK_LEVELS = {
    (0,  30):  "LOW",
    (31, 60):  "MODERATE",
    (61, 80):  "HIGH",
    (81, 100): "VERY_HIGH",
}

FORBIDDEN_WORDS = [
    "corrupt", "bribe", "guilty", "criminal", "illegal",
    "fraud", "suspect", "launder", "steal", "theft",
]


def score_to_level(score: int) -> str:
    for (lo, hi), level in RISK_LEVELS.items():
        if lo <= score <= hi:
            return level
    return "UNKNOWN"


def generate_explanation(entity_name: str, score: int,
                          factors: list) -> str:
    level  = score_to_level(score)
    active = [f for f in factors if f["raw_score"] > 0]

    if score == 0 or not active:
        return (
            f"No structural indicators were identified for {entity_name} "
            "in the current dataset. Limited data coverage may affect this result."
        )

    factor_names = [f["name"].replace("_", " ") for f in active]
    factor_list  = ", ".join(factor_names)

    if level == "LOW":
        return (
            f"Low structural indicators detected for {entity_name}. "
            f"{len(active)} pattern(s) identified: {factor_list}. "
            "Signals are within normal range for publicly available data."
        )
    if level == "MODERATE":
        return (
            f"Moderate structural indicators detected for {entity_name}. "
            f"{len(active)} pattern(s) identified: {factor_list}. "
            "Further review of the associated evidence is warranted. "
            "This is an analytical observation based on public records."
        )
    if level == "HIGH":
        return (
            f"High structural indicators detected for {entity_name}. "
            f"{len(active)} significant pattern(s) identified: {factor_list}. "
            "The combination of these indicators across procurement and audit "
            "data warrants investigative attention. "
            "This is an analytical indicator derived from official public records, "
            "not a legal finding."
        )
    return (
        f"Very high structural indicators detected for {entity_name}. "
        f"{len(active)} strong pattern(s) identified: {factor_list}. "
        "Multiple overlapping patterns across procurement, audit, and disclosure "
        "data are present. All findings are based on official public records. "
        "This is a statistical structural indicator, not a legal determination."
    )


def validate_language(text: str) -> str:
    text_lower = text.lower()
    for word in FORBIDDEN_WORDS:
        if word in text_lower:
            raise ValueError(
                f"Output contains prohibited accusatory term '{word}'. "
                "Revise to use neutral analytical language."
            )
    return text
