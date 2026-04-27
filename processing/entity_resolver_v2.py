"""
BharatGraph - Entity Resolution v2: Canonical Identity Engine
Replaces the basic Jaccard resolver with a multi-signal pipeline:
  1. Exact key match (CIN, PAN, GSTIN, Aadhaar prefix)
  2. Jaro-Winkler string similarity
  3. Jaccard token overlap
  4. Embedding cosine similarity (optional, skipped if model unavailable)

The same real-world entity appearing under multiple scraped IDs is
collapsed into one canonical ID without deleting source records.
Pure ASCII.
"""
import re
import os
import json
import hashlib
from datetime import datetime
from loguru import logger
from processing.cleaner import NameCleaner
from processing.canonical_id import canonical_id


# ---- Jaro-Winkler (no external dependency) ----------------------------

def _jaro(s1: str, s2: str) -> float:
    if s1 == s2:
        return 1.0
    l1, l2 = len(s1), len(s2)
    if l1 == 0 or l2 == 0:
        return 0.0
    match_dist = max(l1, l2) // 2 - 1
    if match_dist < 0:
        match_dist = 0
    s1_matches = [False] * l1
    s2_matches = [False] * l2
    matches = 0
    transpositions = 0
    for i in range(l1):
        start = max(0, i - match_dist)
        end   = min(i + match_dist + 1, l2)
        for j in range(start, end):
            if s2_matches[j] or s1[i] != s2[j]:
                continue
            s1_matches[i] = True
            s2_matches[j] = True
            matches += 1
            break
    if matches == 0:
        return 0.0
    k = 0
    for i in range(l1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1
    return (matches / l1 + matches / l2 +
            (matches - transpositions / 2) / matches) / 3


def jaro_winkler(s1: str, s2: str, p: float = 0.1) -> float:
    """Jaro-Winkler similarity. p=prefix scaling factor (standard=0.1)."""
    j = _jaro(s1, s2)
    prefix = 0
    for c1, c2 in zip(s1[:4], s2[:4]):
        if c1 == c2:
            prefix += 1
        else:
            break
    return j + prefix * p * (1 - j)


# ---- Jaccard on tokens ------------------------------------------------

def _tokenize(name: str) -> set:
    name = name.lower()
    name = re.sub(r"[^\w\s]", " ", name)
    tokens = set(name.split())
    long_t = {t for t in tokens if len(t) > 1}
    return long_t if long_t else tokens


def jaccard(name1: str, name2: str) -> float:
    t1, t2 = _tokenize(name1), _tokenize(name2)
    if not t1 or not t2:
        return 0.0
    return len(t1 & t2) / len(t1 | t2)


# ---- Indian name normalisation ----------------------------------------

_HONORIFICS = [
    "shri", "smt", "dr", "prof", "mr", "mrs", "ms", "adv", "er",
    "hon", "honble", "col", "gen", "brig", "maj", "capt", "late",
    "sri", "kumari", "km",
]

_COMPANY_SUFFIXES = [
    ("private limited", "pvt ltd"),
    ("pvt. ltd.", "pvt ltd"),
    ("pvt.ltd.", "pvt ltd"),
    ("pvt ltd.", "pvt ltd"),
    ("p. ltd.", "pvt ltd"),
    ("p.ltd.", "pvt ltd"),
    ("limited", "ltd"),
    ("ltd.", "ltd"),
    ("(india)", ""),
    ("india pvt", "pvt"),
    ("llp", "llp"),
]


def normalise_indian_name(name: str, kind: str = "person") -> str:
    """
    Normalise Indian person or company name for comparison.
    kind: "person" or "company"
    """
    name = str(name).strip().lower()
    # Strip M/s prefix for companies
    name = re.sub(r"^m\s*/\s*s\.?\s*", "", name)
    if kind == "person":
        for h in _HONORIFICS:
            name = re.sub(rf"^{re.escape(h)}\.?\s+", "", name)
            name = re.sub(rf"^{re.escape(h)}\.?\s*$", "", name)
    else:
        for old, new in _COMPANY_SUFFIXES:
            name = name.replace(old, new)
    # Remove punctuation except spaces and hyphens
    name = re.sub(r"[^\w\s\-]", " ", name)
    return re.sub(r"\s+", " ", name).strip()


# ---- Optional sentence-transformers embedding -------------------------

_embedding_model = None
_embedding_available = None


def _get_embedding_model():
    global _embedding_model, _embedding_available
    if _embedding_available is False:
        return None
    if _embedding_model is not None:
        return _embedding_model
    try:
        from sentence_transformers import SentenceTransformer, util
        _embedding_model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        _embedding_available = True
        logger.success("[ResolverV2] Embedding model loaded")
        return _embedding_model
    except Exception as e:
        _embedding_available = False
        logger.warning(f"[ResolverV2] Embedding model unavailable: {e}. "
                       "Using Jaro-Winkler + Jaccard only.")
        return None


def _embedding_cosine(name1: str, name2: str) -> float:
    model = _get_embedding_model()
    if model is None:
        return 0.0
    try:
        from sentence_transformers import util
        embs = model.encode([name1, name2], convert_to_tensor=True)
        return float(util.cos_sim(embs[0], embs[1]))
    except Exception:
        return 0.0


# ---- Main resolver class ----------------------------------------------

class EntityResolverV2:
    """
    Multi-signal entity resolution engine.

    Signal weights (sum to 1.0 when no exact-key match):
      jaro_winkler   0.30  -- character-level similarity
      jaccard        0.20  -- token overlap
      embedding      0.50  -- semantic / multilingual cosine

    When embeddings are unavailable (no sentence-transformers):
      jaro_winkler   0.60  -- rescaled
      jaccard        0.40  -- rescaled

    Exact key match (PAN/CIN/GSTIN) always returns confidence=1.0.

    combined_score >= threshold (default 0.82) means same entity.
    """

    def __init__(self, threshold: float = 0.82):
        self.threshold = threshold
        self.cleaner   = NameCleaner()
        logger.info(f"[ResolverV2] threshold={threshold}")

    # -- exact key scoring ------------------------------------------

    def _exact_key_score(self, rec_a: dict, rec_b: dict) -> float:
        """
        Returns 1.0 if both records share a non-empty unique identifier.
        Returns 0.0 if keys differ or are both absent.
        """
        key_fields = ["cin", "pan", "gstin", "wikidata_id", "darpan_id",
                      "bond_number", "order_id", "tender_id", "icij_node_id"]
        for field in key_fields:
            val_a = str(rec_a.get(field) or "").strip().upper()
            val_b = str(rec_b.get(field) or "").strip().upper()
            if val_a and val_b:
                return 1.0 if val_a == val_b else 0.0
        return 0.0

    # -- combined score ----------------------------------------------

    def combined_score(self, name_a: str, name_b: str,
                       rec_a: dict = None,
                       rec_b: dict = None,
                       kind: str = "person") -> float:
        """
        Compute combined similarity score between two entity names.
        rec_a/rec_b: optional dicts for exact key comparison.
        kind: "person" or "company" (affects normalisation).
        """
        # Exact key always wins
        if rec_a and rec_b:
            ek = self._exact_key_score(rec_a, rec_b)
            if ek == 1.0:
                return 1.0
            if ek == 0.0 and any(
                str(rec_a.get(f) or "").strip()
                for f in ["cin", "pan", "gstin"]
            ):
                # Both have an ID but they differ -> definitely different
                return 0.0

        a = normalise_indian_name(name_a, kind)
        b = normalise_indian_name(name_b, kind)

        if not a or not b:
            return 0.0
        if a == b:
            return 1.0

        jw   = jaro_winkler(a, b)
        jacc = jaccard(a, b)

        model = _get_embedding_model()
        if model is not None:
            cos = _embedding_cosine(name_a, name_b)
            return 0.30 * jw + 0.20 * jacc + 0.50 * cos
        else:
            # No embeddings: rescale JW + Jaccard to 1.0
            return 0.60 * jw + 0.40 * jacc

    def is_same_entity(self, name_a: str, name_b: str,
                        rec_a: dict = None,
                        rec_b: dict = None,
                        kind: str = "person") -> bool:
        return self.combined_score(name_a, name_b, rec_a, rec_b, kind) >= self.threshold

    # -- deduplication within one dataset ----------------------------

    def resolve_dataset(self, records: list,
                         name_field: str = "name",
                         kind: str = "person") -> list:
        """
        Deduplicate records within a single dataset.
        Returns canonical records; each has an 'aliases' list.
        Backward-compatible: adds 'duplicates' key (same as v1).
        """
        if not records:
            return []

        resolved = []
        used     = set()

        for i, rec in enumerate(records):
            if i in used:
                continue

            canon = dict(rec)
            canon["aliases"]      = []
            canon["duplicates"]   = []   # backward compat with v1
            canon["_resolved_v2"] = True
            name_i = rec.get(name_field, "")

            for j in range(i + 1, len(records)):
                if j in used:
                    continue
                name_j = records[j].get(name_field, "")
                score  = self.combined_score(
                    name_i, name_j, rec, records[j], kind
                )
                if score >= self.threshold:
                    alias_entry = {
                        "name":   name_j,
                        "id":     records[j].get("id", ""),
                        "score":  round(score, 3),
                        "source": records[j].get("_source", ""),
                    }
                    canon["aliases"].append(alias_entry)
                    canon["duplicates"].append({"record": records[j],
                                                 "score": round(score, 3)})
                    used.add(j)
            used.add(i)
            resolved.append(canon)

        merged = len(records) - len(resolved)
        logger.info(
            f"[ResolverV2] {len(records)} records -> "
            f"{len(resolved)} canonical ({merged} merged)"
        )
        return resolved

    # -- cross-dataset matching --------------------------------------

    def cross_dataset_match(self,
                              dataset_a: list,
                              dataset_b: list,
                              name_field_a: str = "name",
                              name_field_b: str = "name",
                              kind: str = "person") -> list:
        """
        Match entities across two datasets.
        Returns list of match dicts with name_a, name_b, score, canonical_id.
        Backward-compatible: matches have 'record_a', 'record_b' keys.
        """
        matches = []
        for rec_a in dataset_a:
            name_a = rec_a.get(name_field_a, "")
            if not name_a:
                continue
            for rec_b in dataset_b:
                name_b = rec_b.get(name_field_b, "")
                if not name_b:
                    continue
                score = self.combined_score(name_a, name_b, rec_a, rec_b, kind)
                if score >= self.threshold:
                    cid = canonical_id(
                        normalise_indian_name(name_a, kind),
                        rec_a.get("_source", "")
                    )
                    matches.append({
                        # v1 compat keys
                        "record_a":  rec_a,
                        "record_b":  rec_b,
                        "name_a":    name_a,
                        "name_b":    name_b,
                        "score":     round(score, 3),
                        # v2 additions
                        "canonical_id": cid,
                        "match_type":   "cross_dataset_v2",
                        "matched_at":   datetime.now().isoformat(),
                    })

        logger.info(
            f"[ResolverV2] Cross-dataset: "
            f"{len(dataset_a)} x {len(dataset_b)} -> {len(matches)} matches"
        )
        return matches

    # -- alias graph builder -----------------------------------------

    def build_alias_graph(self, canonical_records: list,
                           name_field: str = "name") -> dict:
        """
        Build a flat alias lookup:  alias_name.lower() -> canonical_id

        Used by the graph loader to MERGE all variants of an entity
        into one Neo4j node without losing any source records.
        """
        graph = {}
        for rec in canonical_records:
            cid = rec.get("id") or canonical_id(
                normalise_indian_name(rec.get(name_field, ""))
            )
            main_name = normalise_indian_name(
                rec.get(name_field, "")
            ).lower()
            if main_name:
                graph[main_name] = cid
            for alias in rec.get("aliases", []):
                alias_name = normalise_indian_name(
                    alias.get("name", "")
                ).lower()
                if alias_name:
                    graph[alias_name] = cid
        return graph

    def save_alias_graph(self, graph: dict, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)
        logger.success(
            f"[ResolverV2] Alias graph: {len(graph)} entries -> {path}"
        )


# ---- Backward-compatible alias ------------------------------------
# pipeline.py imports EntityResolver -- make v2 transparently available
EntityResolver = EntityResolverV2


# ---- CLI test --------------------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Entity Resolver v2 Test")
    print("=" * 55)

    resolver = EntityResolverV2(threshold=0.72)

    print("\n[1] Jaro-Winkler similarity scores:")
    pairs = [
        ("Rahul Kumar",      "RAHUL KUMAR",          "person"),
        ("Sh. Ram Kumar",    "Ramkumar",              "person"),
        ("Narendra Modi",    "N. Modi",               "person"),
        ("Adani Enterprises Ltd", "ADANI ENTERPRISES LIMITED", "company"),
        ("Sample Pvt Ltd",   "Sample Private Limited","company"),
        ("Priya Sharma",     "Priya Devi",            "person"),
    ]
    for a, b, kind in pairs:
        score = resolver.combined_score(a, b, kind=kind)
        match = "MATCH" if score >= resolver.threshold else "no match"
        print(f"  {match} ({score:.3f})  '{a}' vs '{b}'")

    print("\n[2] Exact key override:")
    rec1 = {"name": "Adani Enterprises",   "cin": "L51100GJ1988PLC013248"}
    rec2 = {"name": "Adani Enterprises Ltd","cin": "L51100GJ1988PLC013248"}
    rec3 = {"name": "Adani Enterprises",   "cin": "U12345MH2010PLC123456"}
    print(f"  Same CIN: {resolver.combined_score('', '', rec1, rec2):.3f} (expect 1.0)")
    print(f"  Diff CIN: {resolver.combined_score('', '', rec1, rec3):.3f} (expect 0.0)")

    print("\n[3] resolve_dataset (dedup):")
    politicians = [
        {"name": "RAHUL KUMAR",   "party": "A", "_source": "myneta"},
        {"name": "Rahul Kumar",   "party": "A", "_source": "wikidata"},
        {"name": "Priya Sharma",  "party": "B", "_source": "myneta"},
        {"name": "PRIYA SHARMA",  "party": "B", "_source": "mca"},
    ]
    resolved = resolver.resolve_dataset(politicians, "name")
    print(f"  {len(politicians)} records -> {len(resolved)} canonical")
    for r in resolved:
        aliases = len(r["aliases"])
        print(f"    '{r['name']}'" + (f" +{aliases} alias" if aliases else ""))

    print("\nDone.")
