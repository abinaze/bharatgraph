import os, sys, hashlib, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, date
from loguru import logger

AUDIT_LOG = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "logs", "audit.jsonl")


def compute_daily_root(log_path: str = AUDIT_LOG) -> str:
    if not os.path.exists(log_path):
        return hashlib.sha256(b"empty").hexdigest()

    hashes = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                today = date.today().isoformat()
                if entry.get("ts", "").startswith(today):
                    hashes.append(entry.get("hash", ""))
            except Exception:
                continue

    if not hashes:
        return hashlib.sha256(b"no_entries_today").hexdigest()

    combined    = "|".join(hashes)
    root_hash   = hashlib.sha256(combined.encode()).hexdigest()
    logger.info(f"[AuditChain] Daily root hash: {root_hash[:16]}... ({len(hashes)} entries)")
    return root_hash


def store_root_hash(root_hash: str, driver) -> bool:
    if not driver:
        return False
    try:
        with driver.session() as session:
            session.run(
                """
                MERGE (a:AuditRoot {date: $date})
                SET a.root_hash = $hash,
                    a.computed_at = $ts,
                    a.entry_count = $count
                """,
                date=date.today().isoformat(),
                hash=root_hash,
                ts=datetime.now().isoformat(),
                count=0,
            )
        logger.success(f"[AuditChain] Root hash stored in Neo4j for {date.today()}")
        return True
    except Exception as e:
        logger.error(f"[AuditChain] Failed to store root hash: {e}")
        return False


def verify_chain(log_path: str = AUDIT_LOG) -> dict:
    if not os.path.exists(log_path):
        return {"valid": True, "entries": 0, "message": "No log file yet"}

    entries   = []
    broken_at = None

    with open(log_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                entry       = json.loads(line)
                stored_hash = entry.pop("hash", "")
                computed    = hashlib.sha256(
                    json.dumps(entry, separators=(",", ":")).encode()
                ).hexdigest()
                entry["hash"] = stored_hash
                if stored_hash != computed and i > 0:
                    broken_at = i
                    break
                entries.append(entry)
            except Exception:
                broken_at = i
                break

    valid = broken_at is None
    return {
        "valid":     valid,
        "entries":   len(entries),
        "broken_at": broken_at,
        "message":   "Chain intact" if valid else f"Chain broken at entry {broken_at}",
    }


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Audit Chain Test")
    print("=" * 55)
    root  = compute_daily_root()
    print(f"\n  Daily root hash: {root[:32]}...")
    chain = verify_chain()
    print(f"  Chain valid:     {chain['valid']}")
    print(f"  Entries:         {chain['entries']}")
    print(f"  Message:         {chain['message']}")
    print("\nDone!")
