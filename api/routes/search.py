import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from loguru import logger

from api.models import SearchResponse, SearchResult, SourceDocument
from api.dependencies import get_db

router = APIRouter()

# BUG-10 FIX: expanded from 8 to 20 node types so every label gets proper
# source attribution instead of falling back to "BharatGraph/Knowledge Graph/#".
SOURCE_MAP = {
    "Politician":        ("Election Commission of India / MyNeta", "Candidate Affidavit",         "https://myneta.info"),
    "Company":           ("Ministry of Corporate Affairs",         "MCA21 Company Master",         "https://www.mca.gov.in"),
    "AuditReport":       ("Comptroller and Auditor General",       "CAG Audit Report",             "https://cag.gov.in"),
    "Contract":          ("Government e-Marketplace",              "GeM Contract",                 "https://gem.gov.in"),
    "Ministry":          ("Government of India",                   "Ministry Directory",            "https://india.gov.in"),
    "Party":             ("Election Commission of India",          "Party Registration",            "https://eci.gov.in"),
    "Scheme":            ("NITI Aayog / Ministries",               "Scheme Database",              "https://myscheme.gov.in"),
    # BUG-18 FIX: key was "pressrelease" but scraper produces "pib" — normalised
    "PressRelease":      ("Press Information Bureau",              "PIB Press Release",             "https://pib.gov.in"),
    "NGO":               ("NGO Darpan / NITI Aayog",              "NGO Registration Record",       "https://ngodarpan.gov.in"),
    "ElectoralBond":     ("Election Commission of India",          "Electoral Bond Transaction",    "https://eci.gov.in"),
    "InsolvencyOrder":   ("Insolvency and Bankruptcy Board",       "IBBI Insolvency Order",         "https://ibbi.gov.in"),
    "Tender":            ("Central Public Procurement Portal",     "CPPP Tender Notice",            "https://eprocure.gov.in"),
    "RegulatoryOrder":   ("Securities and Exchange Board of India","SEBI Enforcement Order",        "https://sebi.gov.in"),
    "EnforcementAction": ("Enforcement Directorate",               "ED Press Release",              "https://enforcementdirectorate.gov.in"),
    "ParliamentQuestion":("Lok Sabha Secretariat",                 "Parliamentary Question",        "https://loksabha.nic.in"),
    "VigilanceCircular": ("Central Vigilance Commission",          "CVC Circular",                  "https://cvc.gov.in"),
    "ICIJEntity":        ("ICIJ Offshore Leaks Database",          "Offshore Leaks Record",         "https://offshoreleaks.icij.org"),
    "SanctionedEntity":  ("OpenSanctions",                        "Sanctions / PEP Record",         "https://www.opensanctions.org"),
    "CourtCase":         ("National Judicial Data Grid",           "Court Pendency Record",         "https://njdg.ecourts.gov.in"),
    "LocalBody":         ("Local Government Directory",            "LGD Entity Record",             "https://lgdirectory.gov.in"),
}

# BUG-4 FIX: added ParliamentQuestion, VigilanceCircular, ICIJEntity,
# SanctionedEntity, CourtCase, LocalBody — previously these node types were
# loaded into Neo4j but had no LABEL_QUERIES entry, making them unsearchable
# via the label-scan fallback path.
LABEL_QUERIES = {
    "politician": ("Politician",
        "MATCH (n:Politician) "
        "WHERE toLower(n.name) CONTAINS toLower($q) "
        "   OR any(a IN coalesce(n.aliases,[]) WHERE toLower(a) CONTAINS toLower($q)) "
        "RETURN n.id AS id, n.name AS name, n.state AS state, n.party AS party LIMIT $limit"),
    "company": ("Company",
        "MATCH (n:Company) "
        "WHERE toLower(n.name) CONTAINS toLower($q) "
        "   OR toLower(coalesce(n.cin,'')) CONTAINS toLower($q) "
        "RETURN n.id AS id, n.name AS name, n.state AS state, null AS party LIMIT $limit"),
    "audit": ("AuditReport",
        "MATCH (n:AuditReport) "
        "WHERE toLower(n.title) CONTAINS toLower($q) "
        "   OR toLower(coalesce(n.ministry,'')) CONTAINS toLower($q) "
        "RETURN n.id AS id, n.title AS name, n.state AS state, null AS party LIMIT $limit"),
    "contract": ("Contract",
        "MATCH (n:Contract) "
        "WHERE toLower(coalesce(n.item_desc,'')) CONTAINS toLower($q) "
        "   OR toLower(coalesce(n.product,'')) CONTAINS toLower($q) "
        "   OR toLower(coalesce(n.buyer_org,'')) CONTAINS toLower($q) "
        "   OR toLower(coalesce(n.order_id,'')) CONTAINS toLower($q) "
        "RETURN n.id AS id, "
        "       coalesce(n.item_desc, n.product, n.order_id) AS name, "
        "       null AS state, null AS party LIMIT $limit"),
    "ministry": ("Ministry",
        "MATCH (n:Ministry) WHERE toLower(n.name) CONTAINS toLower($q) "
        "RETURN n.id AS id, n.name AS name, null AS state, null AS party LIMIT $limit"),
    "party": ("Party",
        "MATCH (n:Party) "
        "WHERE toLower(n.name) CONTAINS toLower($q) "
        "   OR toLower(coalesce(n.abbreviation,'')) CONTAINS toLower($q) "
        "RETURN n.id AS id, n.name AS name, null AS state, null AS party LIMIT $limit"),
    "scheme": ("Scheme",
        "MATCH (n:Scheme) WHERE toLower(n.name) CONTAINS toLower($q) "
        "RETURN n.id AS id, n.name AS name, null AS state, null AS party LIMIT $limit"),
    "regulatory": ("RegulatoryOrder",
        "MATCH (n:RegulatoryOrder) "
        "WHERE toLower(coalesce(n.title,'')) CONTAINS toLower($q) "
        "   OR toLower(coalesce(n.entity_name,'')) CONTAINS toLower($q) "
        "RETURN n.id AS id, n.title AS name, null AS state, null AS party LIMIT $limit"),
    "enforcement": ("EnforcementAction",
        "MATCH (n:EnforcementAction) "
        "WHERE toLower(coalesce(n.title,'')) CONTAINS toLower($q) "
        "   OR toLower(coalesce(n.accused,'')) CONTAINS toLower($q) "
        "RETURN n.id AS id, n.title AS name, null AS state, null AS party LIMIT $limit"),
    "tender": ("Tender",
        "MATCH (n:Tender) "
        "WHERE toLower(coalesce(n.title,'')) CONTAINS toLower($q) "
        "   OR toLower(coalesce(n.ministry,'')) CONTAINS toLower($q) "
        "RETURN n.id AS id, n.title AS name, null AS state, null AS party LIMIT $limit"),
    "electoralbond": ("ElectoralBond",
        "MATCH (n:ElectoralBond) "
        "WHERE toLower(coalesce(n.purchaser_name,'')) CONTAINS toLower($q) "
        "   OR toLower(coalesce(n.redeemed_by,'')) CONTAINS toLower($q) "
        "RETURN n.id AS id, coalesce(n.purchaser_name,n.redeemed_by) AS name, "
        "null AS state, null AS party LIMIT $limit"),
    "insolvency": ("InsolvencyOrder",
        "MATCH (n:InsolvencyOrder) "
        "WHERE toLower(coalesce(n.company_name,'')) CONTAINS toLower($q) "
        "RETURN n.id AS id, n.company_name AS name, null AS state, null AS party LIMIT $limit"),
    "ngo": ("NGO",
        "MATCH (n:NGO) "
        "WHERE toLower(coalesce(n.ngo_name,'')) CONTAINS toLower($q) "
        "RETURN n.id AS id, n.ngo_name AS name, n.state AS state, null AS party LIMIT $limit"),
    # BUG-18 FIX: key renamed from "pressrelease" to "pib" to match scraper key,
    # so SOURCE_MAP lookup returns the correct PIB attribution.
    "pib": ("PressRelease",
        "MATCH (n:PressRelease) "
        "WHERE toLower(coalesce(n.title,'')) CONTAINS toLower($q) "
        "RETURN n.id AS id, coalesce(n.title, n.id) AS name, null AS state, null AS party LIMIT $limit"),
    # BUG-4 FIX: 6 new searchable types
    "parliamentquestion": ("ParliamentQuestion",
        "MATCH (n:ParliamentQuestion) "
        "WHERE toLower(coalesce(n.subject,'')) CONTAINS toLower($q) "
        "   OR toLower(coalesce(n.member_name,'')) CONTAINS toLower($q) "
        "RETURN n.id AS id, n.subject AS name, null AS state, null AS party LIMIT $limit"),
    "vigilancecircular": ("VigilanceCircular",
        "MATCH (n:VigilanceCircular) "
        "WHERE toLower(coalesce(n.title,'')) CONTAINS toLower($q) "
        "   OR toLower(coalesce(n.subject,'')) CONTAINS toLower($q) "
        "RETURN n.id AS id, n.title AS name, null AS state, null AS party LIMIT $limit"),
    "icijentity": ("ICIJEntity",
        "MATCH (n:ICIJEntity) "
        "WHERE toLower(coalesce(n.name,'')) CONTAINS toLower($q) "
        "   OR toLower(coalesce(n.jurisdiction,'')) CONTAINS toLower($q) "
        "RETURN n.id AS id, n.name AS name, null AS state, null AS party LIMIT $limit"),
    "sanctionedentity": ("SanctionedEntity",
        "MATCH (n:SanctionedEntity) "
        "WHERE toLower(coalesce(n.name,'')) CONTAINS toLower($q) "
        "RETURN n.id AS id, n.name AS name, null AS state, null AS party LIMIT $limit"),
    "courtcase": ("CourtCase",
        "MATCH (n:CourtCase) "
        "WHERE toLower(coalesce(n.court_name,'')) CONTAINS toLower($q) "
        "   OR toLower(coalesce(n.state,'')) CONTAINS toLower($q) "
        "RETURN n.id AS id, n.court_name AS name, n.state AS state, null AS party LIMIT $limit"),
    "localbody": ("LocalBody",
        "MATCH (n:LocalBody) "
        "WHERE toLower(coalesce(n.name,'')) CONTAINS toLower($q) "
        "   OR toLower(coalesce(n.district,'')) CONTAINS toLower($q) "
        "RETURN n.id AS id, n.name AS name, n.state AS state, null AS party LIMIT $limit"),
}


@router.get("/search", response_model=SearchResponse)
def search_entities(
    q:                str           = Query(..., min_length=2),
    entity_type:      Optional[str] = Query(None),
    # BUG-1 FIX: renamed from `type` (which shadowed Python's built-in type())
    # to entity_type_param with alias="type" so the API contract is unchanged.
    entity_type_param:Optional[str] = Query(None, alias="type"),
    limit:            int           = Query(20, le=100),
    lang:             Optional[str] = Query("en"),
    driver=Depends(get_db),
):
    filter_type = (entity_type or entity_type_param or "all").lower().strip()
    logger.info(f"[Search] q='{q}' filter={filter_type} lang={lang} limit={limit}")

    results = []

    if filter_type in ("all", ""):
        try:
            with driver.session() as session:
                ft_rows = session.run(
                    """
                    CALL db.index.fulltext.queryNodes('globalSearch', $q)
                    YIELD node, score
                    RETURN node.id AS id,
                           labels(node)[0] AS label,
                           coalesce(node.name, node.title, node.ngo_name,
                                    node.company_name, node.subject) AS name,
                           node.state AS state,
                           node.party AS party,
                           node.source AS source,
                           score
                    ORDER BY score DESC LIMIT $limit
                    """,
                    q=q, limit=limit
                ).data()

            if ft_rows:
                for r in ft_rows:
                    label = r.get("label", "Unknown")
                    src = SOURCE_MAP.get(label, ("BharatGraph", "Knowledge Graph", "#"))
                    results.append(SearchResult(
                        entity_id=r["id"] or "",
                        entity_type=label,
                        name=r["name"] or "",
                        state=r.get("state"),
                        party=r.get("party"),
                        sources=[SourceDocument(
                            institution=src[0],
                            document_title=src[1],
                            url=src[2],
                        )],
                    ))
                return SearchResponse(
                    query=q, total=len(results),
                    results=results[:limit],
                    generated_at=datetime.now().isoformat(),
                )
        except Exception as ft_err:
            # BUG-1 FIX: was type(ft_err).__name__ — crashed because `type`
            # was shadowed by the query parameter. Now uses __class__.__name__.
            logger.debug(
                f"[Search] Full-text index unavailable, using label scan: "
                f"{ft_err.__class__.__name__}"
            )

    with driver.session() as session:
        if filter_type in ("all", ""):
            targets = list(LABEL_QUERIES.keys())
        else:
            normalized = filter_type.rstrip("s")
            targets = [k for k in LABEL_QUERIES if k.startswith(normalized)]
            if not targets:
                targets = list(LABEL_QUERIES.keys())

        per_label = max(10, (limit * 2) // max(len(targets), 1))

        for key in targets:
            label, cypher = LABEL_QUERIES[key]
            try:
                rows = session.run(cypher, q=q, limit=per_label).data()
                src  = SOURCE_MAP.get(label, ("BharatGraph", "Knowledge Graph", "#"))
                for r in rows:
                    if not r.get("id") or not r.get("name"):
                        continue
                    results.append(SearchResult(
                        entity_id=r["id"],
                        entity_type=label,
                        name=r["name"],
                        state=r.get("state"),
                        party=r.get("party"),
                        sources=[SourceDocument(
                            institution=src[0],
                            document_title=src[1],
                            url=src[2],
                        )],
                    ))
            except Exception as e:
                logger.warning(f"[Search] {label} query failed: {e}")

    ql = q.lower()
    results.sort(key=lambda r: (0 if r.name.lower().startswith(ql) else 1, r.name))

    return SearchResponse(
        query=q,
        total=len(results),
        results=results[:limit],
        generated_at=datetime.now().isoformat(),
    )
