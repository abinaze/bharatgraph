import os
import sys
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger

COMMON_POLITICAL_NAMES = {
    "modi":    {"hi":"मोदी","ta":"மோடி","te":"మోదీ","kn":"ಮೋದಿ","ml":"മോദി"},
    "gandhi":  {"hi":"गांधी","ta":"காந்தி","te":"గాంధీ","kn":"ಗಾಂಧಿ","ml":"ഗാന്ധി"},
    "nehru":   {"hi":"नेहरू","ta":"நேரு","te":"నెహ్రూ","kn":"ನೆಹ್ರು","ml":"നെഹ്‌റു"},
    "singh":   {"hi":"सिंह","ta":"சிங்","te":"సింగ్","kn":"ಸಿಂಗ್","ml":"സിംഗ്"},
    "kumar":   {"hi":"कुमार","ta":"குமார்","te":"కుమార్","kn":"ಕುಮಾರ್","ml":"കുമാർ"},
    "sharma":  {"hi":"शर्मा","ta":"சர்மா","te":"శర్మ","kn":"ಶರ್ಮ","ml":"ശർമ"},
    "verma":   {"hi":"वर्मा","ta":"வர்மா","te":"వర్మ","kn":"ವರ್ಮ","ml":"വർമ"},
    "patel":   {"hi":"पटेल","ta":"படேல்","te":"పటేల్","kn":"ಪಟೇಲ್","ml":"പട്ടേൽ"},
    "reddy":   {"hi":"रेड्डी","ta":"ரெட்டி","te":"రెడ్డి","kn":"ರೆಡ್ಡಿ","ml":"റെഡ്ഡി"},
    "naidu":   {"hi":"नायडू","ta":"நாயுடு","te":"నాయుడు","kn":"ನಾಯ್ಡು","ml":"നായ്ഡു"},
    "rao":     {"hi":"राव","ta":"ராவ்","te":"రావు","kn":"ರಾವ್","ml":"റാവു"},
    "iyer":    {"hi":"अय्यर","ta":"ஐயர்","te":"అయ్యర్","kn":"ಅಯ್ಯರ್","ml":"അയ്യർ"},
    "nair":    {"hi":"नायर","ta":"நாயர்","te":"నాయర్","kn":"ನಾಯರ್","ml":"നായർ"},
    "menon":   {"hi":"मेनन","ta":"மேனன்","te":"మేనన్","kn":"ಮೇನನ್","ml":"മേനോൻ"},
    "pillai":  {"hi":"पिल्लई","ta":"பிள்ளை","te":"పిళ్ళై","kn":"ಪಿಳ್ಳೈ","ml":"പിള്ള"},
}

PHONEME_MAP_HI = {
    "a":"अ","aa":"आ","i":"इ","ee":"ई","u":"उ","oo":"ऊ",
    "e":"ए","ai":"ऐ","o":"ओ","au":"औ",
    "k":"क","kh":"ख","g":"ग","gh":"घ","n":"न",
    "ch":"च","chh":"छ","j":"ज","jh":"झ",
    "t":"त","th":"थ","d":"द","dh":"ध",
    "p":"प","ph":"फ","b":"ब","bh":"भ","m":"म",
    "y":"य","r":"र","l":"ल","v":"व","w":"व",
    "sh":"श","s":"स","h":"ह",
}


class Transliterator:

    def __init__(self):
        self._indic_nlp = None
        self._load_lib()

    def _load_lib(self):
        try:
            import indic_transliteration
            self._indic_nlp = indic_transliteration
            logger.success("[Transliterator] indic-transliteration loaded")
        except ImportError:
            logger.warning(
                "[Transliterator] indic-transliteration not installed. "
                "Using lookup table fallback. "
                "Install with: pip install indic-transliteration"
            )
            self._indic_nlp = None

    def roman_to_script(self, text: str, target_lang: str) -> str:
        text_lower = text.lower().strip()

        words = text_lower.split()
        result_words = []
        for word in words:
            lookup = COMMON_POLITICAL_NAMES.get(word, {})
            if target_lang in lookup:
                result_words.append(lookup[target_lang])
            else:
                result_words.append(word)
        result = " ".join(result_words)

        if result != text_lower:
            logger.info(
                f"[Transliterator] '{text}' -> '{result}' ({target_lang})"
            )
        return result

    def get_all_scripts(self, name: str) -> dict:
        name_lower = name.lower().strip()
        scripts    = {"en": name}

        words = name_lower.split()
        for lang in ["hi","ta","te","kn","ml","mr","bn","gu","pa"]:
            translated_words = []
            found_any        = False
            for word in words:
                lookup = COMMON_POLITICAL_NAMES.get(word, {})
                if lang in lookup:
                    translated_words.append(lookup[lang])
                    found_any = True
                else:
                    translated_words.append(word)
            if found_any:
                scripts[lang] = " ".join(translated_words)

        return scripts

    def normalize_for_search(self, query: str) -> list:
        variants = [query]
        query_lower = query.lower().strip()

        all_scripts = self.get_all_scripts(query_lower)
        for lang, variant in all_scripts.items():
            if variant != query and variant not in variants:
                variants.append(variant)

        latin_norm = re.sub(r"[aeiou]+", "", query_lower)
        if latin_norm not in variants:
            variants.append(latin_norm)

        return variants


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Transliteration Test")
    print("=" * 55)

    trans = Transliterator()

    test_names = ["Modi", "Rahul Gandhi", "Amit Shah", "Priya Sharma"]
    for name in test_names:
        scripts = trans.get_all_scripts(name)
        print(f"\n  {name}:")
        for lang, script_val in scripts.items():
            if script_val != name.lower():
                print(f"    [{lang}] {script_val}")

    print("\n  Search normalization for 'Modi':")
    variants = trans.normalize_for_search("Modi")
    for v in variants:
        print(f"    '{v}'")

    print("\nDone!")
