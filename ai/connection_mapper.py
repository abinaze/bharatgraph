import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from loguru import logger


RELATIONSHIP_LABELS = {
    "DIRECTOR_OF":    {"label":"director","strength":"strong","color":"#FF9933"},
    "WON_CONTRACT":   {"label":"contract","strength":"strong","color":"#138808"},
    "AWARDED_BY":     {"label":"awarded_by","strength":"strong","color":"#000080"},
    "FLAGS":          {"label":"audit_flag","strength":"strong","color":"#DC3545"},
    "MEMBER_OF":      {"label":"party","strength":"medium","color":"#6F42C1"},
    "AUDITS":         {"label":"audits","strength":"strong","color":"#DC3545"},
    "MENTIONED_IN":   {"label":"mentioned","strength":"weak","color":"#6C757D"},
}


class ConnectionMapper:

    def __init__(self, driver=None):
        self.driver = driver

    def find_paths(self, entity_a: str, entity_b: str,
                   max_hops: int = 5) -> dict:
        logger.info(f"[ConnectionMapper] {entity_a} → {entity_b} (max {max_hops} hops)")

        if not self.driver:
            return {"status":"no_database","paths":[],"path_count":0}

        with self.driver.session() as session:
            rows = session.run(
                """
                MATCH path = shortestPath(
                  (a {id:$a})-[*1..5]-(b {id:$b})
                )
                RETURN [n IN nodes(path) | {id:n.id, name:n.name,
                        label:labels(n)[0]}] AS nodes,
                       [r IN relationships(path) | type(r)] AS rels,
                       length(path) AS hops
                LIMIT 10
                """,
                a=entity_a, b=entity_b
            ).data()

        paths = []
        for row in rows:
            nodes = row.get("nodes", [])
            rels  = row.get("rels", [])
            hops  = row.get("hops", 0)

            steps = []
            for i, rel in enumerate(rels):
                rel_meta = RELATIONSHIP_LABELS.get(rel, {
                    "label": rel.lower(), "strength":"unknown","color":"#6C757D"
                })
                steps.append({
                    "from":        nodes[i].get("name") or nodes[i].get("id"),
                    "from_id":     nodes[i].get("id"),
                    "from_type":   nodes[i].get("label"),
                    "relationship":rel,
                    "rel_label":   rel_meta["label"],
                    "strength":    rel_meta["strength"],
                    "color":       rel_meta["color"],
                    "to":          nodes[i+1].get("name") or nodes[i+1].get("id"),
                    "to_id":       nodes[i+1].get("id"),
                    "to_type":     nodes[i+1].get("label"),
                    "why":         self._explain_relationship(rel),
                    "how":         "Graph shortest path algorithm (Neo4j)",
                    "source":      self._get_source(rel),
                })

            confidence = "HIGH" if hops <= 2 else "MEDIUM" if hops <= 3 else "LOW"

            paths.append({
                "hops":         hops,
                "confidence":   confidence,
                "steps":        steps,
                "path_summary": " → ".join(
                    n.get("name") or n.get("id","?") for n in nodes
                ),
            })

        logger.success(f"[ConnectionMapper] Found {len(paths)} paths")

        return {
            "entity_a":    entity_a,
            "entity_b":    entity_b,
            "path_count":  len(paths),
            "paths":       paths,
            "mapped_at":   datetime.now().isoformat(),
        }

    def get_node_evidence(self, entity_id: str) -> dict:
        logger.info(f"[ConnectionMapper] Evidence for node {entity_id}")

        if not self.driver:
            return {"entity_id": entity_id, "edges": [], "status": "no_database"}

        with self.driver.session() as session:
            rows = session.run(
                """
                MATCH (n {id:$id})-[r]-(m)
                RETURN type(r) AS rel, labels(m)[0] AS node_type,
                       m.name AS name, m.id AS mid,
                       m.state AS state
                LIMIT 30
                """,
                id=entity_id
            ).data()
            entity_row = session.run(
                "MATCH (n {id:$id}) RETURN n.name AS name, labels(n)[0] AS label, "
                "n.risk_score AS score, n.risk_level AS level, n.state AS state,"
                "n.party AS party",
                id=entity_id
            ).single()

        edges = []
        for row in rows:
            rel      = row.get("rel","")
            rel_meta = RELATIONSHIP_LABELS.get(rel, {
                "label":rel.lower(),"strength":"unknown","color":"#6C757D"
            })
            edges.append({
                "relationship": rel,
                "rel_label":    rel_meta["label"],
                "strength":     rel_meta["strength"],
                "color":        rel_meta["color"],
                "connected_to": row.get("name"),
                "connected_id": row.get("mid"),
                "node_type":    row.get("node_type"),
                "why":          self._explain_relationship(rel),
                "how":          "Official government record",
                "source":       self._get_source(rel),
                "next_leads":   self._suggest_leads(rel, row.get("node_type","")),
            })

        entity_info = {}
        if entity_row:
            entity_info = {
                "name":       entity_row.get("name"),
                "label":      entity_row.get("label"),
                "risk_score": entity_row.get("score"),
                "risk_level": entity_row.get("level"),
                "state":      entity_row.get("state"),
                "party":      entity_row.get("party"),
            }

        return {
            "entity_id":   entity_id,
            "entity_info": entity_info,
            "edge_count":  len(edges),
            "edges":       edges,
            "fetched_at":  datetime.now().isoformat(),
        }

    def _explain_relationship(self, rel: str) -> str:
        explanations = {
            "DIRECTOR_OF":  "Entity holds directorship in this company per MCA21 filings.",
            "WON_CONTRACT": "Company received government contract via GeM procurement.",
            "AWARDED_BY":   "Contract was awarded by this ministry/department.",
            "FLAGS":        "CAG audit report flagged this scheme or department.",
            "MEMBER_OF":    "Entity is a registered member of this political party.",
            "AUDITS":       "CAG conducted audit of this ministry.",
            "MENTIONED_IN": "Entity is mentioned in this document.",
        }
        return explanations.get(rel, f"Relationship type: {rel}")

    def _get_source(self, rel: str) -> str:
        sources = {
            "DIRECTOR_OF":  "Ministry of Corporate Affairs — MCA21",
            "WON_CONTRACT": "Government e-Marketplace (GeM)",
            "AWARDED_BY":   "Government e-Marketplace (GeM)",
            "FLAGS":        "Comptroller and Auditor General (CAG)",
            "MEMBER_OF":    "Election Commission of India",
            "AUDITS":       "Comptroller and Auditor General (CAG)",
        }
        return sources.get(rel, "BharatGraph Knowledge Graph")

    def _suggest_leads(self, rel: str, node_type: str) -> list:
        leads = {
            "DIRECTOR_OF":  ["Check other companies this director controls",
                             "Look for contracts from ministries this entity oversees"],
            "WON_CONTRACT": ["Check if company was incorporated recently",
                             "Compare contract value vs company paid-up capital"],
            "FLAGS":        ["Read full CAG report for specific irregularity amount",
                             "Check if irregularity led to prosecution"],
            "MEMBER_OF":    ["Check donation records from this party",
                             "Check policy changes benefiting entity after joining party"],
        }
        return leads.get(rel, ["Expand graph one more hop", "Check timeline alignment"])
