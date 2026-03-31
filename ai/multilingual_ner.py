import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from datetime import datetime
from loguru import logger


SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "pa": "Punjabi",
}

INDICNER_MODEL = "Davlan/bert-base-multilingual-cased-ner-hrl"

HINDI_TITLE_WORDS = [
    "मंत्री", "सचिव", "मुख्यमंत्री", "राज्यपाल", "सांसद", "विधायक",
    "अधिकारी", "निदेशक", "आयुक्त", "कलेक्टर",
]


class MultilingualNER:

    def __init__(self):
        self._pipeline = None
        self._lang_detect = None
        self._load_models()

    def _load_models(self):
        try:
            from transformers import pipeline as hf_pipeline
            self._pipeline = hf_pipeline(
                "token-classification",
                model=INDICNER_MODEL,
                aggregation_strategy="simple",
            )
            logger.success(f"[MultilingualNER] Loaded {INDICNER_MODEL}")
        except Exception as e:
            logger.warning(f"[MultilingualNER] HuggingFace model not available: {e}")
            logger.warning("[MultilingualNER] Using pattern-based fallback for Hindi")
            self._pipeline = None

    def detect_language(self, text: str) -> str:
        devanagari = len(re.findall(r'[\u0900-\u097F]', text))
        tamil_chars = len(re.findall(r'[\u0B80-\u0BFF]', text))
        telugu_chars = len(re.findall(r'[\u0C00-\u0C7F]', text))

        if devanagari > 5:
            return "hi"
        if tamil_chars > 5:
            return "ta"
        if telugu_chars > 5:
            return "te"
        return "en"

    def extract_entities(self, text: str, language: str = None) -> list:
        if not text or not text.strip():
            return []

        detected_lang = language or self.detect_language(text)
        logger.info(
            f"[MultilingualNER] Extracting from "
            f"{SUPPORTED_LANGUAGES.get(detected_lang, detected_lang)} text"
        )

        if self._pipeline and detected_lang != "en":
            return self._extract_with_model(text, detected_lang)
        return self._extract_with_patterns(text, detected_lang)

    def _extract_with_model(self, text: str, language: str) -> list:
        try:
            results = self._pipeline(text[:512])
            entities = []
            for r in results:
                entities.append({
                    "text":        r.get("word", ""),
                    "label":       r.get("entity_group", ""),
                    "score":       round(r.get("score", 0), 4),
                    "language":    language,
                    "model":       INDICNER_MODEL,
                    "extracted_at":datetime.now().isoformat(),
                })
            logger.success(f"[MultilingualNER] Model extracted {len(entities)} entities")
            return entities
        except Exception as e:
            logger.warning(f"[MultilingualNER] Model inference failed: {e}")
            return self._extract_with_patterns(text, language)

    def _extract_with_patterns(self, text: str, language: str) -> list:
        entities = []

        if language == "hi":
            for title in HINDI_TITLE_WORDS:
                pattern = re.compile(
                    title + r"\s+([^\s।\n]{2,20}(?:\s+[^\s।\n]{2,20})?)"
                )
                for match in pattern.finditer(text):
                    entities.append({
                        "text":        match.group(1).strip(),
                        "label":       "PERSON",
                        "score":       0.7,
                        "language":    language,
                        "model":       "pattern_fallback",
                        "extracted_at":datetime.now().isoformat(),
                    })

            amount_pattern = re.compile(
                r"([\d,]+(?:\.\d+)?\s*(?:करोड़|लाख|हजार))"
            )
            for match in amount_pattern.finditer(text):
                entities.append({
                    "text":        match.group(1),
                    "label":       "MONEY",
                    "score":       0.9,
                    "language":    language,
                    "model":       "pattern_fallback",
                    "extracted_at":datetime.now().isoformat(),
                })

        seen = set()
        unique = []
        for e in entities:
            key = (e["text"].strip().lower(), e["label"])
            if key not in seen and e["text"].strip():
                seen.add(key)
                unique.append(e)

        logger.info(f"[MultilingualNER] Pattern fallback extracted {len(unique)} entities")
        return unique


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Multilingual NER Test")
    print("=" * 55)

    ner = MultilingualNER()

    samples = [
        ("Hindi", "hi",
         "मंत्री राजेश कुमार और सचिव प्रिया शर्मा ने 45 करोड़ रुपये की "
         "अनियमितता की जांच का आदेश दिया।"),
        ("English", "en",
         "Minister Rajesh Kumar approved a contract worth Rs 45 crore "
         "for ABC Infrastructure Private Limited."),
    ]

    for lang_name, lang_code, text in samples:
        print(f"\n  [{lang_name}]")
        print(f"  Text: {text[:80]}...")
        entities = ner.extract_entities(text, lang_code)
        print(f"  Extracted: {len(entities)} entities")
        for e in entities[:4]:
            print(f"    {e['label']}: {e['text']} (model={e['model']})")

    print("\nDone!")
