import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from api.models import RiskResponse, RiskFactor, SourceDocument
from api.dependencies import get_db
from ai.benfords_analyzer import BenfordsAnalyzer
from ai.ghost_company    import GhostCompanyDetector
from ai.shadow_director  import ShadowDirectorDetector
from ai.explainer        import generate_explanation

router = APIRouter()

RISK_LEVELS = {
    (0,   0):  "NONE",      # M-06 FIX: explicit zero-score state (no factors found)
    (1,  30):  "LOW",
    (31, 60):  "MODERATE",
    (61, 80):  "HIGH",
    (81, 100): "VERY_HIGH",
}


def score_to_level(score: int) -> str:
    # M-08 FIX: clamp to 0-100 before lookup -- scores >100 returned "UNKNOWN"
    clamped = max(0, min(int(score), 100))
    for (lo, hi), level in RISK_LEVELS.items():
        if lo <= clamped <= hi:
            return level
    return "UNKNOWN"


@router.get("/risk/{entity_id}", response_model=RiskResponse)
def get_risk(entity_id: str, driver=Depends(get_db)):
    logger.info(f"[Risk] entity_id={entity_id}")

    with driver.session() as session:
        entity = session.run(
            """
            MATCH (n {id: $id})
            RETURN n.name AS name, labels(n)[0] AS type
            """,
            id=entity_id
        ).single()

        if not entity:
            raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

        entity_name = entity["name"] or entity_id
        factors = []
        total_score = 0

        contract_rows = session.run(
            """
            MATCH (p {id: $id})-[:DIRECTOR_OF]->(c:Company)-[:WON_CONTRACT]->(ct:Contract)
            RETURN count(ct) AS contract_count, sum(ct.amount_crore) AS total_crore
            """,
            id=entity_id
        ).single()

        contract_count = contract_rows["contract_count"] if contract_rows else 0
        # C-02 FIX: SUM() returns None (Python None) when no rows match.
        # None cannot be formatted with :.1f -- guard with "or 0"
        total_crore = (contract_rows["total_crore"] if contract_rows else 0) or 0

        if contract_count and contract_count > 0:
            raw = min(contract_count * 10, 35)
            factors.append(RiskFactor(
                name="politician_company_contract_overlap",
                score=raw,
                weight=0.35,
                description=(
                    f"Entity is linked to {contract_count} government contract(s) "
                    f"totalling Rs {total_crore:.1f} Cr through company directorships."
                ),
                evidence=[
                    f"{contract_count} contract(s) via DIRECTOR_OF -> WON_CONTRACT path",
                    f"Total contract value: Rs {total_crore:.2f} Cr",
                ],
            ))
            total_score += raw

        repeat_rows = session.run(
            """
            MATCH (co:Company {id: $id})-[:WON_CONTRACT]->(ct:Contract)
            WITH count(ct) AS cnt
            WHERE cnt >= 2
            RETURN cnt
            """,
            id=entity_id
        ).single()

        if repeat_rows:
            raw = min(repeat_rows["cnt"] * 8, 25)
            factors.append(RiskFactor(
                name="contract_concentration",
                score=raw,
                weight=0.25,
                description=(
                    f"Company won {repeat_rows['cnt']} contracts from government portals. "
                    "Repeated contract awards to the same entity indicate concentration."
                ),
                evidence=[
                    f"{repeat_rows['cnt']} contracts found via WON_CONTRACT relationships",
                    "Source: Government e-Marketplace procurement records",
                ],
            ))
            total_score += raw

        # H-08 FIX: name substring match causes massive false positives
        # (e.g. "India" matches every CAG report). Use relationship-based
        # matching first; fall back to exact-word name match only.
        audit_rows = session.run(
            """
            OPTIONAL MATCH (n {id: $id})-[:MENTIONED_IN]->(a1:AuditReport)
            WITH collect(a1) AS direct
            OPTIONAL MATCH (a2:AuditReport)
            WHERE size(direct) = 0
              AND (toLower(a2.title) CONTAINS (' ' + toLower($name) + ' ')
                   OR toLower(a2.title) STARTS WITH (toLower($name) + ' ')
                   OR toLower(a2.title) ENDS WITH (' ' + toLower($name)))
            RETURN count(direct) + count(a2) AS audit_count
            """,
            id=entity_id, name=entity_name
        ).single()

        audit_count = audit_rows["audit_count"] if audit_rows else 0
        if audit_count and audit_count > 0:
            raw = min(audit_count * 10, 20)
            factors.append(RiskFactor(
                name="audit_mention_frequency",
                score=raw,
                weight=0.20,
                description=(
                    f"Entity or associated names appear in {audit_count} CAG audit report(s)."
                ),
                evidence=[
                    f"{audit_count} CAG report mention(s)",
                    "Source: Comptroller and Auditor General reports, cag.gov.in",
                ],
            ))
            total_score += raw

        criminal_rows = session.run(
            """
            MATCH (p:Politician {id: $id})
            WHERE toInteger(p.criminal_cases) > 0
            RETURN toInteger(p.criminal_cases) AS cases
            """,
            id=entity_id
        ).single()

        if criminal_rows:
            raw = min(criminal_rows["cases"] * 3, 5)
            factors.append(RiskFactor(
                name="declared_criminal_cases",
                score=raw,
                weight=0.05,
                description=(
                    f"Entity has declared {criminal_rows['cases']} criminal case(s) "
                    "in their Election Commission affidavit."
                ),
                evidence=[
                    f"{criminal_rows['cases']} declared criminal case(s)",
                    "Source: Election Commission of India candidate affidavit",
                ],
            ))
            total_score += raw

        # Phase 34: Benford Law analysis on affidavit asset values
        try:
            ba = BenfordsAnalyzer()
            asset_rows = session.run(
                "MATCH (p {id:})-[:FILED_AFFIDAVIT]->(a:Affidavit)"
                " RETURN a.total_assets_crore AS v",
                id=entity_id
            ).data()
            asset_vals = [r["v"] for r in asset_rows if r.get("v")]
            if len(asset_vals) >= 5:
                bf = ba.analyze(asset_vals)
                chi2 = bf.get("chi2_statistic", 0) or 0
                if chi2 > 15.5:  # p<0.05 threshold
                    raw = min(int(chi2 / 2), 20)
                    factors.append(RiskFactor(
                        name="benfords_law_anomaly",
                        score=raw,
                        weight=0.20,
                        description=(
                            f"Asset declarations deviate significantly from "
                            f"Benford Law distribution (chi2={chi2:.1f}). "
                            "Fabricated or rounded figures can cause this pattern."
                        ),
                        evidence=[
                            f"Chi-squared statistic: {chi2:.2f} (threshold 15.5)",
                            f"Analysed {len(asset_vals)} affidavit asset values",
                            "Source: Election Commission affidavit data",
                        ],
                    ))
                    total_score += raw
        except Exception as _bf_e:
            logger.debug(f"[Risk] Benford analysis skipped: {type(_bf_e).__name__}")

        # Phase 34: ghost company detection
        try:
            co_rows = session.run(
                "MATCH (co:Company)-[:DIRECTOR_OF|:LINKED_TO*1..2]-(n {id:})"
                " RETURN co.id AS id, co.name AS name,"
                "        co.employee_count AS emp,"
                "        co.registered_capital_crore AS cap"
                " LIMIT 20",
                id=entity_id
            ).data()
            if co_rows:
                gcd = GhostCompanyDetector(driver=driver)
                scored = [gcd.score_company(r) for r in co_rows]
                ghosts = [s for s in scored if s.get("ghost_score", 0) >= 70]
                if ghosts:
                    raw = min(len(ghosts) * 12, 24)
                    factors.append(RiskFactor(
                        name="ghost_company_association",
                        score=raw,
                        weight=0.24,
                        description=(
                            f"Entity is linked to {len(ghosts)} company/companies "
                            "showing ghost company indicators (no employees, "
                            "minimal capital, high contract volume)."
                        ),
                        evidence=[
                            f"{len(ghosts)} ghost company indicator(s) detected",
                            ", ".join(g.get("name","") for g in ghosts[:3]),
                            "Source: MCA filings + GeM procurement records",
                        ],
                    ))
                    total_score += raw
        except Exception as _gc_e:
            logger.debug(f"[Risk] Ghost company check skipped: {type(_gc_e).__name__}")

        # Phase 34: shadow director detection
        try:
            dir_rows = session.run(
                "MATCH (n {id:})-[:DIRECTOR_OF]->(co:Company)"
                " RETURN count(co) AS dir_count",
                id=entity_id
            ).single()
            dir_count = dir_rows["dir_count"] if dir_rows else 0
            if dir_count >= 10:
                raw = min(dir_count * 2, 15)
                factors.append(RiskFactor(
                    name="high_directorship_count",
                    score=raw,
                    weight=0.15,
                    description=(
                        f"Entity is director of {dir_count} companies. "
                        "High directorship counts are a shadow director indicator."
                    ),
                    evidence=[
                        f"{dir_count} DIRECTOR_OF relationships in graph",
                        "Source: MCA company filings",
                    ],
                ))
                total_score += raw
        except Exception as _sd_e:
            logger.debug(f"[Risk] Shadow director check skipped: {type(_sd_e).__name__}")

        final_score = max(0, min(total_score, 100))  # M-08 FIX: clamp both directions
        level = score_to_level(final_score)

        if final_score == 0:
            explanation = (
                f"No structural risk indicators found for {entity_name} in the current "
                "dataset. This may reflect limited data coverage rather than the absence "
                "of patterns."
            )
        elif final_score <= 30:
            explanation = (
                f"Low structural indicators detected for {entity_name}. "
                f"{len(factors)} factor(s) identified with minor pattern signals."
            )
        elif final_score <= 60:
            explanation = (
                f"Moderate structural indicators detected for {entity_name}. "
                f"{len(factors)} factor(s) identified. Further investigation warranted."
            )
        else:
            explanation = (
                f"High structural indicators detected for {entity_name}. "
                f"{len(factors)} significant pattern(s) identified across procurement "
                "and audit data. This is an analytical indicator, not a legal finding."
            )

        return RiskResponse(
            entity_id=entity_id,
            entity_name=entity_name,
            risk_score=final_score,
            risk_level=level,
            factors=factors,
            explanation=explanation,
            sources=[
                SourceDocument(
                    institution="Government e-Marketplace",
                    document_title="GeM Procurement Records",
                    url="https://gem.gov.in",
                ),
                SourceDocument(
                    institution="Comptroller and Auditor General",
                    document_title="CAG Audit Reports",
                    url="https://cag.gov.in",
                ),
            ],
            generated_at=datetime.now().isoformat(),
        )
