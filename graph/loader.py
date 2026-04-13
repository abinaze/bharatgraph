"""
BharatGraph - Neo4j Graph Loader
Loads cleaned + resolved data from Phase 2 pipeline into Neo4j.

What this does:
  1. Connects to Neo4j AuraDB (free tier)
  2. Creates constraints and indexes (from schema.py)
  3. Loads each entity type as nodes
  4. Creates relationships between connected entities
  5. Reports stats: nodes created, relationships created

Usage:
    python -m graph.loader
    python -m graph.loader --dry-run  (shows what would be loaded)
"""

import os
import sys
import json
import hashlib
import argparse
from datetime import datetime
from loguru import logger

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.schema import SETUP_QUERIES, NODE_SCHEMAS


def make_id(*parts) -> str:
    """Create a stable ID by hashing multiple string parts."""
    combined = "|".join(str(p).lower().strip() for p in parts)
    return hashlib.md5(combined.encode()).hexdigest()[:16]


class GraphLoader:
    """
    Loads BharatGraph data into Neo4j.
    Handles connection, node creation, and relationship creation.
    """

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.driver  = None
        self.stats   = {
            "nodes_created":   0,
            "nodes_merged":    0,
            "rels_created":    0,
            "errors":          0,
        }
        if dry_run:
            logger.info("[Loader] DRY RUN mode - no data written to Neo4j")
        else:
            self._connect()

    def _connect(self):
        """Connect to Neo4j AuraDB using credentials from .env"""
        try:
            from neo4j import GraphDatabase
            from dotenv import load_dotenv
            load_dotenv()

            uri  = os.getenv("NEO4J_URI", "")
            user = os.getenv("NEO4J_USER",     "neo4j")
            pwd  = os.getenv("NEO4J_PASSWORD", "")

            if not pwd:
                logger.error("[Loader] NEO4J_PASSWORD not set in .env")
                raise ValueError("NEO4J_PASSWORD missing")

            self.driver = GraphDatabase.driver(uri, auth=(user, pwd))
            self.driver.verify_connectivity()
            logger.success(f"[Loader] Connected to Neo4j: {uri[:40]}...")

        except ImportError:
            logger.error("[Loader] neo4j package not installed. Run: pip install neo4j")
            raise
        except Exception as e:
            logger.error(f"[Loader] Connection failed: {e}")
            raise

    def setup_schema(self):
        """Create constraints and indexes defined in schema.py"""
        if self.dry_run:
            logger.info(f"[Loader] DRY RUN: would run {len(SETUP_QUERIES)} setup queries")
            return
        with self.driver.session() as session:
            # Try fulltext index (silent fail if already exists or unsupported)
            try:
                session.run(
                    "CALL db.index.fulltext.createNodeIndex("
                    "'globalSearch',"
                    "['Politician','Company','Contract','AuditReport',"
                    " 'Scheme','Ministry','Party','PressRelease'],"
                    "['name','title','aliases','item_desc','product','buyer_org',"
                    " 'cin','ministry','summary','seller_name']"
                    ")"
                )
            except Exception as e:
                logger.debug(f"[Loader] Full-text index note: {e}")

            for query in SETUP_QUERIES:
                try:
                    session.run(query)
                except Exception as e:
                    logger.debug(f"[Loader] Schema query skipped (may exist): {e}")
        logger.success("[Loader] Schema constraints and indexes ready")

    def _run(self, query: str, params: dict = None):
        """Execute a single Cypher query."""
        if self.dry_run:
            logger.debug(f"[Loader] DRY RUN query: {query[:80]}...")
            return None
        try:
            with self.driver.session() as session:
                result = session.run(query, params or {})
                return result
        except Exception as e:
            logger.error(f"[Loader] Query failed: {e}\nQuery: {query[:100]}")
            self.stats["errors"] += 1
            return None

    # ── Node loaders ──────────────────────────────────────

    def load_politicians(self, records: list) -> int:
        """Load politician records as (Politician) nodes."""
        count = 0
        for r in records:
            name = r.get("name", "").strip()
            if not name:
                continue
            node_id = make_id(name, r.get("state", ""), r.get("source_election", ""))
            query = """
            MERGE (p:Politician {id: $id})
            SET p.name           = $name,
                p.name_raw       = $name_raw,
                p.party          = $party,
                p.state          = $state,
                p.election       = $election,
                p.total_assets   = $total_assets,
                p.liabilities    = $liabilities,
                p.criminal_cases = $criminal_cases,
                p.education      = $education,
                p.source         = $source,
                p.scraped_at     = $scraped_at
            """
            params = {
                "id":            node_id,
                "name":          name,
                "name_raw":      r.get("name_raw", name),
                "party":         r.get("party", ""),
                "state":         r.get("state", ""),
                "election":      r.get("source_election", ""),
                "total_assets":  str(r.get("total_assets", "")),
                "liabilities":   str(r.get("liabilities", "")),
                "criminal_cases":str(r.get("criminal_case_count", "0")),
                "education":     r.get("education", ""),
                "source":        r.get("_source", "myneta"),
                "scraped_at":    r.get("scraped_at", datetime.now().isoformat()),
            }
            self._run(query, params)
            count += 1

            # Create Party node + MEMBER_OF relationship
            party = r.get("party", "").strip()
            if party:
                self._create_party_and_link(node_id, party)

        logger.success(f"[Loader] Politicians loaded: {count}")
        self.stats["nodes_created"] += count
        return count

    def _create_party_and_link(self, politician_id: str, party_name: str):
        """Create Party node and link politician to it."""
        party_id = make_id(party_name)
        query = """
        MERGE (party:Party {id: $party_id})
        SET party.name = $party_name
        WITH party
        MATCH (p:Politician {id: $pol_id})
        MERGE (p)-[:MEMBER_OF]->(party)
        """
        self._run(query, {
            "party_id": party_id,
            "party_name": party_name,
            "pol_id": politician_id,
        })

    def load_companies(self, records: list) -> int:
        """Load company records as (Company) nodes."""
        count = 0
        for r in records:
            name = r.get("name", "").strip()
            if not name:
                continue
            node_id = r.get("cin", make_id(name, r.get("state", "")))
            query = """
            MERGE (c:Company {id: $id})
            SET c.name              = $name,
                c.name_raw          = $name_raw,
                c.cin               = $cin,
                c.status            = $status,
                c.state             = $state,
                c.registration_date = $reg_date,
                c.company_class     = $company_class,
                c.source            = $source,
                c.scraped_at        = $scraped_at
            """
            params = {
                "id":           node_id,
                "name":         name,
                "name_raw":     r.get("name_raw", name),
                "cin":          r.get("cin", ""),
                "status":       r.get("status", ""),
                "state":        r.get("state", ""),
                "reg_date":     r.get("registration_date", ""),
                "company_class":r.get("company_class", ""),
                "source":       r.get("_source", "mca"),
                "scraped_at":   r.get("scraped_at", datetime.now().isoformat()),
            }
            self._run(query, params)
            count += 1

        logger.success(f"[Loader] Companies loaded: {count}")
        self.stats["nodes_created"] += count
        return count

    def load_contracts(self, records: list) -> int:
        """Load GeM contract records as (Contract) nodes + relationships."""
        count = 0
        for r in records:
            order_id = r.get("order_id", "").strip()
            seller   = r.get("seller_name", r.get("seller_name_raw","")).strip()
            if not order_id:
                continue
            node_id = make_id(order_id)
            # Create Contract node
            query = """
            MERGE (c:Contract {id: $id})
            SET c.order_id     = $order_id,
                c.seller_name  = $seller,
                c.buyer_org    = $buyer,
                c.product      = $product,
                c.amount_crore = $amount,
                c.order_date   = $date,
                c.state        = $state,
                c.source       = $source,
                c.scraped_at   = $scraped_at
            """
            params = {
                "id":         node_id,
                "order_id":   order_id,
                "seller":     seller,
                "buyer":      r.get("buyer_org", ""),
                "product":    r.get("product", ""),
                "amount":     float(r.get("amount_crore", 0) or 0),
                "date":       r.get("order_date", ""),
                "state":      r.get("state", ""),
                "source":     r.get("_source", "gem"),
                "scraped_at": r.get("scraped_at", datetime.now().isoformat()),
            }
            self._run(query, params)
            count += 1

            # Link seller company to this contract
            if seller:
                self._link_company_to_contract(seller, node_id,
                                                float(r.get("amount_crore", 0) or 0))

            # Link contract to ministry
            buyer = r.get("buyer_org", "").strip()
            if buyer:
                self._link_contract_to_ministry(node_id, buyer)

        logger.success(f"[Loader] Contracts loaded: {count}")
        self.stats["nodes_created"] += count
        return count

    def _link_company_to_contract(self, seller_name: str,
                                   contract_id: str, amount: float):
        """Create WON_CONTRACT relationship from Company to Contract."""
        company_id = make_id(seller_name)
        query = """
        MERGE (co:Company {id: $co_id})
        SET co.name = $seller_name
        WITH co
        MATCH (c:Contract {id: $contract_id})
        MERGE (co)-[r:WON_CONTRACT]->(c)
        SET r.amount_crore = $amount
        """
        self._run(query, {
            "co_id":       company_id,
            "seller_name": seller_name,
            "contract_id": contract_id,
            "amount":      amount,
        })
        self.stats["rels_created"] += 1

    def _link_contract_to_ministry(self, contract_id: str, ministry_name: str):
        """Create AWARDED_BY relationship from Contract to Ministry."""
        ministry_id = make_id(ministry_name)
        query = """
        MERGE (m:Ministry {id: $m_id})
        SET m.name = $m_name
        WITH m
        MATCH (c:Contract {id: $contract_id})
        MERGE (c)-[:AWARDED_BY]->(m)
        """
        self._run(query, {
            "m_id":        ministry_id,
            "m_name":      ministry_name,
            "contract_id": contract_id,
        })
        self.stats["rels_created"] += 1

    def load_audit_reports(self, records: list) -> int:
        """Load CAG audit report records as (AuditReport) nodes."""
        count = 0
        for r in records:
            title = r.get("title", "").strip()
            if not title:
                continue
            node_id = make_id(title, r.get("url", ""))
            query = """
            MERGE (a:AuditReport {id: $id})
            SET a.title             = $title,
                a.url               = $url,
                a.year              = $year,
                a.state             = $state,
                a.scheme            = $scheme,
                a.amount_crore      = $amount,
                a.irregularity_type = $irr_type,
                a.finding           = $finding,
                a.alert_keywords    = $keywords,
                a.source            = $source,
                a.scraped_at        = $scraped_at
            """
            params = {
                "id":         node_id,
                "title":      title,
                "url":        r.get("url", ""),
                "year":       str(r.get("year", "")),
                "state":      r.get("state", ""),
                "scheme":     r.get("scheme", ""),
                "amount":     float(r.get("amount_crore", 0) or 0),
                "irr_type":   r.get("irregularity_type", ""),
                "finding":    r.get("finding", ""),
                "keywords":   str(r.get("alert_keywords", [])),
                "source":     r.get("_source", "cag"),
                "scraped_at": r.get("scraped_at", datetime.now().isoformat()),
            }
            self._run(query, params)
            count += 1

            # Link to scheme if present
            scheme = r.get("scheme", "").strip()
            if scheme:
                self._link_audit_to_scheme(node_id, scheme,
                                            float(r.get("amount_crore", 0) or 0))

        logger.success(f"[Loader] Audit reports loaded: {count}")
        self.stats["nodes_created"] += count
        return count

    def _link_audit_to_scheme(self, audit_id: str, scheme_name: str,
                               amount: float):
        """Create FLAGS relationship from AuditReport to Scheme."""
        scheme_id = make_id(scheme_name)
        query = """
        MERGE (s:Scheme {id: $s_id})
        SET s.name = $s_name
        WITH s
        MATCH (a:AuditReport {id: $audit_id})
        MERGE (a)-[r:FLAGS]->(s)
        SET r.amount_crore = $amount
        """
        self._run(query, {
            "s_id":     scheme_id,
            "s_name":   scheme_name,
            "audit_id": audit_id,
            "amount":   amount,
        })
        self.stats["rels_created"] += 1

    def load_press_releases(self, records: list) -> int:
        """Load PIB press release records as (PressRelease) nodes."""
        count = 0
        for r in records:
            title = r.get("title", "").strip()
            if not title:
                continue
            node_id = make_id(title, r.get("link", ""))
            query = """
            MERGE (pr:PressRelease {id: $id})
            SET pr.title          = $title,
                pr.link           = $link,
                pr.published      = $published,
                pr.alert_keywords = $keywords,
                pr.source         = $source,
                pr.scraped_at     = $scraped_at
            """
            params = {
                "id":         node_id,
                "title":      title,
                "link":       r.get("link", ""),
                "published":  r.get("published", ""),
                "keywords":   str(r.get("alert_keywords", [])),
                "source":     r.get("_source", "pib"),
                "scraped_at": r.get("scraped_at", datetime.now().isoformat()),
            }
            self._run(query, params)
            count += 1

        logger.success(f"[Loader] Press releases loaded: {count}")
        self.stats["nodes_created"] += count
        return count

    def load_politician_company_links(self, matches: list) -> int:
        """
        Create DIRECTOR_OF relationships for politician-company matches.
        These are the CORE corruption-detection links.
        """
        count = 0
        for match in matches:
            pol_name = match.get("name_a", "").strip()
            co_name  = match.get("name_b", "").strip()
            score    = match.get("score", 0.0)
            if not pol_name or not co_name:
                continue
            pol_id = make_id(pol_name)
            co_id  = make_id(co_name)
            query = """
            MERGE (p:Politician {id: $pol_id})
            SET p.name = $pol_name
            MERGE (c:Company {id: $co_id})
            SET c.name = $co_name
            MERGE (p)-[r:DIRECTOR_OF]->(c)
            SET r.confidence  = $score,
                r.source      = 'entity_resolution',
                r.detected_at = $now
            """
            self._run(query, {
                "pol_id":   pol_id,
                "pol_name": pol_name,
                "co_id":    co_id,
                "co_name":  co_name,
                "score":    score,
                "now":      datetime.now().isoformat(),
            })
            count += 1
            self.stats["rels_created"] += 1

        if count > 0:
            logger.warning(f"[Loader] DIRECTOR_OF links created: {count}")
        else:
            logger.info("[Loader] No politician-company links to load")
        return count

    def load_from_pipeline_output(self, filepath: str) -> dict:
        """
        Load everything from a pipeline JSON output file.
        This is the main entry point.
        """
        logger.info(f"[Loader] Loading from: {filepath}")
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        raw   = data.get("raw",   {})
        links = data.get("links", [])

        self.setup_schema()

        results = {}
        if raw.get("myneta"):
            results["politicians"]     = self.load_politicians(raw["myneta"])
        if raw.get("mca"):
            results["companies"]       = self.load_companies(raw["mca"])
        if raw.get("gem"):
            results["contracts"]       = self.load_contracts(raw["gem"])
        if raw.get("cag"):
            results["audit_reports"]   = self.load_audit_reports(raw["cag"])
        if raw.get("pib"):
            results["press_releases"]  = self.load_press_releases(raw["pib"])
        if links:
            results["director_of_links"] = self.load_politician_company_links(links)

        logger.success(f"[Loader] Load complete. Stats: {self.stats}")
        return {**results, "stats": self.stats}

    def close(self):
        if self.driver:
            self.driver.close()
            logger.info("[Loader] Neo4j connection closed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BharatGraph Graph Loader")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be loaded without writing to Neo4j")
    parser.add_argument("--file", type=str, default=None,
                        help="Path to pipeline output JSON file")
    args = parser.parse_args()

    print("=" * 55)
    print("BharatGraph - Graph Loader")
    print("=" * 55)

    loader = GraphLoader(dry_run=args.dry_run)

    if args.file:
        results = loader.load_from_pipeline_output(args.file)
    else:
        # Find latest pipeline output
        import glob
        files = sorted(glob.glob("data/processed/pipeline_*.json"))
        if files:
            latest = files[-1]
            print(f"\nLoading latest pipeline output: {latest}")
            results = loader.load_from_pipeline_output(latest)
        else:
            print("\nNo pipeline output found.")
            print("Run first: python -m processing.pipeline --scrapers cag,gem,pib")
            results = {}

    loader.close()

    print(f"\n{'='*55}")
    print("LOAD SUMMARY")
    print(f"{'='*55}")
    s = loader.stats
    print(f"  Nodes created:    {s['nodes_created']}")
    print(f"  Nodes merged:     {s['nodes_merged']}")
    print(f"  Relationships:    {s['rels_created']}")
    print(f"  Errors:           {s['errors']}")
    if args.dry_run:
        print("\n  (DRY RUN - nothing was written to Neo4j)")
    print(f"{'='*55}")
