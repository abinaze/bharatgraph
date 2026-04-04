import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger

NAME   = "MathematicalInvestigator"
FOCUS  = "mathematical_pattern_analysis"
WEIGHT = 0.08


def investigate(entity_id: str, entity_name: str,
                session=None, driver=None) -> dict:
    logger.info(f"[{NAME}] Investigating {entity_name}")

    findings  = []
    positive  = []
    evidence  = []

    try:
        from ai.math.spectral_analyzer import SpectralAnalyzer
        spectral = SpectralAnalyzer()
        sr = spectral.analyze(entity_id, driver)
        findings.extend(sr.get("findings", []))
        if sr.get("fiedler_value", 1.0) > 0.5:
            positive.append(
                f"Spectral analysis: well-connected in institutional network "
                f"(Fiedler λ₁ = {sr['fiedler_value']:.4f})"
            )
        evidence.append({
            "institution": "Mathematical Analysis",
            "document":    "Spectral Graph Analysis",
            "method":      "Laplacian Eigenvalue (Fiedler Value)",
        })
    except Exception as e:
        logger.warning(f"[{NAME}] Spectral analysis failed: {e}")

    try:
        contract_events = []
        if session:
            rows = session.run(
                """
                MATCH (n {id: $id})-[:DIRECTOR_OF]->(:Company)
                      -[:WON_CONTRACT]->(ct:Contract)
                RETURN ct.order_date AS date, ct.amount_crore AS amount
                ORDER BY ct.order_date
                """,
                id=entity_id
            ).data()
            contract_events = [{"date": r["date"], "amount_crore": r.get("amount", 0)}
                               for r in rows if r.get("date")]

        if len(contract_events) >= 4:
            from ai.math.fourier_timeline import FourierTimelineAnalyzer
            fourier = FourierTimelineAnalyzer()
            fr = fourier.analyze(entity_id, contract_events)
            findings.extend(fr.get("findings", []))
            evidence.append({
                "institution": "Mathematical Analysis",
                "document":    "Fourier Timeline Analysis",
                "method":      "Fast Fourier Transform on Contract Sequence",
            })
    except Exception as e:
        logger.warning(f"[{NAME}] Fourier analysis failed: {e}")

    try:
        from ai.benfords_analyzer import BenfordAnalyzer
        ba = BenfordAnalyzer()
        if session:
            rows = session.run(
                "MATCH (p:Politician {id:$id}) RETURN p.total_assets_crore AS assets",
                id=entity_id
            ).data()
            assets = [r["assets"] for r in rows if r.get("assets")]
            if assets:
                br = ba.analyze(assets)
                if br.get("anomaly"):
                    findings.append({
                        "type":        "benford_anomaly",
                        "severity":    "MODERATE",
                        "description": (
                            "Benford's Law analysis flags statistical anomaly "
                            "in declared asset figures."
                        ),
                        "evidence": [f"Chi-squared: {br.get('chi_squared',0):.2f}",
                                     f"p-value: {br.get('p_value',1.0):.4f}"],
                    })
    except Exception as e:
        logger.warning(f"[{NAME}] Benford analysis failed: {e}")

    if not findings and not positive:
        positive.append(
            "Mathematical pattern analysis found no statistically significant "
            "anomalies in the available data."
        )

    logger.success(
        f"[{NAME}] Complete: {len(findings)} findings, "
        f"{len(positive)} positive"
    )

    return {
        "investigator": NAME,
        "focus":        FOCUS,
        "weight":       WEIGHT,
        "findings":     findings,
        "positive":     positive,
        "evidence":     evidence,
        "investigated_at": datetime.now().isoformat(),
    }
