"""
BharatGraph - Neo4j Graph Schema
Defines all node types and relationship types for the knowledge graph.

Graph Model:
  (Politician)-[:MEMBER_OF]->(Party)
  (Politician)-[:DIRECTOR_OF]->(Company)
  (Politician)-[:CONTESTED_IN]->(Election)
  (Company)-[:WON_CONTRACT]->(Contract)
  (Contract)-[:AWARDED_BY]->(Ministry)
  (AuditReport)-[:FLAGS]->(Scheme)
  (AuditReport)-[:MENTIONS]->(Ministry)
  (PressRelease)-[:ISSUED_BY]->(Ministry)

This is the schema that makes BharatGraph powerful:
- Query: Find all companies where politician X is a director
- Query: Find contracts won by companies linked to politicians
- Query: Show audit reports flagging the same ministry
"""

# ── Node Labels ───────────────────────────────────────────
# Each dict defines the properties a node of that type can have.

NODE_SCHEMAS = {

    "Politician": {
        "description": "An elected official or political candidate",
        "properties": {
            "id":             "Unique ID (name_election hash)",
            "name":           "Cleaned full name",
            "name_raw":       "Original name from source",
            "party":          "Political party",
            "state":          "State they represent/contested",
            "election":       "Election name (Lok Sabha 2024 etc.)",
            "total_assets":   "Declared assets (string from affidavit)",
            "liabilities":    "Declared liabilities",
            "criminal_cases": "Number of declared criminal cases",
            "education":      "Declared education qualification",
            "source":         "Data source (myneta/eci)",
            "scraped_at":     "When this was scraped",
        },
        "required": ["name", "state"],
        "indexes":  ["name", "state", "party"],
    },

    "Company": {
        "description": "A registered company (from MCA/corporate registry)",
        "properties": {
            "id":                "CIN (Corporate Identity Number)",
            "name":              "Cleaned company name",
            "name_raw":          "Original name from MCA",
            "cin":               "Corporate Identity Number",
            "status":            "Active/Inactive/Struck Off",
            "state":             "State of registration",
            "registration_date": "Date of incorporation",
            "company_class":     "Private/Public/LLP etc.",
            "source":            "Data source (mca)",
            "scraped_at":        "When this was scraped",
        },
        "required": ["name"],
        "indexes":  ["name", "cin", "state"],
    },

    "Contract": {
        "description": "A government procurement contract from GeM",
        "properties": {
            "id":           "Order ID from GeM",
            "order_id":     "GeM order reference number",
            "seller_name":  "Company that won the contract",
            "buyer_org":    "Government department that bought",
            "product":      "What was procured",
            "amount_crore": "Contract value in crore rupees",
            "order_date":   "Date of contract",
            "state":        "State of buyer organisation",
            "source":       "Data source (gem)",
            "scraped_at":   "When this was scraped",
        },
        "required": ["order_id", "seller_name"],
        "indexes":  ["order_id", "seller_name", "amount_crore"],
    },

    "AuditReport": {
        "description": "A CAG audit report flagging financial irregularities",
        "properties": {
            "id":                "URL hash",
            "title":             "Report title",
            "url":               "Source URL on cag.gov.in",
            "year":              "Audit year",
            "state":             "State audited (or National)",
            "scheme":            "Scheme/programme audited",
            "amount_crore":      "Amount of irregularities found",
            "irregularity_type": "Type of irregularity",
            "finding":           "Key finding summary",
            "alert_keywords":    "Fraud keywords found in title",
            "source":            "Data source (cag)",
            "scraped_at":        "When this was scraped",
        },
        "required": ["title"],
        "indexes":  ["title", "state", "year"],
    },

    "PressRelease": {
        "description": "An official government press release from PIB",
        "properties": {
            "id":             "URL hash",
            "title":          "Press release title",
            "link":           "Source URL on pib.gov.in",
            "published":      "Publication date",
            "alert_keywords": "Alert keywords found in title",
            "source":         "Data source (pib)",
            "scraped_at":     "When this was scraped",
        },
        "required": ["title"],
        "indexes":  ["title"],
    },

    "Ministry": {
        "description": "A government ministry or department",
        "properties": {
            "id":   "Slug (ministry-of-finance etc.)",
            "name": "Full ministry name",
        },
        "required": ["name"],
        "indexes":  ["name"],
    },

    "Party": {
        "description": "A political party",
        "properties": {
            "id":   "Slug",
            "name": "Party name",
        },
        "required": ["name"],
        "indexes":  ["name"],
    },

    "Scheme": {
        "description": "A government welfare/development scheme",
        "properties": {
            "id":   "Slug",
            "name": "Scheme name (MGNREGA, PM-KISAN etc.)",
        },
        "required": ["name"],
        "indexes":  ["name"],
    },
}


# ── Relationship Types ────────────────────────────────────

RELATIONSHIP_SCHEMAS = {

    "MEMBER_OF": {
        "from": "Politician", "to": "Party",
        "description": "Politician is a member of this party",
        "properties": {"since": "Year joined"},
    },

    "DIRECTOR_OF": {
        "from": "Politician", "to": "Company",
        "description": "Politician is/was a director of this company",
        "properties": {
            "confidence": "Match confidence score (0-1)",
            "source":     "How this link was detected",
        },
    },

    "WON_CONTRACT": {
        "from": "Company", "to": "Contract",
        "description": "Company won this procurement contract",
        "properties": {"amount_crore": "Contract value"},
    },

    "AWARDED_BY": {
        "from": "Contract", "to": "Ministry",
        "description": "Contract was awarded by this ministry/dept",
        "properties": {},
    },

    "FLAGS": {
        "from": "AuditReport", "to": "Scheme",
        "description": "Audit report flagged irregularities in this scheme",
        "properties": {"amount_crore": "Amount flagged", "year": "Audit year"},
    },

    "AUDITS": {
        "from": "AuditReport", "to": "Ministry",
        "description": "Audit report covers this ministry",
        "properties": {},
    },

    "CONTESTED_IN": {
        "from": "Politician", "to": "Scheme",
        "description": "Politician contested election from this state/constituency",
        "properties": {"year": "Election year", "result": "Won/Lost"},
    },
}


# ── Cypher constraint + index statements ─────────────────
# Run these once when setting up a new Neo4j database.

# ── Full-text index (run once) ───────────────────────────────────────────────
# This powers instant search across all labels and fields simultaneously.
FULLTEXT_INDEX_QUERY = (
    # BUG-19 FIX: expanded from 8 to 16 node types + 14 searchable fields.
    # Auto-scales: add new node labels and field names to the lists below.
    "CALL db.index.fulltext.createNodeIndex("
    "  \'globalSearch\',"
    "  [\'Politician\',\'Company\',\'Contract\',\'AuditReport\',\'Scheme\',"
    "   \'Ministry\',\'Party\',\'PressRelease\',\'Tender\',\'RegulatoryOrder\',"
    "   \'EnforcementAction\',\'ElectoralBond\',\'InsolvencyOrder\',"
    "   \'NGO\',\'CourtCase\',\'LocalBody\'],"
    "  [\'name\',\'title\',\'aliases\',\'description\',\'item_desc\',"
    "   \'buyer_org\',\'seller_name\',\'ngo_name\',\'company_name\',"
    "   \'purchaser_name\',\'accused\',\'ministry\',\'constituency\',\'state\']"
    ")"
)

SETUP_QUERIES = [
    # Uniqueness constraints (also create indexes automatically)
    "CREATE CONSTRAINT politician_id IF NOT EXISTS FOR (n:Politician) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT company_id    IF NOT EXISTS FOR (n:Company)    REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT contract_id   IF NOT EXISTS FOR (n:Contract)   REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT audit_id      IF NOT EXISTS FOR (n:AuditReport) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT ministry_id   IF NOT EXISTS FOR (n:Ministry)   REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT party_id      IF NOT EXISTS FOR (n:Party)      REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT scheme_id     IF NOT EXISTS FOR (n:Scheme)     REQUIRE n.id IS UNIQUE",
    # Additional indexes for frequent lookups
    "CREATE INDEX politician_name IF NOT EXISTS FOR (n:Politician) ON (n.name)",
    "CREATE INDEX company_name    IF NOT EXISTS FOR (n:Company)    ON (n.name)",
    "CREATE INDEX contract_date   IF NOT EXISTS FOR (n:Contract)   ON (n.order_date)",
    # Full-text index across all searchable labels and fields
    "CALL db.index.fulltext.createNodeIndex('globalSearch', "
    "['Politician','Company','Contract','AuditReport','Scheme','Ministry','Party','PressRelease'], "
    "['name','title','aliases','description','item_desc','buyer_org','cin','ministry','summary'])"
    " IF NOT EXISTS",
]


def print_schema():
    """Print a human-readable summary of the graph schema."""
    print("=" * 55)
    print("  BharatGraph — Neo4j Schema")
    print("=" * 55)
    print(f"\nNode types ({len(NODE_SCHEMAS)}):")
    for label, schema in NODE_SCHEMAS.items():
        props = len(schema["properties"])
        print(f"  ({label})  — {schema['description'][:50]}")
        print(f"    {props} properties, indexes on: {schema['indexes']}")
    print(f"\nRelationship types ({len(RELATIONSHIP_SCHEMAS)}):")
    for rel, schema in RELATIONSHIP_SCHEMAS.items():
        print(f"  (:{schema['from']})-[:{rel}]->(:{schema['to']})")
        print(f"    {schema['description']}")
    print(f"\nSetup queries: {len(SETUP_QUERIES)} constraints + indexes")


if __name__ == "__main__":
    print_schema()
