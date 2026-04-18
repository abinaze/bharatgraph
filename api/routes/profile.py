import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from api.models import ProfileResponse, ProfileSection, SourceDocument
from api.dependencies import get_db

router = APIRouter()


@router.get("/profile/{entity_id}", response_model=ProfileResponse)
def get_profile(entity_id: str, driver=Depends(get_db)):
    logger.info(f"[Profile] entity_id={entity_id}")

    with driver.session() as session:
        pol = session.run(
            "MATCH (p:Politician {id: $id}) RETURN p", id=entity_id
        ).single()

        if pol:
            p = dict(pol["p"])
            sections = []

            contracts = session.run(
                """
                MATCH (p:Politician {id: $id})-[:DIRECTOR_OF]->(c:Company)
                      -[:WON_CONTRACT]->(ct:Contract)
                RETURN c.name AS company, ct.order_id AS order_id,
                       ct.amount_crore AS amount, ct.buyer_org AS buyer,
                       ct.order_date AS date
                ORDER BY ct.amount_crore DESC
                """,
                id=entity_id
            ).data()

            if contracts:
                sections.append(ProfileSection(
                    section="Contracts via Associated Companies",
                    data=contracts,
                    sources=[SourceDocument(
                        institution="Government e-Marketplace",
                        document_title="GeM Procurement Order",
                        url="https://gem.gov.in",
                    )]
                ))

            audits = session.run(
                """
                MATCH (a:AuditReport)-[:FLAGS]->(s:Scheme)
                WHERE toLower(a.title) CONTAINS toLower($name)
                RETURN a.title AS title, a.year AS year,
                       a.amount_crore AS amount, s.name AS scheme
                """,
                name=p.get("name", "")
            ).data()

            if audits:
                sections.append(ProfileSection(
                    section="CAG Audit Mentions",
                    data=audits,
                    sources=[SourceDocument(
                        institution="Comptroller and Auditor General",
                        document_title="Performance Audit Report",
                        url="https://cag.gov.in/en/audit-report",
                    )]
                ))

            return ProfileResponse(
                entity_id=entity_id,
                entity_type="Politician",
                name=p.get("name", ""),
                overview={
                    "party":          p.get("party"),
                    "state":          p.get("state"),
                    "criminal_cases": p.get("criminal_cases"),
                    "total_assets":   p.get("total_assets"),
                    "education":      p.get("education"),
                    "source":         p.get("source"),
                },
                sections=sections,
                generated_at=datetime.now().isoformat(),
            )

        co = session.run(
            "MATCH (c:Company {id: $id}) RETURN c", id=entity_id
        ).single()

        if co:
            c = dict(co["c"])
            contracts = session.run(
                """
                MATCH (c:Company {id: $id})-[:WON_CONTRACT]->(ct:Contract)
                RETURN ct.order_id AS order_id, ct.amount_crore AS amount,
                       ct.buyer_org AS buyer, ct.order_date AS date
                ORDER BY ct.amount_crore DESC
                """,
                id=entity_id
            ).data()

            sections = []
            if contracts:
                sections.append(ProfileSection(
                    section="Government Contracts Won",
                    data=contracts,
                    sources=[SourceDocument(
                        institution="Government e-Marketplace",
                        document_title="GeM Procurement Order",
                        url="https://gem.gov.in",
                    )]
                ))

            return ProfileResponse(
                entity_id=entity_id,
                entity_type="Company",
                name=c.get("name", ""),
                overview={
                    "cin":    c.get("cin"),
                    "status": c.get("status"),
                    "state":  c.get("state"),
                    "class":  c.get("company_class"),
                },
                sections=sections,
                generated_at=datetime.now().isoformat(),
            )

    # Generic fallback: return whatever node exists for this ID
    with driver.session() as session:
        generic = session.run(
            """
            MATCH (n {id: $id})
            RETURN n, labels(n)[0] AS label
            """,
            id=entity_id
        ).single()

    if generic:
        n = dict(generic["n"])
        label = generic["label"] or "Unknown"
        name = n.get("name") or n.get("title") or n.get("ngo_name") or n.get("company_name") or entity_id

        # Build context-aware sections
        sections = []
        overview = {k: v for k, v in n.items()
                    if k not in ("id",) and v is not None}

        return ProfileResponse(
            entity_id=entity_id,
            entity_type=label,
            name=name,
            overview=overview,
            sections=sections,
            sources=[SourceDocument(
                institution="BharatGraph Knowledge Graph",
                document_title=f"{label} Record",
                url="https://abinaze.github.io/bharatgraph",
            )],
            generated_at=datetime.now().isoformat(),
        )

    raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
