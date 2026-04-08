"""
BharatGraph - Cypher Query Library
Pre-built queries for corruption pattern detection.

Each query answers a real investigative question:
  Q: Which politicians are directors of companies that won contracts?
  Q: Which ministries have the most CAG audit flags?
  Q: Which companies won contracts repeatedly from the same ministry?
  Q: Show all entities linked to a named politician
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger


QUERIES = {

    # ── Core corruption pattern ───────────────────────────
    "politician_company_contracts": {
        "description": "Find politicians linked to companies that won govt contracts",
        "cypher": """
        MATCH (p:Politician)-[:DIRECTOR_OF]->(c:Company)-[:WON_CONTRACT]->(ct:Contract)
        RETURN p.name        AS politician,
               p.party       AS party,
               p.state       AS state,
               c.name        AS company,
               ct.order_id   AS contract_id,
               ct.amount_crore AS amount_crore,
               ct.buyer_org  AS buyer_org,
               ct.order_date AS order_date
        ORDER BY ct.amount_crore DESC
        LIMIT 50
        """,
        "risk_level": "HIGH",
    },

    # ── Repeated contract winners ─────────────────────────
    "repeated_contract_winners": {
        "description": "Companies that won multiple contracts - concentration risk",
        "cypher": """
        MATCH (c:Company)-[:WON_CONTRACT]->(ct:Contract)
        WITH c, count(ct) AS contract_count, sum(ct.amount_crore) AS total_crore
        WHERE contract_count >= 2
        RETURN c.name        AS company,
               contract_count,
               total_crore
        ORDER BY total_crore DESC
        LIMIT 20
        """,
        "risk_level": "MEDIUM",
    },

    # ── Ministry audit flags ──────────────────────────────
    "ministry_audit_flags": {
        "description": "Ministries most flagged by CAG audit reports",
        "cypher": """
        MATCH (a:AuditReport)-[:AUDITS]->(m:Ministry)
        WITH m, count(a) AS audit_count, sum(a.amount_crore) AS total_flagged
        RETURN m.name       AS ministry,
               audit_count,
               total_flagged AS total_crore_flagged
        ORDER BY total_crore_flagged DESC
        LIMIT 20
        """,
        "risk_level": "MEDIUM",
    },

    # ── Scheme irregularities ─────────────────────────────
    "scheme_irregularities": {
        "description": "Government schemes with largest CAG-flagged irregularities",
        "cypher": """
        MATCH (a:AuditReport)-[r:FLAGS]->(s:Scheme)
        WITH s, count(a) AS report_count, sum(r.amount_crore) AS total_crore
        RETURN s.name      AS scheme,
               report_count,
               total_crore
        ORDER BY total_crore DESC
        LIMIT 20
        """,
        "risk_level": "HIGH",
    },

    # ── Politicians with criminal cases ───────────────────
    "politicians_with_cases": {
        "description": "Politicians with declared criminal cases",
        "cypher": """
        MATCH (p:Politician)
        WHERE toInteger(p.criminal_cases) > 0
        RETURN p.name          AS name,
               p.party         AS party,
               p.state         AS state,
               p.criminal_cases AS criminal_cases,
               p.total_assets  AS total_assets
        ORDER BY toInteger(p.criminal_cases) DESC
        LIMIT 50
        """,
        "risk_level": "MEDIUM",
    },

    # ── Full profile: one politician ──────────────────────
    "politician_profile": {
        "description": "Full graph profile for a named politician",
        "cypher": """
        MATCH (p:Politician)
        WHERE toLower(p.name) CONTAINS toLower($name)
        OPTIONAL MATCH (p)-[:MEMBER_OF]->(party:Party)
        OPTIONAL MATCH (p)-[:DIRECTOR_OF]->(co:Company)
        OPTIONAL MATCH (co)-[:WON_CONTRACT]->(ct:Contract)
        RETURN p.name          AS politician,
               p.party         AS party,
               p.state         AS state,
               p.criminal_cases AS criminal_cases,
               p.total_assets  AS total_assets,
               collect(DISTINCT co.name)     AS companies,
               collect(DISTINCT ct.order_id) AS contracts,
               collect(DISTINCT ct.amount_crore) AS contract_amounts
        """,
        "risk_level": "INFO",
        "params": {"name": "politician name to search"},
    },

    # ── High value contracts ──────────────────────────────
    "high_value_contracts": {
        "description": "All contracts above threshold crore value",
        "cypher": """
        MATCH (c:Company)-[:WON_CONTRACT]->(ct:Contract)-[:AWARDED_BY]->(m:Ministry)
        WHERE ct.amount_crore >= $min_crore
        RETURN ct.order_id    AS order_id,
               c.name         AS seller,
               ct.amount_crore AS crore,
               m.name         AS ministry,
               ct.order_date  AS date
        ORDER BY ct.amount_crore DESC
        LIMIT 50
        """,
        "risk_level": "HIGH",
        "params": {"min_crore": 1.0},
    },

    # ── Node counts (health check) ────────────────────────
    "node_counts": {
        "description": "Count of all node types in the graph",
        "cypher": """
        MATCH (n)
        RETURN labels(n)[0] AS node_type, count(n) AS count
        ORDER BY count DESC
        """,
        "risk_level": "INFO",
    },

    # ── Relationship counts (health check) ────────────────
    "relationship_counts": {
        "description": "Count of all relationship types in the graph",
        "cypher": """
        MATCH ()-[r]->()
        RETURN type(r) AS relationship_type, count(r) AS count
        ORDER BY count DESC
        """,
        "risk_level": "INFO",
    },
}


class QueryRunner:
    """
    Runs pre-built Cypher queries against the Neo4j graph.
    """

    def __init__(self):
        self.driver = None
        self._connect()

    def _connect(self):
        try:
            from neo4j import GraphDatabase
            from dotenv import load_dotenv
            load_dotenv()
            uri  = os.getenv("NEO4J_URI", "")
            user = os.getenv("NEO4J_USER",     "neo4j")
            pwd  = os.getenv("NEO4J_PASSWORD", "")
            self.driver = GraphDatabase.driver(uri, auth=(user, pwd))
            self.driver.verify_connectivity()
            logger.success(f"[Queries] Connected to Neo4j")
        except Exception as e:
            logger.error(f"[Queries] Connection failed: {e}")
            raise

    def run(self, query_name: str, params: dict = None) -> list:
        """Run a named query and return results as list of dicts."""
        if query_name not in QUERIES:
            logger.error(f"[Queries] Unknown query: {query_name}")
            return []
        q = QUERIES[query_name]
        logger.info(f"[Queries] Running: {query_name} ({q['risk_level']})")
        try:
            with self.driver.session() as session:
                result = session.run(q["cypher"], params or {})
                rows = [dict(r) for r in result]
                logger.success(f"[Queries] {query_name}: {len(rows)} rows")
                return rows
        except Exception as e:
            logger.error(f"[Queries] {query_name} failed: {e}")
            return []

    def run_all_checks(self) -> dict:
        """Run all INFO-level checks and return summary."""
        results = {}
        results["node_counts"]         = self.run("node_counts")
        results["relationship_counts"] = self.run("relationship_counts")
        return results

    def close(self):
        if self.driver:
            self.driver.close()


def print_query_library():
    """Print all available queries."""
    print("=" * 55)
    print("  BharatGraph — Cypher Query Library")
    print("=" * 55)
    for name, q in QUERIES.items():
        risk  = q["risk_level"]
        emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "INFO": "🟢"}.get(risk, "⚪")
        print(f"\n  {emoji} {name}")
        print(f"     {q['description']}")
        if "params" in q:
            print(f"     Params: {q['params']}")
    print(f"\n  Total: {len(QUERIES)} queries")


if __name__ == "__main__":
    print_query_library()

    print("\n\nTesting Neo4j connection...")
    try:
        runner = QueryRunner()
        print("\nRunning health checks...")
        checks = runner.run_all_checks()

        print("\nNode counts:")
        for row in checks.get("node_counts", []):
            print(f"  ({row['node_type']}): {row['count']}")

        print("\nRelationship counts:")
        for row in checks.get("relationship_counts", []):
            print(f"  [{row['relationship_type']}]: {row['count']}")

        runner.close()
        print("\nAll queries ready.")
    except Exception as e:
        print(f"\nCould not connect: {e}")
        print("Check NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD in .env")
