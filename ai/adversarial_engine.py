import os, sys, math, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from loguru import logger

CONFIDENCE_THRESHOLD = 0.6   # minimum evidence score to keep a hypothesis
MIN_FINDINGS_FOR_DEBATE = 2


class AdversarialEngine:
    """
    Forced counterevidence engine with competing hypotheses mode.

    For every HIGH-severity finding, the engine:
    1. Generates an alternative (contra) hypothesis that explains
       the same data without implying wrongdoing.
    2. Searches for evidence that supports the contra hypothesis.
    3. Produces a scorecard with evidence-for and evidence-against
       each hypothesis.
    4. Adjusts finding confidence based on counterevidence strength.

    This prevents confirmation bias in the investigation pipeline
    and produces legally defensible, balanced outputs.
    """

    CONTRA_TEMPLATES = {
        "contract_concentration": [
            "Entity operates in a specialised sector where few vendors qualify, "
            "making repeated awards to the same company structurally expected.",
            "Contracts were awarded through open competitive tender. Repeated wins "
            "reflect competitive pricing, not preferential treatment.",
        ],
        "ghost_company": [
            "Company was incorporated shortly before the contract because the "
            "contract opportunity itself prompted the business formation.",
            "Registration date proximity to contract may reflect data lag in "
            "official records rather than actual operational timeline.",
        ],
        "affidavit_wealth": [
            "Asset growth reflects legitimate investment returns, property "
            "appreciation, and inheritance not captured in salary declarations.",
            "Declared assets in earlier years may have been understated due "
            "to lack of independent valuation, not deliberate underreporting.",
        ],
        "granger_causality": [
            "Statistical correlation between policy events and contract awards "
            "reflects normal government procurement cycles, not causal influence.",
            "Both policy changes and contract awards are driven by the same "
            "underlying budget allocations, producing apparent but spurious correlation.",
        ],
        "bid_document_similarity": [
            "Bid documents use standard government procurement templates, making "
            "structural similarity across vendors expected and unrelated to coordination.",
            "Similarity reflects industry-standard specifications published by the "
            "procuring ministry, not copying between vendors.",
        ],
        "cooling_off_violation": [
            "The appointment was to a non-regulated sector not covered by "
            "the cooling-off policy applicable to this official's role.",
            "The private sector role is advisory in nature and does not involve "
            "the same subject matter as the official's prior government function.",
        ],
        "benami": [
            "Director relationship reflects a legitimate family business structure "
            "where multiple family members hold formal positions.",
            "Address sharing reflects co-location in a business park or registered "
            "office service, common among small and medium enterprises.",
        ],
        "default": [
            "The observed pattern may reflect coincidence, data quality issues, "
            "or structural features of the sector rather than intentional conduct.",
            "Additional context from primary source documents is required before "
            "drawing conclusions from this structural indicator.",
        ],
    }

    def analyze(self, entity_id: str, entity_name: str,
                findings: list[dict], driver=None) -> dict:
        logger.info(
            f"[AdversarialEngine] Analyzing {len(findings)} findings "
            f"for {entity_name}"
        )

        if not findings:
            return {
                "entity_id":       entity_id,
                "entity_name":     entity_name,
                "status":          "no_findings",
                "hypotheses":      [],
                "analyzed_at":     datetime.now().isoformat(),
            }

        high_findings = [f for f in findings
                         if f.get("severity") in ("HIGH", "VERY_HIGH")]
        if not high_findings:
            high_findings = findings[:3]

        hypotheses = []
        for finding in high_findings:
            h = self._build_hypothesis_pair(finding, entity_name, driver)
            hypotheses.append(h)

        overall = self._overall_assessment(hypotheses)

        logger.success(
            f"[AdversarialEngine] {entity_name}: "
            f"{len(hypotheses)} hypothesis pairs, "
            f"overall={overall['verdict']}"
        )

        return {
            "entity_id":       entity_id,
            "entity_name":     entity_name,
            "hypotheses":      hypotheses,
            "overall":         overall,
            "methodology": (
                "For each HIGH finding, a primary hypothesis (finding as stated) "
                "and a contra hypothesis (alternative innocent explanation) are "
                "evaluated against available evidence. Confidence is adjusted "
                "based on the strength of counterevidence."
            ),
            "analyzed_at":     datetime.now().isoformat(),
        }

    def _build_hypothesis_pair(self, finding: dict,
                                entity_name: str,
                                driver) -> dict:
        finding_type = finding.get("type", "default")

        primary = {
            "label":       "Primary Hypothesis",
            "description": finding.get("description",""),
            "type":        finding_type,
            "evidence_for":  finding.get("evidence", []),
            "evidence_against": [],
            "confidence":  1.0,
        }

        contra_texts = self.CONTRA_TEMPLATES.get(
            finding_type,
            self.CONTRA_TEMPLATES["default"]
        )

        db_evidence = self._search_counterevidence(
            finding_type, entity_name, driver
        )

        contra = {
            "label":       "Contra Hypothesis",
            "description": contra_texts[0],
            "type":        f"contra_{finding_type}",
            "evidence_for":  [contra_texts[1]] + db_evidence,
            "evidence_against": finding.get("evidence", []),
            "confidence":  self._score_contra(db_evidence, finding),
        }

        primary["confidence"] = max(
            0.1, 1.0 - contra["confidence"] * 0.4
        )

        verdict = self._verdict(primary["confidence"], contra["confidence"])

        return {
            "finding_type": finding_type,
            "severity":     finding.get("severity",""),
            "primary":      primary,
            "contra":       contra,
            "verdict":      verdict,
            "note": (
                "This scorecard presents both the primary structural indicator "
                "and an alternative explanation. Neither constitutes a legal "
                "finding. Further primary source investigation is required."
            ),
        }

    def _search_counterevidence(self, finding_type: str,
                                  entity_name: str,
                                  driver) -> list[str]:
        if not driver:
            return []
        evidence = []
        try:
            with driver.session() as s:
                if finding_type == "contract_concentration":
                    row = s.run(
                        """
                        MATCH (c:Company)-[:WON_CONTRACT]->(ct:Contract)
                        WHERE toLower(c.name) CONTAINS toLower($name)
                        WITH ct.buyer_org AS buyer, count(*) AS n
                        WHERE n >= 2
                        RETURN count(*) AS repeat_buyers
                        """, name=entity_name
                    ).single()
                    if row and row.get("repeat_buyers",0) == 0:
                        evidence.append(
                            "No repeat buyers found — contracts came from "
                            "different ministries, suggesting open competition."
                        )

                elif finding_type in ("granger_causality", "transfer_entropy"):
                    row = s.run(
                        """
                        MATCH (p {id:$name})-[:MEMBER_OF]->(party:Party)
                        RETURN party.name AS party
                        """, name=entity_name
                    ).single()
                    if row:
                        evidence.append(
                            f"Entity is a member of {row['party']} — budget "
                            "allocations are party-level, not individual decisions."
                        )
        except Exception as e:
            logger.warning(f"[Adversarial] Counterevidence search failed: {e}")
        return evidence

    def _score_contra(self, db_evidence: list[str],
                       finding: dict) -> float:
        base  = 0.25
        boost = min(0.4, len(db_evidence) * 0.15)
        sev   = finding.get("severity","")
        if sev == "LOW":
            base = 0.45
        elif sev == "MODERATE":
            base = 0.30
        elif sev in ("HIGH", "VERY_HIGH"):
            base = 0.15
        return round(min(0.90, base + boost), 3)

    def _verdict(self, primary_conf: float, contra_conf: float) -> str:
        ratio = primary_conf / max(contra_conf, 0.01)
        if ratio > 3.0:
            return "PRIMARY_HYPOTHESIS_SUPPORTED"
        elif ratio > 1.5:
            return "PRIMARY_HYPOTHESIS_PROBABLE"
        elif ratio > 0.8:
            return "INCONCLUSIVE"
        else:
            return "CONTRA_HYPOTHESIS_PROBABLE"

    def _overall_assessment(self, hypotheses: list[dict]) -> dict:
        if not hypotheses:
            return {"verdict": "NO_FINDINGS", "summary": "No findings to assess."}

        verdicts = [h["verdict"] for h in hypotheses]
        supported = sum(1 for v in verdicts
                        if v in ("PRIMARY_HYPOTHESIS_SUPPORTED",
                                 "PRIMARY_HYPOTHESIS_PROBABLE"))
        inconclusive = sum(1 for v in verdicts if v == "INCONCLUSIVE")
        contra_wins  = sum(1 for v in verdicts if v == "CONTRA_HYPOTHESIS_PROBABLE")

        if supported > inconclusive + contra_wins:
            verdict = "FINDINGS_SUPPORTED"
            summary = (
                f"{supported} of {len(hypotheses)} findings remain supported "
                f"after counterevidence analysis."
            )
        elif contra_wins > supported:
            verdict = "FINDINGS_WEAKENED"
            summary = (
                f"Counterevidence analysis weakens {contra_wins} of "
                f"{len(hypotheses)} findings. Additional investigation recommended."
            )
        else:
            verdict = "INCONCLUSIVE"
            summary = (
                f"Mixed results across {len(hypotheses)} findings. "
                f"Neither primary nor contra hypotheses are clearly dominant."
            )

        return {
            "verdict":        verdict,
            "summary":        summary,
            "supported":      supported,
            "inconclusive":   inconclusive,
            "contra_wins":    contra_wins,
            "total_assessed": len(hypotheses),
        }


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph — Adversarial Engine Test")
    print("=" * 55)
    engine = AdversarialEngine()
    sample_findings = [
        {
            "type":     "contract_concentration",
            "severity": "HIGH",
            "description": "Three contracts from the same ministry in 18 months.",
            "evidence": ["Contract CT001: Rs 12 Cr", "Contract CT002: Rs 18 Cr",
                         "Contract CT003: Rs 9 Cr"],
        },
        {
            "type":     "granger_causality",
            "severity": "HIGH",
            "description": "Policy events predict contract awards (F=3.2).",
            "evidence": ["F-statistic: 3.2", "Lag: 2"],
        },
    ]
    r = engine.analyze("pol_001", "Test Entity", sample_findings, driver=None)
    print(f"\n  Hypotheses: {len(r['hypotheses'])}")
    print(f"  Overall:    {r['overall']['verdict']}")
    print(f"  Summary:    {r['overall']['summary']}")
    for h in r["hypotheses"]:
        print(f"\n  [{h['finding_type']}]")
        print(f"    Primary confidence:  {h['primary']['confidence']:.2f}")
        print(f"    Contra confidence:   {h['contra']['confidence']:.2f}")
        print(f"    Verdict:             {h['verdict']}")
    print("\nDone!")
