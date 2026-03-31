import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from loguru import logger


class CircularOwnershipDetector:

    def __init__(self, driver=None):
        self.driver = driver
        try:
            import networkx as nx
            self._nx = nx
        except ImportError:
            logger.error("[CircularOwnership] NetworkX not installed")
            raise

    def _fetch_ownership_edges(self) -> list:
        if not self.driver:
            return []
        with self.driver.session() as session:
            rows = session.run(
                """
                MATCH (a:Company)-[r:OWNS|DIRECTOR_OF|SUBSIDIARY_OF]->(b:Company)
                RETURN a.id AS src, a.name AS src_name,
                       b.id AS tgt, b.name AS tgt_name,
                       type(r) AS rel
                LIMIT 2000
                """
            ).data()
        return rows

    def detect_cycles(self, ownership_edges: list = None) -> list:
        if ownership_edges is None:
            ownership_edges = self._fetch_ownership_edges()

        if not ownership_edges:
            logger.warning("[CircularOwnership] No ownership edges to analyse")
            return []

        nx = self._nx
        G  = nx.DiGraph()
        id_to_name = {}

        for edge in ownership_edges:
            src = edge.get("src") or edge.get("source", "")
            tgt = edge.get("tgt") or edge.get("target", "")
            if src and tgt:
                G.add_edge(src, tgt,
                           rel=edge.get("rel", "OWNS"))
                id_to_name[src] = edge.get("src_name", src)
                id_to_name[tgt] = edge.get("tgt_name", tgt)

        cycles_raw = list(nx.simple_cycles(G))

        if not cycles_raw:
            logger.info("[CircularOwnership] No circular ownership detected")
            return []

        results = []
        for cycle in cycles_raw:
            if len(cycle) < 2:
                continue
            members = [
                {"id": node_id, "name": id_to_name.get(node_id, node_id)}
                for node_id in cycle
            ]
            cycle_str = " -> ".join(
                id_to_name.get(n, n) for n in cycle
            ) + " -> " + id_to_name.get(cycle[0], cycle[0])

            results.append({
                "cycle_length":    len(cycle),
                "members":         members,
                "cycle_path":      cycle_str,
                "interpretation": (
                    f"Circular ownership structure detected involving "
                    f"{len(cycle)} entities. This structural pattern is "
                    "commonly used to obscure ultimate beneficial ownership. "
                    "This is an analytical indicator, not a legal finding."
                ),
                "detected_at": datetime.now().isoformat(),
            })

        logger.warning(
            f"[CircularOwnership] Detected {len(results)} circular "
            "ownership structure(s)"
        )
        return results


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Circular Ownership Detector Test")
    print("=" * 55)

    detector = CircularOwnershipDetector(driver=None)

    edges_with_cycle = [
        {"src": "C001", "src_name": "Alpha Corp",
         "tgt": "C002", "tgt_name": "Beta Ltd",    "rel": "OWNS"},
        {"src": "C002", "src_name": "Beta Ltd",
         "tgt": "C003", "tgt_name": "Gamma Pvt",   "rel": "OWNS"},
        {"src": "C003", "src_name": "Gamma Pvt",
         "tgt": "C001", "tgt_name": "Alpha Corp",  "rel": "OWNS"},
        {"src": "C004", "src_name": "Delta Inc",
         "tgt": "C005", "tgt_name": "Epsilon Ltd",  "rel": "OWNS"},
    ]

    print("\n  Test 1: Graph with a 3-node cycle")
    cycles = detector.detect_cycles(edges_with_cycle)
    print(f"  Cycles found: {len(cycles)}")
    for c in cycles:
        print(f"    Path:   {c['cycle_path']}")
        print(f"    Length: {c['cycle_length']}")

    edges_no_cycle = [
        {"src": "C001", "src_name": "Alpha Corp",
         "tgt": "C002", "tgt_name": "Beta Ltd",   "rel": "OWNS"},
        {"src": "C002", "src_name": "Beta Ltd",
         "tgt": "C003", "tgt_name": "Gamma Pvt",  "rel": "OWNS"},
    ]

    print("\n  Test 2: Graph with no cycle")
    cycles2 = detector.detect_cycles(edges_no_cycle)
    print(f"  Cycles found: {len(cycles2)}")

    print("\nDone!")
