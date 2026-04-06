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

        rows = session.run(
            f"""
            MATCH path = (start {{id: $id}})-[*1..{depth}]-(end)
            RETURN path LIMIT 200
            """,
            id=entity_id
        ).data()

        for row in rows:
            path = row.get("path", {})
            for node in path.get("nodes", []):
                nid   = node.get("id", str(id(node)))
                labs  = list(node.labels) if hasattr(node, "labels") else ["Unknown"]
                props = dict(node)
                if nid not in nodes:
                    nodes[nid] = GraphNode(
                        id=nid,
                        label=labs[0] if labs else "Unknown",
                        name=props.get("name", props.get("title", nid)),
                        properties={k: str(v) for k, v in props.items()
                                    if k not in ("id","name","title")},
                    )
            for rel in path.get("relationships", []):
                src   = rel.start_node.get("id","") if hasattr(rel,"start_node") else ""
                tgt   = rel.end_node.get("id","")   if hasattr(rel,"end_node")   else ""
                rtype = rel.type if hasattr(rel,"type") else "RELATED_TO"
                if src and tgt:
                    edges.append(GraphEdge(
                        source=src, target=tgt, relationship=rtype,
                        properties={k: str(v) for k, v in dict(rel).items()},
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
