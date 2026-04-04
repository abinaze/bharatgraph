import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from loguru import logger


LAYER_NAMES = [
    "direct_evidence",
    "relationship_expansion",
    "pattern_investigation",
    "timeline_investigation",
    "network_influence",
    "evidence_validation",
]


class DeepInvestigator:

    def __init__(self, driver=None):
        self.driver = driver

    def investigate(self, entity_id: str, entity_name: str = "") -> dict:
        logger.info(f"[DeepInvestigator] 6-layer analysis: {entity_name or entity_id}")

        if not self.driver:
            return {
                "entity_id":   entity_id,
                "entity_name": entity_name,
                "layers":      [],
                "total_items": 0,
                "status":      "no_database",
                "investigated_at": datetime.now().isoformat(),
            }

        layers = []
        with self.driver.session() as session:
            if not entity_name:
                row = session.run(
                    "MATCH (n {id:$id}) RETURN n.name AS name",
                    id=entity_id
                ).single()
                entity_name = (row["name"] if row else entity_id) or entity_id

            for i, fn in enumerate([
                lambda s: self._layer_1_direct(entity_id, s),
                lambda s: self._layer_2_expansion(entity_id, s),
                lambda s: self._layer_3_patterns(entity_id, s),
                lambda s: self._layer_4_timeline(entity_id, s),
                lambda s: self._layer_5_influence(entity_id, s),
                lambda s: self._layer_6_validation(entity_id, entity_name, s),
            ], 1):
                try:
                    result = fn(session)
                    layers.append(result)
                    logger.info(f"[DeepInvestigator] Layer {i}: {result.get('count',0)} items")
                except Exception as e:
                    logger.warning(f"[DeepInvestigator] Layer {i} failed: {e}")
                    layers.append({"layer": i, "name": LAYER_NAMES[i-1],
                                   "count": 0, "error": str(e)})

        total = sum(l.get("count", 0) for l in layers)
        logger.success(f"[DeepInvestigator] Complete: {total} items across 6 layers")

        return {
            "entity_id":       entity_id,
            "entity_name":     entity_name,
            "layer_count":     len(layers),
            "total_items":     total,
            "layers":          layers,
            "investigated_at": datetime.now().isoformat(),
        }

    def _layer_1_direct(self, entity_id: str, session) -> dict:
        rows = session.run(
            """
            MATCH (n {id:$id})-[r]-(m)
            RETURN type(r) AS rel, labels(m)[0] AS node_type,
                   m.name AS name, m.id AS mid
            LIMIT 50
            """,
            id=entity_id
        ).data()
        items = [{"type":"direct_relationship","relationship":r.get("rel"),
                  "connected_to":r.get("name"),"node_type":r.get("node_type"),
                  "node_id":r.get("mid"),
                  "why":"Directly linked in knowledge graph",
                  "how":"Graph traversal — single hop",
                  "confidence":"HIGH","source":"Neo4j graph database"}
                 for r in rows]
        return {"layer":1,"name":"Direct Evidence","count":len(items),"items":items}

    def _layer_2_expansion(self, entity_id: str, session) -> dict:
        rows = session.run(
            """
            MATCH (n {id:$id})-[:DIRECTOR_OF]->(:Company)<-[:DIRECTOR_OF]-(p)
            WHERE p.id <> $id
            RETURN p.name AS shared_person, p.id AS pid,
                   labels(p)[0] AS ptype
            LIMIT 20
            """,
            id=entity_id
        ).data()
        items = [{"type":"shared_directorship",
                  "connected_to":r.get("shared_person"),
                  "node_id":r.get("pid"),
                  "why":"Shares company directorship with target entity",
                  "how":"Two-hop graph traversal via shared company",
                  "confidence":"HIGH","source":"MCA21 Director Records"}
                 for r in rows]
        return {"layer":2,"name":"Relationship Expansion","count":len(items),"items":items}

    def _layer_3_patterns(self, entity_id: str, session) -> dict:
        rows = session.run(
            """
            MATCH (n {id:$id})-[:DIRECTOR_OF]->(c:Company)
                  -[:WON_CONTRACT]->(ct:Contract)
            WITH ct.buyer_org AS buyer, count(ct) AS cnt,
                 sum(ct.amount_crore) AS total
            WHERE cnt >= 2
            RETURN buyer, cnt, total
            ORDER BY cnt DESC LIMIT 10
            """,
            id=entity_id
        ).data()
        items = [{"type":"contract_concentration",
                  "buyer":r.get("buyer"),
                  "contract_count":r.get("cnt"),
                  "total_crore":r.get("total"),
                  "why":f"Repeated contracts ({r.get('cnt')}) from same buyer",
                  "how":"Pattern analysis — frequency count",
                  "confidence":"HIGH","source":"GeM Procurement Data"}
                 for r in rows]
        return {"layer":3,"name":"Pattern Investigation","count":len(items),"items":items}

    def _layer_4_timeline(self, entity_id: str, session) -> dict:
        rows = session.run(
            """
            MATCH (n {id:$id})-[:DIRECTOR_OF|WON_CONTRACT*1..2]->(ct:Contract)
            RETURN ct.order_date AS date, ct.amount_crore AS amount,
                   ct.buyer_org AS buyer, ct.order_id AS contract_id
            ORDER BY ct.order_date LIMIT 30
            """,
            id=entity_id
        ).data()
        items = [{"type":"timeline_event","date":r.get("date"),
                  "event":"Contract Awarded",
                  "amount_crore":r.get("amount"),
                  "buyer":r.get("buyer"),
                  "why":"Temporal sequence event in entity history",
                  "how":"Timeline reconstruction from contract dates",
                  "confidence":"HIGH","source":"GeM"}
                 for r in rows if r.get("date")]
        return {"layer":4,"name":"Timeline Investigation","count":len(items),"items":items}

    def _layer_5_influence(self, entity_id: str, session) -> dict:
        row = session.run(
            """
            MATCH (n {id:$id})
            RETURN n.betweenness_centrality AS bc, n.pagerank AS pr
            """,
            id=entity_id
        ).single()
        items = []
        if row:
            bc = row.get("bc") or 0
            if bc > 0.05:
                items.append({
                    "type":"network_gatekeeper",
                    "metric":"betweenness_centrality",
                    "value":round(bc, 4),
                    "why":f"Betweenness centrality {bc:.4f} — entity connects clusters",
                    "how":"NetworkX betweenness_centrality algorithm",
                    "confidence":"HIGH","source":"Graph Analytics",
                })
        return {"layer":5,"name":"Network Influence","count":len(items),"items":items}

    def _layer_6_validation(self, entity_id: str, entity_name: str,
                              session) -> dict:
        items = []
        row = session.run(
            "MATCH (n:Politician {id:$id}) RETURN n.state AS state",
            id=entity_id
        ).single()
        if row and row.get("state"):
            sebi = session.run(
                """
                MATCH (s:RegulatoryOrder)
                WHERE toLower(s.title) CONTAINS toLower($name)
                  AND s.state IS NOT NULL AND s.state <> $state
                RETURN s.state AS sebi_state, s.title AS title LIMIT 1
                """,
                name=entity_name, state=row["state"]
            ).single()
            if sebi:
                items.append({
                    "type":"conflicting_disclosure",
                    "why":"State differs between MCA and regulatory filing",
                    "how":"Cross-source contradiction detection",
                    "confidence":"MEDIUM","source":"MCA vs SEBI",
                })
        return {"layer":6,"name":"Evidence Validation","count":len(items),"items":items}


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph — Deep Investigator Test (offline)")
    print("=" * 55)
    d = DeepInvestigator(driver=None)
    r = d.investigate("test_001", "Test Entity")
    print(f"  Status: {r.get('status')}")
    print(f"  Layers: {r.get('layer_count', 0)}")
    print("\nDone!")
