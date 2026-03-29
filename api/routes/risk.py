import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from api.models import RiskResponse, RiskFactor, SourceDocument
from api.dependencies import get_db

router = APIRouter()

RISK_LEVELS = {
    (0,  30):  "LOW",
    (31, 60):  "MODERATE",
    (61, 80):  "HIGH",
    (81, 100): "VERY_HIGH",
}


def score_to_level(score: int) -> str:
    for (lo, hi), level in RISK_LEVELS.items():
        if lo <= score <= hi:
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
        total_crore    = contract_rows["total_crore"]    if contract_rows else 0

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

        audit_rows = session.run(
            """
            MATCH (a:AuditReport)
            WHERE toLower(a.title) CONTAINS toLower($name)
            RETURN count(a) AS audit_count
            """,
            name=entity_name
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

        final_score = min(total_score, 100)
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
