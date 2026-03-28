"""
BharatGraph - Data Cleaner
Normalizes messy Indian names, titles, and text fields
scraped from government datasets.
"""

import re
import unicodedata
from loguru import logger


INDIAN_TITLES = [
    "shri", "smt", "smt.", "shri.", "dr", "dr.", "prof", "prof.",
    "mr", "mr.", "mrs", "mrs.", "ms", "ms.", "adv", "adv.",
    "hon", "hon.", "honble", "hon'ble", "er", "er.",
    "col", "col.", "gen", "brig", "maj", "capt",
    "justice", "judge", "chief justice",
]


class NameCleaner:
    """
    Cleans and normalizes Indian personal names and company names.
    Used before entity resolution to ensure consistent matching.
    """

    def clean_person_name(self, name: str) -> str:
        """
        Normalize a person name.
        'SHRI RAHUL KUMAR' -> 'Rahul Kumar'
        'Dr. A.P.J. Abdul Kalam' -> 'A.P.J. Abdul Kalam'
        """
        if not name or not isinstance(name, str):
            return ""
        name = unicodedata.normalize("NFKC", name).strip()
        name = re.sub(r"\(.*?\)", "", name).strip()
        name = re.sub(r"[^\w\s.\-']", " ", name)
        name = name.title()
        for title in INDIAN_TITLES:
            for pat in [rf"^{re.escape(title)}\s+", rf"^{re.escape(title)}\.\s*"]:
                name = re.sub(pat, "", name, flags=re.IGNORECASE).strip()
        return re.sub(r"\s+", " ", name).strip()

    def clean_company_name(self, name: str) -> str:
        """
        Normalize a company name.
        'M/S. DELHI ROADS LTD' -> 'Delhi Roads Ltd'
        'M/S SAMPLE INFRASTRUCTURE PRIVATE LIMITED' -> 'Sample Infrastructure Pvt Ltd'
        'ABC CONSTRUCTIONS PVT. LTD.' -> 'Abc Constructions Pvt Ltd'
        """
        if not name or not isinstance(name, str):
            return ""
        name = unicodedata.normalize("NFKC", name).strip()
        name = re.sub(r"\s+", " ", name)
        # Strip M/s prefix before title case
        name = re.sub(r"^m\s*/\s*s\.?\s*", "", name, flags=re.IGNORECASE).strip()
        name = name.title()
        # Normalize end suffixes
        end_map = [
            (r"private limited$", "Pvt Ltd"),
            (r"pvt\.\s*ltd\.$",   "Pvt Ltd"),
            (r"pvt\.\s*ltd$",     "Pvt Ltd"),
            (r"pvt\s+ltd$",       "Pvt Ltd"),
            (r"p\s*ltd$",         "Pvt Ltd"),
            (r"l\.l\.p\.?$",      "LLP"),
            (r"llp$",             "LLP"),
            (r"limited$",         "Ltd"),
            (r"ltd\.$",           "Ltd"),
        ]
        for pattern, replacement in end_map:
            name, n = re.subn(pattern, replacement, name, flags=re.IGNORECASE)
            if n:
                break
        return re.sub(r"\s+", " ", name).strip()

    def clean_amount(self, amount_str: str) -> float:
        """
        Parse Indian currency strings to float in crore.
        '150 Cr' -> 150.0,  '500 lakh' -> 5.0,
        '1500000' -> 1.5 (raw rupees),  '₹75cr' -> 75.0
        """
        if not amount_str:
            return 0.0
        s = str(amount_str).strip()
        # Plain number -> treat as raw rupees
        try:
            return round(float(s.replace(",", "")) / 1e7, 4)
        except ValueError:
            pass
        # Remove currency symbols and commas
        s = re.sub(r"[₹,\s]", "", s)
        s = re.sub(r"^rs\.?", "", s, flags=re.IGNORECASE)
        # Detect suffix
        if re.search(r"crore|cr", s, re.IGNORECASE):
            s = re.sub(r"crore|cr", "", s, flags=re.IGNORECASE)
            multiplier = 1.0
        elif re.search(r"lakh|lac", s, re.IGNORECASE):
            s = re.sub(r"lakh|lac", "", s, flags=re.IGNORECASE)
            multiplier = 0.01
        else:
            multiplier = 1 / 1e7
        try:
            return round(float(s.strip()) * multiplier, 4)
        except ValueError:
            return 0.0

    def clean_state_name(self, state: str) -> str:
        """Normalize Indian state names. 'TN' -> 'Tamil Nadu'"""
        if not state:
            return ""
        STATE_MAP = {
            "tn": "Tamil Nadu",       "tamilnadu": "Tamil Nadu",
            "mh": "Maharashtra",      "maharashtra": "Maharashtra",
            "dl": "Delhi",            "delhi": "Delhi",
            "ka": "Karnataka",        "karnataka": "Karnataka",
            "up": "Uttar Pradesh",    "uttarpradesh": "Uttar Pradesh",
            "wb": "West Bengal",      "westbengal": "West Bengal",
            "rj": "Rajasthan",        "rajasthan": "Rajasthan",
            "mp": "Madhya Pradesh",   "madhyapradesh": "Madhya Pradesh",
            "gj": "Gujarat",          "gujarat": "Gujarat",
            "ap": "Andhra Pradesh",   "andhrapradesh": "Andhra Pradesh",
            "ts": "Telangana",        "telangana": "Telangana",
            "kl": "Kerala",           "kerala": "Kerala",
            "pb": "Punjab",           "punjab": "Punjab",
            "hr": "Haryana",          "haryana": "Haryana",
            "br": "Bihar",            "bihar": "Bihar",
            "or": "Odisha",           "odisha": "Odisha",
            "as": "Assam",            "assam": "Assam",
            "jh": "Jharkhand",        "jharkhand": "Jharkhand",
            "hp": "Himachal Pradesh", "himachalpradesh": "Himachal Pradesh",
            "uk": "Uttarakhand",      "uttarakhand": "Uttarakhand",
            "ct": "Chhattisgarh",     "chhattisgarh": "Chhattisgarh",
            "ga": "Goa",              "goa": "Goa",
            "mn": "Manipur",          "manipur": "Manipur",
            "ml": "Meghalaya",        "meghalaya": "Meghalaya",
            "mz": "Mizoram",          "mizoram": "Mizoram",
            "nl": "Nagaland",         "nagaland": "Nagaland",
            "tr": "Tripura",          "tripura": "Tripura",
            "sk": "Sikkim",           "sikkim": "Sikkim",
            "ar": "Arunachal Pradesh",
        }
        key = re.sub(r"\s+", "", state.lower().strip())
        return STATE_MAP.get(key, state.title())

    def clean_record(self, record: dict, record_type: str = "person") -> dict:
        """Clean all fields in a scraped record dict."""
        cleaned = dict(record)
        if record_type == "person":
            if "name" in cleaned:
                cleaned["name_raw"] = cleaned["name"]
                cleaned["name"]     = self.clean_person_name(cleaned["name"])
            if "party" in cleaned:
                cleaned["party"]    = cleaned["party"].strip().title()
            if "state" in cleaned:
                cleaned["state"]    = self.clean_state_name(cleaned["state"])
        elif record_type == "company":
            if "name" in cleaned:
                cleaned["name_raw"] = cleaned["name"]
                cleaned["name"]     = self.clean_company_name(cleaned["name"])
            if "state" in cleaned:
                cleaned["state"]    = self.clean_state_name(cleaned["state"])
        elif record_type == "contract":
            if "seller_name" in cleaned:
                cleaned["seller_name_raw"] = cleaned["seller_name"]
                cleaned["seller_name"]     = self.clean_company_name(cleaned["seller_name"])
            if "buyer_org" in cleaned:
                cleaned["buyer_org"]       = cleaned["buyer_org"].strip().title()
            if "state" in cleaned:
                cleaned["state"]           = self.clean_state_name(cleaned["state"])
            if "amount_inr" in cleaned:
                cleaned["amount_crore"]    = self.clean_amount(
                    str(cleaned.get("amount_crore", cleaned.get("amount_inr", 0)))
                )
        cleaned["_cleaned"] = True
        return cleaned


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Name Cleaner Test")
    print("=" * 55)
    c = NameCleaner()

    print("\n[1] Person names:")
    for n in ["SHRI RAHUL KUMAR","smt. priya devi","Dr. A.P.J. Abdul Kalam",
              "Hon. Justice Ranjan Gogoi","MR. NARENDRA  MODI","  adv. sunita sharma  "]:
        print(f"  '{n}' -> '{c.clean_person_name(n)}'")

    print("\n[2] Company names:")
    for n in ["M/S SAMPLE INFRASTRUCTURE PRIVATE LIMITED",
              "ABC CONSTRUCTIONS PVT. LTD.","xyz trading co. llp","M/S. DELHI ROADS LTD"]:
        print(f"  '{n}' -> '{c.clean_company_name(n)}'")

    print("\n[3] Amounts (to crore):")
    for a in ["150 Cr","500 lakh","1500000","Rs. 2,50,00,000","₹75cr"]:
        print(f"  '{a}' -> {c.clean_amount(a)} Cr")

    print("\n[4] States:")
    for s in ["TN","tamilnadu","MH","dl","UP","wb"]:
        print(f"  '{s}' -> '{c.clean_state_name(s)}'")

    print("\n[5] Full record:")
    r = {"name":"SHRI RAMESH KUMAR","party":"sample party","state":"TN","criminal_cases":"3"}
    print(f"  In:  {r}")
    print(f"  Out: {c.clean_record(r,'person')}")
    print("\nDone!")
