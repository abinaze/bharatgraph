import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from loguru import logger

from api.models import SearchResponse, SearchResult, SourceDocument
from api.dependencies import get_db

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
def search_entities(
    q: str = Query(..., min_length=2, description="Search term"),
    entity_type: Optional[str] = Query(None, description="politician|company|contract|audit"),
    limit: int = Query(20, le=100),
    driver=Depends(get_db),
):
    logger.info(f"[Search] query='{q}' type={entity_type} limit={limit}")

    results = []

    with driver.session() as session:
        if entity_type == "politician" or entity_type is None:
            rows = session.run(
                """
                MATCH (p:Politician)
                WHERE toLower(p.name) CONTAINS toLower($q)
                RETURN p.id AS id, 'Politician' AS type, p.name AS name,
                       p.state AS state, p.party AS party
                LIMIT $limit
                """,
                q=q, limit=limit
            ).data()
            for r in rows:
                results.append(SearchResult(
                    entity_id=r["id"] or "",
                    entity_type="Politician",
                    name=r["name"] or "",
                    state=r.get("state"),
                    party=r.get("party"),
                    sources=[SourceDocument(
                        institution="Election Commission of India / MyNeta",
                        document_title="Candidate Affidavit",
                        url="https://myneta.info",
                    )]
                ))

        if entity_type == "company" or entity_type is None:
            rows = session.run(
                """
                MATCH (c:Company)
                WHERE toLower(c.name) CONTAINS toLower($q)
                RETURN c.id AS id, 'Company' AS type, c.name AS name,
                       c.state AS state
                LIMIT $limit
                """,
                q=q, limit=limit
            ).data()
            for r in rows:
                results.append(SearchResult(
                    entity_id=r["id"] or "",
                    entity_type="Company",
                    name=r["name"] or "",
                    state=r.get("state"),
                    sources=[SourceDocument(
                        institution="Ministry of Corporate Affairs",
                        document_title="MCA21 Company Master",
                        url="https://www.mca.gov.in",
                    )]
                ))

        if entity_type == "audit" or entity_type is None:
            rows = session.run(
                """
                MATCH (a:AuditReport)
                WHERE toLower(a.title) CONTAINS toLower($q)
                RETURN a.id AS id, 'AuditReport' AS type, a.title AS name,
                       a.state AS state
                LIMIT $limit
                """,
                q=q, limit=limit
            ).data()
            for r in rows:
                results.append(SearchResult(
                    entity_id=r["id"] or "",
                    entity_type="AuditReport",
                    name=r["name"] or "",
                    state=r.get("state"),
                    sources=[SourceDocument(
                        institution="Comptroller and Auditor General of India",
                        document_title="CAG Audit Report",
                        url="https://cag.gov.in",
                    )]
                ))

    return SearchResponse(
        query=q,
        total=len(results),
        results=results[:limit],
        generated_at=datetime.now().isoformat(),
    )
