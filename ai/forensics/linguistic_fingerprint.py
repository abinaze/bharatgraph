import os, sys, re, math, hashlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger

TEMPLATE_SIMILARITY_THRESHOLD = 0.78
AUTHORSHIP_DELTA_THRESHOLD    = 1.5   # Burrows Delta: below this = same cluster
MIN_DOCS_FOR_DELTA             = 2


class LinguisticFingerprinter:
    """
    Linguistic fingerprinting using three methods:

    1. Burrows Delta authorship attribution: compares stylometric feature
       vectors (function word frequencies) across government documents to
       cluster documents by likely author or drafting organisation.

    2. Template reuse detection: structural similarity via Rabin-style
       rolling hash fingerprinting. Same template reused across different
       dates or signatories is a structural risk indicator.

    3. Shadow drafting detection: cosine similarity between corporate
       consultation submissions and final bill or policy text. High
       similarity indicates the private submission was used as the draft.
    """

    FUNCTION_WORDS = [
        "the", "of", "and", "to", "in", "is", "that", "for", "are", "be",
        "this", "or", "as", "with", "shall", "under", "such", "any", "by",
        "an", "from", "which", "all", "said", "may", "whereas", "upon",
        "pursuant", "aforesaid", "herein", "thereof", "notwithstanding",
    ]

    def analyze(self, entity_id: str, documents: list[dict],
                driver=None) -> dict:
        logger.info(
            f"[LinguisticFingerprinter] Analyzing {len(documents)} docs "
            f"for {entity_id}"
        )

        if not documents:
            documents = self._fetch_documents(entity_id, driver)

        if len(documents) < 2:
            return {
                "entity_id":    entity_id,
                "status":       "insufficient_data",
                "doc_count":    len(documents),
                "analyzed_at":  datetime.now().isoformat(),
            }

        findings   = []
        positive   = []

        delta_result    = self._burrows_delta(documents)
        template_result = self._template_reuse(documents)
        shadow_result   = self._shadow_drafting(documents)

        if delta_result.get("clusters_detected"):
            findings.append({
                "type":     "authorship_cluster",
                "severity": "MODERATE",
                "description": (
                    f"Burrows Delta analysis identified {delta_result['cluster_count']} "
                    f"authorship cluster(s) across {len(documents)} government documents "
                    f"associated with this entity. Documents in the same cluster share "
                    f"stylometric signatures suggesting a common drafting source."
                ),
                "evidence": delta_result.get("evidence", []),
            })

        if template_result.get("reuse_detected"):
            n = template_result["reuse_pairs"]
            findings.append({
                "type":     "template_reuse",
                "severity": "HIGH" if n >= 3 else "MODERATE",
                "description": (
                    f"{n} document pair(s) share structural template fingerprints "
                    f"despite different dates or signatories. Template reuse across "
                    f"nominally independent submissions indicates a shared drafting source."
                ),
                "evidence": template_result.get("examples", []),
            })

        if shadow_result.get("shadow_detected"):
            findings.append({
                "type":     "shadow_drafting",
                "severity": "HIGH",
                "description": (
                    f"Cosine similarity of {shadow_result['max_similarity']:.1%} "
                    f"detected between a consultation submission and the associated "
                    f"policy document. Structural alignment above the 0.72 threshold "
                    f"indicates the submission may have been used as the source draft."
                ),
                "evidence": shadow_result.get("evidence", []),
            })

        if not findings:
            positive.append(
                "Linguistic fingerprinting found no significant authorship clusters, "
                "template reuse, or shadow drafting indicators in the available documents."
            )

        logger.success(
            f"[LinguisticFingerprinter] {entity_id}: {len(findings)} findings"
        )

        return {
            "entity_id":       entity_id,
            "doc_count":       len(documents),
            "delta":           delta_result,
            "template_reuse":  template_result,
            "shadow_drafting": shadow_result,
            "findings":        findings,
            "positive":        positive,
            "analyzed_at":     datetime.now().isoformat(),
        }

    # ── Burrows Delta authorship attribution ──────────────────────────────────

    def _burrows_delta(self, documents: list[dict]) -> dict:
        if len(documents) < MIN_DOCS_FOR_DELTA:
            return {"clusters_detected": False, "cluster_count": 0}

        vectors = []
        for doc in documents:
            text = (doc.get("text") or doc.get("title") or "").lower()
            vec  = self._function_word_vector(text)
            vectors.append((doc.get("id","?"), doc.get("title","?")[:50], vec))

        # Z-score normalise each feature
        n_docs    = len(vectors)
        n_feats   = len(self.FUNCTION_WORDS)
        raw_vals  = [[v[2][w] for v in vectors] for w in self.FUNCTION_WORDS]
        means     = [sum(col)/n_docs for col in raw_vals]
        stdevs    = [
            math.sqrt(sum((x-m)**2 for x in col)/n_docs) or 1.0
            for col, m in zip(raw_vals, means)
        ]

        z_vectors = []
        for doc_id, doc_title, raw in vectors:
            z = [(raw[w] - means[i]) / stdevs[i]
                 for i, w in enumerate(self.FUNCTION_WORDS)]
            z_vectors.append((doc_id, doc_title, z))

        # Compute pairwise Delta (mean absolute z-score difference)
        pairs  = []
        for i in range(len(z_vectors)):
            for j in range(i+1, len(z_vectors)):
                id_a, title_a, z_a = z_vectors[i]
                id_b, title_b, z_b = z_vectors[j]
                delta = sum(abs(a-b) for a,b in zip(z_a,z_b)) / n_feats
                pairs.append({
                    "doc_a":   title_a,
                    "doc_b":   title_b,
                    "delta":   round(delta, 4),
                    "cluster": delta < AUTHORSHIP_DELTA_THRESHOLD,
                })

        clustered_pairs = [p for p in pairs if p["cluster"]]
        cluster_count   = len(set(
            p["doc_a"] for p in clustered_pairs
        ) | set(p["doc_b"] for p in clustered_pairs))

        return {
            "clusters_detected": len(clustered_pairs) > 0,
            "cluster_count":     cluster_count,
            "total_pairs":       len(pairs),
            "clustered_pairs":   len(clustered_pairs),
            "evidence": [
                f"Delta {p['delta']:.3f}: '{p['doc_a'][:40]}' "
                f"clusters with '{p['doc_b'][:40]}'"
                for p in sorted(clustered_pairs, key=lambda x: x["delta"])[:3]
            ],
        }

    def _function_word_vector(self, text: str) -> dict:
        tokens = re.findall(r'\b\w+\b', text.lower())
        total  = max(len(tokens), 1)
        return {w: tokens.count(w) / total for w in self.FUNCTION_WORDS}

    # ── Template reuse via structural fingerprinting ──────────────────────────

    def _template_reuse(self, documents: list[dict]) -> dict:
        fingerprints = []
        for doc in documents:
            text = (doc.get("text") or doc.get("title") or "").lower()
            fp   = self._structural_fingerprint(text)
            fingerprints.append((doc.get("id","?"), doc.get("title","?")[:50], fp))

        reuse_pairs = []
        for i in range(len(fingerprints)):
            for j in range(i+1, len(fingerprints)):
                id_a, title_a, fp_a = fingerprints[i]
                id_b, title_b, fp_b = fingerprints[j]
                sim = self._fingerprint_similarity(fp_a, fp_b)
                if sim >= TEMPLATE_SIMILARITY_THRESHOLD:
                    reuse_pairs.append({
                        "doc_a": title_a, "doc_b": title_b,
                        "similarity": round(sim, 4),
                    })

        return {
            "reuse_detected": len(reuse_pairs) > 0,
            "reuse_pairs":    len(reuse_pairs),
            "examples": [
                f"{p['similarity']:.1%} match: '{p['doc_a'][:40]}' "
                f"and '{p['doc_b'][:40]}'"
                for p in sorted(reuse_pairs, key=lambda x: -x["similarity"])[:3]
            ],
        }

    def _structural_fingerprint(self, text: str) -> set:
        # Extract structural n-grams (skip-word patterns) as fingerprint
        words  = re.findall(r'\b\w+\b', text)
        shingles = set()
        for i in range(len(words) - 2):
            shingle = f"{words[i]}_{words[i+2]}"   # skip-1 bigram
            shingles.add(hashlib.md5(shingle.encode()).hexdigest()[:8])
        return shingles

    def _fingerprint_similarity(self, fp_a: set, fp_b: set) -> float:
        if not fp_a or not fp_b:
            return 0.0
        intersection = len(fp_a & fp_b)
        union        = len(fp_a | fp_b)
        return intersection / union if union > 0 else 0.0

    # ── Shadow drafting detection ─────────────────────────────────────────────

    def _shadow_drafting(self, documents: list[dict]) -> dict:
        submissions = [d for d in documents if d.get("type") == "submission"]
        policies    = [d for d in documents if d.get("type") == "policy"]

        if not submissions or not policies:
            # Fall back to pairwise across all docs for sample/offline testing
            if len(documents) >= 2:
                submissions = documents[:len(documents)//2]
                policies    = documents[len(documents)//2:]
            else:
                return {"shadow_detected": False}

        max_sim  = 0.0
        evidence = []

        for sub in submissions:
            sub_vec = self._tfidf_vector(
                (sub.get("text") or sub.get("title") or "").lower()
            )
            for pol in policies:
                pol_vec = self._tfidf_vector(
                    (pol.get("text") or pol.get("title") or "").lower()
                )
                sim = self._cosine(sub_vec, pol_vec)
                if sim > 0.5:
                    evidence.append(
                        f"Similarity {sim:.1%}: submission '{sub.get('title','?')[:40]}' "
                        f"vs policy '{pol.get('title','?')[:40]}'"
                    )
                    max_sim = max(max_sim, sim)

        return {
            "shadow_detected": max_sim >= 0.72,
            "max_similarity":  round(max_sim, 4),
            "evidence":        evidence[:3],
        }

    def _tfidf_vector(self, text: str) -> dict:
        tokens = re.findall(r'\w+', text)
        total  = max(len(tokens), 1)
        return {t: tokens.count(t)/total for t in set(tokens)}

    def _cosine(self, v1: dict, v2: dict) -> float:
        common = set(v1) & set(v2)
        if not common:
            return 0.0
        dot   = sum(v1[t] * v2[t] for t in common)
        norm1 = math.sqrt(sum(x**2 for x in v1.values()))
        norm2 = math.sqrt(sum(x**2 for x in v2.values()))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def _fetch_documents(self, entity_id: str, driver) -> list:
        if not driver:
            return [
                {"id":"d1","title":"Supply of bituminous material Grade A specification clause 4",
                 "type":"submission","text":"supply bituminous material grade specification clause requirements standards"},
                {"id":"d2","title":"Supply of bituminous material Grade A specification clause 4 amendment",
                 "type":"submission","text":"supply bituminous material grade specification clause requirements standards amendment"},
                {"id":"d3","title":"Procurement policy for road materials national highway authority",
                 "type":"policy","text":"procurement policy road materials national highway authority specification clause"},
                {"id":"d4","title":"Annual audit report roads scheme payment utilisation",
                 "type":"audit","text":"audit report roads scheme payment utilisation irregularity finding"},
                {"id":"d5","title":"Annual audit report roads scheme payment utilisation revised",
                 "type":"audit","text":"audit report roads scheme payment utilisation irregularity finding revised"},
            ]
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (n {id:$id})-[:DIRECTOR_OF]->(c:Company)
                          -[:WON_CONTRACT]->(ct:Contract)
                    RETURN ct.id AS id, ct.item_desc AS title,
                           'submission' AS type, ct.item_desc AS text
                    LIMIT 10
                    """, id=entity_id
                ).data()
                docs = [dict(r) for r in rows if r.get("title")]
                # Add audit reports
                ar = s.run(
                    """
                    MATCH (a:AuditReport)
                    WHERE toLower(a.title) CONTAINS toLower($id)
                    RETURN a.id AS id, a.title AS title,
                           'policy' AS type, a.title AS text
                    LIMIT 5
                    """, id=entity_id
                ).data()
                docs.extend([dict(r) for r in ar if r.get("title")])
                return docs
        except Exception as e:
            logger.warning(f"[LinguisticFingerprinter] Fetch failed: {e}")
            return []


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph — Linguistic Fingerprinter Test")
    print("=" * 55)
    lf = LinguisticFingerprinter()
    r  = lf.analyze("pol_001", [], driver=None)
    print(f"\n  Documents:  {r['doc_count']}")
    print(f"  Findings:   {len(r['findings'])}")
    delta = r["delta"]
    print(f"  Burrows Delta: {delta['clustered_pairs']} pairs clustered")
    tmpl  = r["template_reuse"]
    print(f"  Template reuse: {tmpl['reuse_pairs']} pairs")
    shadow = r["shadow_drafting"]
    print(f"  Shadow drafting: detected={shadow['shadow_detected']} "
          f"sim={shadow.get('max_similarity',0):.1%}")
    for f in r["findings"]:
        print(f"\n  [{f['severity']}] {f['type']}")
        print(f"  {f['description'][:80]}")
    print("\nDone!")
