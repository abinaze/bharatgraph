import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger

FORBIDDEN = {
    "corrupt","bribe","guilty","criminal","illegal","fraud",
    "suspect","launder","steal","theft","scam","embezzle",
}

CATEGORY_LABELS = {
    "political":  "Parliamentary and Electoral Activity",
    "financial":  "Financial and Procurement Activity",
    "regulatory": "Regulatory and Audit Activity",
    "legal":      "Legal Proceedings",
    "corporate":  "Corporate Directorships",
    "media":      "Official Communications",
}


class BiographyGenerator:

    def generate(self, entity_name: str, timeline: dict,
                  convergences: dict, risk_score: int = 0) -> dict:
        logger.info(f"[BiographyGenerator] Generating biography: {entity_name}")

        events      = timeline.get("events", [])
        by_year     = timeline.get("by_year", {})
        conv_list   = convergences.get("convergences", [])
        event_count = len(events)
        year_count  = len(by_year)

        categories  = {}
        for e in events:
            cat = e.get("category", "other")
            categories.setdefault(cat, []).append(e)

        sections  = []
        full_text = []

        intro = self._safe(
            f"{entity_name} has an institutional record spanning "
            f"{year_count} years across {event_count} documented events "
            f"derived from {self._source_count(events)} official sources. "
            f"The following summary is based entirely on public records."
        )
        sections.append({"heading": "Overview", "text": intro})
        full_text.append(intro)

        if by_year:
            first_year = min(by_year.keys())
            last_year  = max(by_year.keys())
            span_text  = self._safe(
                f"The earliest recorded institutional activity dates to {first_year}. "
                f"The most recent entry is from {last_year}."
            )
            sections.append({"heading": "Timeline Span", "text": span_text})
            full_text.append(span_text)

        for cat, label in CATEGORY_LABELS.items():
            cat_events = categories.get(cat, [])
            if not cat_events:
                continue
            text = self._summarise_category(cat, cat_events, entity_name)
            if text:
                sections.append({"heading": label, "text": text})
                full_text.append(text)

        if conv_list:
            high = [c for c in conv_list if c["severity"] == "HIGH"]
            text = self._safe(
                f"Temporal analysis identified {len(conv_list)} event convergences "
                f"where two institutionally significant events occurred within "
                f"defined time windows. Of these, {len(high)} are classified as "
                f"high-proximity convergences requiring further contextual examination."
            )
            if high:
                text += " The most notable: " + self._safe(
                    f"{high[0]['event_a']} and {high[0]['event_b']} "
                    f"occurred {high[0]['gap_days']} days apart."
                )
            sections.append({"heading": "Temporal Convergences", "text": text})
            full_text.append(text)

        disclaimer = (
            "This biography is generated from public institutional records. "
            "All findings are structural indicators derived from official data. "
            "No legal conclusions are drawn. Outputs are provided for research "
            "and public interest journalism."
        )
        sections.append({"heading": "Disclaimer", "text": disclaimer})

        logger.success(
            f"[BiographyGenerator] Generated {len(sections)} sections "
            f"for {entity_name}"
        )

        return {
            "entity_name":   entity_name,
            "section_count": len(sections),
            "sections":      sections,
            "full_text":     "\n\n".join(full_text),
            "event_count":   event_count,
            "year_span":     f"{min(by_year.keys()) if by_year else '?'}–{max(by_year.keys()) if by_year else '?'}",
            "generated_at":  datetime.now().isoformat(),
        }

    def _summarise_category(self, cat: str, events: list,
                              name: str) -> str:
        n = len(events)
        if cat == "political":
            years = sorted(set(e["date"][:4] for e in events if e.get("date")))
            return self._safe(
                f"{name} has {n} recorded electoral or parliamentary events "
                f"across the years {', '.join(years)}."
            )
        elif cat == "financial":
            total = sum(float(e.get("amount") or 0) for e in events)
            return self._safe(
                f"Records show {n} procurement-related events. "
                f"Total contract value associated with linked entities: "
                f"Rs {total:.1f} Cr."
            ) if total > 0 else self._safe(
                f"Records show {n} procurement-related events."
            )
        elif cat == "regulatory":
            return self._safe(
                f"{n} regulatory or audit document(s) reference this entity "
                f"or associated schemes."
            )
        elif cat == "legal":
            return self._safe(
                f"{n} court proceeding record(s) are associated with this entity."
            )
        elif cat == "corporate":
            cos = list(set(e.get("detail","") for e in events))[:3]
            return self._safe(
                f"{name} holds or has held directorships in "
                f"{n} registered company/companies per MCA21 records."
            )
        return ""

    def _source_count(self, events: list) -> int:
        return len(set(e.get("source","") for e in events if e.get("source")))

    def _safe(self, text: str) -> str:
        for w in FORBIDDEN:
            text = text.replace(w, "[redacted]")
        return text
