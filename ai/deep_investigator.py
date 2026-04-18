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

LAYER_DESCRIPTIONS = {
    "direct_evidence": "All relationships directly connected to this entity in the graph.",
    "relationship_expansion": "One-hop neighbours — entities connected through this entity.",
    "pattern_investigation": "Structural patterns: circular ownership, shell indicators, procurement anomalies.",
    "timeline_investigation": "Temporal patterns: contract awards near elections, entity formation dates.",
    "network_influence": "Centrality and bridge-node analysis within the local subgraph.",
    "evidence_validation": "Cross-source confirmation: how many independent sources agree on each finding.",
}


class DeepInvestigator:

    def __init__(self, driver=None):
        self.driver = driver

    def investigate(self, entity_id: str, entity_name: str = "") -> dict:
        logger.info(f"[DeepInvestigator] 6-layer analysis: {entity_name or entity_id}")

        if not self.driver:
            return self._offline_response(entity_id, entity_name)

        layers = []
        with self.driver.session() as session:
            # Resolve name if not given
            if not entity_name:
                row = session.run(
                    "MATCH (n {id:$id}) RETURN n.name AS name, labels(n)[0] AS label",
                    id=entity_id
                ).single()
                entity_name = (row["name"] if row else entity_id) or entity_id
                entity_label = (row["label"] if row else "Unknown") or "Unknown"
            else:
                row = session.run(
                    "MATCH (n {id:$id}) RETURN labels(n)[0] AS label", id=entity_id
                ).single()
                entity_label = (row["label"] if row else "Unknown") or "Unknown"

            # BUG-04 FIX: default-argument capture prevents lambda closure over loop var
            layer_fns = [
                (1, lambda s, _id=entity_id: self._layer_1_direct(_id, s)),
                (2, lambda s, _id=entity_id: self._layer_2_expansion(_id, s)),
                (3, lambda s, _id=entity_id: self._layer_3_patterns(_id, s)),
                (4, lambda s, _id=entity_id: self._layer_4_timeline(_id, s)),
                (5, lambda s, _id=entity_id: self._layer_5_influence(_id, s)),
                (6, lambda s, _id=entity_id, _nm=entity_name: self._layer_6_validation(_id, _nm, s)),
            ]
            for i, fn in layer_fns:
                try:
                    result = fn(session)
                    result["description"] = LAYER_DESCRIPTIONS.get(result.get("name",""), "")
                    layers.append(result)
                    logger.info(f"[DeepInvestigator] Layer {i}: {result.get('count',0)} items")
                except Exception as e:
                    logger.warning(f"[DeepInvestigator] Layer {i} failed: {e}")
                    layers.append({
                        "layer": i,
                        "name": LAYER_NAMES[i-1],
                        "count": 0,
                        "items": [],
                        "description": LAYER_DESCRIPTIONS.get(LAYER_NAMES[i-1],""),
                        "error": str(e),
                        "status": "layer_error"
                    })

        total = sum(l.get("count", 0) for l in layers)
        logger.success(f"[DeepInvestigator] Complete: {total} items across 6 layers")

        # Build confidence assessment
        confidence = self._assess_confidence(layers, total)

        return {
            "entity_id":       entity_id,
            "entity_name":     entity_name,
            "entity_type":     entity_label,
            "layer_count":     len(layers),
            "total_items":     total,
            "layers":          layers,
            "confidence":      confidence["score"],
            "confidence_level": confidence["level"],
            "confidence_reason": confidence["reason"],
            "investigation_status": "complete" if total > 0 else "no_data",
            "data_coverage_note": (
                "Investigation complete. Results reflect data currently loaded in the graph database. "
                "Run /admin/pipeline to ingest fresh data from all 21 sources."
            ) if total == 0 else None,
            "investigated_at": datetime.now().isoformat(),
        }

    def _assess_confidence(self, layers: list, total: int) -> dict:
        """Assess overall investigation confidence."""
        if total == 0:
            return {
                "score": 0,
                "level": "INSUFFICIENT_DATA",
                "reason": "No graph data found for this entity. Seed data or run pipeline to ingest records."
            }
        
        layer_counts = [l.get("count", 0) for l in layers]
        layers_with_data = sum(1 for c in layer_counts if c > 0)
        
        if layers_with_data >= 4:
            return {"score": 85, "level": "HIGH", "reason": f"{layers_with_data}/6 investigation layers returned data."}
        elif layers_with_data >= 2:
            return {"score": 55, "level": "MODERATE", "reason": f"{layers_with_data}/6 investigation layers returned data."}
        else:
            return {"score": 25, "level": "LOW", "reason": f"Only {layers_with_data}/6 investigation layers returned data. More data sources needed."}

    def _layer_1_direct(self, entity_id: str, session) -> dict:
        rows = session.run(
            """
            MATCH (n {id:$id})-[r]-(m)
            RETURN type(r) AS rel, labels(m)[0] AS node_type,
                   coalesce(m.name, m.title, m.product, m.id) AS name,
                   m.id AS mid, m.state AS state,
                   coalesce(m.amount_crore, m.total_assets, 0) AS amount
            LIMIT 50
            """,
            id=entity_id
        ).data()

        items = []
        for row in rows:
            items.append({
                "relationship": row.get("rel"),
                "connected_entity": row.get("name"),
                "connected_id": row.get("mid"),
                "entity_type": row.get("node_type"),
                "state": row.get("state"),
                "amount": row.get("amount"),
                "significance": self._rate_significance(row.get("rel"), row.get("amount")),
            })

        return {
            "layer": 1,
            "name": "direct_evidence",
            "count": len(items),
            "items": items,
        }

    def _layer_2_expansion(self, entity_id: str, session) -> dict:
        rows = session.run(
            """
            MATCH (n {id:$id})-[r1]-(m)-[r2]-(o)
            WHERE o.id <> $id
            RETURN type(r1) AS rel1, labels(m)[0] AS via_type,
                   coalesce(m.name,m.title,m.id) AS via_name,
                   type(r2) AS rel2, labels(o)[0] AS node_type,
                   coalesce(o.name,o.title,o.id) AS name,
                   o.id AS oid
            LIMIT 40
            """,
            id=entity_id
        ).data()

        items = []
        seen = set()
        for row in rows:
            key = row.get("oid","")
            if key in seen: continue
            seen.add(key)
            items.append({
                "path": f"{row.get('via_name')} ({row.get('rel2')}) →",
                "connected_entity": row.get("name"),
                "connected_id": row.get("oid"),
                "entity_type": row.get("node_type"),
                "via": row.get("via_name"),
                "via_type": row.get("via_type"),
                "hops": 2,
            })

        return {
            "layer": 2,
            "name": "relationship_expansion",
            "count": len(items),
            "items": items,
        }

    def _layer_3_patterns(self, entity_id: str, session) -> dict:
        findings = []

        # Pattern 1: Company with multiple directors that won contracts
        rows = session.run(
            """
            MATCH (n {id:$id})-[:DIRECTOR_OF]->(c:Company)-[:WON_CONTRACT]->(ct:Contract)
            RETURN c.name AS company, count(ct) AS contract_count,
                   sum(coalesce(ct.amount_crore,0)) AS total_value
            ORDER BY total_value DESC LIMIT 10
            """, id=entity_id
        ).data()
        for row in rows:
            findings.append({
                "pattern": "DIRECTOR_CONTRACT_LINK",
                "description": f"Director of {row.get('company')} which won {row.get('contract_count')} contract(s) worth ₹{row.get('total_value',0):.1f} Cr",
                "severity": "HIGH" if row.get("total_value",0) > 10 else "MODERATE",
            })

        # Pattern 2: Audit flags on connected schemes
        rows = session.run(
            """
            MATCH (n {id:$id})-[*1..2]-(a:AuditReport)
            RETURN a.title AS title, a.year AS year, a.amount_crore AS amount LIMIT 5
            """, id=entity_id
        ).data()
        for row in rows:
            findings.append({
                "pattern": "AUDIT_PROXIMITY",
                "description": f"CAG audit report '{row.get('title','')}' ({row.get('year','')}) within 2 hops",
                "severity": "MODERATE",
            })

        # Pattern 3: Electoral bond connections
        rows = session.run(
            """
            MATCH (n {id:$id})-[*1..2]-(e:ElectoralBond)
            RETURN e.donor_name AS donor, e.amount AS amount, e.party AS party LIMIT 5
            """, id=entity_id
        ).data()
        for row in rows:
            findings.append({
                "pattern": "ELECTORAL_BOND_PROXIMITY",
                "description": f"Electoral bond donor proximity: {row.get('donor','')} → {row.get('party','')} ₹{row.get('amount',0)} Cr",
                "severity": "MODERATE",
            })

        return {
            "layer": 3,
            "name": "pattern_investigation",
            "count": len(findings),
            "items": findings,
        }

    def _layer_4_timeline(self, entity_id: str, session) -> dict:
        events = []

        # Timeline events from multiple sources
        rows = session.run(
            """
            MATCH (n {id:$id})-[:DIRECTOR_OF|WON_CONTRACT|FLAGS|MENTIONED_IN|AUDITS*1..2]-(m)
            WHERE m.order_date IS NOT NULL OR m.year IS NOT NULL OR m.scraped_at IS NOT NULL
            RETURN coalesce(m.name,m.title,m.id) AS name,
                   labels(m)[0] AS type,
                   coalesce(m.order_date, toString(m.year), m.scraped_at) AS date,
                   coalesce(m.amount_crore, 0) AS amount
            ORDER BY date DESC LIMIT 20
            """, id=entity_id
        ).data()

        for row in rows:
            events.append({
                "date": row.get("date","Unknown"),
                "entity": row.get("name"),
                "entity_type": row.get("type"),
                "amount": row.get("amount"),
                "event_type": "TIMELINE_EVENT",
            })

        return {
            "layer": 4,
            "name": "timeline_investigation",
            "count": len(events),
            "items": events,
        }

    def _layer_5_influence(self, entity_id: str, session) -> dict:
        metrics = []

        # Degree centrality
        degree_row = session.run(
            "MATCH (n {id:$id})-[r]-() RETURN count(r) AS degree",
            id=entity_id
        ).single()
        degree = degree_row["degree"] if degree_row else 0

        metrics.append({
            "metric": "degree_centrality",
            "value": degree,
            "description": f"Connected to {degree} other nodes in the graph.",
            "significance": "HIGH" if degree > 20 else "MODERATE" if degree > 5 else "LOW",
        })

        # Check if this entity is a bridge (connected to otherwise unconnected clusters)
        bridge_rows = session.run(
            """
            MATCH (n {id:$id})-[]-(m)
            WITH n, collect(DISTINCT labels(m)[0]) AS connected_types
            RETURN connected_types, size(connected_types) AS type_diversity
            """, id=entity_id
        ).single()

        if bridge_rows:
            types = bridge_rows["connected_types"] or []
            diversity = bridge_rows["type_diversity"] or 0
            if diversity >= 3:
                metrics.append({
                    "metric": "bridge_indicator",
                    "value": diversity,
                    "description": f"Connected to {diversity} different node types: {', '.join(types)}. Possible bridge entity.",
                    "significance": "HIGH",
                })

        return {
            "layer": 5,
            "name": "network_influence",
            "count": len(metrics),
            "items": metrics,
        }

    def _layer_6_validation(self, entity_id: str, entity_name: str, session) -> dict:
        validations = []

        # Count how many independent sources mention this entity
        source_rows = session.run(
            """
            MATCH (n {id:$id})-[]-(m)
            RETURN DISTINCT coalesce(m.source, m.data_source, 'unknown') AS source
            LIMIT 20
            """, id=entity_id
        ).data()

        sources = [r["source"] for r in source_rows if r["source"] != "unknown"]
        if sources:
            validations.append({
                "validation": "SOURCE_DIVERSITY",
                "sources": sources,
                "count": len(sources),
                "description": f"Found in {len(sources)} independent data source(s): {', '.join(set(sources)[:5])}",
                "confidence": "HIGH" if len(sources) >= 3 else "MODERATE" if len(sources) == 2 else "LOW",
            })

        # Cross-reference: check if name appears in press releases
        pr_rows = session.run(
            """
            MATCH (p:PressRelease)
            WHERE toLower(p.title) CONTAINS toLower($name)
               OR toLower(coalesce(p.content,'')) CONTAINS toLower($name)
            RETURN p.title AS title LIMIT 3
            """, name=entity_name
        ).data()

        if pr_rows:
            validations.append({
                "validation": "PRESS_RELEASE_MENTION",
                "count": len(pr_rows),
                "description": f"Named in {len(pr_rows)} official PIB press release(s)",
                "confidence": "MODERATE",
            })

        return {
            "layer": 6,
            "name": "evidence_validation",
            "count": len(validations),
            "items": validations,
        }

    def _rate_significance(self, relationship: str, amount) -> str:
        if relationship in ("WON_CONTRACT", "DIRECTOR_OF", "FLAGS", "AUDITS"):
            if amount and float(amount) > 10:
                return "HIGH"
            return "MODERATE"
        return "LOW"

    def _offline_response(self, entity_id: str, entity_name: str) -> dict:
        return {
            "entity_id":   entity_id,
            "entity_name": entity_name or entity_id,
            "layers":      [],
            "total_items": 0,
            "confidence":  0,
            "confidence_level": "NO_DATABASE",
            "investigation_status": "offline",
            "data_coverage_note": "Database not connected. Configure NEO4J_URI in environment secrets.",
            "investigated_at": datetime.now().isoformat(),
        }
