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
            # Try fulltext index — silent fail if already exists
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
                logger.info("[Loader] Full-text index created or verified")
            except Exception as e:
                logger.debug(f"[Loader] Full-text index note: {e}")

            # Run all constraint/index setup queries inside the same session
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
                "amount":     float(r.get("amount_crore") or (r.get("amount_inr",0)/1e7) or 0),
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
                "amount":     float(r.get("amount_crore") or (r.get("amount_inr",0)/1e7) or 0),
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
        BUG-17 FIX: was using make_id(name) which doesn't match canonical IDs
        created by load_politicians() (which uses make_id(name, state, election)).
        Fix: MATCH by name using toLower() to find existing nodes, only MERGE the
        relationship. If no existing node found, create one with name-only ID as
        fallback so the edge is never silently lost.
        """
        count = 0
        for match in matches:
            pol_name = match.get("name_a", match.get("politician_name", "")).strip()
            co_name  = match.get("name_b", match.get("company_name", "")).strip()
            score    = match.get("score", 0.0)
            if not pol_name or not co_name:
                continue

            # BUG-17 FIX: match by name (case-insensitive) to find the canonical node,
            # fall back to make_id(name) only if not found in graph yet.
            query = """
            MERGE (p:Politician {id: coalesce(
                (MATCH (x:Politician) WHERE toLower(x.name) = toLower($pol_name) RETURN x.id LIMIT 1)[0],
                $pol_id_fallback
            )})
            SET p.name = coalesce(p.name, $pol_name)
            MERGE (c:Company {id: coalesce(
                (MATCH (x:Company) WHERE toLower(x.name) = toLower($co_name) RETURN x.id LIMIT 1)[0],
                $co_id_fallback
            )})
            SET c.name = coalesce(c.name, $co_name)
            MERGE (p)-[r:DIRECTOR_OF]->(c)
            SET r.confidence  = $score,
                r.source      = 'entity_resolution',
                r.detected_at = $now
            """
            # Simpler, more reliable approach using two separate lookups
            link_query = """
            OPTIONAL MATCH (existing_p:Politician)
            WHERE toLower(existing_p.name) = toLower($pol_name)
            WITH coalesce(existing_p.id, $pol_id_fallback) AS pol_id
            MERGE (p:Politician {id: pol_id})
            SET p.name = coalesce(p.name, $pol_name)
            WITH p
            OPTIONAL MATCH (existing_c:Company)
            WHERE toLower(existing_c.name) = toLower($co_name)
            WITH p, coalesce(existing_c.id, $co_id_fallback) AS co_id
            MERGE (c:Company {id: co_id})
            SET c.name = coalesce(c.name, $co_name)
            MERGE (p)-[r:DIRECTOR_OF]->(c)
            SET r.confidence  = $score,
                r.source      = 'entity_resolution',
                r.detected_at = $now
            """
            try:
                self._run(link_query, {
                    "pol_name":        pol_name,
                    "pol_id_fallback": make_id(pol_name),
                    "co_name":         co_name,
                    "co_id_fallback":  make_id(co_name),
                    "score":           score,
                    "now":             datetime.now().isoformat(),
                })
                count += 1
                self.stats["rels_created"] += 1
            except Exception as e:
                logger.warning(f"[Loader] DIRECTOR_OF link {pol_name}→{co_name} failed: {e}")

        logger.info(f"[Loader] DIRECTOR_OF links created/updated: {count}")
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
        if raw.get("sebi"):
            results["regulatory_orders"]    = self.load_regulatory_orders(raw["sebi"])
        if raw.get("ed"):
            results["enforcement_actions"]  = self.load_enforcement_actions(raw["ed"])
        if raw.get("electoral_bond"):
            results["electoral_bonds"]      = self.load_electoral_bonds(raw["electoral_bond"])
        if raw.get("ibbi"):
            results["insolvency_orders"]    = self.load_insolvency_orders(raw["ibbi"])
        if raw.get("ngo_darpan"):
            results["ngos"]                 = self.load_ngos(raw["ngo_darpan"])
        if raw.get("cppp"):
            results["tenders"]              = self.load_tenders(raw["cppp"])
        if raw.get("loksabha"):
            results["parliament_questions"] = self.load_parliament_questions(raw["loksabha"])
        if raw.get("cvc"):
            results["vigilance_circulars"]  = self.load_vigilance_circulars(raw["cvc"])


        logger.success(f"[Loader] Load complete. Stats: {self.stats}")
        return {**results, "stats": self.stats}


    # ── Phase 28: 8 new dataset loaders ──────────────────────────────────────

    def load_regulatory_orders(self, records: list) -> int:
        """SEBI enforcement orders → RegulatoryOrder nodes."""
        count = 0
        for r in records:
            title = (r.get("title") or "").strip()
            if not title: continue
            node_id = make_id(title)
            try:
                self._run("""
                    MERGE (n:RegulatoryOrder {id:$id})
                    SET n.title=$title, n.url=$url, n.order_type=$order_type,
                        n.entity_name=$entity_name, n.violation=$violation,
                        n.source=$source, n.dataset="sebi", n.scraped_at=$scraped_at
                """, id=node_id, title=title, url=r.get("url",""),
                   order_type=r.get("order_type",""),
                   entity_name=r.get("entity_name",r.get("accused","")),
                   violation=r.get("violation",""), source=r.get("source","SEBI"),
                   scraped_at=r.get("scraped_at",""))
                count += 1
            except Exception as e:
                logger.warning(f"[Loader] RegulatoryOrder failed: {e}")
        self.stats["regulatory_orders"] = count
        logger.success(f"[Loader] Loaded {count} SEBI regulatory orders")
        return count

    def load_enforcement_actions(self, records: list) -> int:
        """ED enforcement actions → EnforcementAction nodes."""
        count = 0
        for r in records:
            title = (r.get("title") or "").strip()
            if not title: continue
            node_id = make_id(title)
            try:
                self._run("""
                    MERGE (n:EnforcementAction {id:$id})
                    SET n.title=$title, n.url=$url, n.date=$date,
                        n.amount_crore=$amount_crore, n.case_type=$case_type,
                        n.accused=$accused, n.source=$source,
                        n.dataset="ed", n.scraped_at=$scraped_at
                """, id=node_id, title=title, url=r.get("url",""),
                   date=r.get("date",""),
                   amount_crore=float(r.get("amount_crore",0) or 0),
                   case_type=r.get("case_type",""), accused=r.get("accused",""),
                   source=r.get("source","ED"), scraped_at=r.get("scraped_at",""))
                count += 1
                accused = r.get("accused","").strip()
                if accused:
                    self._run("""
                        MATCH (p:Politician)
                        WHERE toLower(p.name) CONTAINS toLower($accused)
                        MATCH (n:EnforcementAction {id:$id})
                        MERGE (p)-[:SUBJECT_OF]->(n)
                    """, accused=accused, id=node_id)
            except Exception as e:
                logger.warning(f"[Loader] EnforcementAction failed: {e}")
        self.stats["enforcement_actions"] = count
        logger.success(f"[Loader] Loaded {count} ED enforcement actions")
        return count

    def load_electoral_bonds(self, records: list) -> int:
        """Electoral bonds → ElectoralBond nodes + DONATED_VIA/REDEEMED_BY."""
        count = 0
        for r in records:
            purchaser = (r.get("purchaser_name") or "").strip()
            if not purchaser: continue
            node_id = make_id(f"bond_{r.get('bond_number','')}_{purchaser}")
            try:
                self._run("""
                    MERGE (n:ElectoralBond {id:$id})
                    SET n.bond_number=$bond_no, n.purchaser_name=$purchaser,
                        n.denomination_crore=$denom, n.purchase_date=$p_date,
                        n.redemption_date=$r_date, n.redeemed_by=$redeemer,
                        n.source=$source, n.dataset="electoral_bond",
                        n.scraped_at=$scraped_at
                """, id=node_id, bond_no=r.get("bond_number",""),
                   purchaser=purchaser,
                   denom=float(r.get("denomination_crore",0) or 0),
                   p_date=r.get("purchase_date",""), r_date=r.get("redemption_date",""),
                   redeemer=r.get("redeemed_by",""), source=r.get("source","ECI"),
                   scraped_at=r.get("scraped_at",""))
                count += 1
                redeemer = r.get("redeemed_by","").strip()
                if purchaser and redeemer:
                    self._run("""
                        MERGE (c:Company {id:$co_id})
                        ON CREATE SET c.name=$purchaser, c.source="electoral_bond"
                        MERGE (p:Party {id:$pt_id})
                        ON CREATE SET p.name=$redeemer, p.source="electoral_bond"
                        MATCH (b:ElectoralBond {id:$b_id})
                        MERGE (c)-[:DONATED_VIA]->(b)-[:REDEEMED_BY]->(p)
                    """, co_id=make_id(purchaser), purchaser=purchaser,
                       pt_id=make_id(redeemer), redeemer=redeemer, b_id=node_id)
            except Exception as e:
                logger.warning(f"[Loader] ElectoralBond failed: {e}")
        self.stats["electoral_bonds"] = count
        logger.success(f"[Loader] Loaded {count} electoral bonds")
        return count

    def load_insolvency_orders(self, records: list) -> int:
        """IBBI insolvency orders → InsolvencyOrder + HAS_INSOLVENCY link."""
        count = 0
        for r in records:
            company = (r.get("company_name") or "").strip()
            if not company: continue
            node_id = make_id(f"ibbi_{company}")
            try:
                self._run("""
                    MERGE (n:InsolvencyOrder {id:$id})
                    SET n.company_name=$company, n.cin=$cin,
                        n.process_type=$process_type, n.admitted_date=$admitted_date,
                        n.status=$status, n.admitted_claims=$claims,
                        n.source=$source, n.dataset="ibbi", n.scraped_at=$scraped_at
                """, id=node_id, company=company, cin=r.get("cin",""),
                   process_type=r.get("process_type",""),
                   admitted_date=r.get("admitted_date",""), status=r.get("status",""),
                   claims=float(r.get("admitted_claims",0) or 0),
                   source=r.get("source","IBBI"), scraped_at=r.get("scraped_at",""))
                count += 1
                self._run("""
                    MATCH (c:Company)
                    WHERE toLower(c.name) CONTAINS toLower($company)
                    MATCH (n:InsolvencyOrder {id:$id})
                    MERGE (c)-[:HAS_INSOLVENCY]->(n)
                """, company=company, id=node_id)
            except Exception as e:
                logger.warning(f"[Loader] InsolvencyOrder failed: {e}")
        self.stats["insolvency_orders"] = count
        logger.success(f"[Loader] Loaded {count} IBBI insolvency orders")
        return count

    def load_ngos(self, records: list) -> int:
        """NGO Darpan → NGO nodes."""
        count = 0
        for r in records:
            name = (r.get("ngo_name") or "").strip()
            if not name: continue
            node_id = make_id(f"ngo_{r.get('darpan_id',name)}")
            try:
                self._run("""
                    MERGE (n:NGO {id:$id})
                    SET n.ngo_name=$name, n.darpan_id=$darpan_id,
                        n.state=$state, n.district=$district,
                        n.registration_type=$reg_type, n.year_of_reg=$year,
                        n.key_issues=$issues, n.csr_receipts=$csr,
                        n.govt_grants=$grants, n.source=$source,
                        n.dataset="ngo_darpan", n.scraped_at=$scraped_at
                """, id=node_id, name=name, darpan_id=r.get("darpan_id",""),
                   state=r.get("state",""), district=r.get("district",""),
                   reg_type=r.get("registration_type",""),
                   year=str(r.get("year_of_reg","")),
                   issues=str(r.get("key_issues",[])),
                   csr=float(r.get("csr_receipts",0) or 0),
                   grants=float(r.get("govt_grants",0) or 0),
                   source=r.get("source","NGO Darpan"), scraped_at=r.get("scraped_at",""))
                count += 1
            except Exception as e:
                logger.warning(f"[Loader] NGO failed: {e}")
        self.stats["ngos"] = count
        logger.success(f"[Loader] Loaded {count} NGOs")
        return count

    def load_tenders(self, records: list) -> int:
        """CPPP tenders → Tender nodes + ISSUED_TENDER ministry link."""
        count = 0
        for r in records:
            title = (r.get("title") or "").strip()
            if not title: continue
            node_id = make_id(f"tender_{r.get('tender_id',title)}")
            try:
                self._run("""
                    MERGE (n:Tender {id:$id})
                    SET n.tender_id=$tender_id, n.title=$title,
                        n.ministry=$ministry, n.department=$dept,
                        n.estimated_crore=$value, n.tender_type=$t_type,
                        n.bid_end_date=$bid_end, n.status=$status,
                        n.awarded_to=$awarded_to, n.awarded_value=$awarded_val,
                        n.single_bid=$single_bid, n.source=$source,
                        n.dataset="cppp", n.scraped_at=$scraped_at
                """, id=node_id, tender_id=r.get("tender_id",""), title=title,
                   ministry=r.get("ministry",""), dept=r.get("department",""),
                   value=float(r.get("estimated_crore",0) or 0),
                   t_type=r.get("tender_type",""), bid_end=r.get("bid_submission_end",""),
                   status=r.get("status",""), awarded_to=r.get("awarded_to",""),
                   awarded_val=float(r.get("awarded_value",0) or 0),
                   single_bid=bool(r.get("single_bid",False)),
                   source=r.get("source","CPPP"), scraped_at=r.get("scraped_at",""))
                count += 1
                ministry = r.get("ministry","").strip()
                if ministry:
                    self._run("""
                        MERGE (m:Ministry {id:$m_id})
                        ON CREATE SET m.name=$ministry, m.source="cppp"
                        MATCH (t:Tender {id:$t_id})
                        MERGE (m)-[:ISSUED_TENDER]->(t)
                    """, m_id=make_id(ministry), ministry=ministry, t_id=node_id)
                if r.get("single_bid"):
                    self._run("MATCH (t:Tender {id:$id}) SET t.risk_flag='SINGLE_BID'",
                              id=node_id)
            except Exception as e:
                logger.warning(f"[Loader] Tender failed: {e}")
        self.stats["tenders"] = count
        logger.success(f"[Loader] Loaded {count} CPPP tenders")
        return count

    def load_parliament_questions(self, records: list) -> int:
        """Lok Sabha questions → ParliamentQuestion nodes."""
        count = 0
        for r in records:
            subject = (r.get("subject") or "").strip()
            if not subject: continue
            node_id = make_id(f"pq_{r.get('question_number','')}_{r.get('member_name','')}")
            try:
                self._run("""
                    MERGE (n:ParliamentQuestion {id:$id})
                    SET n.subject=$subject, n.question_number=$qno,
                        n.member_name=$member, n.ministry=$ministry,
                        n.session=$session, n.source=$source,
                        n.dataset="loksabha", n.scraped_at=$scraped_at
                """, id=node_id, subject=subject,
                   qno=r.get("question_number",""), member=r.get("member_name",""),
                   ministry=r.get("ministry",""), session=r.get("session",""),
                   source=r.get("source","Lok Sabha"), scraped_at=r.get("scraped_at",""))
                count += 1
                member = r.get("member_name","").strip()
                if member:
                    self._run("""
                        MATCH (p:Politician)
                        WHERE toLower(p.name) CONTAINS toLower($member)
                        MATCH (q:ParliamentQuestion {id:$id})
                        MERGE (p)-[:ASKED_QUESTION]->(q)
                    """, member=member, id=node_id)
            except Exception as e:
                logger.warning(f"[Loader] ParliamentQuestion failed: {e}")
        self.stats["parliament_questions"] = count
        logger.success(f"[Loader] Loaded {count} Lok Sabha questions")
        return count

    def load_vigilance_circulars(self, records: list) -> int:
        """CVC circulars → VigilanceCircular nodes."""
        count = 0
        for r in records:
            title = (r.get("title") or "").strip()
            if not title: continue
            node_id = make_id(f"cvc_{r.get('circular_number',title)}")
            try:
                self._run("""
                    MERGE (n:VigilanceCircular {id:$id})
                    SET n.title=$title, n.circular_number=$cno,
                        n.date=$date, n.ministry=$ministry,
                        n.subject=$subject, n.source=$source,
                        n.dataset="cvc", n.scraped_at=$scraped_at
                """, id=node_id, title=title, cno=r.get("circular_number",""),
                   date=r.get("date",""), ministry=r.get("ministry",""),
                   subject=r.get("subject",""), source=r.get("source","CVC"),
                   scraped_at=r.get("scraped_at",""))
                count += 1
            except Exception as e:
                logger.warning(f"[Loader] VigilanceCircular failed: {e}")
        self.stats["vigilance_circulars"] = count
        logger.success(f"[Loader] Loaded {count} CVC circulars")
        return count

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
