import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from fastapi import APIRouter, Depends, Query
from loguru import logger

from api.models import GraphResponse, GraphNode, GraphEdge
from api.dependencies import get_db

router = APIRouter()


@router.get("/graph/connections/{entity_id}", response_model=GraphResponse)
def get_connections(
    entity_id: str,
    depth: int = Query(2, ge=1, le=3),
    driver=Depends(get_db),
):
    logger.info(f"[Graph] entity_id={entity_id} depth={depth}")

    nodes = {}
    edges = []

    with driver.session() as session:
        # Always load anchor node first — guarantees non-empty response
        anchor = session.run(
            "MATCH (n {id:$id}) RETURN n", id=entity_id
        ).single()

        if anchor and anchor.get("n"):
            n     = anchor["n"]
            nid   = n.get("id", entity_id)
            labs  = list(n.labels) if hasattr(n, "labels") else ["Unknown"]
            props = dict(n)
            nodes[nid] = GraphNode(
                id=nid,
                label=labs[0] if labs else "Unknown",
                name=props.get("name", props.get("title", nid)),
                properties={k: str(v) for k, v in props.items()
                            if k not in ("id", "name", "title")},
            )

        # BUG-09 FIX: Use explicit node/rel return instead of path object (avoids
        # Neo4j Python driver path API inconsistencies). Depth via param not f-string.
        depth_safe = min(max(int(depth), 1), 3)
        rows = session.run(
            """
            MATCH (start {id: $id})-[r*1..$depth]-(end)
            RETURN DISTINCT
                start.id AS src_id,
                labels(start)[0] AS src_label,
                coalesce(start.name, start.title, start.id) AS src_name,
                properties(start) AS src_props,
                [rel IN r | {
                    src: startNode(rel).id,
                    tgt: endNode(rel).id,
                    type: type(rel)
                }] AS rels,
                end.id AS end_id,
                labels(end)[0] AS end_label,
                coalesce(end.name, end.title, end.id) AS end_name,
                properties(end) AS end_props
            LIMIT 200
            """,
            id=entity_id, depth=depth_safe
        ).data()

        for row in rows:
            for nid, nlabel, nname, nprops in [
                (row.get("src_id"), row.get("src_label"), row.get("src_name"), row.get("src_props") or {}),
                (row.get("end_id"), row.get("end_label"), row.get("end_name"), row.get("end_props") or {}),
            ]:
                if nid and nid not in nodes:
                    nodes[nid] = GraphNode(
                        id=nid,
                        label=nlabel or "Unknown",
                        name=nname or nid,
                        properties={k: str(v) for k, v in nprops.items()
                                    if k not in ("id","name","title") and v is not None},
                    )
            for rel_step in (row.get("rels") or []):
                src   = rel_step.get("src", "")
                tgt   = rel_step.get("tgt", "")
                rtype = rel_step.get("type", "RELATED_TO")
                if src and tgt:
                    edges.append(GraphEdge(
                        source=src, target=tgt, relationship=rtype,
                        properties={},
                    ))

    return GraphResponse(
        entity_id=entity_id,
        depth=depth,
        nodes=list(nodes.values()),
        edges=edges,
        generated_at=datetime.now().isoformat(),
    )


@router.get("/graph/pattern/politician-contracts")
def politician_contracts_pattern(
    limit: int = Query(50, le=200),
    driver=Depends(get_db),
):
    with driver.session() as session:
        rows = session.run(
            """
            MATCH (p:Politician)-[:DIRECTOR_OF]->(c:Company)-[:WON_CONTRACT]->(ct:Contract)
            RETURN p.name AS politician, p.party AS party, p.state AS state,
                   c.name AS company, ct.order_id AS contract_id,
                   ct.amount_crore AS amount_crore, ct.buyer_org AS buyer,
                   ct.order_date AS order_date
            ORDER BY ct.amount_crore DESC LIMIT $limit
            """,
            limit=limit
        ).data()
    return {"pattern":"politician -> company -> contract",
            "total":len(rows),"results":rows,
            "generated_at":datetime.now().isoformat()}
