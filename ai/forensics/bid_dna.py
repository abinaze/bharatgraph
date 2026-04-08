import os, sys, math, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger

SIMILARITY_THRESHOLD = 0.72
MIN_BIDS_FOR_ANALYSIS = 3


class BidDNA:
    """
    Procurement bid fingerprinting.
    Detects structural similarity between supposedly independent bids
    using TF-IDF + cosine similarity.
    """

    def analyze(self, entity_id: str, driver=None) -> dict:
        logger.info(f"[BidDNA] Fingerprinting bids for {entity_id}")

        bids = self._fetch_bids(entity_id, driver)
        if len(bids) < MIN_BIDS_FOR_ANALYSIS:
            return {
                "entity_id": entity_id,
                "status":    "insufficient_data",
                "bid_count": len(bids),
            }

        similarity_pairs = self._compute_similarity(bids)
        suspicious       = [p for p in similarity_pairs
                            if p["similarity"] >= SIMILARITY_THRESHOLD]

        findings = []
        if suspicious:
            findings.append({
                "type":     "bid_document_similarity",
                "severity": "HIGH" if len(suspicious) >= 3 else "MODERATE",
                "description": (
                    f"{len(suspicious)} bid document pair(s) show structural "
                    f"similarity above {SIMILARITY_THRESHOLD:.0%}. Identical or "
                    f"near-identical bid text across different vendors indicates "
                    f"coordinated submission."
                ),
                "evidence": [
                    f"Bid '{p['a'][:40]}' ↔ '{p['b'][:40]}': "
                    f"{p['similarity']:.1%} similar"
                    for p in suspicious[:3]
                ],
            })

        price_anomaly = self._detect_price_anomaly(bids)
        if price_anomaly:
            findings.append(price_anomaly)

        return {
            "entity_id":      entity_id,
            "bid_count":      len(bids),
            "pairs_checked":  len(similarity_pairs),
            "suspicious_pairs": len(suspicious),
            "findings":       findings,
            "positive":       ["No bid document similarities detected."] if not findings else [],
            "analyzed_at":    datetime.now().isoformat(),
        }

    def _fetch_bids(self, entity_id: str, driver) -> list:
        if not driver:
            return [
                {"id":"b1","desc":"Supply of road construction material Grade A bitumen",
                 "amount":12.5,"vendor":"Alpha Traders"},
                {"id":"b2","desc":"Supply of road construction material Grade A bitumen",
                 "amount":13.1,"vendor":"Beta Suppliers"},
                {"id":"b3","desc":"Provision of IT infrastructure networking hardware",
                 "amount":45.0,"vendor":"TechCorp"},
                {"id":"b4","desc":"Supply of road construction material Grade A",
                 "amount":11.9,"vendor":"Gamma Enterprises"},
            ]
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (p {id:$id})-[:DIRECTOR_OF]->(c:Company)
                          -[:WON_CONTRACT]->(ct:Contract)
                    RETURN ct.id AS id, ct.item_desc AS desc,
                           ct.amount_crore AS amount, c.name AS vendor
                    LIMIT 50
                    """, id=entity_id
                ).data()
                return [dict(r) for r in rows if r.get("desc")]
        except Exception as e:
            logger.warning(f"[BidDNA] Fetch failed: {e}")
            return []

    def _tfidf_vector(self, text: str) -> dict:
        """Minimal TF-IDF: term frequency only (no corpus needed for similarity)."""
        tokens = re.findall(r'\w+', text.lower())
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        total = max(len(tokens), 1)
        return {t: c/total for t, c in tf.items()}

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

    def _compute_similarity(self, bids: list) -> list:
        vectors = [(b, self._tfidf_vector(b.get("desc","") or ""))
                   for b in bids]
        pairs   = []
        for i in range(len(vectors)):
            for j in range(i+1, len(vectors)):
                bid_a, vec_a = vectors[i]
                bid_b, vec_b = vectors[j]
                sim = self._cosine(vec_a, vec_b)
                if sim > 0.3:
                    pairs.append({
                        "a":          bid_a.get("vendor","?"),
                        "b":          bid_b.get("vendor","?"),
                        "similarity": round(sim, 4),
                    })
        pairs.sort(key=lambda x: -x["similarity"])
        return pairs

    def _detect_price_anomaly(self, bids: list) -> dict | None:
        amounts = [float(b.get("amount") or 0) for b in bids if b.get("amount")]
        if len(amounts) < 3:
            return None
        mean = sum(amounts) / len(amounts)
        variance = sum((x - mean)**2 for x in amounts) / len(amounts)
        std  = math.sqrt(variance)
        if std == 0:
            return None

        sorted_amounts = sorted(amounts)
        gaps = [sorted_amounts[i+1] - sorted_amounts[i]
                for i in range(len(sorted_amounts)-1)]
        if gaps and max(gaps) < std * 0.1:
            return {
                "type":     "cover_bid_pattern",
                "severity": "MODERATE",
                "description": (
                    f"Contract amounts cluster unusually closely "
                    f"(std dev Rs {std:.2f} Cr across {len(amounts)} bids). "
                    f"Tight clustering of competing bids is a known indicator "
                    f"of coordinated bidding."
                ),
                "evidence": [
                    f"Mean: Rs {mean:.2f} Cr",
                    f"Std:  Rs {std:.2f} Cr",
                    f"Range: Rs {min(amounts):.2f} – Rs {max(amounts):.2f} Cr",
                ],
            }
        return None


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph — Bid DNA Test")
    print("=" * 55)
    b = BidDNA()
    r = b.analyze("pol_001", driver=None)
    print(f"\n  Bids:      {r['bid_count']}")
    print(f"  Suspicious:{r['suspicious_pairs']}")
    print(f"  Findings:  {len(r['findings'])}")
    for f in r["findings"]:
        print(f"  [{f['severity']}] {f['description'][:70]}")
    print("\nDone!")
