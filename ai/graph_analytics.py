import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from loguru import logger


class GraphAnalytics:

    def __init__(self, driver=None):
        self.driver = driver
        self._nx    = None
        self._load_networkx()

    def _load_networkx(self):
        try:
            import networkx as nx
            self._nx = nx
            logger.success(f"[GraphAnalytics] NetworkX {nx.__version__} loaded")
        except ImportError:
            logger.error("[GraphAnalytics] NetworkX not installed. Run: pip install networkx")
            raise

    def _fetch_graph_from_neo4j(self, entity_id: str = None,
                                  depth: int = 3) -> tuple:
        if not self.driver:
            return [], []

        with self.driver.session() as session:
            if entity_id:
                rows = session.run(
                    f"""
                    MATCH path = (start {{id: $id}})-[*1..{depth}]-(end)
                    RETURN path LIMIT 500
                    """,
                    id=entity_id
                ).data()
            else:
                rows = session.run(
                    """
                    MATCH (a)-[r]->(b)
                    RETURN a.id AS src, a.name AS src_name,
                           labels(a)[0] AS src_type,
                           type(r) AS rel,
                           b.id AS tgt, b.name AS tgt_name,
                           labels(b)[0] AS tgt_type
                    LIMIT 2000
                    """
                ).data()

        nodes = {}
        edges = []
        for row in rows:
            src = row.get("src", "")
            tgt = row.get("tgt", "")
            if src and tgt:
                nodes[src] = {
                    "name":  row.get("src_name", src),
                    "type":  row.get("src_type", "Unknown"),
                }
                nodes[tgt] = {
                    "name":  row.get("tgt_name", tgt),
                    "type":  row.get("tgt_type", "Unknown"),
                }
                edges.append((src, tgt, {"rel": row.get("rel", "")}))

        return list(nodes.items()), edges

    def _build_nx_graph(self, nodes: list, edges: list,
                         directed: bool = True):
        nx = self._nx
        G  = nx.DiGraph() if directed else nx.Graph()
        for node_id, attrs in nodes:
            G.add_node(node_id, **attrs)
        for src, tgt, attrs in edges:
            G.add_edge(src, tgt, **attrs)
        return G

    def compute_betweenness_centrality(self, nodes: list,
                                        edges: list) -> list:
        nx = self._nx
        G  = self._build_nx_graph(nodes, edges, directed=False)

        if G.number_of_nodes() < 3:
            logger.warning("[GraphAnalytics] Too few nodes for centrality")
            return []

        centrality = nx.betweenness_centrality(G, normalized=True)
        results = []
        for node_id, score in sorted(
            centrality.items(), key=lambda x: x[1], reverse=True
        )[:20]:
            attrs = G.nodes.get(node_id, {})
            results.append({
                "entity_id":            node_id,
                "name":                 attrs.get("name", node_id),
                "type":                 attrs.get("type", "Unknown"),
                "betweenness_centrality": round(score, 6),
                "interpretation": (
                    "High betweenness: entity acts as a key bridge "
                    "between institutional networks"
                    if score > 0.1 else
                    "Low betweenness: entity is not a primary network bridge"
                ),
            })

        logger.success(
            f"[GraphAnalytics] Betweenness computed for {len(centrality)} nodes. "
            f"Top: {results[0]['name']} ({results[0]['betweenness_centrality']:.4f})"
            if results else
            "[GraphAnalytics] Betweenness computed — no results"
        )
        return results

    def compute_pagerank(self, nodes: list, edges: list) -> list:
        nx = self._nx
        G  = self._build_nx_graph(nodes, edges, directed=True)

        if G.number_of_nodes() < 2:
            return []

        pagerank = nx.pagerank(G, alpha=0.85)
        results = []
        for node_id, score in sorted(
            pagerank.items(), key=lambda x: x[1], reverse=True
        )[:20]:
            attrs = G.nodes.get(node_id, {})
            results.append({
                "entity_id": node_id,
                "name":      attrs.get("name", node_id),
                "type":      attrs.get("type", "Unknown"),
                "pagerank":  round(score, 6),
            })

        logger.success(
            f"[GraphAnalytics] PageRank computed for {len(pagerank)} nodes"
        )
        return results

    def detect_communities(self, nodes: list, edges: list) -> list:
        nx  = self._nx
        G   = self._build_nx_graph(nodes, edges, directed=False)

        if G.number_of_nodes() < 4:
            return []

        try:
            from networkx.algorithms.community import greedy_modularity_communities
            communities = list(greedy_modularity_communities(G))
        except Exception:
            communities = list(nx.connected_components(G))

        results = []
        for i, community in enumerate(communities):
            if len(community) < 2:
                continue
            members = []
            for node_id in community:
                attrs = G.nodes.get(node_id, {})
                members.append({
                    "id":   node_id,
                    "name": attrs.get("name", node_id),
                    "type": attrs.get("type", "Unknown"),
                })
            results.append({
                "community_id":    i + 1,
                "size":            len(community),
                "members":         members,
                "interpretation": (
                    "Large community detected — may indicate a procurement "
                    "cluster or shared-director network warranting review"
                    if len(community) >= 5 else
                    "Small community — limited network cluster"
                ),
            })

        logger.success(
            f"[GraphAnalytics] {len(results)} communities detected"
        )
        return results

    def write_centrality_to_graph(self, results: list, metric: str):
        if not self.driver or not results:
            return
        with self.driver.session() as session:
            for r in results:
                session.run(
                    f"MATCH (n {{id: $id}}) SET n.{metric} = $score",
                    id=r["entity_id"],
                    score=r.get(metric, 0.0),
                )
        logger.success(
            f"[GraphAnalytics] Wrote {metric} scores to {len(results)} nodes"
        )

    def run_full_analysis(self, entity_id: str = None) -> dict:
        logger.info("[GraphAnalytics] Running full graph analysis")
        nodes, edges = self._fetch_graph_from_neo4j(entity_id)

        if not nodes:
            logger.warning("[GraphAnalytics] No graph data from Neo4j")
            return {"status": "no_data", "analyzed_at": datetime.now().isoformat()}

        betweenness  = self.compute_betweenness_centrality(nodes, edges)
        pagerank     = self.compute_pagerank(nodes, edges)
        communities  = self.detect_communities(nodes, edges)

        if self.driver:
            self.write_centrality_to_graph(betweenness, "betweenness_centrality")
            self.write_centrality_to_graph(pagerank, "pagerank")

        return {
            "node_count":      len(nodes),
            "edge_count":      len(edges),
            "top_betweenness": betweenness[:5],
            "top_pagerank":    pagerank[:5],
            "communities":     communities[:10],
            "analyzed_at":     datetime.now().isoformat(),
        }


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Graph Analytics Test")
    print("=" * 55)

    sample_nodes = [
        ("P001", {"name": "Politician A", "type": "Politician"}),
        ("P002", {"name": "Politician B", "type": "Politician"}),
        ("C001", {"name": "Company X",    "type": "Company"}),
        ("C002", {"name": "Company Y",    "type": "Company"}),
        ("C003", {"name": "Company Z",    "type": "Company"}),
        ("CT01", {"name": "Contract 1",   "type": "Contract"}),
        ("CT02", {"name": "Contract 2",   "type": "Contract"}),
        ("M001", {"name": "Ministry A",   "type": "Ministry"}),
    ]
    sample_edges = [
        ("P001", "C001", {"rel": "DIRECTOR_OF"}),
        ("P001", "C002", {"rel": "DIRECTOR_OF"}),
        ("P002", "C003", {"rel": "DIRECTOR_OF"}),
        ("C001", "CT01", {"rel": "WON_CONTRACT"}),
        ("C002", "CT01", {"rel": "WON_CONTRACT"}),
        ("C003", "CT02", {"rel": "WON_CONTRACT"}),
        ("M001", "CT01", {"rel": "AWARDED_BY"}),
        ("M001", "CT02", {"rel": "AWARDED_BY"}),
        ("P001", "P002", {"rel": "MEMBER_OF"}),
    ]

    analytics = GraphAnalytics(driver=None)

    print("\n  Betweenness Centrality:")
    bc = analytics.compute_betweenness_centrality(sample_nodes, sample_edges)
    for r in bc[:3]:
        print(f"    {r['name']:20s} {r['betweenness_centrality']:.4f}")

    print("\n  PageRank:")
    pr = analytics.compute_pagerank(sample_nodes, sample_edges)
    for r in pr[:3]:
        print(f"    {r['name']:20s} {r['pagerank']:.4f}")

    print("\n  Communities:")
    comms = analytics.detect_communities(sample_nodes, sample_edges)
    for c in comms:
        names = [m["name"] for m in c["members"]]
        print(f"    Community {c['community_id']}: {names}")

    print("\nDone!")
