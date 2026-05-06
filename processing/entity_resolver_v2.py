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
    "sh", "kum", "shr", "retd", "rtd", "ex",
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
    name = str(name).strip().lower()
    name = re.sub(r"^m\s*/\s*s\.?\s*", "", name)
    if kind == "person":
        _changed = True
        while _changed:
            _prev = name
            for h in _HONORIFICS:
                name = re.sub(rf"^{re.escape(h)}\.?\s+", "", name)
                name = re.sub(rf"^{re.escape(h)}\.?\s*$", "", name)
            _changed = name != _prev
    else:
        for old, new in _COMPANY_SUFFIXES:
            name = name.replace(old, new)
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
    def __init__(self, threshold: float = 0.82):
        self.threshold = threshold
        self.cleaner   = NameCleaner()
        logger.info(f"[ResolverV2] threshold={threshold}")

    def _exact_key_score(self, rec_a: dict, rec_b: dict) -> float:
        key_fields = ["cin", "pan", "gstin", "wikidata_id", "darpan_id",
                      "bond_number", "order_id", "tender_id", "icij_node_id"]
        for field in key_fields:
            val_a = str(rec_a.get(field) or "").strip().upper()
            val_b = str(rec_b.get(field) or "").strip().upper()
            if val_a and val_b:
                return 1.0 if val_a == val_b else 0.0
        return 0.0

    def combined_score(self, name_a: str, name_b: str,
                       rec_a: dict = None, rec_b: dict = None,
                       kind: str = "person") -> float:
        if rec_a and rec_b:
            ek = self._exact_key_score(rec_a, rec_b)
            if ek == 1.0:
                return 1.0
            if ek == 0.0 and any(
                str(rec_a.get(f) or "").strip()
                for f in ["cin", "pan", "gstin"]
            ):
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
            return 0.60 * jw + 0.40 * jacc

    def is_same_entity(self, name_a: str, name_b: str,
                        rec_a: dict = None, rec_b: dict = None,
                        kind: str = "person") -> bool:
        return self.combined_score(name_a, name_b, rec_a, rec_b, kind) >= self.threshold

    def resolve_dataset(self, records: list,
                         name_field: str = "name",
                         kind: str = "person") -> list:
        if not records:
            return []
        resolved = []
        used     = set()
        for i, rec in enumerate(records):
            if i in used:
                continue
            canon = dict(rec)
            canon["aliases"]      = []
            canon["duplicates"]   = []
            canon["_resolved_v2"] = True
            name_i = rec.get(name_field, "")
            for j in range(i + 1, len(records)):
                if j in used:
                    continue
                name_j = records[j].get(name_field, "")
                score  = self.combined_score(name_i, name_j, rec, records[j], kind)
                if score >= self.threshold:
                    alias_entry = {
                        "name":   name_j,
                        "id":     records[j].get("id", ""),
                        "score":  round(score, 3),
                        "source": records[j].get("_source", ""),
                    }
                    canon["aliases"].append(alias_entry)
                    canon["duplicates"].append({"record": records[j], "score": round(score, 3)})
                    used.add(j)
            used.add(i)
            resolved.append(canon)
        merged = len(records) - len(resolved)
        logger.info(f"[ResolverV2] {len(records)} records -> {len(resolved)} canonical ({merged} merged)")
        return resolved

    def cross_dataset_match(self, dataset_a: list, dataset_b: list,
                              name_field_a: str = "name",
                              name_field_b: str = "name",
                              kind: str = "person") -> list:
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
                    cid = canonical_id(normalise_indian_name(name_a, kind), rec_a.get("_source", ""))
                    matches.append({
                        "record_a": rec_a, "record_b": rec_b,
                        "name_a": name_a, "name_b": name_b,
                        "score": round(score, 3),
                        "canonical_id": cid,
                        "match_type": "cross_dataset_v2",
                        "matched_at": datetime.now().isoformat(),
                    })
        logger.info(f"[ResolverV2] Cross-dataset: {len(dataset_a)} x {len(dataset_b)} -> {len(matches)} matches")
        return matches

    def build_alias_graph(self, canonical_records: list, name_field: str = "name") -> dict:
        graph = {}
        for rec in canonical_records:
            cid = rec.get("id") or canonical_id(normalise_indian_name(rec.get(name_field, "")))
            main_name = normalise_indian_name(rec.get(name_field, "")).lower()
            if main_name:
                graph[main_name] = cid
            for alias in rec.get("aliases", []):
                alias_name = normalise_indian_name(alias.get("name", "")).lower()
                if alias_name:
                    graph[alias_name] = cid
        return graph

    def save_alias_graph(self, graph: dict, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)
        logger.success(f"[ResolverV2] Alias graph: {len(graph)} entries -> {path}")


# ---- Backward-compatible alias ------------------------------------
EntityResolver = EntityResolverV2


if __name__ == "__main__":
    resolver = EntityResolverV2(threshold=0.72)
    tests = [
        ("Sh. Ram Kumar",          "Ramkumar",               "person"),
        ("Narendra Modi",          "N. Modi",                "person"),
        ("Sample Pvt Ltd",         "Sample Private Limited", "company"),
    ]
    for a, b, kind in tests:
        score = resolver.combined_score(a, b, kind=kind)
        print(f"{score:.3f}  {a!r} vs {b!r}")
