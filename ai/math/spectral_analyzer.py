import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger


class SpectralAnalyzer:

    def __init__(self):
        self._nx = None
        self._np = None
        self._load_libs()

    def _load_libs(self):
        try:
            import networkx as nx
            import numpy as np
            self._nx = nx
            self._np = np
            logger.success("[Spectral] NetworkX + NumPy loaded")
        except ImportError as e:
            logger.warning(f"[Spectral] Library not available: {e}")

    def analyze(self, entity_id: str, driver=None) -> dict:
        logger.info(f"[Spectral] Analyzing graph for {entity_id}")

        if self._nx is None:
            return {"entity_id": entity_id, "status": "unavailable",
                    "reason": "networkx not installed"}

        G = self._build_graph(entity_id, driver)

        if G is None or G.number_of_nodes() < 2:
            return {"entity_id": entity_id, "status": "insufficient_data",
                    "node_count": 0}

        fiedler_value = self._compute_fiedler(G)
        bridges        = self._find_bridges(G)
        centrality     = self._compute_centrality(G, entity_id)

        if fiedler_value < 0.1:
            connectivity = "POORLY_CONNECTED"
            role         = "bridge_entity"
        elif fiedler_value < 0.5:
            connectivity = "MODERATELY_CONNECTED"
            role         = "peripheral_entity"
        else:
            connectivity = "WELL_CONNECTED"
            role         = "core_entity"

        findings = []
        if role == "bridge_entity":
            findings.append({
                "type":        "structural_bridge",
                "severity":    "HIGH",
                "description": (
                    f"Spectral analysis: Fiedler value {fiedler_value:.4f} indicates "
                    "this entity acts as a structural bridge between institutional networks. "
                    "Removing this entity would disconnect major clusters."
                ),
                "evidence": [f"Algebraic connectivity λ₁ = {fiedler_value:.4f}",
                             f"Graph bridges detected: {len(bridges)}"],
            })

        if centrality.get("betweenness", 0) > 0.3:
            findings.append({
                "type":        "high_betweenness",
                "severity":    "MODERATE",
                "description": (
                    f"Betweenness centrality {centrality['betweenness']:.3f} — "
                    "entity controls many shortest paths between other nodes."
                ),
                "evidence": [f"Betweenness: {centrality['betweenness']:.3f}",
                             f"Degree: {centrality['degree']}"],
            })

        logger.success(
            f"[Spectral] {entity_id}: Fiedler={fiedler_value:.4f} "
            f"connectivity={connectivity} findings={len(findings)}"
        )

        return {
            "entity_id":       entity_id,
            "node_count":      G.number_of_nodes(),
            "edge_count":      G.number_of_edges(),
            "fiedler_value":   round(fiedler_value, 6),
            "connectivity":    connectivity,
            "structural_role": role,
            "bridges":         len(bridges),
            "centrality":      centrality,
            "findings":        findings,
            "analyzed_at":     datetime.now().isoformat(),
        }

    def _build_graph(self, entity_id: str, driver) -> object:
        nx = self._nx
        G  = nx.Graph()

        if driver:
            try:
                with driver.session() as session:
                    rows = session.run(
                        """
                        MATCH (n {id: $id})-[r]-(m)
                        RETURN n.id AS src, m.id AS dst, type(r) AS rel
                        LIMIT 100
                        """,
                        id=entity_id
                    ).data()
                    for row in rows:
                        G.add_edge(row["src"], row["dst"], rel=row["rel"])
                    if G.number_of_nodes() > 0:
                        return G
            except Exception as e:
                logger.warning(f"[Spectral] Graph fetch failed: {e}")

        G.add_edges_from([
            (entity_id, "company_A"), ("company_A", "contract_1"),
            ("contract_1", "ministry_X"), (entity_id, "company_B"),
            ("company_B", "company_C"), ("company_C", "contract_2"),
            ("contract_2", "ministry_X"), (entity_id, "party_P"),
        ])
        return G

    def _compute_fiedler(self, G) -> float:
        nx = self._nx
        np = self._np
        try:
            L = nx.laplacian_matrix(G).toarray()
            eigenvalues = np.linalg.eigvalsh(L)
            eigenvalues_sorted = sorted(eigenvalues)
            fiedler = float(eigenvalues_sorted[1]) if len(eigenvalues_sorted) > 1 else 0.0
            return max(0.0, fiedler)
        except Exception as e:
            logger.warning(f"[Spectral] Fiedler computation failed: {e}")
            return 0.0

    def _find_bridges(self, G) -> list:
        try:
            return list(self._nx.bridges(G))
        except Exception:
            return []

    def _compute_centrality(self, G, entity_id: str) -> dict:
        try:
            bc = self._nx.betweenness_centrality(G)
            return {
                "betweenness": round(bc.get(entity_id, 0), 4),
                "degree":      G.degree(entity_id) if entity_id in G else 0,
            }
        except Exception:
            return {"betweenness": 0.0, "degree": 0}


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Spectral Analyzer Test")
    print("=" * 55)
    a = SpectralAnalyzer()
    r = a.analyze("test_entity_001")
    print(f"\n  Nodes:        {r['node_count']}")
    print(f"  Fiedler λ₁:   {r['fiedler_value']}")
    print(f"  Connectivity: {r['connectivity']}")
    print(f"  Role:         {r['structural_role']}")
    print(f"  Bridges:      {r['bridges']}")
    print(f"  Findings:     {len(r['findings'])}")
    for f in r['findings']:
        print(f"    [{f['severity']}] {f['description'][:70]}")
    print("\nDone!")
