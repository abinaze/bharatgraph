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
    _edge_seen = set()

    with driver.session() as session:
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

        # BUG-1 FIX: Neo4j does NOT allow query parameters inside
        # variable-length path patterns [r*1..$depth] -- the depth MUST be
        # baked into the Cypher string as a literal integer using f-string/str().
        # Passing depth as a parameter causes CypherSyntaxError on every call.
        depth_safe = min(max(int(depth), 1), 3)
        cypher = (
            "MATCH (start {id: $id})-[r*1.."
            + str(depth_safe)
            + "]-(end) "
            "RETURN DISTINCT "
            "start.id AS src_id, "
            "labels(start)[0] AS src_label, "
            "coalesce(start.name, start.title, start.id) AS src_name, "
            "properties(start) AS src_props, "
            "[rel IN r | { "
            "    src: startNode(rel).id, "
            "    tgt: endNode(rel).id, "
            "    type: type(rel) "
            "}] AS rels, "
            "end.id AS end_id, "
            "labels(end)[0] AS end_label, "
            "coalesce(end.name, end.title, end.id) AS end_name, "
            "properties(end) AS end_props "
            "LIMIT 200"
        )
        rows = session.run(cypher, id=entity_id).data()

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
                if src and tgt and isinstance(src, str) and isinstance(tgt, str):
                    edge_key = (src, tgt, rtype)
                    if edge_key not in _edge_seen:
                        _edge_seen.add(edge_key)
                        edges.append(GraphEdge(
                            source=src, target=tgt, relationship=rtype,
                            properties={},
                        ))

    return GraphResponse(
        entity_id=entity_id,
        depth=depth_safe,
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
    return {"pattern": "politician -> company -> contract",
            "total": len(rows), "results": rows,
            "generated_at": datetime.now().isoformat()}


# ── Phase 33: Graph Intelligence endpoints ───────────────────────────────────

@router.get("/graph/analytics/{entity_id}")
def entity_graph_analytics(
    entity_id: str,
    depth: int = Query(3, ge=1, le=4),
    driver=Depends(get_db),
):
    """
    Run full graph analytics for one entity:
    betweenness centrality, PageRank, and community detection
    on the entity local sub-graph (up to depth hops out).
    """
    logger.info(f"[GraphAnalytics] entity={entity_id[:8]} depth={depth}")
    try:
        from ai.graph_analytics import GraphAnalytics
        ga    = GraphAnalytics(driver=driver)
        nodes, edges = ga._fetch_graph_from_neo4j(entity_id=entity_id, depth=depth)
        if not nodes:
            return {
                "entity_id":   entity_id,
                "status":      "no_data",
                "note":        "Entity not found or graph has no connections at this depth",
                "analyzed_at": datetime.now().isoformat(),
            }
        betweenness = ga.compute_betweenness_centrality(nodes, edges)
        pagerank    = ga.compute_pagerank(nodes, edges)
        communities = ga.detect_communities(nodes, edges)
        return {
            "entity_id":      entity_id,
            "depth":          depth,
            "node_count":     len(nodes),
            "edge_count":     len(edges),
            "betweenness":    betweenness[:10],
            "pagerank":       pagerank[:10],
            "communities":    communities[:5],
            "analyzed_at":    datetime.now().isoformat(),
        }
    except ImportError:
        return {"status": "error", "detail": "networkx not installed"}
    except Exception as e:
        logger.error(f"[GraphAnalytics] entity={entity_id[:8]}: {type(e).__name__}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Analytics failed")


@router.get("/graph/centrality/betweenness")
def global_betweenness(
    limit: int = Query(20, ge=5, le=100),
    driver=Depends(get_db),
):
    """
    Top entities ranked by betweenness centrality across the entire graph.
    High betweenness = acts as a bridge between institutional networks.
    Expensive on large graphs -- cached by the caller for 10 minutes.
    """
    logger.info("[GraphAnalytics] global betweenness requested")
    try:
        from ai.graph_analytics import GraphAnalytics
        ga    = GraphAnalytics(driver=driver)
        nodes, edges = ga._fetch_graph_from_neo4j()
        if not nodes:
            return {"status": "no_data", "results": []}
        results = ga.compute_betweenness_centrality(nodes, edges)
        return {
            "metric":      "betweenness_centrality",
            "node_count":  len(nodes),
            "edge_count":  len(edges),
            "top":         results[:limit],
            "analyzed_at": datetime.now().isoformat(),
        }
    except ImportError:
        return {"status": "error", "detail": "networkx not installed"}
    except Exception as e:
        logger.error(f"[GraphAnalytics] betweenness error: {type(e).__name__}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Betweenness centrality failed")


@router.get("/graph/centrality/pagerank")
def global_pagerank(
    limit: int = Query(20, ge=5, le=100),
    driver=Depends(get_db),
):
    """
    Top entities ranked by PageRank across the entire graph.
    High PageRank = many high-influence entities point to this node.
    """
    logger.info("[GraphAnalytics] global pagerank requested")
    try:
        from ai.graph_analytics import GraphAnalytics
        ga    = GraphAnalytics(driver=driver)
        nodes, edges = ga._fetch_graph_from_neo4j()
        if not nodes:
            return {"status": "no_data", "results": []}
        results = ga.compute_pagerank(nodes, edges)
        return {
            "metric":      "pagerank",
            "node_count":  len(nodes),
            "edge_count":  len(edges),
            "top":         results[:limit],
            "analyzed_at": datetime.now().isoformat(),
        }
    except ImportError:
        return {"status": "error", "detail": "networkx not installed"}
    except Exception as e:
        logger.error(f"[GraphAnalytics] pagerank error: {type(e).__name__}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="PageRank failed")


@router.get("/graph/communities")
def global_communities(
    min_size: int = Query(3, ge=2, le=50),
    driver=Depends(get_db),
):
    """
    Detect institutional clusters (communities) in the full graph.
    Returns communities with >= min_size members.
    Large communities often indicate procurement clusters, shell company
    networks, or party-linked directorships warranting investigation.
    """
    logger.info("[GraphAnalytics] community detection requested")
    try:
        from ai.graph_analytics import GraphAnalytics
        ga    = GraphAnalytics(driver=driver)
        nodes, edges = ga._fetch_graph_from_neo4j()
        if not nodes:
            return {"status": "no_data", "communities": []}
        communities = ga.detect_communities(nodes, edges)
        filtered    = [c for c in communities if c["size"] >= min_size]
        return {
            "total_communities": len(communities),
            "shown":             len(filtered),
            "min_size":          min_size,
            "communities":       filtered,
            "analyzed_at":       datetime.now().isoformat(),
        }
    except ImportError:
        return {"status": "error", "detail": "networkx not installed"}
    except Exception as e:
        logger.error(f"[GraphAnalytics] communities error: {type(e).__name__}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Community detection failed")
