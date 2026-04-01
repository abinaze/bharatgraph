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
            "{entity_name} के लिए संरचनात्मक जोखिम स्कोर {score}/100 है। "
            "जोखिम स्तर: {level}। यह एक विश्लेषणात्मक संकेतक है, "
            "कोई कानूनी निर्णय नहीं।"
        ),
        "ta": (
            "{entity_name}-க்கான கட்டமைப்பு அபாய மதிப்பெண் {score}/100 ஆகும். "
            "அபாய நிலை: {level}। இது ஒரு பகுப்பாய்வு குறிகாட்டி, "
            "சட்டரீதியான தீர்ப்பு அல்ல।"
        ),
        "te": (
            "{entity_name} కోసం నిర్మాణాత్మక ప్రమాద స్కోర్ {score}/100. "
            "ప్రమాద స్థాయి: {level}। ఇది విశ్లేషణ సూచిక, "
            "చట్టపరమైన నిర్ణయం కాదు।"
        ),
        "kn": (
            "{entity_name} ಗಾಗಿ ರಚನಾತ್ಮಕ ಅಪಾಯ ಸ್ಕೋರ್ {score}/100 ಆಗಿದೆ. "
            "ಅಪಾಯ ಮಟ್ಟ: {level}। ಇದು ಒಂದು ವಿಶ್ಲೇಷಣಾ ಸೂಚಕ, "
            "ಕಾನೂನು ನಿರ್ಣಯ ಅಲ್ಲ।"
        ),
        "ml": (
            "{entity_name}-നായുള്ള ഘടനാപരമായ അപകട സ്കോർ {score}/100 ആണ്. "
            "അപകട നില: {level}। ഇത് ഒരു വിശകലന സൂചകമാണ്, "
            "നിയമ നിർണ്ണയം അല്ല।"
        ),
    },
    "no_data": {
        "hi":  "इस इकाई के लिए वर्तमान में कोई डेटा उपलब्ध नहीं है।",
        "ta":  "இந்த நிறுவனத்திற்கு தற்போது தரவு கிடைக்கவில்லை.",
        "te":  "ఈ సంస్థకు ప్రస్తుతం డేటా అందుబాటులో లేదు.",
        "kn":  "ಈ ಘಟಕಕ್ಕೆ ಪ್ರಸ್ತುತ ಯಾವುದೇ ಡೇಟಾ ಲಭ್ಯವಿಲ್ಲ.",
        "ml":  "ഈ സ്ഥാപനത്തിനായി ഇപ്പോൾ ഡാറ്റ ലഭ്യമല്ല.",
        "mr":  "या घटकासाठी सध्या कोणताही डेटा उपलब्ध नाही.",
        "bn":  "এই সত্তার জন্য বর্তমানে কোনো তথ্য পাওয়া যাচ্ছে না।",
        "gu":  "આ સ્ઘ્ઠ ment for these entities.",
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
            f"{entity_name} — Structural risk score: {score}/100. "
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
        ("मंत्री राजेश कुमार की जांच की जाए",  "auto"),
        ("Minister Rajesh Kumar should be investigated", "en"),
        ("ராஜேஷ் குமார் அமைச்சர்",              "auto"),
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
