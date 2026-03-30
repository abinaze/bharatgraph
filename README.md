# BharatGraph

An AI-powered public transparency and institutional intelligence platform for India.

BharatGraph aggregates official government records, corporate filings, audit reports,
parliamentary data, court judgments, and international investigative datasets into
a unified knowledge graph. It applies entity resolution, graph analytics, and machine
learning to surface structural relationships between politicians, companies, contracts,
ministries, and public schemes. Every output is traceable to a primary source document.

The platform does not make accusations. It identifies structural patterns, relationship
indicators, and governance anomalies derived from publicly available information.
All language is analytically neutral and legally defensible.

---

## What It Builds

Two public-facing interfaces backed by one analytical engine.

**Investigation Intelligence (Tab 1)**

A user enters any entity — politician, minister, civil servant, company, NGO,
investor — and receives a structured dossier: identity verification, corporate
directorships, government contracts, audit mentions, parliamentary activity,
international connections, asset declarations across election cycles, and a
composite structural risk indicator. Every claim links to its source document
with a date and credibility rating. The graph browser allows multi-hop exploration:
find how entity A connects to entity B through any chain of verified relationships.

**Live Transparency Feed (Tab 2)**

A continuously updated stream of AI-generated intelligence derived from new CAG
reports, GeM contracts, court filings, PIB releases, SEBI orders, and verified
news. Each headline opens a mini investigation report with a timeline, evidence
chain, and relationship graph. Users subscribe to watchlists for named entities
and receive email alerts when new data links to them.

---

## Core Analytical Pattern

```
(Politician)-[:DIRECTOR_OF]->(Company)-[:WON_CONTRACT]->(Contract)
                                    |
                            (AuditReport)-[:FLAGS]->(Scheme)
                                    |
                         (Ministry)-[:AWARDED_BY]->(Contract)
```

When these patterns converge — a company whose director holds public office
wins repeated contracts from a ministry that official oversees, and audit reports
flag the same schemes — the platform surfaces a structural risk indicator with
full evidence documentation.

---

## Architecture

```
bharatgraph/
    scrapers/           Data collectors from official Indian and international sources
    processing/         Name normalisation, entity resolution, pipeline orchestration
    graph/              Neo4j schema, loader, and Cypher query library
    ai/                 Risk scoring, NLP analysis, anomaly detection, chatbot
    api/                FastAPI REST and WebSocket backend
    frontend/           Next.js and D3.js interactive dashboard
    blockchain/         Append-only audit log for data provenance
    tests/              Unit and integration tests
    config/             Environment configuration
    docs/               Extended documentation
    data/
        raw/            Downloaded source files (git-ignored)
        processed/      Pipeline output (git-ignored)
        samples/        Small test fixtures (git-ignored)
```

---

## Data Sources

**Indian Government**

| Source | Institution | Intelligence Value |
|---|---|---|
| MyNeta / ECI | Election Commission of India | Assets, liabilities, criminal cases, education per candidate |
| MCA21 | Ministry of Corporate Affairs | Company registration, directors, CIN, shareholding patterns |
| data.gov.in | Open Government Data Platform | MGNREGA, PM-KISAN, sectoral beneficiary datasets |
| GeM | Government e-Marketplace | Procurement contracts, values, buyer organisations |
| PIB | Press Information Bureau | Cabinet decisions, scheme launches, official announcements |
| CAG | Comptroller and Auditor General | Audit reports, irregularity amounts, flagged schemes |
| e-Gazette | Ministry of Law and Justice | Statutory notifications, gazette orders |
| Lok Sabha and Rajya Sabha | Parliament of India | Questions, debates, committee assignments |
| PRS India | PRS Legislative Research | Bill text, amendment history, legislative status |
| eCourts | Supreme Court e-Committee | Judgment search, case status |
| SEBI | Securities and Exchange Board | Insider trading, enforcement orders, market misconduct |
| Electoral Bonds | Supreme Court ordered disclosure | Donor-recipient bond transaction data |

**International Free Sources**

| Source | What It Provides |
|---|---|
| OpenSanctions | Global PEP and sanctions list, daily updates, free API |
| ICIJ Offshore Leaks | Panama, Pandora, Paradise Papers entity search, free API |
| OpenCorporates | 223 million companies across 140 jurisdictions, free tier |
| Wikidata | Structured entity data: education, career timeline, nationality |
| World Bank Open Data | Governance indicators, development scores |

---

## Free Infrastructure Stack

| Component | Service | Free Allowance |
|---|---|---|
| Source code and CI | GitHub and GitHub Actions | Unlimited public repos, 2,000 CI minutes/month |
| Python backend | Render.com | 750 hours/month |
| React frontend | Vercel | Unlimited static deployments |
| Graph database | Neo4j AuraDB | 50,000 nodes, 175,000 relationships |
| Vector search | Qdrant Cloud | 1 GB storage |
| LLM inference | Hugging Face Inference API | Rate-limited free tier |
| Multilingual NER | AI4Bharat IndicNER on Hugging Face | Free local inference |
| Satellite imagery | Copernicus Open Access Hub | Free Sentinel-2 data |
| Email alerts | Resend.com | 3,000 emails/month |
| Relational backup | Supabase | 500 MB PostgreSQL |
| Object storage | Cloudflare R2 | 10 GB, 1M requests |

---

## Development Phases

### Completed

**Phase 1 — Data Collection**

Seven scrapers collecting from official government sources. Confirmed live:
3,199 MGNREGA records from DataGov API, 30 CAG audit report links from
cag.gov.in, 27 PIB press releases from pib.gov.in HTML scraping. Base scraper
with automatic `.env` loading, polite rate limiting, and JSON output.

**Phase 2 — Data Processing**

Indian name normalisation stripping honorifics (Shri, Smt, Dr, Hon). Company
name standardisation for M/s prefixes and Ltd/Pvt Ltd/LLP suffixes. Jaccard
token similarity for cross-source entity matching. Full pipeline orchestrating
all scrapers and saving to `data/processed/`.

**Phase 3 — Graph Database**

Neo4j schema with 7 node types, 6 relationship types, and 10 constraint and
index setup queries. Graph loader using MERGE with stable MD5 ID hashing.
8 pre-built Cypher queries covering the core corruption detection patterns.

### Planned

**Phase 4 — FastAPI Backend**

REST API: entity search, dossier assembly, risk profile, graph traversal.
WebSocket for live feed broadcast. Pydantic models with typed source citations.
Dependency injection for shared Neo4j driver.

**Phase 5 — Risk Scoring Engine**

Composite 0-100 risk score per entity. Factors with weights: contract
concentration (0.25), politician-company director overlap (0.35), CAG audit
mention frequency (0.20), asset growth anomaly across election cycles (0.15),
criminal case presence (0.05). Every factor output cites its source document.
Output language uses structural indicator, not accusation.

**Phase 6 — Expanded Data Sources**

New scrapers: Lok Sabha question database, PRS bill tracker, SEBI enforcement
orders, eCourts judgment search, electoral bond transaction data. Integration
of OpenSanctions free PEP and sanctions API, ICIJ Offshore Leaks free entity
search API, and Wikidata for entity enrichment.

**Phase 7 — NLP and Document Intelligence**

Named entity recognition on CAG and PIB text using spaCy and Hugging Face free
models. Shadow drafting detection comparing corporate consultation responses
against bill text. Multilingual NER for Hindi using AI4Bharat IndicNER (free,
runs locally). Benford's Law anomaly detection on declared asset figures in
election affidavits to detect statistically improbable distributions.

**Phase 8 — Advanced Graph Analytics**

NetworkX graph algorithms: betweenness centrality to identify institutional
gatekeepers, community detection to find procurement clusters and bidding rings,
PageRank on reverse contract links to identify beneficiary networks. Circular
ownership detector using graph cycle detection. Shadow director identification.
Ghost company detector: companies registered within 90 days of winning a
tender with no prior commercial activity.

**Phase 9 — React Frontend and Graph Visualisation**

Next.js 14 with D3.js force-directed knowledge graph browser. Entity dossier
with tabbed evidence locker. Risk score dashboard with ranked entity list.
Timeline reconstruction for relationship evolution. Sankey diagram for money
flows. Geospatial view using Leaflet with free OpenStreetMap tiles. Watchlist
with WebSocket alert subscriptions.

**Phase 10 — Live Monitoring and GitHub Actions**

GitHub Actions cron jobs refreshing all scrapers daily within the 2,000
minute/month free allowance. Diff-based alert engine detecting new CAG mentions
of known graph entities. Headline generation for the live feed. Email alerts
via Resend.com free tier. Autonomous scan of new data for known risk patterns.

**Phase 11 — LLM Chatbot and Dossier Export**

Conversational interface using free Hugging Face inference. Natural language
queries: "Show all contracts linked to companies where this minister is a
director." Evidence assembled from Neo4j with citations. Hypothesis testing
with full multi-hop path explanation. PDF dossier export for journalists using
WeasyPrint (free, open source).

**Phase 12 — Geospatial Infrastructure Verification**

Sentinel-2 satellite imagery via free Copernicus API. Cross-reference GPS
coordinates from GeM contract locations against NDVI change detection to
verify road and building construction. Flag discrepancy when payment is
disbursed but imagery shows less than 50 percent physical completion.

**Phase 13 — Revolving Door and TBML Detection**

Revolving Door Indicator: career transitions from regulatory roles to private
boards of companies that held contracts during that tenure. FATF-aligned
Trade-Based Money Laundering flags: commodity mismatch, single-bid contracts,
price anomaly against category median, director change within 30 days of
contract award, sub-contracting loop where winner re-awards to a losing bidder.

**Phase 14 — Free Deployment**

Render.com backend, Vercel frontend, Neo4j AuraDB production, GitHub Actions
CI/CD with automated tests on every pull request. Zero monthly cost target.

---

## Quick Start

```bash
git clone https://github.com/abinaze/bharatgraph.git
cd bharatgraph
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```
DATAGOV_API_KEY=register_free_at_data.gov.in_user_register
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_generated_password
```

Run the full pipeline:

```bash
python -m processing.pipeline --scrapers cag,gem,pib,myneta,mca
python -m graph.loader
python -m graph.queries
```

---

## Git Workflow

One long-lived branch: `main`. All branches merge directly into `main`.
No develop branch.

```
feature/phase-N-short-name    New phase development
fix/issue-N-description        Bug fix referencing a GitHub issue number
docs/description               Documentation only
```

```bash
git checkout main
git pull origin main
git checkout -b feature/phase-4-api
git commit -m "feat(api): description of what changed"
git push origin feature/phase-4-api
```

Commit prefixes: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`.

Never resolve merge conflicts using the GitHub web editor. Resolve locally,
then push.

---

## Confirmed Live Results

```
DataGov API    3,199 real MGNREGA records
CAG            30 real audit report links from cag.gov.in
PIB            27 real press releases from pib.gov.in
GeM            gem.gov.in statistics page connected
Pipeline       47 records processed and saved in 15 seconds
```

---

## Reference Documents

- [Contributing Guidelines](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)
- [Phase Roadmap](PHASE_ROADMAP.md)
- [MIT License](LICENSE)