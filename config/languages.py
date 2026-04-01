import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


SCHEDULED_LANGUAGES = {
    "hi":  {"name": "Hindi",      "script": "Devanagari", "native": "हिन्दी"},
    "ta":  {"name": "Tamil",      "script": "Tamil",      "native": "தமிழ்"},
    "te":  {"name": "Telugu",     "script": "Telugu",     "native": "తెలుగు"},
    "kn":  {"name": "Kannada",    "script": "Kannada",    "native": "ಕನ್ನಡ"},
    "ml":  {"name": "Malayalam",  "script": "Malayalam",  "native": "മലയാളം"},
    "mr":  {"name": "Marathi",    "script": "Devanagari", "native": "मराठी"},
    "bn":  {"name": "Bengali",    "script": "Bengali",    "native": "বাংলা"},
    "gu":  {"name": "Gujarati",   "script": "Gujarati",   "native": "ગુજરાતી"},
    "pa":  {"name": "Punjabi",    "script": "Gurmukhi",   "native": "ਪੰਜਾਬੀ"},
    "or":  {"name": "Odia",       "script": "Odia",       "native": "ଓଡ଼ିଆ"},
    "as":  {"name": "Assamese",   "script": "Bengali",    "native": "অসমীয়া"},
    "ur":  {"name": "Urdu",       "script": "Nastaliq",   "native": "اردو"},
    "sd":  {"name": "Sindhi",     "script": "Arabic",     "native": "سنڌي"},
    "kok": {"name": "Konkani",    "script": "Devanagari", "native": "कोंकणी"},
    "mai": {"name": "Maithili",   "script": "Devanagari", "native": "मैथिली"},
    "mni": {"name": "Manipuri",   "script": "Meitei",     "native": "ꯃꯩꯇꯩꯂꯣꯟ"},
    "sat": {"name": "Santali",    "script": "Ol Chiki",   "native": "ᱥᱟᱱᱛᱟᱲᱤ"},
    "ks":  {"name": "Kashmiri",   "script": "Nastaliq",   "native": "كٲشُر"},
    "ne":  {"name": "Nepali",     "script": "Devanagari", "native": "नेपाली"},
    "doi": {"name": "Dogri",      "script": "Devanagari", "native": "डोगरी"},
    "sa":  {"name": "Sanskrit",   "script": "Devanagari", "native": "संस्कृतम्"},
    "en":  {"name": "English",    "script": "Latin",      "native": "English"},
}

SCRIPT_UNICODE_RANGES = {
    "Devanagari": (0x0900, 0x097F),
    "Tamil":      (0x0B80, 0x0BFF),
    "Telugu":     (0x0C00, 0x0C7F),
    "Kannada":    (0x0C80, 0x0CFF),
    "Malayalam":  (0x0D00, 0x0D7F),
    "Bengali":    (0x0980, 0x09FF),
    "Gujarati":   (0x0A80, 0x0AFF),
    "Gurmukhi":   (0x0A00, 0x0A7F),
    "Odia":       (0x0B00, 0x0B7F),
}

RISK_LEVEL_TRANSLATIONS = {
    "LOW":       {"hi":"निम्न","ta":"குறைந்த","te":"తక్కువ","kn":"ಕಡಿಮೆ","ml":"കുറഞ്ഞ","mr":"कमी","bn":"কম","gu":"ઓછું","pa":"ਘੱਟ"},
    "MODERATE":  {"hi":"मध्यम","ta":"மிதமான","te":"మధ్యమ","kn":"ಮಧ್ಯಮ","ml":"മിതമായ","mr":"मध्यम","bn":"মাঝারি","gu":"મધ્યમ","pa":"ਮੱਧਮ"},
    "HIGH":      {"hi":"उच्च","ta":"அதிகம்","te":"అధిక","kn":"ಹೆಚ್ಚು","ml":"ഉയർന്ന","mr":"उच्च","bn":"উচ্চ","gu":"ઊંચું","pa":"ਉੱਚ"},
    "VERY_HIGH": {"hi":"अति उच्च","ta":"மிக அதிகம்","te":"చాలా అధిక","kn":"ಬಹಳ ಹೆಚ್ಚು","ml":"വളരെ ഉയർന്ന","mr":"अती उच्च","bn":"অতি উচ্চ","gu":"ખૂબ ઊંચું","pa":"ਬਹੁਤ ਉੱਚ"},
}

UI_LABELS = {
    "search_placeholder": {
        "en": "Search any politician, company, or scheme",
        "hi": "कोई भी नेता, कंपनी या योजना खोजें",
        "ta": "எந்த அரசியல்வாதி, நிறுவனம் அல்லது திட்டத்தையும் தேடுங்கள்",
        "te": "ఏ రాజకీయ నాయకుడు, కంపెనీ లేదా పథకమైనా శోధించండి",
        "kn": "ಯಾವುದೇ ರಾಜಕಾರಣಿ, ಕಂಪನಿ ಅಥವಾ ಯೋಜನೆ ಹುಡುಕಿ",
        "ml": "ഏതൊരു രാഷ്ട്രീയക്കാരൻ, കമ്പനി അല്ലെങ്കിൽ പദ്ധതി തിരയൂ",
    },
    "risk_indicator": {
        "en": "Structural Risk Indicator",
        "hi": "संरचनात्मक जोखिम संकेतक",
        "ta": "கட்டமைப்பு அபாய குறிகாட்டி",
        "te": "నిర్మాణాత్మక ప్రమాద సూచిక",
        "kn": "ರಚನಾತ್ಮಕ ಅಪಾಯ ಸೂಚಕ",
        "ml": "ഘടനാപരമായ അപകട സൂചകം",
    },
    "evidence_locker": {
        "en": "Evidence Locker",
        "hi": "साक्ष्य लॉकर",
        "ta": "சான்று பெட்டகம்",
        "te": "సాక్ష్య లాకర్",
        "kn": "ಸಾಕ್ಷ್ಯ ಲಾಕರ್",
        "ml": "തെളിവ് ലോക്കർ",
    },
    "legal_disclaimer": {
        "en": "This is an analytical report based on official public records. It is not a legal finding.",
        "hi": "यह आधिकारिक सार्वजनिक अभिलेखों पर आधारित एक विश्लेषणात्मक रिपोर्ट है। यह कोई कानूनी निष्कर्ष नहीं है।",
        "ta": "இது அதிகாரப்பூர்வ பொது ஆவணங்களை அடிப்படையாகக் கொண்ட ஒரு பகுப்பாய்வு அறிக்கை. இது சட்டரீதியான கண்டுபிடிப்பு அல்ல.",
        "te": "ఇది అధికారిక ప్రజా రికార్డుల ఆధారంగా రూపొందించిన విశ్లేషణ నివేదిక. ఇది చట్టపరమైన నిర్ణయం కాదు.",
        "kn": "ಇದು ಅಧಿಕೃತ ಸಾರ್ವಜನಿಕ ದಾಖಲೆಗಳ ಆಧಾರದ ಮೇಲೆ ತಯಾರಿಸಲಾದ ವಿಶ್ಲೇಷಣಾ ವರದಿ. ಇದು ಕಾನೂನು ತೀರ್ಪು ಅಲ್ಲ.",
        "ml": "ഇത് ഔദ്യോഗിക പൊതു രേഖകളെ അടിസ്ഥാനമാക്കിയ ഒരു വിശകലന റിപ്പോർട്ടാണ്. ഇത് ഒരു നിയമ നിർണ്ണയം അല്ല.",
    },
}


def get_language_name(lang_code: str) -> str:
    return SCHEDULED_LANGUAGES.get(lang_code, {}).get("name", "English")


def get_native_name(lang_code: str) -> str:
    return SCHEDULED_LANGUAGES.get(lang_code, {}).get("native", "English")


def get_risk_translation(level: str, lang_code: str) -> str:
    return RISK_LEVEL_TRANSLATIONS.get(level, {}).get(lang_code, level)


def get_ui_label(key: str, lang_code: str) -> str:
    return UI_LABELS.get(key, {}).get(lang_code,
           UI_LABELS.get(key, {}).get("en", key))


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Languages Configuration")
    print("=" * 55)
    print(f"\n  Scheduled languages: {len(SCHEDULED_LANGUAGES)}")
    for code, info in list(SCHEDULED_LANGUAGES.items())[:5]:
        print(f"  {code}: {info['name']} ({info['native']}) — {info['script']} script")

    print("\n  Risk level translations (Hindi):")
    for level in ["LOW","MODERATE","HIGH","VERY_HIGH"]:
        print(f"  {level}: {get_risk_translation(level, 'hi')}")

    print("\n  UI label test:")
    for label in ["search_placeholder","risk_indicator","legal_disclaimer"]:
        print(f"  [{label}] hi: {get_ui_label(label,'hi')[:50]}")
