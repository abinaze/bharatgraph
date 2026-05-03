import os
import sys
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger

COMMON_POLITICAL_NAMES = {
    "modi":    {"hi":"\u092e\u094b\u0926\u0940","ta":"\u0bae\u0bcb\u0b9f\u0bbf","te":"\u0c2e\u0c4b\u0c26\u0c40","kn":"\u0cae\u0ccb\u0ca6\u0cbf","ml":"\u0d2e\u0d4b\u0d26\u0d3f"},
    "gandhi":  {"hi":"\u0917\u093e\u0902\u0927\u0940","ta":"\u0b95\u0bbe\u0ba8\u0bcd\u0ba4\u0bbf","te":"\u0c17\u0c3e\u0c02\u0c27\u0c40","kn":"\u0c97\u0cbe\u0c82\u0ca7\u0cbf","ml":"\u0d17\u0d3e\u0d28\u0d4d\u0d27\u0d3f"},
    "nehru":   {"hi":"\u0928\u0947\u0939\u0930\u0942","ta":"\u0ba8\u0bc7\u0bb0\u0bc1","te":"\u0c28\u0c46\u0c39\u0c4d\u0c30\u0c42","kn":"\u0ca8\u0cc6\u0cb9\u0ccd\u0cb0\u0cc1","ml":"\u0d28\u0d46\u0d39\u0d4d\u200c\u0d31\u0d41"},
    "singh":   {"hi":"\u0938\u093f\u0902\u0939","ta":"\u0b9a\u0bbf\u0b99\u0bcd","te":"\u0c38\u0c3f\u0c02\u0c17\u0c4d","kn":"\u0cb8\u0cbf\u0c82\u0c97\u0ccd","ml":"\u0d38\u0d3f\u0d02\u0d17\u0d4d"},
    "kumar":   {"hi":"\u0915\u0941\u092e\u093e\u0930","ta":"\u0b95\u0bc1\u0bae\u0bbe\u0bb0\u0bcd","te":"\u0c15\u0c41\u0c2e\u0c3e\u0c30\u0c4d","kn":"\u0c95\u0cc1\u0cae\u0cbe\u0cb0\u0ccd","ml":"\u0d15\u0d41\u0d2e\u0d3e\u0d7c"},
    "sharma":  {"hi":"\u0936\u0930\u094d\u092e\u093e","ta":"\u0b9a\u0bb0\u0bcd\u0bae\u0bbe","te":"\u0c36\u0c30\u0c4d\u0c2e","kn":"\u0cb6\u0cb0\u0ccd\u0cae","ml":"\u0d36\u0d7c\u0d2e"},
    "verma":   {"hi":"\u0935\u0930\u094d\u092e\u093e","ta":"\u0bb5\u0bb0\u0bcd\u0bae\u0bbe","te":"\u0c35\u0c30\u0c4d\u0c2e","kn":"\u0cb5\u0cb0\u0ccd\u0cae","ml":"\u0d35\u0d7c\u0d2e"},
    "patel":   {"hi":"\u092a\u091f\u0947\u0932","ta":"\u0baa\u0b9f\u0bc7\u0bb2\u0bcd","te":"\u0c2a\u0c1f\u0c47\u0c32\u0c4d","kn":"\u0caa\u0c9f\u0cc7\u0cb2\u0ccd","ml":"\u0d2a\u0d1f\u0d4d\u0d1f\u0d47\u0d7d"},
    "reddy":   {"hi":"\u0930\u0947\u0921\u094d\u0921\u0940","ta":"\u0bb0\u0bc6\u0b9f\u0bcd\u0b9f\u0bbf","te":"\u0c30\u0c46\u0c21\u0c4d\u0c21\u0c3f","kn":"\u0cb0\u0cc6\u0ca1\u0ccd\u0ca1\u0cbf","ml":"\u0d31\u0d46\u0d21\u0d4d\u0d21\u0d3f"},
    "naidu":   {"hi":"\u0928\u093e\u092f\u0921\u0942","ta":"\u0ba8\u0bbe\u0baf\u0bc1\u0b9f\u0bc1","te":"\u0c28\u0c3e\u0c2f\u0c41\u0c21\u0c41","kn":"\u0ca8\u0cbe\u0caf\u0ccd\u0ca1\u0cc1","ml":"\u0d28\u0d3e\u0d2f\u0d4d\u0d21\u0d41"},
    "rao":     {"hi":"\u0930\u093e\u0935","ta":"\u0bb0\u0bbe\u0bb5\u0bcd","te":"\u0c30\u0c3e\u0c35\u0c41","kn":"\u0cb0\u0cbe\u0cb5\u0ccd","ml":"\u0d31\u0d3e\u0d35\u0d41"},
    "iyer":    {"hi":"\u0905\u092f\u094d\u092f\u0930","ta":"\u0b90\u0baf\u0bb0\u0bcd","te":"\u0c05\u0c2f\u0c4d\u0c2f\u0c30\u0c4d","kn":"\u0c85\u0caf\u0ccd\u0caf\u0cb0\u0ccd","ml":"\u0d05\u0d2f\u0d4d\u0d2f\u0d7c"},
    "nair":    {"hi":"\u0928\u093e\u092f\u0930","ta":"\u0ba8\u0bbe\u0baf\u0bb0\u0bcd","te":"\u0c28\u0c3e\u0c2f\u0c30\u0c4d","kn":"\u0ca8\u0cbe\u0caf\u0cb0\u0ccd","ml":"\u0d28\u0d3e\u0d2f\u0d7c"},
    "menon":   {"hi":"\u092e\u0947\u0928\u0928","ta":"\u0bae\u0bc7\u0ba9\u0ba9\u0bcd","te":"\u0c2e\u0c47\u0c28\u0c28\u0c4d","kn":"\u0cae\u0cc7\u0ca8\u0ca8\u0ccd","ml":"\u0d2e\u0d47\u0d28\u0d4b\u0d7b"},
    "pillai":  {"hi":"\u092a\u093f\u0932\u094d\u0932\u0908","ta":"\u0baa\u0bbf\u0bb3\u0bcd\u0bb3\u0bc8","te":"\u0c2a\u0c3f\u0c33\u0c4d\u0c33\u0c48","kn":"\u0caa\u0cbf\u0cb3\u0ccd\u0cb3\u0cc8","ml":"\u0d2a\u0d3f\u0d33\u0d4d\u0d33"},
}

PHONEME_MAP_HI = {
    "a":"\u0905","aa":"\u0906","i":"\u0907","ee":"\u0908","u":"\u0909","oo":"\u090a",
    "e":"\u090f","ai":"\u0910","o":"\u0913","au":"\u0914",
    "k":"\u0915","kh":"\u0916","g":"\u0917","gh":"\u0918","n":"\u0928",
    "ch":"\u091a","chh":"\u091b","j":"\u091c","jh":"\u091d",
    "t":"\u0924","th":"\u0925","d":"\u0926","dh":"\u0927",
    "p":"\u092a","ph":"\u092b","b":"\u092c","bh":"\u092d","m":"\u092e",
    "y":"\u092f","r":"\u0930","l":"\u0932","v":"\u0935","w":"\u0935",
    "sh":"\u0936","s":"\u0938","h":"\u0939",
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
