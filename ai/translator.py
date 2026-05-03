import os
import sys
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from config.languages import SCHEDULED_LANGUAGES, SCRIPT_UNICODE_RANGES


INDICTRANS_MODEL = "Helsinki-NLP/opus-mt-en-hi"
LIBRE_TRANSLATE_URL = "https://libretranslate.com/translate"

SCRIPT_TO_LANG = {
    "Devanagari": "hi",
    "Tamil":      "ta",
    "Telugu":     "te",
    "Kannada":    "kn",
    "Malayalam":  "ml",
    "Bengali":    "bn",
    "Gujarati":   "gu",
    "Gurmukhi":   "pa",
    "Odia":       "or",
}

FIELD_TEMPLATES = {
    "risk_explanation": {
        "hi": (
            "{entity_name} \u0915\u0947 \u0932\u093f\u090f \u0938\u0902\u0930\u091a\u0928\u093e\u0924\u094d\u092e\u0915 \u091c\u094b\u0916\u093f\u092e \u0938\u094d\u0915\u094b\u0930 {score}/100 \u0939\u0948\u0964 "
            "\u091c\u094b\u0916\u093f\u092e \u0938\u094d\u0924\u0930: {level}\u0964 \u092f\u0939 \u090f\u0915 \u0935\u093f\u0936\u094d\u0932\u0947\u0937\u0923\u093e\u0924\u094d\u092e\u0915 \u0938\u0902\u0915\u0947\u0924\u0915 \u0939\u0948, "
            "\u0915\u094b\u0908 \u0915\u093e\u0928\u0942\u0928\u0940 \u0928\u093f\u0930\u094d\u0923\u092f \u0928\u0939\u0940\u0902\u0964"
        ),
        "ta": (
            "{entity_name}-\u0b95\u0bcd\u0b95\u0bbe\u0ba9 \u0b95\u0b9f\u0bcd\u0b9f\u0bae\u0bc8\u0baa\u0bcd\u0baa\u0bc1 \u0b85\u0baa\u0bbe\u0baf \u0bae\u0ba4\u0bbf\u0baa\u0bcd\u0baa\u0bc6\u0ba3\u0bcd {score}/100 \u0b86\u0b95\u0bc1\u0bae\u0bcd. "
            "\u0b85\u0baa\u0bbe\u0baf \u0ba8\u0bbf\u0bb2\u0bc8: {level}\u0964 \u0b87\u0ba4\u0bc1 \u0b92\u0bb0\u0bc1 \u0baa\u0b95\u0bc1\u0baa\u0bcd\u0baa\u0bbe\u0baf\u0bcd\u0bb5\u0bc1 \u0b95\u0bc1\u0bb1\u0bbf\u0b95\u0bbe\u0b9f\u0bcd\u0b9f\u0bbf, "
            "\u0b9a\u0b9f\u0bcd\u0b9f\u0bb0\u0bc0\u0ba4\u0bbf\u0baf\u0bbe\u0ba9 \u0ba4\u0bc0\u0bb0\u0bcd\u0baa\u0bcd\u0baa\u0bc1 \u0b85\u0bb2\u0bcd\u0bb2\u0964"
        ),
        "te": (
            "{entity_name} \u0c15\u0c4b\u0c38\u0c02 \u0c28\u0c3f\u0c30\u0c4d\u0c2e\u0c3e\u0c23\u0c3e\u0c24\u0c4d\u0c2e\u0c15 \u0c2a\u0c4d\u0c30\u0c2e\u0c3e\u0c26 \u0c38\u0c4d\u0c15\u0c4b\u0c30\u0c4d {score}/100. "
            "\u0c2a\u0c4d\u0c30\u0c2e\u0c3e\u0c26 \u0c38\u0c4d\u0c25\u0c3e\u0c2f\u0c3f: {level}\u0964 \u0c07\u0c26\u0c3f \u0c35\u0c3f\u0c36\u0c4d\u0c32\u0c47\u0c37\u0c23 \u0c38\u0c42\u0c1a\u0c3f\u0c15, "
            "\u0c1a\u0c1f\u0c4d\u0c1f\u0c2a\u0c30\u0c2e\u0c48\u0c28 \u0c28\u0c3f\u0c30\u0c4d\u0c23\u0c2f\u0c02 \u0c15\u0c3e\u0c26\u0c41\u0964"
        ),
        "kn": (
            "{entity_name} \u0c97\u0cbe\u0c97\u0cbf \u0cb0\u0c9a\u0ca8\u0cbe\u0ca4\u0ccd\u0cae\u0c95 \u0c85\u0caa\u0cbe\u0caf \u0cb8\u0ccd\u0c95\u0ccb\u0cb0\u0ccd {score}/100 \u0c86\u0c97\u0cbf\u0ca6\u0cc6. "
            "\u0c85\u0caa\u0cbe\u0caf \u0cae\u0c9f\u0ccd\u0c9f: {level}\u0964 \u0c87\u0ca6\u0cc1 \u0c92\u0c82\u0ca6\u0cc1 \u0cb5\u0cbf\u0cb6\u0ccd\u0cb2\u0cc7\u0cb7\u0ca3\u0cbe \u0cb8\u0cc2\u0c9a\u0c95, "
            "\u0c95\u0cbe\u0ca8\u0cc2\u0ca8\u0cc1 \u0ca8\u0cbf\u0cb0\u0ccd\u0ca3\u0caf \u0c85\u0cb2\u0ccd\u0cb2\u0964"
        ),
        "ml": (
            "{entity_name}-\u0d28\u0d3e\u0d2f\u0d41\u0d33\u0d4d\u0d33 \u0d18\u0d1f\u0d28\u0d3e\u0d2a\u0d30\u0d2e\u0d3e\u0d2f \u0d05\u0d2a\u0d15\u0d1f \u0d38\u0d4d\u0d15\u0d4b\u0d7c {score}/100 \u0d06\u0d23\u0d4d. "
            "\u0d05\u0d2a\u0d15\u0d1f \u0d28\u0d3f\u0d32: {level}\u0964 \u0d07\u0d24\u0d4d \u0d12\u0d30\u0d41 \u0d35\u0d3f\u0d36\u0d15\u0d32\u0d28 \u0d38\u0d42\u0d1a\u0d15\u0d2e\u0d3e\u0d23\u0d4d, "
            "\u0d28\u0d3f\u0d2f\u0d2e \u0d28\u0d3f\u0d7c\u0d23\u0d4d\u0d23\u0d2f\u0d02 \u0d05\u0d32\u0d4d\u0d32\u0964"
        ),
    },
    "no_data": {
        "hi":  "\u0907\u0938 \u0907\u0915\u093e\u0908 \u0915\u0947 \u0932\u093f\u090f \u0935\u0930\u094d\u0924\u092e\u093e\u0928 \u092e\u0947\u0902 \u0915\u094b\u0908 \u0921\u0947\u091f\u093e \u0909\u092a\u0932\u092c\u094d\u0927 \u0928\u0939\u0940\u0902 \u0939\u0948\u0964",
        "ta":  "\u0b87\u0ba8\u0bcd\u0ba4 \u0ba8\u0bbf\u0bb1\u0bc1\u0bb5\u0ba9\u0ba4\u0bcd\u0ba4\u0bbf\u0bb1\u0bcd\u0b95\u0bc1 \u0ba4\u0bb1\u0bcd\u0baa\u0bcb\u0ba4\u0bc1 \u0ba4\u0bb0\u0bb5\u0bc1 \u0b95\u0bbf\u0b9f\u0bc8\u0b95\u0bcd\u0b95\u0bb5\u0bbf\u0bb2\u0bcd\u0bb2\u0bc8.",
        "te":  "\u0c08 \u0c38\u0c02\u0c38\u0c4d\u0c25\u0c15\u0c41 \u0c2a\u0c4d\u0c30\u0c38\u0c4d\u0c24\u0c41\u0c24\u0c02 \u0c21\u0c47\u0c1f\u0c3e \u0c05\u0c02\u0c26\u0c41\u0c2c\u0c3e\u0c1f\u0c41\u0c32\u0c4b \u0c32\u0c47\u0c26\u0c41.",
        "kn":  "\u0c88 \u0c98\u0c9f\u0c95\u0c95\u0ccd\u0c95\u0cc6 \u0caa\u0ccd\u0cb0\u0cb8\u0ccd\u0ca4\u0cc1\u0ca4 \u0caf\u0cbe\u0cb5\u0cc1\u0ca6\u0cc7 \u0ca1\u0cc7\u0c9f\u0cbe \u0cb2\u0cad\u0ccd\u0caf\u0cb5\u0cbf\u0cb2\u0ccd\u0cb2.",
        "ml":  "\u0d08 \u0d38\u0d4d\u0d25\u0d3e\u0d2a\u0d28\u0d24\u0d4d\u0d24\u0d3f\u0d28\u0d3e\u0d2f\u0d3f \u0d07\u0d2a\u0d4d\u0d2a\u0d4b\u0d7e \u0d21\u0d3e\u0d31\u0d4d\u0d31 \u0d32\u0d2d\u0d4d\u0d2f\u0d2e\u0d32\u0d4d\u0d32.",
        "mr":  "\u092f\u093e \u0918\u091f\u0915\u093e\u0938\u093e\u0920\u0940 \u0938\u0927\u094d\u092f\u093e \u0915\u094b\u0923\u0924\u093e\u0939\u0940 \u0921\u0947\u091f\u093e \u0909\u092a\u0932\u092c\u094d\u0927 \u0928\u093e\u0939\u0940.",
        "bn":  "\u098f\u0987 \u09b8\u09a4\u09cd\u09a4\u09be\u09b0 \u099c\u09a8\u09cd\u09af \u09ac\u09b0\u09cd\u09a4\u09ae\u09be\u09a8\u09c7 \u0995\u09cb\u09a8\u09cb \u09a4\u09a5\u09cd\u09af \u09aa\u09be\u0993\u09af\u09bc\u09be \u09af\u09be\u099a\u09cd\u099b\u09c7 \u09a8\u09be\u0964",
        "gu":  "\u0a86 \u0ab8\u0a82\u0ab8\u0acd\u0aa5\u0abe \u0aae\u0abe\u0a9f\u0ac7 \u0ab9\u0abe\u0ab2\u0aae\u0abe\u0a82 \u0aa1\u0ac7\u0a9f\u0abe \u0a89\u0aaa\u0ab2\u0aac\u0acd\u0aa7 \u0aa8\u0aa5\u0ac0.",
        "en":  "No data currently available for this entity.",
    },
}


class Translator:

    def __init__(self):
        self._model     = None
        self._tokenizer = None
        self._load_model()

    def _load_model(self):
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(
                INDICTRANS_MODEL, trust_remote_code=True
            )
            self._model = AutoModelForSeq2SeqLM.from_pretrained(
                INDICTRANS_MODEL, trust_remote_code=True
            )
            logger.success(f"[Translator] IndicTrans2 loaded: {INDICTRANS_MODEL}")
        except Exception as e:
            logger.warning(f"[Translator] IndicTrans2 not available: {e}")
            logger.info("[Translator] Using template-based translation fallback")
            self._model = None

    def detect_language(self, text: str) -> str:
        if not text:
            return "en"
        for script_name, (start, end) in SCRIPT_UNICODE_RANGES.items():
            count = sum(1 for ch in text if start <= ord(ch) <= end)
            if count > max(3, len(text) * 0.1):
                lang = SCRIPT_TO_LANG.get(script_name, "en")
                logger.info(
                    f"[Translator] Detected {script_name} script -> {lang}"
                )
                return lang
        return "en"

    def translate(self, text: str, source_lang: str,
                  target_lang: str) -> str:
        if source_lang == target_lang or target_lang == "en":
            return text

        if self._model and self._tokenizer:
            return self._translate_with_model(text, source_lang, target_lang)
        return self._template_translate(text, source_lang, target_lang)

    def _translate_with_model(self, text: str, source_lang: str,
                               target_lang: str) -> str:
        try:
            inputs = self._tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            )
            outputs = self._model.generate(
                **inputs,
                num_beams=4,
                max_length=512,
            )
            translated = self._tokenizer.batch_decode(
                outputs, skip_special_tokens=True
            )
            return translated[0] if translated else text
        except Exception as e:
            logger.warning(f"[Translator] Model translation failed: {e}")
            return text

    def _template_translate(self, text: str, source_lang: str,
                             target_lang: str) -> str:
        if len(text) < 5:
            return text
        lang_name = SCHEDULED_LANGUAGES.get(target_lang, {}).get("name", target_lang)
        return (
            f"[{lang_name}] {text}"
        )

    def translate_risk_explanation(self, entity_name: str, score: int,
                                    level: str, lang: str) -> str:
        template = FIELD_TEMPLATES["risk_explanation"].get(lang)
        if template:
            return template.format(entity_name=entity_name,
                                   score=score, level=level)
        return (
            f"{entity_name} \u2014 Structural risk score: {score}/100. "
            f"Risk level: {level}. "
            "This is an analytical indicator, not a legal finding."
        )

    def get_no_data_message(self, lang: str) -> str:
        return FIELD_TEMPLATES["no_data"].get(lang,
               FIELD_TEMPLATES["no_data"]["en"])


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Translator Test")
    print("=" * 55)

    translator = Translator()

    test_texts = [
        ("\u092e\u0902\u0924\u094d\u0930\u0940 \u0930\u093e\u091c\u0947\u0936 \u0915\u0941\u092e\u093e\u0930 \u0915\u0940 \u091c\u093e\u0902\u091a \u0915\u0940 \u091c\u093e\u090f",  "auto"),
        ("Minister Rajesh Kumar should be investigated", "en"),
        ("\u0bb0\u0bbe\u0b9c\u0bc7\u0bb7\u0bcd \u0b95\u0bc1\u0bae\u0bbe\u0bb0\u0bcd \u0b85\u0bae\u0bc8\u0b9a\u0bcd\u0b9a\u0bb0\u0bcd",              "auto"),
    ]

    print("\n  Language Detection:")
    for text, _ in test_texts:
        lang = translator.detect_language(text)
        print(f"  '{text[:40]}' -> {lang} "
              f"({SCHEDULED_LANGUAGES.get(lang, {}).get('name', '?')})")

    print("\n  Risk Explanation Templates:")
    for lang in ["hi","ta","te","kn","ml"]:
        explanation = translator.translate_risk_explanation(
            "Test Entity", 75, "HIGH", lang
        )
        print(f"  [{lang}] {explanation[:70]}")

    print("\nDone!")
