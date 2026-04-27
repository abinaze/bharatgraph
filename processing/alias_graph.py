"""
BharatGraph - Alias Graph
Maps every known name variant of an entity to its canonical ID.
Loaded at startup and used during all entity lookups so that
"RAHUL KUMAR", "Rahul Kumar", and "R. Kumar" all resolve to one node.
Pure ASCII.
"""
import json
import os
from loguru import logger


class AliasGraph:
    """
    In-memory lookup: alias_name.lower() -> canonical_id

    Built from EntityResolverV2.build_alias_graph() output and
    persisted at data/processed/alias_graph.json.
    """

    DEFAULT_PATH = "data/processed/alias_graph.json"

    def __init__(self):
        self._graph = {}   # alias_lower -> canonical_id

    def load(self, path: str = None) -> int:
        """Load alias graph from disk. Returns number of entries loaded."""
        path = path or self.DEFAULT_PATH
        if not os.path.exists(path):
            logger.warning(
                f"[AliasGraph] File not found: {path}. "
                "Run pipeline first to build alias graph."
            )
            return 0
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._graph = json.load(f)
            logger.success(
                f"[AliasGraph] Loaded {len(self._graph)} aliases from {path}"
            )
            return len(self._graph)
        except Exception as e:
            logger.error(f"[AliasGraph] Load failed: {e}")
            return 0

    def save(self, path: str = None):
        """Persist current alias graph to disk."""
        path = path or self.DEFAULT_PATH
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._graph, f, indent=2, ensure_ascii=False)
        logger.success(
            f"[AliasGraph] Saved {len(self._graph)} aliases to {path}"
        )

    def resolve(self, name: str) -> str:
        """
        Resolve a name variant to its canonical ID.
        Returns the canonical ID if found, else empty string.
        """
        return self._graph.get(name.lower().strip(), "")

    def add(self, alias: str, canonical_id: str):
        """Add or update a single alias -> canonical_id mapping."""
        self._graph[alias.lower().strip()] = canonical_id

    def merge(self, other: dict):
        """Merge another {alias: canonical_id} dict into this graph."""
        normalised = {k.lower().strip(): v for k, v in other.items()}
        self._graph.update(normalised)
        logger.info(
            f"[AliasGraph] Merged {len(other)} entries. "
            f"Total: {len(self._graph)}"
        )

    def bulk_add(self, records: list, name_field: str,
                  canonical_id_field: str):
        """
        Add aliases from a list of records.
        Each record[name_field] becomes an alias for record[canonical_id_field].
        """
        added = 0
        for rec in records:
            name = str(rec.get(name_field, "")).strip()
            cid  = str(rec.get(canonical_id_field, "")).strip()
            if name and cid:
                self._graph[name.lower()] = cid
                added += 1
        logger.info(f"[AliasGraph] Bulk-added {added} aliases")

    def __len__(self) -> int:
        return len(self._graph)

    def __contains__(self, name: str) -> bool:
        return name.lower().strip() in self._graph

    def stats(self) -> dict:
        """Return basic statistics about the alias graph."""
        canonical_ids = set(self._graph.values())
        return {
            "total_aliases":        len(self._graph),
            "unique_canonical_ids": len(canonical_ids),
            "avg_aliases_per_id":   round(
                len(self._graph) / max(len(canonical_ids), 1), 2
            ),
        }
