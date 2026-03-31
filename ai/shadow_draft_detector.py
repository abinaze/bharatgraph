import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from datetime import datetime
from loguru import logger


ALIGNMENT_THRESHOLD = 65.0

STOPWORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "by","from","is","are","was","were","be","been","being","have","has",
    "had","do","does","did","will","would","could","should","may","might",
    "shall","can","that","this","these","those","it","its","their","which",
}


class ShadowDraftDetector:

    def __init__(self):
        self._model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer, util
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            self._util  = util
            logger.success("[ShadowDraft] sentence-transformers loaded: all-MiniLM-L6-v2")
        except Exception as e:
            logger.warning(f"[ShadowDraft] sentence-transformers not available: {e}")
            logger.warning("[ShadowDraft] Using token overlap fallback")
            self._model = None

    def _tokenize(self, text: str) -> set:
        tokens = re.findall(r"\b[a-z]{3,}\b", text.lower())
        return {t for t in tokens if t not in STOPWORDS}

    def _jaccard_similarity(self, text_a: str, text_b: str) -> float:
        tokens_a = self._tokenize(text_a)
        tokens_b = self._tokenize(text_b)
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = len(tokens_a & tokens_b)
        union        = len(tokens_a | tokens_b)
        return round((intersection / union) * 100, 2) if union > 0 else 0.0

    def _semantic_similarity(self, text_a: str, text_b: str) -> float:
        try:
            import torch
            emb_a = self._model.encode(text_a, convert_to_tensor=True)
            emb_b = self._model.encode(text_b, convert_to_tensor=True)
            score = self._util.cos_sim(emb_a, emb_b).item()
            return round(score * 100, 2)
        except Exception as e:
            logger.warning(f"[ShadowDraft] Semantic similarity failed: {e}")
            return self._jaccard_similarity(text_a, text_b)

    def split_into_sections(self, text: str, max_length: int = 500) -> list:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        sections  = []
        current   = ""
        for sentence in sentences:
            if len(current) + len(sentence) <= max_length:
                current += " " + sentence
            else:
                if current.strip():
                    sections.append(current.strip())
                current = sentence
        if current.strip():
            sections.append(current.strip())
        return sections

    def compare(self, submission_text: str, bill_text: str,
                submission_name: str = "Submission",
                bill_name: str = "Bill") -> dict:
        logger.info(
            f"[ShadowDraft] Comparing '{submission_name}' "
            f"against '{bill_name}'"
        )

        submission_sections = self.split_into_sections(submission_text)
        bill_sections       = self.split_into_sections(bill_text)

        if not submission_sections or not bill_sections:
            return {
                "status":          "insufficient_text",
                "alignment_score": 0.0,
                "flagged":         False,
            }

        matched_pairs = []
        for sub_sec in submission_sections:
            if len(sub_sec.split()) < 5:
                continue
            best_score = 0.0
            best_bill  = ""
            for bill_sec in bill_sections:
                if len(bill_sec.split()) < 5:
                    continue
                if self._model:
                    score = self._semantic_similarity(sub_sec, bill_sec)
                else:
                    score = self._jaccard_similarity(sub_sec, bill_sec)
                if score > best_score:
                    best_score = score
                    best_bill  = bill_sec
            if best_score >= 40.0:
                matched_pairs.append({
                    "submission_section": sub_sec[:200],
                    "bill_section":       best_bill[:200],
                    "similarity_score":   best_score,
                    "method": "semantic" if self._model else "token_overlap",
                })

        matched_pairs.sort(key=lambda x: x["similarity_score"], reverse=True)

        if matched_pairs:
            top_scores = [p["similarity_score"] for p in matched_pairs[:5]]
            alignment_score = round(sum(top_scores) / len(top_scores), 2)
        else:
            alignment_score = 0.0

        effective_threshold = (
            ALIGNMENT_THRESHOLD if self._model
            else ALIGNMENT_THRESHOLD * 0.6
        )
        flagged = alignment_score >= effective_threshold

        if flagged:
            logger.warning(
                f"[ShadowDraft] HIGH ALIGNMENT: {alignment_score:.1f}% "
                f"between '{submission_name}' and '{bill_name}'"
            )
        else:
            logger.info(
                f"[ShadowDraft] Alignment: {alignment_score:.1f}% "
                f"(threshold={ALIGNMENT_THRESHOLD}%)"
            )

        return {
            "submission_name":  submission_name,
            "bill_name":        bill_name,
            "alignment_score":  alignment_score,
            "threshold":        ALIGNMENT_THRESHOLD,
            "flagged":          flagged,
            "matched_sections": len(matched_pairs),
            "top_matches":      matched_pairs[:5],
            "interpretation": (
                f"High semantic alignment ({alignment_score:.1f}%) detected between "
                "the corporate submission and the legislative text. This is a structural "
                "indicator that the submission's language may have influenced the final "
                "bill text. This is an analytical observation, not a legal finding."
                if flagged else
                f"Alignment score ({alignment_score:.1f}%) is below the threshold "
                f"({ALIGNMENT_THRESHOLD}%). No significant semantic overlap detected."
            ),
            "analyzed_at": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Shadow Draft Detector Test")
    print("=" * 55)

    detector = ShadowDraftDetector()

    corporate_submission = """
    We propose that all digital payment service providers should be exempted
    from the transaction levy when the transaction value is below fifty thousand
    rupees. Further, the regulatory authority should provide a grace period of
    eighteen months for existing operators to achieve compliance with the new
    data localisation requirements.
    """

    bill_text_similar = """
    Digital payment service providers shall be exempt from transaction levy
    for amounts below fifty thousand rupees. Existing operators shall have
    eighteen months to achieve compliance with data localisation requirements
    as specified under this Act.
    """

    bill_text_different = """
    The government shall establish a committee to review taxation policy for
    agricultural produce. All farmers with land holdings below two hectares
    shall receive a subsidy on crop insurance premiums.
    """

    print("\n  Test 1: High alignment expected")
    result1 = detector.compare(
        corporate_submission, bill_text_similar,
        "Industry Body Submission", "Payment Regulation Bill"
    )
    print(f"  Score:   {result1['alignment_score']}%")
    print(f"  Flagged: {result1['flagged']}")

    print("\n  Test 2: Low alignment expected")
    result2 = detector.compare(
        corporate_submission, bill_text_different,
        "Industry Body Submission", "Agriculture Bill"
    )
    print(f"  Score:   {result2['alignment_score']}%")
    print(f"  Flagged: {result2['flagged']}")

    print("\nDone!")
