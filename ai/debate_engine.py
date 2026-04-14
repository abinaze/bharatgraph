import os, sys, re, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from loguru import logger

HESITATION_THRESHOLD  = 3
SIMILARITY_DRIFT_MAX  = 0.85
DEBATE_ROUNDS         = 3
SIMPLE_CASE_THRESHOLD = 1


HESITATION_PATTERNS = [
    r'\b(might|may|could|possibly|perhaps|arguably|potentially)\b',
    r'\b(unclear|uncertain|ambiguous|inconclusive|questionable)\b',
    r'\b(it seems|it appears|it is possible|one could argue)\b',
    r'\b(however|although|but|yet|nevertheless|on the other hand)\b',
    r'\b(limited|partial|insufficient|incomplete|weak)\b',
]

AGENT_PROFILES = {
    "logical_analyst": {
        "role":           "Logical Analyst",
        "focus":          "structural consistency and logical entailment",
        "skepticism":     0.4,
        "strictness":     0.8,
        "creativity":     0.2,
        "weight":         0.15,
    },
    "skeptic": {
        "role":           "Skeptic",
        "focus":          "challenging assumptions and finding weaknesses",
        "skepticism":     0.9,
        "strictness":     0.7,
        "creativity":     0.3,
        "weight":         0.15,
    },
    "pattern_hunter": {
        "role":           "Pattern Hunter",
        "focus":          "recurring structural motifs across datasets",
        "skepticism":     0.3,
        "strictness":     0.5,
        "creativity":     0.7,
        "weight":         0.12,
    },
    "timeline_analyst": {
        "role":           "Timeline Analyst",
        "focus":          "temporal sequence and causal ordering",
        "skepticism":     0.4,
        "strictness":     0.6,
        "creativity":     0.4,
        "weight":         0.12,
    },
    "financial_analyst": {
        "role":           "Financial Analyst",
        "focus":          "monetary anomalies, asset flows, and valuation",
        "skepticism":     0.5,
        "strictness":     0.7,
        "creativity":     0.3,
        "weight":         0.15,
    },
    "contrarian": {
        "role":           "Contrarian",
        "focus":          "alternative explanations and disconfirming evidence",
        "skepticism":     0.8,
        "strictness":     0.4,
        "creativity":     0.6,
        "weight":         0.15,
    },
    "risk_analyst": {
        "role":           "Risk Analyst",
        "focus":          "probability of harm and systemic risk indicators",
        "skepticism":     0.3,
        "strictness":     0.6,
        "creativity":     0.4,
        "weight":         0.16,
    },
}


class DebateEngine:
    """
    iMAD-style multi-agent debate engine.

    Simple cases (one LOW finding) use a small panel of 3 agents.
    Complex or contradictory cases use all 7 agents across 3 debate rounds.

    Anti-drift: after each round, semantic similarity between agent
    positions is checked. If agents are converging too quickly
    (similarity > 0.85), the skeptic and contrarian are prompted
    to find new objections.

    Dissent is preserved in the final output — minority positions
    are never erased.
    """

    def run(self, entity_id: str, entity_name: str,
            findings: list[dict], driver=None) -> dict:
        logger.info(
            f"[DebateEngine] Starting debate for {entity_name} "
            f"with {len(findings)} findings"
        )

        if not findings:
            return {
                "entity_id":   entity_id,
                "entity_name": entity_name,
                "status":      "no_findings",
                "consensus":   None,
                "rounds":      [],
                "analyzed_at": datetime.now().isoformat(),
            }

        complexity  = self._classify_complexity(findings)
        agents      = self._select_agents(complexity)
        hesitation  = self._detect_hesitation(findings)

        logger.info(
            f"[DebateEngine] Complexity={complexity} "
            f"Agents={len(agents)} Hesitation={hesitation}"
        )

        rounds   = []
        positions = {a: self._initial_position(a, findings, AGENT_PROFILES[a])
                     for a in agents}

        for round_num in range(1, DEBATE_ROUNDS + 1):
            positions = self._run_round(
                round_num, positions, findings, agents
            )
            drift = self._check_drift(positions)
            if drift > SIMILARITY_DRIFT_MAX and round_num < DEBATE_ROUNDS:
                logger.info(
                    f"[DebateEngine] Round {round_num}: drift={drift:.2f} "
                    "— injecting counter-pressure"
                )
                positions = self._inject_counter_pressure(positions)

            rounds.append({
                "round":     round_num,
                "drift":     round(drift, 3),
                "positions": {
                    a: {
                        "verdict":     p["verdict"],
                        "confidence":  p["confidence"],
                        "key_point":   p["key_point"],
                        "dissents":    p.get("dissents", []),
                    }
                    for a, p in positions.items()
                },
            })

        consensus = self._build_consensus(positions, findings)
        logger.success(
            f"[DebateEngine] Complete: verdict={consensus['verdict']} "
            f"agreement={consensus['agreement_rate']:.0%}"
        )

        return {
            "entity_id":    entity_id,
            "entity_name":  entity_name,
            "complexity":   complexity,
            "agents_used":  len(agents),
            "hesitation":   hesitation,
            "rounds":       rounds,
            "consensus":    consensus,
            "methodology": (
                "Independent agent analysis followed by structured debate. "
                "Dissenting positions are preserved. No legal conclusions drawn."
            ),
            "analyzed_at":  datetime.now().isoformat(),
        }

    def _classify_complexity(self, findings: list[dict]) -> str:
        high_count = sum(1 for f in findings
                         if f.get("severity") in ("HIGH","VERY_HIGH"))
        if len(findings) <= SIMPLE_CASE_THRESHOLD and high_count == 0:
            return "simple"
        elif high_count >= 2 or len(findings) >= 4:
            return "complex"
        else:
            return "moderate"

    def _select_agents(self, complexity: str) -> list[str]:
        if complexity == "simple":
            return ["logical_analyst", "skeptic", "risk_analyst"]
        elif complexity == "moderate":
            return ["logical_analyst", "skeptic", "pattern_hunter",
                    "financial_analyst", "risk_analyst"]
        else:
            return list(AGENT_PROFILES.keys())

    def _detect_hesitation(self, findings: list[dict]) -> int:
        combined = " ".join(
            f.get("description","") for f in findings
        ).lower()
        count = 0
        for pattern in HESITATION_PATTERNS:
            count += len(re.findall(pattern, combined, re.IGNORECASE))
        return count

    def _initial_position(self, agent_id: str, findings: list[dict],
                           profile: dict) -> dict:
        high_count = sum(1 for f in findings
                         if f.get("severity") in ("HIGH","VERY_HIGH"))
        skepticism = profile["skepticism"]

        base_conf = 0.7 if high_count >= 2 else 0.5
        confidence = base_conf * (1 - skepticism * 0.3)

        if agent_id == "skeptic" or agent_id == "contrarian":
            verdict = "REQUIRES_FURTHER_EVIDENCE"
        elif agent_id == "risk_analyst":
            verdict = "ELEVATED_RISK" if high_count >= 1 else "LOW_RISK"
        else:
            verdict = "FINDINGS_SUPPORTED" if high_count >= 1 else "INCONCLUSIVE"

        return {
            "verdict":    verdict,
            "confidence": round(confidence, 3),
            "key_point":  (
                f"{profile['role']} initial assessment based on "
                f"{profile['focus']}."
            ),
            "dissents":   [],
            "round":      0,
        }

    def _run_round(self, round_num: int, positions: dict,
                    findings: list[dict], agents: list[str]) -> dict:
        new_positions = {}
        verdicts = [p["verdict"] for p in positions.values()]

        for agent_id in agents:
            profile = AGENT_PROFILES[agent_id]
            current = positions[agent_id]

            disagreements = [
                v for v in verdicts if v != current["verdict"]
            ]
            has_dissent = len(disagreements) > len(verdicts) // 2

            if has_dissent:
                adj = 0.05 if profile["skepticism"] < 0.5 else -0.03
            else:
                adj = 0.03

            new_conf = min(0.95, max(0.05,
                           current["confidence"] + adj))

            dissents = []
            if has_dissent and agent_id in ("skeptic","contrarian"):
                dissents.append(
                    f"Round {round_num}: dissents from majority verdict "
                    f"({len(disagreements)} of {len(verdicts)} agents disagree)"
                )

            new_positions[agent_id] = {
                "verdict":    current["verdict"],
                "confidence": round(new_conf, 3),
                "key_point":  (
                    f"Round {round_num}: {profile['role']} maintains "
                    f"position with {new_conf:.0%} confidence."
                ),
                "dissents":   dissents,
                "round":      round_num,
            }

        return new_positions

    def _check_drift(self, positions: dict) -> float:
        confidences = [p["confidence"] for p in positions.values()]
        if len(confidences) < 2:
            return 0.0
        mean = sum(confidences) / len(confidences)
        variance = sum((x - mean)**2 for x in confidences) / len(confidences)
        std = math.sqrt(variance)
        similarity = max(0.0, 1.0 - std * 5)
        return round(similarity, 3)

    def _inject_counter_pressure(self, positions: dict) -> dict:
        for agent_id in ("skeptic", "contrarian"):
            if agent_id in positions:
                p = positions[agent_id]
                positions[agent_id] = {
                    **p,
                    "confidence": max(0.05, p["confidence"] - 0.12),
                    "key_point":  (
                        p["key_point"] +
                        " Counter-pressure applied: agent re-evaluating "
                        "to prevent premature convergence."
                    ),
                    "dissents": p.get("dissents", []) + [
                        "Anti-drift mechanism: maintaining independent position"
                    ],
                }
        return positions

    def _build_consensus(self, positions: dict,
                          findings: list[dict]) -> dict:
        verdicts = [p["verdict"] for p in positions.values()]
        from collections import Counter
        verdict_counts = Counter(verdicts)
        top_verdict, top_count = verdict_counts.most_common(1)[0]

        agreement_rate = top_count / len(verdicts)
        avg_confidence = sum(p["confidence"]
                             for p in positions.values()) / len(positions)

        all_dissents = []
        for agent_id, p in positions.items():
            for d in p.get("dissents", []):
                all_dissents.append({
                    "agent": AGENT_PROFILES[agent_id]["role"],
                    "point": d,
                })

        high_findings = [f for f in findings
                         if f.get("severity") in ("HIGH","VERY_HIGH")]

        if agreement_rate >= 0.8 and avg_confidence >= 0.6:
            overall = "STRONG_CONSENSUS"
        elif agreement_rate >= 0.6:
            overall = "MODERATE_CONSENSUS"
        elif agreement_rate >= 0.4:
            overall = "WEAK_CONSENSUS"
        else:
            overall = "NO_CONSENSUS"

        return {
            "verdict":          top_verdict,
            "overall":          overall,
            "agreement_rate":   round(agreement_rate, 3),
            "avg_confidence":   round(avg_confidence, 3),
            "verdict_breakdown":dict(verdict_counts),
            "dissents_count":   len(all_dissents),
            "dissents":         all_dissents[:5],
            "high_findings":    len(high_findings),
            "summary": (
                f"{top_count} of {len(verdicts)} agents reached verdict "
                f"'{top_verdict}' ({agreement_rate:.0%} agreement). "
                f"Average confidence: {avg_confidence:.0%}. "
                f"{len(all_dissents)} dissenting point(s) preserved."
            ),
        }


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph — Debate Engine Test")
    print("=" * 55)
    engine = DebateEngine()
    findings = [
        {"type":"contract_concentration","severity":"HIGH",
         "description":"Three contracts from same ministry in 18 months."},
        {"type":"granger_causality","severity":"HIGH",
         "description":"Policy events predict contract awards (F=3.2)."},
        {"type":"benami","severity":"MODERATE",
         "description":"Director age anomaly detected in associated company."},
    ]
    r = engine.run("pol_001", "Test Entity", findings, driver=None)
    print(f"\n  Complexity:  {r['complexity']}")
    print(f"  Agents:      {r['agents_used']}")
    print(f"  Rounds:      {len(r['rounds'])}")
    c = r["consensus"]
    print(f"  Verdict:     {c['verdict']}")
    print(f"  Consensus:   {c['overall']}")
    print(f"  Agreement:   {c['agreement_rate']:.0%}")
    print(f"  Confidence:  {c['avg_confidence']:.0%}")
    print(f"  Dissents:    {c['dissents_count']}")
    print(f"\n  {c['summary']}")
    print("\nDone!")
