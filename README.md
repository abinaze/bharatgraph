# BharatGraph

**A public transparency and institutional intelligence platform for India.**

BharatGraph aggregates official government data into a knowledge graph, applies
entity resolution and risk scoring to surface relationships between politicians,
companies, contracts, and audit findings. Every claim is traceable to a primary
source document. No accusations are made. The platform produces statistical
relationship analysis and risk indicators for journalists, researchers, and
civic organisations.

---

## Legal Notice

This platform processes only publicly available government records: election
affidavits published by the Election Commission of India, corporate filings from
the Ministry of Corporate Affairs, procurement orders from the Government
e-Marketplace, audit reports from the Comptroller and Auditor General, and
official press releases from the Press Information Bureau.

All outputs are statistical observations, not legal findings. Language describing
risk indicators does not constitute an accusation of wrongdoing. Entities
featured have the right to submit corrections through the issue tracker.

---

## What It Does

A user enters any entity — a politician, company, ministry, or scheme — and
the platform returns a structured dossier containing:

- Identity and role verification from official registries
- Corporate directorships and shareholding patterns
- Government contracts awarded to linked entities
- CAG audit findings mentioning those entities or their schemes
- A risk score derived from structural graph patterns
- A full evidence trail linking every data point to its source

The core analytical pattern is:

```
(Politician) -[DIRECTOR_OF]-> (Company) -[WON_CONTRACT]-> (Contract)
(AuditReport) -[FLAGS]-> (Scheme) <-[FUNDED_BY]- (Ministry)
```

When these patterns overlap — for example, when a company whose director is a
sitting politician repeatedly wins contracts from a ministry that the same
politician oversees — the platform flags a structural risk indicator.

---

## Architecture

```
bharatgraph/
    scrapers/           Data collection from seven official sources
    processing/         Name normalisation and cross-source entity matching
    graph/              Neo4j schema, loader, and Cypher query library
    ai/                 Risk scoring, anomaly detection, NLP analysis
    api/                FastAPI REST and WebSocket backend
    frontend/           React and D3.js interactive dashboard
    blockchain/         Append-only audit log for data provenance
    data/
        raw/            Downloaded source files (git-ignored)
        processed/      Pipeline output JSON (git-ignored)
        samples/        Small test fixtures (git-ignored)
    config/             Environment and settings
    tests/              Unit and integration tests
    docs/               Extended documentation
```

---

## Data Sources

| Source | Institution | Data Collected |
|---|---|---|
| MyNeta / ECI | Election Commission of India | Candidate affidavits: assets, liabilities, criminal cases, education |
| data.gov.in | Open Government Data Platform | MGNREGA records, PM-KISAN beneficiary data |
| MCA21 | Ministry of Corporate Affairs | Company registration, directors, CIN |
| GeM | Government e-Marketplace | Procurement contracts, order values, buyer organisations |
| PIB | Press Information Bureau | Official press releases, cabinet decisions |
| CAG | Comptroller and Auditor General | Audit reports, irregularity findings |
| e-Gazette | Ministry of Law and Justice | Official notifications, statutory orders |

---

## Free Infrastructure Stack

Every component of this platform runs on a free tier.

| Component | Service | Free Tier Limit |
|---|---|---|
| Source code | GitHub | Unlimited public repositories |
| Python backend | Render.com | 750 hours per month |
| React frontend | Vercel | Unlimited static deployments |
| Graph database | Neo4j AuraDB | 50,000 nodes, 175,000 relationships |
| Relational backup | Supabase PostgreSQL | 500 MB storage |
| AI inference | Hugging Face Inference API | Rate-limited free tier |
| Scheduled jobs | GitHub Actions | 2,000 minutes per month |
| Object storage | Cloudflare R2 | 10 GB storage, 1M requests |

---

## Development Phases

### Completed

**Phase 1 — Data Collection**
Seven scrapers collecting from official government sources. Base scraper with
rate limiting, retry logic, and automatic `.env` loading. Confirmed live:
3,199 MGNREGA records from DataGov, 30 CAG report links, 27 PIB press releases.

**Phase 2 — Data Processing**
Indian name normalisation stripping honorifics (Shri, Smt, Dr, Hon). Company
name standardisation for M/s prefixes and Ltd/Pvt Ltd/LLP suffixes. Jaccard
token similarity for cross-source entity matching. Full orchestration pipeline
saving to `data/processed/`.

**Phase 3 — Graph Database**
Neo4j schema with seven node types and six relationship types. Loader creating
nodes via MERGE with stable ID hashing. Eight pre-built Cypher queries covering
the core corruption detection patterns.

### Planned

**Phase 4 — FastAPI Backend**
REST API exposing graph queries. Endpoints for entity search, risk profiles,
relationship traversal, and live data ingestion. WebSocket feed for real-time
updates.

**Phase 5 — Risk Scoring Engine**
Composite risk score per entity combining: contract concentration ratio,
politician-company director overlap, CAG audit mention frequency, asset growth
anomaly detection from affidavit data. Explainable scoring — every factor
cited with source.

**Phase 6 — NLP and Document Intelligence**
Named entity recognition on CAG reports and PIB releases using spaCy and
Hugging Face models. Shadow drafting detection comparing corporate lobby
submissions against bill text. Sentiment analysis on parliamentary transcripts.

**Phase 7 — React Frontend and Graph Visualisation**
Interactive D3.js knowledge graph browser. Entity dossier view with evidence
locker. Risk score dashboard. Timeline reconstruction for relationship evolution.
Watchlist with alert subscriptions.

**Phase 8 — Live Monitoring Pipeline**
GitHub Actions scheduled jobs refreshing all scrapers daily. WebSocket broadcast
on new CAG filings, PIB releases, and GeM contracts. Alert engine notifying
watchlist subscribers.

**Phase 9 — Free Deployment**
Render.com for FastAPI backend. Vercel for React frontend. GitHub Actions for
scheduled data collection. Neo4j AuraDB as production graph database. Full
CI/CD pipeline with automated tests on every pull request.

**Phase 10 — Advanced Analytics**
Graph Neural Network anomaly detection for bid-rigging pattern identification.
Revolving door indicator tracking career transitions between regulatory roles
and private boards. Trade-based money laundering red flag detection using
commodity mismatch analysis. Geospatial verification correlating satellite
imagery against reported infrastructure spending.

---

## Quick Start

```bash
git clone https://github.com/abinaze/bharatgraph.git
cd bharatgraph
python -m venv venv
source venv/Scripts/activate      # Windows
source venv/bin/activate           # Linux / macOS
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your credentials:

```
DATAGOV_API_KEY=your_key_from_data.gov.in
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

Run the data pipeline:

```bash
python -m processing.pipeline --scrapers cag,gem,pib,myneta,mca
```

Load into Neo4j:

```bash
python -m graph.loader
```

Query the graph:

```bash
python -m graph.queries
```

---

## API Keys (All Free)

| Key | Where to Get It | Used By |
|---|---|---|
| `DATAGOV_API_KEY` | Register at data.gov.in/user/register | DataGov, MCA, GeM scrapers |
| `NEO4J_URI` + password | neo4j.com/cloud/platform/aura-graph-database | Graph loader and queries |
| `NEWSAPI_KEY` | newsapi.org (optional) | Future news monitoring |

---

## Running Individual Scrapers

```bash
python -m scrapers.datagov_scraper
python -m scrapers.pib_scraper
python -m scrapers.myneta_scraper
python -m scrapers.mca_scraper
python -m scrapers.cag_scraper
python -m scrapers.gem_scraper
```

---

## Git Workflow

This project uses a single-level branch strategy. There is no develop branch.
All feature and fix branches merge directly into `main`.

```
main                    Production-ready code at all times
feature/phase-N-name    New phase development
fix/issue-N-description Bug fixes referencing a GitHub issue number
```

Every branch follows the pattern:

```bash
git checkout -b feature/phase-4-api
# make changes
git add .
git commit -m "feat(api): description of change"
git push origin feature/phase-4-api
# open pull request into main
```

Commit message prefixes: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`.

---

## Project Status

| Check | Status |
|---|---|
| All 7 scrapers syntax clean | Passing |
| base_scraper loads .env automatically | Passing |
| PIB HTML scraping mode | Passing |
| Security: no API keys committed | Passing |
| Neo4j schema defined | Passing |
| Pipeline processes 47 records in 15s | Confirmed |

---

## License

MIT License. See `LICENSE` for the full text.

---

## Contributing

See `CONTRIBUTING.md` for the contribution workflow, code style guide, and
pull request checklist.

---

## Security

See `SECURITY.md` for the responsible disclosure policy and security contact.
