import os
import sys
import hashlib
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from loguru import logger


class ReportHasher:

    def generate_hash(self, entity_id: str, generated_at: str,
                       data_snapshot: dict = None) -> str:
        content = f"{entity_id}|{generated_at}"
        if data_snapshot:
            snapshot_str = json.dumps(data_snapshot, sort_keys=True,
                                       ensure_ascii=False)
            content += f"|{snapshot_str}"
        report_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        logger.info(f"[ReportHasher] Hash: {report_hash[:16]}... for {entity_id}")
        return report_hash

    def verify_hash(self, entity_id: str, generated_at: str,
                     claimed_hash: str,
                     data_snapshot: dict = None) -> dict:
        computed = self.generate_hash(entity_id, generated_at, data_snapshot)
        is_valid = computed == claimed_hash
        return {
            "valid":         is_valid,
            "entity_id":     entity_id,
            "claimed_hash":  claimed_hash,
            "computed_hash": computed,
            "verified_at":   datetime.now().isoformat(),
            "status": (
                "VERIFIED — Report integrity confirmed. "
                "Hash matches original generation."
                if is_valid else
                "INVALID — Hash mismatch. Report may have been modified."
            ),
        }

    def store_hash(self, report_hash: str, entity_id: str,
                    generated_at: str, driver) -> bool:
        if not driver:
            return False
        try:
            with driver.session() as session:
                session.run(
                    """
                    MERGE (h:ReportHash {hash: $hash})
                    SET h.entity_id   = $entity_id,
                        h.generated_at = $generated_at,
                        h.stored_at   = $stored_at
                    """,
                    hash=report_hash,
                    entity_id=entity_id,
                    generated_at=generated_at,
                    stored_at=datetime.now().isoformat(),
                )
            logger.success(
                f"[ReportHasher] Stored hash {report_hash[:16]}... in Neo4j"
            )
            return True
        except Exception as e:
            logger.error(f"[ReportHasher] Failed to store hash: {e}")
            return False

    def lookup_hash(self, report_hash: str, driver) -> dict:
        if not driver:
            return {"found": False, "message": "No database connection"}
        try:
            with driver.session() as session:
                row = session.run(
                    """
                    MATCH (h:ReportHash {hash: $hash})
                    RETURN h.entity_id AS entity_id,
                           h.generated_at AS generated_at,
                           h.stored_at AS stored_at
                    """,
                    hash=report_hash
                ).single()
            if row:
                return {
                    "found":        True,
                    "entity_id":    row["entity_id"],
                    "generated_at": row["generated_at"],
                    "stored_at":    row["stored_at"],
                    "status":       "Hash found in BharatGraph registry",
                }
            return {"found": False, "status": "Hash not found in registry"}
        except Exception as e:
            return {"found": False, "error": str(e)}


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Report Hasher Test")
    print("=" * 55)

    hasher = ReportHasher()

    h1 = hasher.generate_hash("P001", "2026-04-01T10:00:00")
    h2 = hasher.generate_hash("P001", "2026-04-01T10:00:00")
    h3 = hasher.generate_hash("P002", "2026-04-01T10:00:00")

    print(f"\n  Hash 1: {h1}")
    print(f"  Hash 2: {h2}")
    print(f"  Stable: {h1 == h2}")
    print(f"  Unique: {h1 != h3}")
    print(f"  Length: {len(h1)} chars")

    result = hasher.verify_hash("P001", "2026-04-01T10:00:00", h1)
    print(f"\n  Verification (correct hash): {result['valid']}")
    print(f"  Status: {result['status']}")

    result2 = hasher.verify_hash("P001", "2026-04-01T10:00:00", "tampered_hash")
    print(f"\n  Verification (tampered hash): {result2['valid']}")
    print(f"  Status: {result2['status']}")

    print("\nDone!")
