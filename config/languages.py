"""
BharatGraph Language Configuration
BUG-13 FIX: expanded UI_LABELS from 5-6 languages to all 10 major languages.
Added new keys: investigation_title, no_results, tagline, nav_home, nav_search,
nav_feed, nav_about, filter_all, filter_politicians, filter_companies,
filter_contracts, filter_audits, btn_investigate, btn_map, btn_dossier.
These are used by applyLanguage() to translate the full UI on language switch.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SCHEDULED_LANGUAGES = {
    "hi":  {"name": "Hindi",     "script": "Devanagari", "native": "हिन्दी"},
    "ta":  {"name": "Tamil",     "script": "Tamil",      "native": "தமிழ்"},
    "te":  {"name": "Telugu",    "script": "Telugu",     "native": "తెలుగు"},
    "kn":  {"name": "Kannada",   "script": "Kannada",    "native": "ಕನ್ನಡ"},
    "ml":  {"name": "Malayalam", "script": "Malayalam",  "native": "മലയാളം"},
    "mr":  {"name": "Marathi",   "script": "Devanagari", "native": "मराठी"},
    "bn":  {"name": "Bengali",   "script": "Bengali",    "native": "বাংলা"},
    "gu":  {"name": "Gujarati",  "script": "Gujarati",   "native": "ગુજરાતી"},
    "pa":  {"name": "Punjabi",   "script": "Gurmukhi",   "native": "ਪੰਜਾਬੀ"},
    "or":  {"name": "Odia",      "script": "Odia",       "native": "ଓଡ଼ିଆ"},
    "as":  {"name": "Assamese",  "script": "Bengali",    "native": "অসমীয়া"},
    "ur":  {"name": "Urdu",      "script": "Nastaliq",   "native": "اردو"},
    "sd":  {"name": "Sindhi",    "script": "Arabic",     "native": "سنڌي"},
    "kok": {"name": "Konkani",   "script": "Devanagari", "native": "कोंकणी"},
    "mai": {"name": "Maithili",  "script": "Devanagari", "native": "मैथिली"},
    "mni": {"name": "Manipuri",  "script": "Meitei",     "native": "ꯃꯩꯇꯩꯂꯣꯟ"},
    "sat": {"name": "Santali",   "script": "Ol Chiki",   "native": "ᱥᱟᱱᱛᱟᱲᱤ"},
    "ks":  {"name": "Kashmiri",  "script": "Nastaliq",   "native": "كٲشُر"},
    "ne":  {"name": "Nepali",    "script": "Devanagari", "native": "नेपाली"},
    "doi": {"name": "Dogri",     "script": "Devanagari", "native": "डोगरी"},
    "sa":  {"name": "Sanskrit",  "script": "Devanagari", "native": "संस्कृतम्"},
    "en":  {"name": "English",   "script": "Latin",      "native": "English"},
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
    "LOW":       {"hi":"निम्न","ta":"குறைந்த","te":"తక్కువ","kn":"ಕಡಿಮೆ","ml":"കുറഞ്ഞ","mr":"कमी","bn":"কম","gu":"ઓછું","pa":"ਘੱਟ","ur":"کم"},
    "MODERATE":  {"hi":"मध्यम","ta":"மிதமான","te":"మధ్యమ","kn":"ಮಧ್ಯಮ","ml":"മിതമായ","mr":"मध्यम","bn":"মাঝারি","gu":"મધ્યમ","pa":"ਮੱਧਮ","ur":"اعتدال"},
    "HIGH":      {"hi":"उच्च","ta":"அதிகம்","te":"అధిక","kn":"ಹೆಚ್ಚು","ml":"ഉയർന്ന","mr":"उच्च","bn":"উচ্চ","gu":"ઊंचुं","pa":"ਉੱਚ","ur":"اعلی"},
    "VERY_HIGH": {"hi":"अति उच्च","ta":"மிக அதிகம்","te":"చాలా అధిక","kn":"ಬಹಳ ಹೆಚ್ಚು","ml":"വളരെ ഉയർന്ന","mr":"अती उच्च","bn":"অতি উচ্চ","gu":"ખૂબ ઊंचुं","pa":"ਬਹੁਤ ਉੱਚ","ur":"بہت اعلی"},
}

# All UI_LABELS are consumed by GET /ui-labels?lang=xx and applied by applyLanguage()
# in the frontend. Add new keys here; the frontend loops over all keys automatically.
UI_LABELS = {
    # ── Search ──────────────────────────────────────────────────────────────────
    "search_placeholder": {
        "en": "Search any politician, company, ministry, or scheme...",
        "hi": "कोई भी नेता, कंपनी या योजना खोजें...",
        "ta": "எந்த அரசியல்வாதி, நிறுவனம் அல்லது திட்டத்தையும் தேடுங்கள்...",
        "te": "ఏ రాజకీయ నాయకుడు, కంపెనీ లేదా పథకమైనా శోధించండి...",
        "kn": "ಯಾವುದೇ ರಾಜಕಾರಣಿ, ಕಂಪನಿ ಅಥವಾ ಯೋಜನೆ ಹುಡುಕಿ...",
        "ml": "ഏതൊരു രാഷ്ട്രീയക്കാരൻ, കമ്പനി അല്ലെങ്കിൽ പദ്ധതി തിരയൂ...",
        "mr": "कोणताही नेता, कंपनी किंवा योजना शोधा...",
        "bn": "যেকোনো রাজনীতিবিদ, কোম্পানি বা প্রকল্প অনুসন্ধান করুন...",
        "gu": "કોઈ પણ નેતા, કંપની અથવા યોજના શોધો...",
        "pa": "ਕੋਈ ਵੀ ਨੇਤਾ, ਕੰਪਨੀ ਜਾਂ ਯੋਜਨਾ ਖੋਜੋ...",
        "ur": "کوئی بھی سیاستدان، کمپنی یا اسکیم تلاش کریں...",
    },
    # ── Navigation ──────────────────────────────────────────────────────────────
    "nav_home": {
        "en":"Home","hi":"होम","ta":"முகப்பு","te":"హోమ్","kn":"ಮುಖಪುಟ",
        "ml":"ഹോം","mr":"मुखपृष्ठ","bn":"হোম","gu":"હોમ","pa":"ਹੋਮ","ur":"ہوم",
    },
    "nav_search": {
        "en":"Search","hi":"खोजें","ta":"தேடு","te":"శోధించు","kn":"ಹುಡುಕಿ",
        "ml":"തിരയൂ","mr":"शोधा","bn":"অনুসন্ধান","gu":"શોધો","pa":"ਖੋਜ","ur":"تلاش",
    },
    "nav_feed": {
        "en":"Live Feed","hi":"लाइव फ़ीड","ta":"நேரடி ஊட்டம்","te":"లైవ్ ఫీడ్",
        "kn":"ನೇರ ಫೀಡ್","ml":"ലൈവ് ഫീഡ്","mr":"थेट फीड","bn":"লাইভ ফিড",
        "gu":"લાઇવ ફીડ","pa":"ਲਾਈਵ ਫੀਡ","ur":"لائیو فیڈ",
    },
    "nav_about": {
        "en":"About","hi":"परिचय","ta":"பற்றி","te":"గురించి","kn":"ಬಗ್ಗೆ",
        "ml":"കുറിച്ച്","mr":"विषयी","bn":"সম্পর্কে","gu":"વિશે","pa":"ਬਾਰੇ","ur":"کے بارے میں",
    },
    # ── Filter buttons ───────────────────────────────────────────────────────────
    "filter_all": {
        "en":"All","hi":"सभी","ta":"அனைத்தும்","te":"అన్నీ","kn":"ಎಲ್ಲಾ",
        "ml":"എല്ലാം","mr":"सर्व","bn":"সব","gu":"બધા","pa":"ਸਭ","ur":"سب",
    },
    "filter_politicians": {
        "en":"Politicians","hi":"नेता","ta":"அரசியல்வாதிகள்","te":"రాజకీయ నాయకులు",
        "kn":"ರಾಜಕಾರಣಿಗಳು","ml":"രാഷ്ട്രീയക്കാർ","mr":"राजकारणी","bn":"রাজনীতিবিদ",
        "gu":"નેતાઓ","pa":"ਨੇਤਾ","ur":"سیاستدان",
    },
    "filter_companies": {
        "en":"Companies","hi":"कंपनियां","ta":"நிறுவனங்கள்","te":"కంపెనీలు",
        "kn":"ಕಂಪನಿಗಳು","ml":"കമ്പനികൾ","mr":"कंपन्या","bn":"কোম্পানি",
        "gu":"કંપનીઓ","pa":"ਕੰਪਨੀਆਂ","ur":"کمپنیاں",
    },
    "filter_contracts": {
        "en":"Contracts","hi":"अनुबंध","ta":"ஒப்பந்தங்கள்","te":"కాంట్రాక్టులు",
        "kn":"ಒಪ್ಪಂದಗಳು","ml":"കരാറുകൾ","mr":"करार","bn":"চুক্তি",
        "gu":"કોન્ટ્રેક્ટ","pa":"ਕੰਟਰੈਕਟ","ur":"معاہدے",
    },
    "filter_audits": {
        "en":"Audits","hi":"ऑडिट","ta":"தணிக்கைகள்","te":"ఆడిట్లు",
        "kn":"ಆಡಿಟ್‌ಗಳು","ml":"ഓഡിറ്റുകൾ","mr":"लेखापरीक्षण","bn":"অডিট",
        "gu":"ઓડિટ","pa":"ਆਡਿਟ","ur":"آڈٹ",
    },
    # ── Entity page buttons ──────────────────────────────────────────────────────
    "btn_investigate": {
        "en":"Investigate","hi":"जांच करें","ta":"விசாரி","te":"దర్యాప్తు",
        "kn":"ತನಿಖೆ","ml":"അന്വേഷിക്കുക","mr":"तपास करा","bn":"তদন্ত করুন",
        "gu":"તપાસ કરો","pa":"ਜਾਂਚ ਕਰੋ","ur":"تحقیق کریں",
    },
    "btn_map": {
        "en":"Map Links","hi":"लिंक मैप","ta":"தொடர்புகள் வரைபடம்","te":"లింక్స్ మ్యాప్",
        "kn":"ಲಿಂಕ್ ನಕ್ಷೆ","ml":"ലിങ്ക് മാപ്പ്","mr":"लिंक नकाशा","bn":"লিঙ্ক মানচিত্র",
        "gu":"લિંક મેપ","pa":"ਲਿੰਕ ਮੈਪ","ur":"لنک نقشہ",
    },
    "btn_dossier": {
        "en":"Full Dossier","hi":"पूर्ण डोजियर","ta":"முழு அறிக்கை","te":"పూర్తి నివేదిక",
        "kn":"ಸಂಪೂರ್ಣ ವರದಿ","ml":"പൂർണ്ണ ഡോസিയർ","mr":"संपूर्ण अहवाल","bn":"সম্পূর্ণ ডোসিয়ার",
        "gu":"સંપૂર્ણ ડોઝિયર","pa":"ਪੂਰੀ ਰਿਪੋਰਟ","ur":"مکمل رپورٹ",
    },
    # ── Headings & labels ────────────────────────────────────────────────────────
    "tagline": {
        "en":"Public Transparency Intelligence Platform",
        "hi":"सार्वजनिक पारदर्शिता बुद्धिमत्ता मंच",
        "ta":"பொது வெளிப்படைத்தன்மை நுண்ணறிவு மேடை",
        "te":"పారదర్శకత మేధస్సు వేదిక",
        "kn":"ಸಾರ್ವಜನಿಕ ಪಾರದರ್ಶಕತೆ ವೇದಿಕೆ",
        "ml":"പൊതു സുതാര്യ ഇന്റലിജൻസ് പ്ലാറ്റ്ഫോം",
        "mr":"सार्वजनिक पारदर्शकता मंच",
        "bn":"পাবলিক স্বচ্ছতা প্ল্যাটফর্ম",
        "gu":"જાહેર પારદર્શિતા મંચ",
        "pa":"ਜਨਤਕ ਪਾਰਦਰਸ਼ਤਾ ਪਲੇਟਫਾਰਮ",
        "ur":"عوامی شفافیت پلیٹ فارم",
    },
    "investigation_title": {
        "en":"Investigation Results","hi":"जांच परिणाम","ta":"விசாரணை முடிவுகள்",
        "te":"దర్యాప్తు ఫలితాలు","kn":"ತನಿಖೆ ಫಲಿತಾಂಶ","ml":"അന്വേഷണ ഫലങ്ങൾ",
        "mr":"तपास निकाल","bn":"তদন্ত ফলাফল","gu":"તપાસ પરિણામ","pa":"ਜਾਂਚ ਨਤੀਜੇ","ur":"تحقیقاتی نتائج",
    },
    "no_results": {
        "en":"No results found. Try a different search term.",
        "hi":"कोई परिणाम नहीं मिला। कोई अलग शब्द आज़माएं।",
        "ta":"முடிவுகள் இல்லை. வேறு தேடல் சொல்லை முயற்சிக்கவும்.",
        "te":"ఫలితాలు కనుగొనబడలేదు. వేరే పదం ప్రయత్నించండి.",
        "kn":"ಫಲಿತಾಂಶ ಸಿಗಲಿಲ್ಲ. ಬೇರೆ ಪದ ಪ್ರಯತ್ನಿಸಿ.",
        "ml":"ഫലങ്ങൾ കണ്ടെത്തിയില്ല. മറ്റൊരു വാക്ക് ശ്രമിക്കൂ.",
        "mr":"कोणतेही परिणाम नाही. वेगळा शब्द वापरून पहा.",
        "bn":"কোনো ফলাফল পাওয়া যায়নি। অন্য শব্দ চেষ্টা করুন।",
        "gu":"કોઈ પરિણામ મળ્યાં નથી. બીજો શ્દ અજમાવો.",
        "pa":"ਕੋਈ ਨਤੀਜੇ ਨਹੀਂ। ਕੋਈ ਹੋਰ ਸ਼ਬਦ ਅਜ਼ਮਾਓ।",
        "ur":"کوئی نتیجہ نہیں ملا۔ دوسرا لفظ آزمائیں۔",
    },
    "risk_indicator": {
        "en":"Structural Risk Indicator","hi":"संरचनात्मक जोखिम संकेतक",
        "ta":"கட்டமைப்பு அபாய குறிகாட்டி","te":"నిర్మాణాత్మక ప్రమాద సూచిక",
        "kn":"ರಚನಾತ್ಮಕ ಅಪಾಯ ಸೂಚಕ","ml":"ഘടനാപരമായ അപകട സൂചകം",
        "mr":"संरचनात्मक जोखीम सूचक","bn":"কাঠামোগত ঝুঁকি সূচক",
        "gu":"માળખાકીય જોખમ સૂચક","pa":"ਢਾਂਚਾਗਤ ਜੋਖਮ ਸੂਚਕ","ur":"ساختی خطرے کا اشارہ",
    },
    "evidence_locker": {
        "en":"Evidence Locker","hi":"साक्ष्य लॉकर","ta":"சான்று பெட்டகம்",
        "te":"సాక్ష్య లాకర్","kn":"ಸಾಕ್ಷ್ಯ ಲಾಕರ್","ml":"തെളിവ് ലോക്കർ",
        "mr":"पुरावा लॉकर","bn":"প্রমাণ লকার","gu":"પુરાવો લૉકર","pa":"ਸਬੂਤ ਲਾਕਰ","ur":"ثبوت لاکر",
    },
    "connections_heading": {
        "en":"Connections","hi":"कनेक्शन","ta":"இணைப்புகள்","te":"కనెక్షన్లు",
        "kn":"ಸಂಪರ್ಕಗಳು","ml":"ബന്ധങ്ങൾ","mr":"कनेक्शन","bn":"সংযোগ",
        "gu":"જોડાણ","pa":"ਕਨੈਕਸ਼ਨ","ur":"روابط",
    },
    "risk_score_heading": {
        "en":"Risk Score","hi":"जोखिम स्कोर","ta":"அபாய மதிப்பெண்","te":"ప్రమాద స్కోర్",
        "kn":"ಅಪಾಯ ಸ್ಕೋರ್","ml":"അപകട സ്കോർ","mr":"जोखीम स्कोर","bn":"ঝুঁকির স্কোর",
        "gu":"જોખમ સ્કોર","pa":"ਜੋਖਮ ਸਕੋਰ","ur":"خطرے کا اسکور",
    },
    "legal_disclaimer": {
        "en":  "This is an analytical report based on official public records. It is not a legal finding.",
        "hi":  "यह आधिकारिक सार्वजनिक अभिलेखों पर आधारित एक विश्लेषणात्मक रिपोर्ट है। यह कोई कानूनी निष्कर्ष नहीं है।",
        "ta":  "இது அதிகாரப்பூர்வ பொது ஆவணங்களை அடிப்படையாகக் கொண்ட பகுப்பாய்வு அறிக்கை. சட்டரீதியான கண்டுபிடிப்பு அல்ல.",
        "te":  "ఇది అధికారిక ప్రజా రికార్డుల ఆధారంగా విశ్లేషణ నివేదిక. చట్టపరమైన నిర్ణయం కాదు.",
        "kn":  "ಇದು ಅಧಿಕೃತ ದಾಖಲೆಗಳ ಆಧಾರದ ಮೇಲೆ ವಿಶ್ಲೇಷಣಾ ವರದಿ. ಕಾನೂನು ತೀರ್ಪು ಅಲ್ಲ.",
        "ml":  "ഇത് ഔദ്യോഗിക ഡോക്യുമെന്റുകളെ അടിസ്ഥാനമാക്കിയ വിശകലന റിപ്പോർട്ടാണ്. ഇത് നിയമ നിർണ്ണയം അല്ല.",
        "mr":  "हे अधिकृत सार्वजनिक नोंदींवर आधारित विश्लेषणात्मक अहवाल आहे. हा कायदेशीर निष्कर्ष नाही.",
        "bn":  "এটি সরকারি রেকর্ডের উপর ভিত্তি করে বিশ্লেষণমূলক প্রতিবেদন। কোনো আইনি রায় নয়।",
        "gu":  "આ સત્તાવાર જાહેર રેકર્ડ પર આધારિત વિશ્લેષણ અહેવાલ છે. કોઈ કાનૂની તારણ નથી.",
        "pa":  "ਇਹ ਸਰਕਾਰੀ ਰਿਕਾਰਡਾਂ 'ਤੇ ਵਿਸ਼ਲੇਸ਼ਣਾਤਮਕ ਰਿਪੋਰਟ ਹੈ। ਕੋਈ ਕਾਨੂੰਨੀ ਫੈਸਲਾ ਨਹੀਂ।",
        "ur":  "یہ سرکاری ریکارڈ پر مبنی تجزیاتی رپورٹ ہے۔ یہ قانونی فیصلہ نہیں ہے۔",
        "or":  "ଏହା ଅଧିକୃତ ରେକର୍ଡ ଉପରେ ବିଶ୍ଳେଷଣ ରିପୋର୍ଟ। ଆଇନଗତ ନିଷ୍ପତ୍ତି ନୁହେଁ।",
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

def get_all_labels_for_lang(lang_code: str) -> dict:
    """Return every UI label translated to lang_code. Used by /ui-labels endpoint.
    Auto-scales: new keys added to UI_LABELS are automatically returned."""
    return {
        key: translations.get(lang_code) or translations.get("en", key)
        for key, translations in UI_LABELS.items()
    }
