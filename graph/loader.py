"""
BharatGraph - Neo4j Graph Loader
Loads cleaned + resolved data from Phase 2 pipeline into Neo4j.
"""

import os, sys, json, hashlib, argparse
from datetime import datetime
from loguru import logger

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from graph.schema import SETUP_QUERIES, NODE_SCHEMAS


# BUG-19 FIX: upgraded from MD5 (16-char) to SHA-256 (20-char) for lower collision
# risk across large datasets.
def make_id(*parts) -> str:
    """Create a stable SHA-256 derived ID from multiple string parts."""
    combined = "|".join(str(p).lower().strip() for p in parts)
    return hashlib.sha256(combined.encode()).hexdigest()[:20]


class GraphLoader:
    """
    Loads BharatGraph data into Neo4j.
    BUG-21 FIX: __init__ now accepts an optional pre-built driver so admin.py
    can pass the FastAPI dependency driver instead of opening a second connection.
    """

    def __init__(self, dry_run: bool = False, driver=None):
        self.dry_run = dry_run
        self.driver  = driver   # BUG-21 FIX: accept injected driver
        self.stats   = {
            "nodes_created": 0,
            "nodes_merged":  0,
            "rels_created":  0,
            "errors":        0,
        }
        if dry_run:
            logger.info("[Loader] DRY RUN mode — no data written to Neo4j")
        elif driver is None:
            self._connect()

    def _connect(self):
        """Connect to Neo4j AuraDB using credentials from .env"""
        try:
            from neo4j import GraphDatabase
            from dotenv import load_dotenv
            load_dotenv()

            uri  = os.getenv("NEO4J_URI", "")
            user = os.getenv("NEO4J_USER", "neo4j")
            pwd  = os.getenv("NEO4J_PASSWORD", "")

            if not pwd:
                logger.error("[Loader] NEO4J_PASSWORD not set in .env")
                raise ValueError("NEO4J_PASSWORD missing")

            self.driver = GraphDatabase.driver(uri, auth=(user, pwd))
            self.driver.verify_connectivity()
            logger.success(f"[Loader] Connected to Neo4j: {uri[:40]}...")
        except ImportError:
            logger.error("[Loader] neo4j package not installed.")
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
            # BUG-3 FIX: fulltext index now covers all 20 node types (was 8).
            try:
                session.run(
                    "CALL db.index.fulltext.createNodeIndex("
                    "'globalSearch',"
                    "['Politician','Company','Contract','AuditReport',"
                    " 'Scheme','Ministry','Party','PressRelease',"
                    " 'NGO','ElectoralBond','InsolvencyOrder','Tender',"
                    " 'RegulatoryOrder','EnforcementAction',"
                    " 'ParliamentQuestion','VigilanceCircular',"
                    " 'ICIJEntity','SanctionedEntity','CourtCase','LocalBody'],"
                    "['name','title','aliases','item_desc','product','buyer_org',"
                    " 'cin','ministry','summary','seller_name','ngo_name',"
                    " 'purchaser_name','redeemed_by','company_name','accused',"
                    " 'entity_name','subject','jurisdiction']"
                    ")"
                )
                logger.info("[Loader] Full-text index created or verified (20 types)")
            except Exception as e:
                logger.debug(f"[Loader] Full-text index note: {e}")

            for query in SETUP_QUERIES:
                try:
                    session.run(query)
                except Exception as e:
                    logger.debug(f"[Loader] Schema query skipped (may exist): {e}")

        logger.success("[Loader] Schema constraints and indexes ready")

    def _run(self, query: str, params: dict = None, **kwargs):
        """
        Execute a single Cypher query.
        BUG-17 FIX: now accepts both calling styles:
          - old style: self._run(query, {"key": val})   ← positional dict
          - new style: self._run(query, key=val, ...)   ← keyword args
        Both are merged so existing callers and the 8 new loaders both work.
        """
        if self.dry_run:
            logger.debug(f"[Loader] DRY RUN query: {query[:80]}...")
            return None
        # Merge positional dict with any keyword args
        all_params = {**(params or {}), **kwargs}
        try:
            with self.driver.session() as session:
                return session.run(query, all_params)
        except Exception as e:
            logger.error(f"[Loader] Query failed: {e}\nQuery: {query[:100]}")
            self.stats["errors"] += 1
            return None

    # ── Node loaders ──────────────────────────────────────

    def load_politicians(self, records: list) -> int:
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
            party = r.get("party", "").strip()
            if party:
                self._create_party_and_link(node_id, party)

        logger.success(f"[Loader] Politicians loaded: {count}")
        self.stats["nodes_created"] += count
        return count

    def _create_party_and_link(self, politician_id: str, party_name: str):
        party_id = make_id(party_name)
        query = """
        MERGE (party:Party {id: $party_id})
        SET party.name = $party_name
        WITH party
        MATCH (p:Politician {id: $pol_id})
        MERGE (p)-[:MEMBER_OF]->(party)
        """
        self._run(query, {
            "party_id":   party_id,
            "party_name": party_name,
            "pol_id":     politician_id,
        })

    def load_companies(self, records: list) -> int:
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
        count = 0
        for r in records:
            order_id = r.get("order_id", "").strip()
            seller   = r.get("seller_name", r.get("seller_name_raw","")).strip()
            if not order_id:
                continue
            node_id = make_id(order_id)
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
            if seller:
                self._link_company_to_contract(seller, node_id, float(r.get("amount_crore", 0) or 0))
            buyer = r.get("buyer_org", "").strip()
            if buyer:
                self._link_contract_to_ministry(node_id, buyer)

        logger.success(f"[Loader] Contracts loaded: {count}")
        self.stats["nodes_created"] += count
        return count

    def _link_company_to_contract(self, seller_name, contract_id, amount):
        company_id = make_id(seller_name)
        self._run("""
        MERGE (co:Company {id: $co_id})
        SET co.name = $seller_name
        WITH co
        MATCH (c:Contract {id: $contract_id})
        MERGE (co)-[r:WON_CONTRACT]->(c)
        SET r.amount_crore = $amount
        """, {"co_id": company_id, "seller_name": seller_name,
              "contract_id": contract_id, "amount": amount})
        self.stats["rels_created"] += 1

    def _link_contract_to_ministry(self, contract_id, ministry_name):
        ministry_id = make_id(ministry_name)
        self._run("""
        MERGE (m:Ministry {id: $m_id})
        SET m.name = $m_name
        WITH m
        MATCH (c:Contract {id: $contract_id})
        MERGE (c)-[:AWARDED_BY]->(m)
        """, {"m_id": ministry_id, "m_name": ministry_name, "contract_id": contract_id})
        self.stats["rels_created"] += 1

    def load_audit_reports(self, records: list) -> int:
        count = 0
        for r in records:
            title = r.get("title", "").strip()
            if not title:
                continue
            node_id = make_id(title, r.get("url", ""))
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
            self._run("""
            MERGE (a:AuditReport {id: $id})
            SET a.title=$title, a.url=$url, a.year=$year, a.state=$state,
                a.scheme=$scheme, a.amount_crore=$amount,
                a.irregularity_type=$irr_type, a.finding=$finding,
                a.alert_keywords=$keywords, a.source=$source, a.scraped_at=$scraped_at
            """, params)
            count += 1
            scheme = r.get("scheme", "").strip()
            if scheme:
                self._link_audit_to_scheme(node_id, scheme, float(r.get("amount_crore", 0) or 0))

        logger.success(f"[Loader] Audit reports loaded: {count}")
        self.stats["nodes_created"] += count
        return count

    def _link_audit_to_scheme(self, audit_id, scheme_name, amount):
        scheme_id = make_id(scheme_name)
        self._run("""
        MERGE (s:Scheme {id: $s_id})
        SET s.name = $s_name
        WITH s
        MATCH (a:AuditReport {id: $audit_id})
        MERGE (a)-[r:FLAGS]->(s)
        SET r.amount_crore = $amount
        """, {"s_id": scheme_id, "s_name": scheme_name, "audit_id": audit_id, "amount": amount})
        self.stats["rels_created"] += 1

    def load_press_releases(self, records: list) -> int:
        count = 0
        for r in records:
            title = r.get("title", "").strip()
            if not title:
                continue
            node_id = make_id(title, r.get("link", ""))
            self._run("""
            MERGE (pr:PressRelease {id: $id})
            SET pr.title=$title, pr.link=$link, pr.published=$published,
                pr.alert_keywords=$keywords, pr.source=$source, pr.scraped_at=$scraped_at
            """, {
                "id": node_id, "title": title, "link": r.get("link", ""),
                "published": r.get("published", ""),
                "keywords":  str(r.get("alert_keywords", [])),
                "source":    r.get("_source", "pib"),
                "scraped_at":r.get("scraped_at", datetime.now().isoformat()),
            })
            count += 1

        logger.success(f"[Loader] Press releases loaded: {count}")
        self.stats["nodes_created"] += count
        return count

    def load_politician_company_links(self, matches: list) -> int:
        count = 0
        for match in matches:
            pol_name = match.get("name_a", match.get("politician_name", "")).strip()
            co_name  = match.get("name_b", match.get("company_name", "")).strip()
            score    = match.get("score", 0.0)
            if not pol_name or not co_name:
                continue
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
        """Load everything from a pipeline JSON output file."""
        logger.info(f"[Loader] Loading from: {filepath}")
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        raw   = data.get("raw",   {})
        links = data.get("links", [])

        self.setup_schema()

        results = {}
        if raw.get("myneta"):       results["politicians"]         = self.load_politicians(raw["myneta"])
        if raw.get("mca"):          results["companies"]           = self.load_companies(raw["mca"])
        if raw.get("gem"):          results["contracts"]           = self.load_contracts(raw["gem"])
        if raw.get("cag"):          results["audit_reports"]       = self.load_audit_reports(raw["cag"])
        if raw.get("pib"):          results["press_releases"]      = self.load_press_releases(raw["pib"])
        if links:                   results["director_of_links"]   = self.load_politician_company_links(links)
        if raw.get("sebi"):         results["regulatory_orders"]   = self.load_regulatory_orders(raw["sebi"])
        if raw.get("ed"):           results["enforcement_actions"] = self.load_enforcement_actions(raw["ed"])
        if raw.get("electoral_bond"):results["electoral_bonds"]    = self.load_electoral_bonds(raw["electoral_bond"])
        if raw.get("ibbi"):         results["insolvency_orders"]   = self.load_insolvency_orders(raw["ibbi"])
        if raw.get("ngo_darpan"):   results["ngos"]                = self.load_ngos(raw["ngo_darpan"])
        if raw.get("cppp"):         results["tenders"]             = self.load_tenders(raw["cppp"])
        if raw.get("loksabha"):     results["parliament_questions"]= self.load_parliament_questions(raw["loksabha"])
        if raw.get("cvc"):          results["vigilance_circulars"] = self.load_vigilance_circulars(raw["cvc"])
        # BUG-2 FIX: 7 previously missing loaders — these datasets were scraped but
        # silently dropped because load_from_pipeline_output never called them.
        if raw.get("icij"):         results["icij_entities"]       = self.load_icij_entities(raw["icij"])
        if raw.get("opensanctions"):results["sanctioned_entities"] = self.load_sanctioned_entities(raw["opensanctions"])
        if raw.get("njdg"):         results["court_cases"]         = self.load_court_cases(raw["njdg"])
        if raw.get("lgd"):          results["local_bodies"]        = self.load_local_bodies(raw["lgd"])
        if raw.get("ncrb"):         results["crime_reports"]       = self.load_crime_reports(raw["ncrb"])
        if raw.get("wikidata"):     results["wikidata_enrichments"]= self.load_wikidata_enrichments(raw["wikidata"])
        if raw.get("datagov"):      results["datagov_documents"]   = self.load_datagov_documents(raw["datagov"])

        logger.success(f"[Loader] Load complete. Stats: {self.stats}")
        return {**results, "stats": self.stats}

    # ── Phase 28 loaders (8 datasets) ────────────────────────────────────────

    def load_regulatory_orders(self, records: list) -> int:
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
                        n.source=$source, n.dataset='sebi', n.scraped_at=$scraped_at
                """, {
                    "id": node_id, "title": title, "url": r.get("url",""),
                    "order_type":  r.get("order_type",""),
                    "entity_name": r.get("entity_name", r.get("accused","")),
                    "violation":   r.get("violation",""),
                    "source":      r.get("source","SEBI"),
                    "scraped_at":  r.get("scraped_at",""),
                })
                count += 1
            except Exception as e:
                logger.warning(f"[Loader] RegulatoryOrder failed: {e}")
        self.stats["regulatory_orders"] = count
        logger.success(f"[Loader] Loaded {count} SEBI regulatory orders")
        return count

    def load_enforcement_actions(self, records: list) -> int:
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
                        n.dataset='ed', n.scraped_at=$scraped_at
                """, {
                    "id": node_id, "title": title, "url": r.get("url",""),
                    "date":         r.get("date",""),
                    "amount_crore": float(r.get("amount_crore",0) or 0),
                    "case_type":    r.get("case_type",""),
                    "accused":      r.get("accused",""),
                    "source":       r.get("source","ED"),
                    "scraped_at":   r.get("scraped_at",""),
                })
                count += 1
                accused = r.get("accused","").strip()
                if accused:
                    self._run("""
                        MATCH (p:Politician)
                        WHERE toLower(p.name) CONTAINS toLower($accused)
                        MATCH (n:EnforcementAction {id:$id})
                        MERGE (p)-[:SUBJECT_OF]->(n)
                    """, {"accused": accused, "id": node_id})
            except Exception as e:
                logger.warning(f"[Loader] EnforcementAction failed: {e}")
        self.stats["enforcement_actions"] = count
        logger.success(f"[Loader] Loaded {count} ED enforcement actions")
        return count

    def load_electoral_bonds(self, records: list) -> int:
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
                        n.source=$source, n.dataset='electoral_bond',
                        n.scraped_at=$scraped_at
                """, {
                    "id": node_id, "bond_no": r.get("bond_number",""),
                    "purchaser": purchaser,
                    "denom":     float(r.get("denomination_crore",0) or 0),
                    "p_date":    r.get("purchase_date",""),
                    "r_date":    r.get("redemption_date",""),
                    "redeemer":  r.get("redeemed_by",""),
                    "source":    r.get("source","ECI"),
                    "scraped_at":r.get("scraped_at",""),
                })
                count += 1
                redeemer = r.get("redeemed_by","").strip()
                if purchaser and redeemer:
                    self._run("""
                        MERGE (c:Company {id:$co_id})
                        ON CREATE SET c.name=$purchaser, c.source='electoral_bond'
                        MERGE (p:Party {id:$pt_id})
                        ON CREATE SET p.name=$redeemer, p.source='electoral_bond'
                        MATCH (b:ElectoralBond {id:$b_id})
                        MERGE (c)-[:DONATED_VIA]->(b)-[:REDEEMED_BY]->(p)
                    """, {
                        "co_id": make_id(purchaser), "purchaser": purchaser,
                        "pt_id": make_id(redeemer),  "redeemer":  redeemer,
                        "b_id":  node_id,
                    })
            except Exception as e:
                logger.warning(f"[Loader] ElectoralBond failed: {e}")
        self.stats["electoral_bonds"] = count
        logger.success(f"[Loader] Loaded {count} electoral bonds")
        return count

    def load_insolvency_orders(self, records: list) -> int:
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
                        n.source=$source, n.dataset='ibbi', n.scraped_at=$scraped_at
                """, {
                    "id": node_id, "company": company, "cin": r.get("cin",""),
                    "process_type":  r.get("process_type",""),
                    "admitted_date": r.get("admitted_date",""),
                    "status":        r.get("status",""),
                    "claims":        float(r.get("admitted_claims",0) or 0),
                    "source":        r.get("source","IBBI"),
                    "scraped_at":    r.get("scraped_at",""),
                })
                count += 1
                self._run("""
                    MATCH (c:Company)
                    WHERE toLower(c.name) CONTAINS toLower($company)
                    MATCH (n:InsolvencyOrder {id:$id})
                    MERGE (c)-[:HAS_INSOLVENCY]->(n)
                """, {"company": company, "id": node_id})
            except Exception as e:
                logger.warning(f"[Loader] InsolvencyOrder failed: {e}")
        self.stats["insolvency_orders"] = count
        logger.success(f"[Loader] Loaded {count} IBBI insolvency orders")
        return count

    def load_ngos(self, records: list) -> int:
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
                        n.dataset='ngo_darpan', n.scraped_at=$scraped_at
                """, {
                    "id": node_id, "name": name,
                    "darpan_id": r.get("darpan_id",""),
                    "state":     r.get("state",""),
                    "district":  r.get("district",""),
                    "reg_type":  r.get("registration_type",""),
                    "year":      str(r.get("year_of_reg","")),
                    "issues":    str(r.get("key_issues",[])),
                    "csr":       float(r.get("csr_receipts",0) or 0),
                    "grants":    float(r.get("govt_grants",0) or 0),
                    "source":    r.get("source","NGO Darpan"),
                    "scraped_at":r.get("scraped_at",""),
                })
                count += 1
            except Exception as e:
                logger.warning(f"[Loader] NGO failed: {e}")
        self.stats["ngos"] = count
        logger.success(f"[Loader] Loaded {count} NGOs")
        return count

    def load_tenders(self, records: list) -> int:
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
                        n.dataset='cppp', n.scraped_at=$scraped_at
                """, {
                    "id": node_id, "tender_id": r.get("tender_id",""),
                    "title":      title,
                    "ministry":   r.get("ministry",""),
                    "dept":       r.get("department",""),
                    "value":      float(r.get("estimated_crore",0) or 0),
                    "t_type":     r.get("tender_type",""),
                    "bid_end":    r.get("bid_submission_end",""),
                    "status":     r.get("status",""),
                    "awarded_to": r.get("awarded_to",""),
                    "awarded_val":float(r.get("awarded_value",0) or 0),
                    "single_bid": bool(r.get("single_bid",False)),
                    "source":     r.get("source","CPPP"),
                    "scraped_at": r.get("scraped_at",""),
                })
                count += 1
                ministry = r.get("ministry","").strip()
                if ministry:
                    self._run("""
                        MERGE (m:Ministry {id:$m_id})
                        ON CREATE SET m.name=$ministry, m.source='cppp'
                        MATCH (t:Tender {id:$t_id})
                        MERGE (m)-[:ISSUED_TENDER]->(t)
                    """, {"m_id": make_id(ministry), "ministry": ministry, "t_id": node_id})
                if r.get("single_bid"):
                    self._run("MATCH (t:Tender {id:$id}) SET t.risk_flag='SINGLE_BID'",
                              {"id": node_id})
            except Exception as e:
                logger.warning(f"[Loader] Tender failed: {e}")
        self.stats["tenders"] = count
        logger.success(f"[Loader] Loaded {count} CPPP tenders")
        return count

    def load_parliament_questions(self, records: list) -> int:
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
                        n.dataset='loksabha', n.scraped_at=$scraped_at
                """, {
                    "id": node_id, "subject": subject,
                    "qno":       r.get("question_number",""),
                    "member":    r.get("member_name",""),
                    "ministry":  r.get("ministry",""),
                    "session":   r.get("session",""),
                    "source":    r.get("source","Lok Sabha"),
                    "scraped_at":r.get("scraped_at",""),
                })
                count += 1
                member = r.get("member_name","").strip()
                if member:
                    self._run("""
                        MATCH (p:Politician)
                        WHERE toLower(p.name) CONTAINS toLower($member)
                        MATCH (q:ParliamentQuestion {id:$id})
                        MERGE (p)-[:ASKED_QUESTION]->(q)
                    """, {"member": member, "id": node_id})
            except Exception as e:
                logger.warning(f"[Loader] ParliamentQuestion failed: {e}")
        self.stats["parliament_questions"] = count
        logger.success(f"[Loader] Loaded {count} Lok Sabha questions")
        return count

    def load_vigilance_circulars(self, records: list) -> int:
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
                        n.dataset='cvc', n.scraped_at=$scraped_at
                """, {
                    "id": node_id, "title": title,
                    "cno":       r.get("circular_number",""),
                    "date":      r.get("date",""),
                    "ministry":  r.get("ministry",""),
                    "subject":   r.get("subject",""),
                    "source":    r.get("source","CVC"),
                    "scraped_at":r.get("scraped_at",""),
                })
                count += 1
            except Exception as e:
                logger.warning(f"[Loader] VigilanceCircular failed: {e}")
        self.stats["vigilance_circulars"] = count
        logger.success(f"[Loader] Loaded {count} CVC circulars")
        return count

    # ── BUG-2 FIX: 7 NEW loaders — were scraped but never loaded ─────────────

    def load_icij_entities(self, records: list) -> int:
        """ICIJ Offshore Leaks entities → ICIJEntity nodes."""
        count = 0
        for r in records:
            name = (r.get("name") or r.get("entity_name") or "").strip()
            if not name: continue
            node_id = make_id(f"icij_{r.get('node_id', name)}")
            try:
                self._run("""
                    MERGE (n:ICIJEntity {id:$id})
                    SET n.name=$name, n.entity_type=$entity_type,
                        n.jurisdiction=$jurisdiction, n.linked_to=$linked_to,
                        n.dataset_name=$dataset_name, n.source='ICIJ',
                        n.dataset='icij', n.scraped_at=$scraped_at
                """, {
                    "id": node_id, "name": name,
                    "entity_type":  r.get("entity_type", r.get("type","")),
                    "jurisdiction": r.get("jurisdiction",""),
                    "linked_to":    str(r.get("linked_to",[])),
                    "dataset_name": r.get("sourceID", r.get("dataset_name","")),
                    "scraped_at":   r.get("scraped_at",""),
                })
                count += 1
                # Cross-link to Indian politicians/companies by name similarity
                self._run("""
                    MATCH (p:Politician)
                    WHERE toLower(p.name) CONTAINS toLower($name)
                    MATCH (n:ICIJEntity {id:$id})
                    MERGE (p)-[:ASSOCIATED_WITH]->(n)
                """, {"name": name, "id": node_id})
            except Exception as e:
                logger.warning(f"[Loader] ICIJEntity failed: {e}")
        self.stats["icij_entities"] = count
        logger.success(f"[Loader] Loaded {count} ICIJ entities")
        return count

    def load_sanctioned_entities(self, records: list) -> int:
        """OpenSanctions → SanctionedEntity nodes."""
        count = 0
        for r in records:
            name = (r.get("name") or r.get("caption") or "").strip()
            if not name: continue
            node_id = make_id(f"sanction_{r.get('id', name)}")
            try:
                self._run("""
                    MERGE (n:SanctionedEntity {id:$id})
                    SET n.name=$name, n.schema_type=$schema_type,
                        n.topics=$topics, n.countries=$countries,
                        n.sanctions_list=$sanctions_list,
                        n.source='OpenSanctions', n.dataset='opensanctions',
                        n.scraped_at=$scraped_at
                """, {
                    "id": node_id, "name": name,
                    "schema_type":   r.get("schema",""),
                    "topics":        str(r.get("topics",[])),
                    "countries":     str(r.get("countries",[])),
                    "sanctions_list":r.get("datasets",""),
                    "scraped_at":    r.get("scraped_at",""),
                })
                count += 1
                self._run("""
                    MATCH (p:Politician)
                    WHERE toLower(p.name) CONTAINS toLower($name)
                    MATCH (n:SanctionedEntity {id:$id})
                    MERGE (p)-[:ASSOCIATED_WITH]->(n)
                """, {"name": name, "id": node_id})
            except Exception as e:
                logger.warning(f"[Loader] SanctionedEntity failed: {e}")
        self.stats["sanctioned_entities"] = count
        logger.success(f"[Loader] Loaded {count} sanctioned entities")
        return count

    def load_court_cases(self, records: list) -> int:
        """NJDG court pendency stats → CourtCase nodes."""
        count = 0
        for r in records:
            court = (r.get("court_name") or r.get("state") or "").strip()
            if not court: continue
            node_id = make_id(f"njdg_{court}_{r.get('year','')}")
            try:
                self._run("""
                    MERGE (n:CourtCase {id:$id})
                    SET n.court_name=$court, n.state=$state,
                        n.pending_cases=$pending, n.disposed_cases=$disposed,
                        n.year=$year, n.source='NJDG',
                        n.dataset='njdg', n.scraped_at=$scraped_at
                """, {
                    "id": node_id, "court": court,
                    "state":    r.get("state",""),
                    "pending":  int(r.get("pending_cases",0) or 0),
                    "disposed": int(r.get("disposed_cases",0) or 0),
                    "year":     str(r.get("year","")),
                    "scraped_at":r.get("scraped_at",""),
                })
                count += 1
            except Exception as e:
                logger.warning(f"[Loader] CourtCase failed: {e}")
        self.stats["court_cases"] = count
        logger.success(f"[Loader] Loaded {count} court case records")
        return count

    def load_local_bodies(self, records: list) -> int:
        """LGD (Local Government Directory) → LocalBody nodes."""
        count = 0
        for r in records:
            name = (r.get("name") or r.get("state_name") or "").strip()
            if not name: continue
            node_id = make_id(f"lgd_{r.get('lgd_code',name)}")
            try:
                self._run("""
                    MERGE (n:LocalBody {id:$id})
                    SET n.name=$name, n.lgd_code=$lgd_code,
                        n.entity_type=$entity_type, n.state=$state,
                        n.district=$district, n.source='LGD',
                        n.dataset='lgd', n.scraped_at=$scraped_at
                """, {
                    "id": node_id, "name": name,
                    "lgd_code":   str(r.get("lgd_code","")),
                    "entity_type":r.get("entity_type", r.get("type","")),
                    "state":      r.get("state",""),
                    "district":   r.get("district",""),
                    "scraped_at": r.get("scraped_at",""),
                })
                count += 1
            except Exception as e:
                logger.warning(f"[Loader] LocalBody failed: {e}")
        self.stats["local_bodies"] = count
        logger.success(f"[Loader] Loaded {count} local bodies")
        return count

    def load_crime_reports(self, records: list) -> int:
        """NCRB crime statistics — stored as metadata nodes for context."""
        count = 0
        for r in records:
            state = (r.get("state") or "").strip()
            year  = str(r.get("year","")).strip()
            if not state or not year: continue
            node_id = make_id(f"ncrb_{state}_{year}")
            try:
                self._run("""
                    MERGE (n:CrimeReport {id:$id})
                    SET n.state=$state, n.year=$year,
                        n.crime_head=$crime_head,
                        n.cases_registered=$cases,
                        n.source='NCRB', n.dataset='ncrb',
                        n.scraped_at=$scraped_at
                """, {
                    "id": node_id, "state": state, "year": year,
                    "crime_head": r.get("crime_head",""),
                    "cases":      int(r.get("cases_registered",0) or 0),
                    "scraped_at": r.get("scraped_at",""),
                })
                count += 1
            except Exception as e:
                logger.warning(f"[Loader] CrimeReport failed: {e}")
        self.stats["crime_reports"] = count
        logger.success(f"[Loader] Loaded {count} NCRB crime reports")
        return count

    def load_wikidata_enrichments(self, records: list) -> int:
        """
        Wikidata — enriches EXISTING Politician nodes; does NOT create new ones.
        Uses MATCH not MERGE to avoid phantom nodes.
        """
        count = 0
        for r in records:
            name = (r.get("name") or "").strip()
            if not name: continue
            try:
                result = self._run("""
                    MATCH (p:Politician)
                    WHERE toLower(p.name) = toLower($name)
                       OR any(a IN coalesce(p.aliases,[]) WHERE toLower(a) = toLower($name))
                    SET p.wikidata_id    = coalesce($wikidata_id, p.wikidata_id),
                        p.birth_year     = coalesce($birth_year,  p.birth_year),
                        p.gender         = coalesce($gender,      p.gender),
                        p.positions      = coalesce($positions,   p.positions),
                        p.wikidata_enriched = true
                    RETURN count(p) AS updated
                """, {
                    "name":       name,
                    "wikidata_id":r.get("wikidata_id",""),
                    "birth_year": str(r.get("birth_year","")),
                    "gender":     r.get("gender",""),
                    "positions":  str(r.get("positions",[])),
                })
                if result:
                    row = result.single()
                    if row and row["updated"] > 0:
                        count += 1
            except Exception as e:
                logger.warning(f"[Loader] Wikidata enrichment failed for {name}: {e}")
        self.stats["wikidata_enrichments"] = count
        logger.success(f"[Loader] Wikidata enriched {count} existing Politician nodes")
        return count

    def load_datagov_documents(self, records: list) -> int:
        """data.gov.in datasets — generic document nodes."""
        count = 0
        for r in records:
            title = (r.get("title") or r.get("resource_title") or "").strip()
            if not title: continue
            node_id = make_id(f"datagov_{r.get('resource_id',title)}")
            try:
                self._run("""
                    MERGE (n:DataGovDocument {id:$id})
                    SET n.title=$title, n.dataset_name=$dataset_name,
                        n.resource_id=$resource_id,
                        n.ministry=$ministry,
                        n.source='data.gov.in', n.dataset='datagov',
                        n.scraped_at=$scraped_at
                """, {
                    "id": node_id, "title": title,
                    "dataset_name":r.get("_dataset",""),
                    "resource_id": r.get("resource_id",""),
                    "ministry":    r.get("ministry",""),
                    "scraped_at":  r.get("scraped_at",""),
                })
                count += 1
            except Exception as e:
                logger.warning(f"[Loader] DataGovDocument failed: {e}")
        self.stats["datagov_documents"] = count
        logger.success(f"[Loader] Loaded {count} DataGov documents")
        return count

    def close(self):
        if self.driver:
            self.driver.close()
            logger.info("[Loader] Neo4j connection closed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BharatGraph Graph Loader")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--file",    type=str, default=None)
    args = parser.parse_args()

    print("=" * 55)
    print("BharatGraph - Graph Loader")
    print("=" * 55)

    loader = GraphLoader(dry_run=args.dry_run)

    if args.file:
        results = loader.load_from_pipeline_output(args.file)
    else:
        import glob
        files = sorted(glob.glob("data/processed/pipeline_*.json"))
        if files:
            results = loader.load_from_pipeline_output(files[-1])
        else:
            print("\nNo pipeline output found. Run: python -m processing.pipeline")
            results = {}

    loader.close()
    s = loader.stats
    print(f"\n{'='*55}\nLOAD SUMMARY\n{'='*55}")
    print(f"  Nodes created:  {s['nodes_created']}")
    print(f"  Nodes merged:   {s['nodes_merged']}")
    print(f"  Relationships:  {s['rels_created']}")
    print(f"  Errors:         {s['errors']}")
    if args.dry_run:
        print("  (DRY RUN — nothing was written to Neo4j)")
    print("=" * 55)
