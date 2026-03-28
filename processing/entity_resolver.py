"""
BharatGraph - Entity Resolver
Matches the SAME person or company appearing under different names
across scrapers.

The core problem in Indian data:
  MyNeta says:  "Rahul Kumar"
  MCA says:     "RAHUL KUMAR"
  GeM says:     "R. Kumar"
  PIB says:     "Shri Rahul Kumar"

Are they the same person? This module figures that out.

Method: fuzzy string matching (no ML needed for Phase 2).
Phase 4 (AI) will upgrade this with graph embeddings.
"""

import re
import json
import os
from datetime import datetime
from loguru import logger
from processing.cleaner import NameCleaner


class EntityResolver:
    """
    Resolves duplicate entities across scraped datasets.

    Approach:
    1. Clean all names first (using NameCleaner)
    2. Build a token set for each name
    3. Compare token overlap ratios
    4. Score >= threshold -> same entity -> merge into canonical record

    Example:
        "Rahul Kumar"  -> tokens: {"rahul", "kumar"}
        "R. Kumar"     -> tokens: {"r", "kumar"}
        overlap = 1/2 = 0.5  -> probably same (threshold 0.6 = no match)

        "Rahul Kumar"  -> tokens: {"rahul", "kumar"}
        "Kumar Rahul"  -> tokens: {"kumar", "rahul"}
        overlap = 2/2 = 1.0  -> definite match
    """

    def __init__(self, threshold: float = 0.7):
        """
        threshold: minimum token overlap ratio to consider a match.
        0.7 means 70% of tokens must match.
        Higher = stricter (fewer false positives).
        Lower = looser (catches more variations but more false positives).
        """
        self.threshold = threshold
        self.cleaner   = NameCleaner()
        logger.info(f"[Resolver] Initialized with threshold={threshold}")

    def _tokenize(self, name: str) -> set:
        """
        Convert a name to a set of lowercase tokens.
        Strips single-char initials that can vary (R. vs Rahul).
        """
        if not name:
            return set()
        # Lowercase, remove punctuation except spaces
        name = name.lower()
        name = re.sub(r"[^\w\s]", " ", name)
        tokens = set(name.split())
        # Remove very short tokens (initials like "r", "k")
        # but keep them if the name is mostly initials
        long_tokens = {t for t in tokens if len(t) > 1}
        return long_tokens if long_tokens else tokens

    def similarity_score(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two names.
        Returns float between 0.0 (no match) and 1.0 (exact match).

        Uses Jaccard similarity on token sets:
        score = |intersection| / |union|
        """
        t1 = self._tokenize(name1)
        t2 = self._tokenize(name2)

        if not t1 or not t2:
            return 0.0

        intersection = t1 & t2
        union        = t1 | t2

        return len(intersection) / len(union)

    def is_same_entity(self, name1: str, name2: str) -> bool:
        """
        Returns True if two names likely refer to the same person/company.
        """
        # First try exact match (after cleaning)
        c1 = self.cleaner.clean_person_name(name1)
        c2 = self.cleaner.clean_person_name(name2)
        if c1.lower() == c2.lower():
            return True

        # Then try fuzzy match
        score = self.similarity_score(c1, c2)
        return score >= self.threshold

    def find_matches(self, name: str, candidates: list,
                     name_field: str = "name") -> list:
        """
        Find all records in candidates that match the given name.

        Args:
            name: the name to search for
            candidates: list of dicts with a name field
            name_field: which dict key contains the name

        Returns:
            list of (record, score) tuples, sorted by score desc
        """
        name_clean = self.cleaner.clean_person_name(name)
        matches = []

        for record in candidates:
            candidate_name = record.get(name_field, "")
            candidate_clean = self.cleaner.clean_person_name(candidate_name)

            score = self.similarity_score(name_clean, candidate_clean)
            if score >= self.threshold:
                matches.append((record, score))

        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def resolve_dataset(self, records: list,
                        name_field: str = "name") -> list:
        """
        Takes a list of records and groups duplicates together.
        Returns list of canonical records, each with a 'duplicates' key.

        This is the main method for deduplication within one dataset.
        """
        if not records:
            return []

        resolved   = []
        used_indices = set()

        for i, record in enumerate(records):
            if i in used_indices:
                continue

            canonical = dict(record)
            canonical["duplicates"]   = []
            canonical["_resolved"]    = True
            canonical["_resolve_ids"] = [i]

            name_i = record.get(name_field, "")

            # Find duplicates
            for j, other in enumerate(records):
                if j <= i or j in used_indices:
                    continue
                name_j = other.get(name_field, "")
                score  = self.similarity_score(
                    self.cleaner.clean_person_name(name_i),
                    self.cleaner.clean_person_name(name_j)
                )
                if score >= self.threshold:
                    canonical["duplicates"].append({
                        "record": other,
                        "score":  round(score, 3),
                    })
                    canonical["_resolve_ids"].append(j)
                    used_indices.add(j)

            used_indices.add(i)
            resolved.append(canonical)

        logger.info(
            f"[Resolver] {len(records)} records -> "
            f"{len(resolved)} unique entities "
            f"({len(records) - len(resolved)} duplicates merged)"
        )
        return resolved

    def cross_dataset_match(self,
                             dataset_a: list, dataset_b: list,
                             name_field_a: str = "name",
                             name_field_b: str = "name") -> list:
        """
        Find matching entities ACROSS two different datasets.
        e.g. match politicians (MyNeta) against company directors (MCA)

        Returns list of match dicts:
        {
          "record_a": {...},
          "record_b": {...},
          "score": 0.85,
          "match_type": "cross_dataset"
        }

        This is the KEY function for finding politician-company links.
        """
        matches = []

        for rec_a in dataset_a:
            name_a = self.cleaner.clean_person_name(
                rec_a.get(name_field_a, "")
            )
            if not name_a:
                continue

            for rec_b in dataset_b:
                name_b = self.cleaner.clean_person_name(
                    rec_b.get(name_field_b, "")
                )
                if not name_b:
                    continue

                score = self.similarity_score(name_a, name_b)
                if score >= self.threshold:
                    matches.append({
                        "record_a":   rec_a,
                        "record_b":   rec_b,
                        "name_a":     name_a,
                        "name_b":     name_b,
                        "score":      round(score, 3),
                        "match_type": "cross_dataset",
                        "matched_at": datetime.now().isoformat(),
                    })

        logger.info(
            f"[Resolver] Cross-dataset: {len(dataset_a)} x {len(dataset_b)} "
            f"-> {len(matches)} matches found"
        )
        return matches

    def save_matches(self, matches: list, filepath: str):
        """Save match results to JSON."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(matches, f, indent=2, ensure_ascii=False)
        logger.success(f"[Resolver] Saved {len(matches)} matches to {filepath}")


# ── Run directly to test ─────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Entity Resolver Test")
    print("=" * 55)

    resolver = EntityResolver(threshold=0.6)

    print("\n[1] Similarity scores:")
    pairs = [
        ("Rahul Kumar",       "RAHUL KUMAR"),
        ("Rahul Kumar",       "Kumar Rahul"),
        ("R. Kumar",          "Rahul Kumar"),
        ("Priya Sharma",      "Priya Devi"),
        ("Sample Infra Ltd",  "SAMPLE INFRASTRUCTURE PVT LTD"),
        ("John Smith",        "Jane Smith"),
        ("Narendra Modi",     "N. Modi"),
    ]
    for a, b in pairs:
        score = resolver.similarity_score(a, b)
        match = "✅ MATCH" if score >= 0.6 else "❌ no match"
        print(f"  {match} ({score:.2f})  '{a}' vs '{b}'")

    print("\n[2] Deduplication within dataset:")
    politicians = [
        {"name": "RAHUL KUMAR",       "party": "Party A", "state": "TN"},
        {"name": "Rahul Kumar",        "party": "Party A", "state": "Tamil Nadu"},
        {"name": "Priya Sharma",       "party": "Party B", "state": "MH"},
        {"name": "PRIYA SHARMA",       "party": "Party B", "state": "Maharashtra"},
        {"name": "Suresh Patel",       "party": "Party C", "state": "GJ"},
    ]
    resolved = resolver.resolve_dataset(politicians, name_field="name")
    print(f"  Input: {len(politicians)} records")
    print(f"  Output: {len(resolved)} unique entities")
    for r in resolved:
        dupes = len(r["duplicates"])
        print(f"  -> '{r['name']}'" + (f" (merged {dupes} duplicate)" if dupes else ""))

    print("\n[3] Cross-dataset matching (politicians vs company directors):")
    directors = [
        {"director_name": "Rahul Kumar",  "company": "Sample Infra Pvt Ltd"},
        {"director_name": "Priya Sharma", "company": "ABC Trading Ltd"},
        {"director_name": "Amit Shah",    "company": "XYZ Holdings Ltd"},
    ]
    matches = resolver.cross_dataset_match(
        politicians, directors,
        name_field_a="name",
        name_field_b="director_name"
    )
    print(f"  Found {len(matches)} cross-dataset matches:")
    for m in matches:
        print(f"  -> '{m['name_a']}' (politician) matches '{m['name_b']}' (director) "
              f"score={m['score']}")
        print(f"     Company: {m['record_b']['company']}")

    print("\nDone!")
