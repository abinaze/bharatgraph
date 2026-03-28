"""
BharatGraph - Data Cleaner
Normalizes messy Indian names, titles, and text fields
scraped from government datasets.

Why this matters:
  "RAHUL KUMAR"  == "Rahul Kumar"  == "rahul kumar"
  "Shri Rahul Kumar" == "Rahul Kumar"
  "Dr. A.P.J. Abdul Kalam" -> normalized form
  "M/S SAMPLE INFRA PVT LTD" -> "Sample Infra Pvt Ltd"
"""

import re
import unicodedata
from loguru import logger


# Honorific titles to strip from Indian names
INDIAN_TITLES = [
    "shri", "smt", "smt.", "shri.", "dr", "dr.", "prof", "prof.",
    "mr", "mr.", "mrs", "mrs.", "ms", "ms.", "adv", "adv.",
    "hon", "hon.", "honble", "hon'ble", "er", "er.",
    "col", "col.", "gen", "brig", "maj", "capt",
    "justice", "judge", "chief justice",
]

# Company suffixes to normalize
COMPANY_SUFFIXES = {
    "pvt ltd": "Pvt Ltd",
    "pvt. ltd.": "Pvt Ltd",
    "pvt. ltd": "Pvt Ltd",
    "private limited": "Pvt Ltd",
    "p ltd": "Pvt Ltd",
    " ltd": " Ltd",
    "limited": "Ltd",
    "llp": "LLP",
    "l.l.p": "LLP",
    "m/s": "",
    "m/s.": "",
}


class NameCleaner:
    """
    Cleans and normalizes Indian personal names and company names.
    Used before entity resolution to ensure consistent matching.
    """

    def clean_person_name(self, name: str) -> str:
        """
        Normalize a person's name.
        - Strip honorific titles (Shri, Dr., Smt. etc.)
        - Fix casing (RAHUL KUMAR -> Rahul Kumar)
        - Remove extra whitespace and punctuation
        - Normalize unicode (Hindi/regional chars to ASCII where possible)

        Example:
            "SHRI RAHUL KUMAR" -> "Rahul Kumar"
            "Dr. A.P.J. Abdul Kalam" -> "A.P.J. Abdul Kalam"
            "smt. priya devi  " -> "Priya Devi"
        """
        if not name or not isinstance(name, str):
            return ""

        # Normalize unicode (handle accented chars, etc.)
        name = unicodedata.normalize("NFKC", name)

        # Strip leading/trailing whitespace
        name = name.strip()

        # Remove content in brackets e.g. "Rahul Kumar (MLA)"
        name = re.sub(r"\(.*?\)", "", name).strip()

        # Remove special characters except dots, hyphens, spaces
        name = re.sub(r"[^\w\s.\-']", " ", name)

        # Fix casing: Title Case
        name = name.title()

        # Strip known titles (case-insensitive)
        name_lower = name.lower()
        for title in INDIAN_TITLES:
            # Match title at start with optional space/dot after
            patterns = [
                rf"^{re.escape(title)}\s+",
                rf"^{re.escape(title)}\.\s*",
            ]
            for pat in patterns:
                name = re.sub(pat, "", name, flags=re.IGNORECASE).strip()

        # Clean up multiple spaces
        name = re.sub(r"\s+", " ", name).strip()

        return name

    def clean_company_name(self, name: str) -> str:
        """
        Normalize a company name.
        - Remove M/s prefix
        - Standardize Ltd/Pvt Ltd/LLP suffixes
        - Fix casing
        - Remove extra punctuation

        Example:
            "M/S SAMPLE INFRASTRUCTURE PRIVATE LIMITED" -> "Sample Infrastructure Pvt Ltd"
            "ABC CONSTRUCTIONS PVT. LTD." -> "Abc Constructions Pvt Ltd"
        """
        if not name or not isinstance(name, str):
            return ""

        name = unicodedata.normalize("NFKC", name).strip()
        name = re.sub(r"\s+", " ", name)

        # Title case first
        name = name.title()

        # Normalize company suffixes
        name_lower = name.lower()
        for old, new in COMPANY_SUFFIXES.items():
            if name_lower.startswith(old):
                name = new + " " + name[len(old):].strip()
                name = name.strip()
                name_lower = name.lower()

        # Fix suffix at end
        for old, new in COMPANY_SUFFIXES.items():
            if name_lower.endswith(old):
                name = name[: -len(old)].strip() + (" " + new if new else "")
                name = name.strip()
                name_lower = name.lower()
                break

        # Remove duplicate spaces
        name = re.sub(r"\s+", " ", name).strip()

        return name

    def clean_amount(self, amount_str: str) -> float:
        """
        Parse Indian currency strings to float (in crore).
        Examples:
            "Rs. 1,50,000" -> 0.015  (in crore)
            "150 Cr"       -> 150.0
            "₹5,00,00,000" -> 50.0
        """
        if not amount_str:
            return 0.0

        s = str(amount_str).lower().strip()

        # Already a number
        try:
            return float(s)
        except ValueError:
            pass

        # Remove currency symbols and commas
        s = re.sub(r"[₹rs.,\s]", "", s)

        # Handle crore/lakh suffixes
        multiplier = 1.0
        if "crore" in s or "cr" in s:
            s = re.sub(r"crore|cr", "", s)
            multiplier = 1.0  # already in crore
        elif "lakh" in s or "lac" in s:
            s = re.sub(r"lakh|lac|l", "", s)
            multiplier = 0.01  # convert lakh to crore

        s = s.strip()
        try:
            return float(s) * multiplier
        except ValueError:
            return 0.0

    def clean_state_name(self, state: str) -> str:
        """
        Normalize Indian state names.
        Example: "TN" -> "Tamil Nadu", "tamilnadu" -> "Tamil Nadu"
        """
        if not state:
            return ""

        STATE_MAP = {
            "tn": "Tamil Nadu", "tamilnadu": "Tamil Nadu",
            "mh": "Maharashtra", "maharashtra": "Maharashtra",
            "dl": "Delhi", "delhi": "Delhi", "new delhi": "Delhi",
            "ka": "Karnataka", "karnataka": "Karnataka",
            "up": "Uttar Pradesh", "uttarpradesh": "Uttar Pradesh",
            "wb": "West Bengal", "westbengal": "West Bengal",
            "rj": "Rajasthan", "rajasthan": "Rajasthan",
            "mp": "Madhya Pradesh", "madhyapradesh": "Madhya Pradesh",
            "gj": "Gujarat", "gujarat": "Gujarat",
            "ap": "Andhra Pradesh", "andhrapradesh": "Andhra Pradesh",
            "ts": "Telangana", "telangana": "Telangana",
            "kl": "Kerala", "kerala": "Kerala",
            "pb": "Punjab", "punjab": "Punjab",
            "hr": "Haryana", "haryana": "Haryana",
            "br": "Bihar", "bihar": "Bihar",
            "or": "Odisha", "odisha": "Odisha", "orissa": "Odisha",
            "as": "Assam", "assam": "Assam",
            "jh": "Jharkhand", "jharkhand": "Jharkhand",
            "hp": "Himachal Pradesh", "himachalpradesh": "Himachal Pradesh",
            "uk": "Uttarakhand", "uttarakhand": "Uttarakhand",
            "ct": "Chhattisgarh", "chhattisgarh": "Chhattisgarh",
            "ga": "Goa", "goa": "Goa",
            "mn": "Manipur", "manipur": "Manipur",
            "ml": "Meghalaya", "meghalaya": "Meghalaya",
            "mz": "Mizoram", "mizoram": "Mizoram",
            "nl": "Nagaland", "nagaland": "Nagaland",
            "tr": "Tripura", "tripura": "Tripura",
            "sk": "Sikkim", "sikkim": "Sikkim",
            "ar": "Arunachal Pradesh",
        }

        key = re.sub(r"\s+", "", state.lower().strip())
        return STATE_MAP.get(key, state.title())

    def clean_record(self, record: dict, record_type: str = "person") -> dict:
        """
        Clean all fields in a scraped record dict.
        record_type: 'person', 'company', or 'contract'
        """
        cleaned = dict(record)  # copy

        if record_type == "person":
            if "name" in cleaned:
                cleaned["name_raw"]    = cleaned["name"]
                cleaned["name"]        = self.clean_person_name(cleaned["name"])
            if "party" in cleaned:
                cleaned["party"]       = cleaned["party"].strip().title()
            if "state" in cleaned:
                cleaned["state"]       = self.clean_state_name(cleaned["state"])

        elif record_type == "company":
            if "name" in cleaned:
                cleaned["name_raw"]    = cleaned["name"]
                cleaned["name"]        = self.clean_company_name(cleaned["name"])
            if "state" in cleaned:
                cleaned["state"]       = self.clean_state_name(cleaned["state"])

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


# ── Run directly to test ─────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Name Cleaner Test")
    print("=" * 55)

    cleaner = NameCleaner()

    print("\n[1] Person name cleaning:")
    test_names = [
        "SHRI RAHUL KUMAR",
        "smt. priya devi",
        "Dr. A.P.J. Abdul Kalam",
        "Hon. Justice Ranjan Gogoi",
        "MR. NARENDRA  MODI",
        "  adv. sunita sharma  ",
    ]
    for name in test_names:
        cleaned = cleaner.clean_person_name(name)
        print(f"  '{name}' -> '{cleaned}'")

    print("\n[2] Company name cleaning:")
    test_companies = [
        "M/S SAMPLE INFRASTRUCTURE PRIVATE LIMITED",
        "ABC CONSTRUCTIONS PVT. LTD.",
        "xyz trading co. llp",
        "M/S. DELHI ROADS LTD",
    ]
    for name in test_companies:
        cleaned = cleaner.clean_company_name(name)
        print(f"  '{name}' -> '{cleaned}'")

    print("\n[3] Amount parsing (to crore):")
    test_amounts = ["150 Cr", "500 lakh", "1500000", "Rs. 2,50,00,000", "₹75cr"]
    for amt in test_amounts:
        val = cleaner.clean_amount(amt)
        print(f"  '{amt}' -> {val} Cr")

    print("\n[4] State normalization:")
    test_states = ["TN", "tamilnadu", "MH", "dl", "UP", "wb"]
    for state in test_states:
        cleaned = cleaner.clean_state_name(state)
        print(f"  '{state}' -> '{cleaned}'")

    print("\n[5] Full record cleaning:")
    record = {
        "name": "SHRI RAMESH KUMAR",
        "party": "sample party",
        "state": "TN",
        "criminal_cases": "3",
        "total_assets": "50 lakh",
    }
    cleaned = cleaner.clean_record(record, record_type="person")
    print(f"  Input:  {record}")
    print(f"  Output: {cleaned}")
    print("\nDone!")
