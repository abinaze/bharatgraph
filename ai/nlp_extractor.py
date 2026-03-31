import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from datetime import datetime
from loguru import logger


ENTITY_LABELS = {"PERSON", "ORG", "GPE", "MONEY", "DATE", "LAW"}

MONETARY_PATTERN = re.compile(
    r"(?:Rs\.?|INR|rupees?)\s*[\d,]+(?:\.\d+)?\s*(?:crore|lakh|thousand|cr|L)?",
    re.IGNORECASE,
)

HONORIFICS = re.compile(
    r"\b(?:Shri|Smt|Dr|Prof|Sri|Mr|Mrs|Ms|Hon|Adv|Er)\.?\s+",
    re.IGNORECASE,
)


class NLPExtractor:

    def __init__(self):
        self._nlp = None
        self._load_model()

    def _load_model(self):
        try:
            import spacy
            self._nlp = spacy.load("en_core_web_sm")
            logger.success("[NLP] spaCy en_core_web_sm loaded")
        except Exception as e:
            logger.warning(f"[NLP] spaCy model not available: {e}")
            logger.warning("[NLP] Run: python -m spacy download en_core_web_sm")
            self._nlp = None

    def extract_entities(self, text: str, source_document: str = "") -> list:
        if not text or not text.strip():
            return []

        entities = []

        monetary = MONETARY_PATTERN.findall(text)
        for m in monetary:
            entities.append({
                "text":        m.strip(),
                "label":       "MONEY",
                "confidence":  "pattern_match",
                "source_doc":  source_document,
                "extracted_at":datetime.now().isoformat(),
            })

        if self._nlp:
            doc = self._nlp(text[:100000])
            for ent in doc.ents:
                if ent.label_ not in ENTITY_LABELS:
                    continue
                clean_text = HONORIFICS.sub("", ent.text).strip()
                if len(clean_text) < 3:
                    continue
                entities.append({
                    "text":        clean_text,
                    "label":       ent.label_,
                    "confidence":  "spacy_ner",
                    "source_doc":  source_document,
                    "extracted_at":datetime.now().isoformat(),
                })
        else:
            person_pattern = re.compile(
                r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b"
            )
            for match in person_pattern.finditer(text):
                name = match.group(1)
                if len(name.split()) >= 2:
                    entities.append({
                        "text":        name,
                        "label":       "PERSON",
                        "confidence":  "regex_fallback",
                        "source_doc":  source_document,
                        "extracted_at":datetime.now().isoformat(),
                    })

        seen = set()
        unique = []
        for e in entities:
            key = (e["text"].lower(), e["label"])
            if key not in seen:
                seen.add(key)
                unique.append(e)

        logger.info(
            f"[NLP] Extracted {len(unique)} entities from "
            f"'{source_document or 'text'}' "
            f"({len([e for e in unique if e['label']=='PERSON'])} persons, "
            f"{len([e for e in unique if e['label']=='ORG'])} orgs, "
            f"{len([e for e in unique if e['label']=='MONEY'])} amounts)"
        )
        return unique

    def extract_from_cag_report(self, report_text: str,
                                 report_title: str = "") -> dict:
        entities = self.extract_entities(report_text, report_title)
        amounts  = [e for e in entities if e["label"] == "MONEY"]
        persons  = [e for e in entities if e["label"] == "PERSON"]
        orgs     = [e for e in entities if e["label"] == "ORG"]
        locations= [e for e in entities if e["label"] == "GPE"]

        return {
            "report_title":  report_title,
            "total_entities":len(entities),
            "persons":       persons,
            "organisations": orgs,
            "locations":     locations,
            "monetary":      amounts,
            "all_entities":  entities,
            "extracted_at":  datetime.now().isoformat(),
        }

    def resolve_against_graph(self, entities: list, driver) -> list:
        resolved = []
        if not driver:
            return entities

        with driver.session() as session:
            for entity in entities:
                if entity["label"] not in ("PERSON", "ORG"):
                    resolved.append({**entity, "graph_match": None})
                    continue

                label = "Politician" if entity["label"] == "PERSON" else "Company"
                row = session.run(
                    f"""
                    MATCH (n:{label})
                    WHERE toLower(n.name) CONTAINS toLower($name)
                    RETURN n.id AS id, n.name AS name
                    LIMIT 1
                    """,
                    name=entity["text"]
                ).single()

                resolved.append({
                    **entity,
                    "graph_match": {
                        "id":   row["id"],
                        "name": row["name"],
                    } if row else None,
                })
        return resolved


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - NLP Extractor Test")
    print("=" * 55)

    extractor = NLPExtractor()

    sample_text = """
    The Comptroller and Auditor General of India has flagged irregularities
    in the implementation of MGNREGA scheme in Karnataka. Minister Rajesh Kumar
    and senior IAS officer Priya Sharma were found responsible for the diversion
    of Rs 45.6 crore from the Rural Development Ministry. ABC Infrastructure
    Private Limited received contracts worth Rs 120 crore without proper tender.
    The funds were disbursed between January 2021 and March 2023.
    """

    result = extractor.extract_from_cag_report(sample_text, "CAG Report Sample")
    print(f"\n  Total entities extracted: {result['total_entities']}")
    print(f"  Persons:       {len(result['persons'])}")
    print(f"  Organisations: {len(result['organisations'])}")
    print(f"  Monetary:      {len(result['monetary'])}")
    print(f"  Locations:     {len(result['locations'])}")

    if result["persons"]:
        print(f"\n  Sample persons:")
        for p in result["persons"][:3]:
            print(f"    {p['text']} ({p['confidence']})")
    if result["monetary"]:
        print(f"\n  Amounts found:")
        for m in result["monetary"][:3]:
            print(f"    {m['text']}")
    print("\nDone!")
