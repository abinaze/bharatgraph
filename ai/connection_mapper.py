import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from loguru import logger


RELATIONSHIP_META = {
    "DIRECTOR_OF":        {"label": "director",        "strength": "strong",  "color": "#FF9933",
                           "why": "Registered as director in official MCA21 company filings.",
                           "source": "Ministry of Corporate Affairs — MCA21"},
    "WON_CONTRACT":       {"label": "contract",        "strength": "strong",  "color": "#138808",
                           "why": "Won a government procurement contract on the GeM portal.",
                           "source": "Government e-Marketplace — gem.gov.in"},
    "AWARDED_BY":         {"label": "awarded by",      "strength": "strong",  "color": "#000080",
                           "why": "Contract was awarded by this ministry or government department.",
                           "source": "Government e-Marketplace — gem.gov.in"},
    "FLAGS":              {"label": "audit flag",      "strength": "strong",  "color": "#DC3545",
                           "why": "Flagged in a CAG audit report for financial irregularity.",
                           "source": "Comptroller and Auditor General — cag.gov.in"},
    "AUDITS":             {"label": "audits",          "strength": "strong",  "color": "#DC3545",
                           "why": "CAG audit report covers the activities of this entity.",
                           "source": "Comptroller and Auditor General — cag.gov.in"},
    "MEMBER_OF":          {"label": "party member",   "strength": "medium",  "color": "#6F42C1",
                           "why": "Declared party membership in ECI affidavit filings.",
                           "source": "Election Commission of India — eci.gov.in"},
    "MENTIONED_IN":       {"label": "mentioned",       "strength": "weak",    "color": "#6C757D",
                           "why": "Entity name appears in this document or report.",
                           "source": "Public record — government document"},
    "ISSUED_BY":          {"label": "issued by",       "strength": "medium",  "color": "#17A2B8",
                           "why": "Official press release issued by this ministry.",
                           "source": "Press Information Bureau — pib.gov.in"},
    "CONTESTED_IN":       {"label": "contested in",   "strength": "medium",  "color": "#FFC107",
                           "why": "Contested an election in this constituency.",
                           "source": "Election Commission of India — eci.gov.in"},
    "ASSOCIATED_WITH":    {"label": "associated",      "strength": "weak",    "color": "#6C757D",
                           "why": "Structural association detected across multiple data sources.",
                           "source": "Cross-source entity resolution"},
}

SOURCE_LABELS = {
    "Company":           "Ministry of Corporate Affairs — MCA21",
    "Politician":        "Election Commission of India — MyNeta",
    "Contract":          "Government e-Marketplace — gem.gov.in",
    "AuditReport":       "Comptroller and Auditor General — cag.gov.in",
    "Ministry":          "Government of India Directory",
    "Party":             "Election Commission of India",
    "Scheme":            "NITI Aayog / Ministry Portal",
    "PressRelease":      "Press Information Bureau — pib.gov.in",
    "ElectoralBond":     "ECI Electoral Bond Disclosure",
    "RegulatoryOrder":   "SEBI — sebi.gov.in",
    "EnforcementAction": "Enforcement Directorate",
    "ICIJEntity":        "ICIJ Offshore Leaks Database",
    "SanctionedEntity":  "OpenSanctions Database",
    "CourtCase":         "eCourts — NJDG",
    "NGO":               "NGO Darpan — NITI Aayog",
    "Tender":            "Central Public Procurement Portal",
}


class ConnectionMapper:

    def __init__(self, driver=None):
        self.driver = driver

    def find_paths(self, entity_a: str, entity_b: str, max_hops: int = 5) -> dict:
        logger.info(f"[ConnectionMapper] Path: {entity_a} → {entity_b} (max {max_hops} hops)")

        if not self.driver:
            return {"status": "no_database", "paths": [], "path_count": 0}

        with self.driver.session() as session:
            rows = session.run(
                """
                MATCH path = shortestPath(
                  (a {id:$a})-[*1..$hops]-(b {id:$b})
                )
                RETURN [n IN nodes(path) | {
                    id: n.id,
                    name: coalesce(n.name, n.title, n.product, n.id),
                    label: labels(n)[0]
                }] AS nodes,
                       [r IN relationships(path) | type(r)] AS rels,
                       length(path) AS hops
                LIMIT 10
                """,
                a=entity_a, b=entity_b, hops=max_hops
            ).data()

        paths = []
        for row in rows:
            nodes = row.get("nodes", [])
            rels  = row.get("rels", [])
            hops  = row.get("hops", 0)

            steps = []
            for i, rel in enumerate(rels):
                meta = RELATIONSHIP_META.get(rel, {
                    "label": rel.lower(), "strength": "unknown",
                    "color": "#6C757D",
                    "why": f"Relationship type: {rel}",
                    "source": "Official government record"
                })
                steps.append({
                    "from":      nodes[i].get("name") or nodes[i].get("id"),
                    "from_id":   nodes[i].get("id"),
                    "from_type": nodes[i].get("label"),
                    "rel":       rel,
                    "rel_label": meta["label"],
                    "strength":  meta["strength"],
                    "color":     meta["color"],
                    "why":       meta["why"],
                    "source":    meta["source"],
                    "to":        nodes[i+1].get("name") or nodes[i+1].get("id") if i+1 < len(nodes) else "",
                    "to_id":     nodes[i+1].get("id") if i+1 < len(nodes) else "",
                    "to_type":   nodes[i+1].get("label") if i+1 < len(nodes) else "",
                })

            paths.append({
                "hops":        hops,
                "steps":       steps,
                "path_nodes":  [n.get("name") or n.get("id") for n in nodes],
                "summary":     self._path_summary(steps),
            })

        return {
            "entity_a": entity_a,
            "entity_b": entity_b,
            "path_count": len(paths),
            "paths": paths,
            "status": "found" if paths else "no_path",
            "searched_at": datetime.now().isoformat(),
        }

    def get_node_evidence(self, entity_id: str) -> dict:
        logger.info(f"[ConnectionMapper] Evidence for node {entity_id}")

        if not self.driver:
            return {"entity_id": entity_id, "edges": [], "status": "no_database"}

        with self.driver.session() as session:
            # Get all relationships
            rows = session.run(
                """
                MATCH (n {id:$id})-[r]-(m)
                RETURN type(r) AS rel,
                       labels(m)[0] AS node_type,
                       coalesce(m.name, m.title, m.product, m.item_desc, m.id) AS name,
                       m.id AS mid,
                       m.state AS state,
                       coalesce(m.amount_crore, m.total_assets, null) AS amount,
                       coalesce(m.order_date, toString(m.year), m.scraped_at, null) AS date,
                       m.source AS source_field
                ORDER BY rel
                LIMIT 40
                """,
                id=entity_id
            ).data()

            # Get entity info
            entity_row = session.run(
                """
                MATCH (n {id:$id})
                RETURN n.name AS name, labels(n)[0] AS label,
                       n.risk_score AS score, n.risk_level AS level,
                       n.state AS state, n.party AS party,
                       n.total_assets AS total_assets,
                       n.criminal_cases AS criminal_cases,
                       n.source AS source
                """,
                id=entity_id
            ).single()

        edges = []
        for row in rows:
            rel      = row.get("rel", "")
            meta     = RELATIONSHIP_META.get(rel, {
                "label": rel.lower(), "strength": "unknown",
                "color": "#6C757D",
                "why": f"Relationship detected: {rel}",
                "source": "Official government record"
            })
            node_type = row.get("node_type", "")

            # Build next investigation leads
            next_leads = self._next_leads(rel, row.get("name",""), row.get("mid",""), node_type)

            edges.append({
                "relationship":  rel,
                "rel_label":     meta["label"],
                "strength":      meta["strength"],
                "color":         meta["color"],
                "connected_to":  row.get("name"),
                "connected_id":  row.get("mid"),
                "node_type":     node_type,
                "state":         row.get("state"),
                "amount":        row.get("amount"),
                "date":          row.get("date"),
                "why":           meta["why"],
                "how":           "Structural link from official government record",
                "source":        meta["source"] or SOURCE_LABELS.get(node_type, "Official record"),
                "data_source":   row.get("source_field") or meta["source"],
                "confidence":    "HIGH" if meta["strength"] == "strong" else "MODERATE",
                "next_leads":    next_leads,
            })

        entity_info = {}
        if entity_row:
            entity_info = {
                "name":           entity_row["name"],
                "entity_type":    entity_row["label"],
                "risk_score":     entity_row["score"],
                "risk_level":     entity_row["level"],
                "state":          entity_row["state"],
                "party":          entity_row["party"],
                "total_assets":   entity_row["total_assets"],
                "criminal_cases": entity_row["criminal_cases"],
                "source":         entity_row["source"],
                "risk_factors":   self._derive_risk_factors(entity_row, edges),
            }

        return {
            "entity_id":   entity_id,
            "entity_info": entity_info,
            "edges":       edges,
            "edge_count":  len(edges),
            "status":      "found" if edges else "no_connections",
            "coverage_note": (
                "No connections found in current graph. "
                "Run POST /admin/seed or POST /admin/pipeline to load data."
            ) if not edges else None,
            "fetched_at": datetime.now().isoformat(),
        }

    def _next_leads(self, rel: str, name: str, mid: str, node_type: str) -> list:
        leads = []
        if rel == "DIRECTOR_OF":
            leads.append(f"Check all contracts won by {name}")
            leads.append(f"Find other directors of {name}")
        elif rel == "WON_CONTRACT":
            leads.append(f"Check the awarding ministry for {name}")
            leads.append(f"Look for similar contracts in same period")
        elif rel in ("FLAGS", "AUDITS"):
            leads.append(f"Read full audit report: {name}")
            leads.append(f"Find all entities flagged in same report")
        elif rel == "MEMBER_OF":
            leads.append(f"Find all politicians in {name}")
            leads.append(f"Check electoral bond donors to {name}")
        elif node_type == "EnforcementAction":
            leads.append(f"Check PMLA details for this action")
            leads.append(f"Find connected entities in the ED case")
        return leads[:3]

    def _derive_risk_factors(self, entity_row: dict, edges: list) -> list:
        factors = []
        if entity_row.get("criminal_cases") and int(entity_row["criminal_cases"] or 0) > 0:
            factors.append(f"{entity_row['criminal_cases']} declared criminal case(s) in ECI affidavit")
        strong_edges = [e for e in edges if e.get("strength") == "strong"]
        if len(strong_edges) >= 3:
            factors.append(f"{len(strong_edges)} high-strength connections to government contracts/audits")
        if any(e.get("relationship") in ("FLAGS","AUDITS") for e in edges):
            factors.append("Connected to CAG audit flags")
        if any(e.get("node_type") in ("EnforcementAction","SanctionedEntity") for e in edges):
            factors.append("Connected to enforcement actions or sanctions")
        return factors

    def _path_summary(self, steps: list) -> str:
        if not steps:
            return "Direct connection"
        parts = []
        for s in steps:
            parts.append(f"{s.get('from','')} →[{s.get('rel_label','')}]→")
        if steps:
            parts.append(steps[-1].get("to",""))
        return " ".join(parts)
