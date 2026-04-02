# BharatGraph

**AI-powered public transparency and institutional intelligence platform for India.**

BharatGraph aggregates official government records, corporate filings, audit reports,
parliamentary data, court judgments, and international investigative datasets into a
unified knowledge graph. It applies entity resolution, graph analytics, and machine
learning to surface structural relationships between politicians, companies, contracts,
ministries, and public schemes. Every output is traceable to a primary source document.

The platform does not make accusations. It identifies structural patterns, relationship
indicators, and governance anomalies derived from publicly available information.
All language is analytically neutral and legally defensible.

---

## What It Builds

**Investigation Intelligence (Tab 1)**

Enter any entity — politician, minister, company, NGO — and receive a structured dossier:
identity verification, corporate directorships, government contracts, audit mentions,
parliamentary activity, international connections, asset declarations across election
cycles, and a composite structural risk indicator. Every claim links to its source
document. The graph browser allows multi-hop exploration of verified relationships.

**Live Transparency Feed (Tab 2)**

A continuously updated stream of AI-generated intelligence derived from new CAG reports,
GeM contracts, court filings, PIB releases, SEBI orders, and verified news.

---

## Core Analytical Pattern

```
(Politician)-[:DIRECTOR_OF]->(Company)-[:WON_CONTRACT]->(Contract)
                                            |
                              (AuditReport)-[:FLAGS]->(Scheme)
                                            |
                              (Ministry)-[:AWARDED_BY]->(Contract)
```

---

## Architecture

```
bharatgraph/
  scrapers/       21 data collectors (Indian govt + international)
  processing/     Name normalisation, entity resolution, pipeline
  graph/          Neo4j schema, loader, Cypher queries
  ai/             Risk scoring, NLP, graph analytics, 12 investigators
  config/         22 language configs, settings
  api/            FastAPI REST + WebSocket (6 routes)
  frontend/       HTML/CSS/JS dashboard, D3.js graph, dark/light theme
  templates/      Jinja2 dossier template (PDF/HTML)
  blockchain/     Audit log
  tests/          Tests
```

---

## Deployment Stack (Zero Cost)

| Component      | Service             | Free Allowance                     |
|----------------|---------------------|------------------------------------|
| Source code    | GitHub              | Unlimited public repos             |
| Backend API    | Hugging Face Spaces | Docker SDK — no cold start         |
| Frontend       | GitHub Pages        | Unlimited static hosting           |
| Graph database | Neo4j AuraDB Free   | 50K nodes, 175K relationships      |
| CDN + DDoS     | Cloudflare Free     | Unlimited caching + DDoS           |
| CI/CD          | GitHub Actions      | 2,000 min/month                    |
| Uptime monitor | UptimeRobot Free    | 50 monitors, 5-min intervals       |

---

## Data Sources (21 Scrapers)

### Indian Government

| Source | Institution | Intelligence |
|--------|-------------|--------------|
| MyNeta / ECI | Election Commission | Assets, criminal cases, affidavits |
| MCA21 | Corporate Affairs | Directors, company registration |
| data.gov.in | Open Data Platform | MGNREGA, PM-KISAN |
| GeM | e-Marketplace | Procurement contracts |
| PIB | Press Information Bureau | Cabinet decisions |
| CAG | Comptroller & Auditor General | Audit irregularities |
| Lok Sabha | Parliament | Questions, debates |
| NJDG | eCourts | Case status |
| ED | Enforcement Directorate | PMLA press releases |
| SEBI | Securities Board | Enforcement orders |
| Electoral Bonds | ECI / SC disclosure | Donor-party data |
| CVC | Vigilance Commission | Vigilance advisories |
| NCRB | Crime Records Bureau | Crime statistics |
| LGD | Panchayati Raj | Local government |
| IBBI | Insolvency Board | Corporate insolvency |
| NGO Darpan | NITI Aayog | NGO funding |
| CPPP | Procurement Portal | Procurement transparency |

### International

| Source | What It Provides |
|--------|-----------------|
| OpenSanctions | Global PEP and sanctions |
| ICIJ Offshore Leaks | Panama, Pandora, Paradise Papers |
| Wikidata | Entity enrichment, career data |

---

## Completed Phases

### Phase 1 — Data Collection
7 scrapers. Confirmed live: 3,199 MGNREGA records, 30 CAG links, 27 PIB articles.
`base_scraper.py`: `load_dotenv()`, rate limiting, JSON output.

### Phase 2 — Data Processing
Indian name normalisation (honorifics, company prefixes). Jaccard token similarity
for cross-source entity resolution. Full pipeline orchestrator.

### Phase 3 — Graph Database
Neo4j schema: 7 node types, 6 relationship types, 10 constraint queries.
`MERGE` with stable MD5 IDs. 8 pre-built Cypher queries.
Connected to Neo4j AuraDB Free: `neo4j+s://1a34e3b8.databases.neo4j.io`

### Phase 4 — FastAPI Backend
FastAPI with lifespan, CORS, 6 route modules registered after `app = FastAPI()`,
WebSocket feed, Pydantic models. Version 0.12.0.

### Phase 5 — Risk Scoring Engine
Composite 0–100 score. Weights: politician_company_overlap (0.35),
contract_concentration (0.25), audit_frequency (0.20), asset_anomaly (0.15),
criminal_case (0.05). `validate_language()` enforces neutral analytical output.

### Phase 6 — Expanded Data Sources
13 scrapers total. ICIJ HTML mode (BeautifulSoup). Wikidata SPARQL confirmed.
All public HuggingFace models — no gating.

### Phase 7 — NLP Document Intelligence
spaCy `en_core_web_sm` NER. Benford's Law chi-squared test on affidavit assets.
Multilingual NER: `Davlan/bert-base-multilingual-cased-ner-hrl`.
Shadow draft detector: `all-MiniLM-L6-v2`, 93.35% alignment confirmed.

### Phase 8 — Advanced Graph Analytics
NetworkX: betweenness centrality, PageRank, Louvain community detection.
Circular ownership `simple_cycles()` — 3-node cycle confirmed.
Ghost company scorer: GHOST_THRESHOLD=60 — Quick Win Pvt Ltd: 100/100 confirmed.

### Phase 9 — Eight New Indian Sources (21 Total)
NJDG (39 live records confirmed), ED, CVC, NCRB, LGD, IBBI, NGO Darpan, CPPP.
All have sample fallbacks when live source unavailable.

### Phase 10 — Multi-Investigator AI Engine
12 parallel investigators in `ThreadPoolExecutor`. SHA-256 report hash: stable,
unique, 64 chars. Synthesis: 3+ investigators agreeing = HIGH confidence.
`FakeSession` for offline testing. `validate_language()` on all output.

### Phase 11 — Multilingual Platform (22 Languages)
All 22 Indian scheduled languages. Unicode script detection confirmed
(Devanagari→hi, Tamil→ta). Helsinki-NLP/opus-mt-en-hi (public, no gating).
Modi→मोदी/மோடி/మోదీ/ಮೋದಿ/മോദി cross-script search confirmed.
Risk levels pre-translated in 9 languages.

### Phase 12 — PDF Dossier Generator
SHA-256 integrity hash per report. Verified tamper detection working.
Jinja2 + WeasyPrint (HTML fallback on Windows, full PDF on Linux).
Template: Indian tricolour design, 8 sections. 10,829 chars rendered confirmed.
`GET /export/pdf/{entity_id}` · `GET /verify/{hash}`

### Phase 13 — Production Frontend
HTML/CSS/JS — no React, no Node.js, no build step. Works from `file://`.

- `design-system.css`: CSS custom properties token layer, dark + light themes
- `components.css`: 25+ component classes
- `router.js`: hash-based client-side routing with named params
- `api.js`: typed API client for all FastAPI endpoints
- `components.js`: HTMLElement factory functions (React-component pattern)
- `graph.js`: D3.js force-directed knowledge graph
- `app.js`: state management, 5 views (home/search/entity/feed/about)
- `index.html`: semantic HTML5 shell

Colours: Saffron #FF9933 · India Green #138808 · Ashoka Blue #000080 · Navy #0A0F2E.
Dark/light theme toggle with localStorage persistence.

---

## Upcoming Phases

| Phase | Title | Key Capability |
|-------|-------|----------------|
| 14 | Zero Cold-Start Deployment | HF Spaces + Cloudflare + Service Worker |
| 15 | Mathematical Intelligence | Path signatures, Fourier, persistent homology |
| 16 | Evidence Connection Map | 6-layer deep investigation, clickable graph |
| 17 | Security Hardening | Rate limiting, audit chain, CSP headers |
| 18 | Self-Learning System | Schema adaptation, pattern discovery |
| 19 | Affidavit Trajectory | Kalman filter unexplained wealth detection |
| 20 | Biography Engine | Complete life timeline from all 28 sources |
| 21+ | Advanced Forensics | Benami, Procurement DNA, Revolving Door |

Full detail in [Phase Roadmap](PHASE_ROADMAP.md).

---

## Confirmed Live Results

```
DataGov API    3,199 real MGNREGA records
CAG            30 audit report links from cag.gov.in
PIB            27 press releases from pib.gov.in
Wikidata       Modi (Q1058), Gandhi (Q10218) confirmed
NJDG           39 court records confirmed live
Pipeline       47 records processed in 15 seconds
SHA-256        Stable, unique, 64 chars — confirmed
Language det.  Devanagari→hi, Tamil→ta, Latin→en — confirmed
Transliteration Modi→5 scripts — confirmed
```

---

## Quick Start

```bash
git clone https://github.com/abinaze/bharatgraph.git
cd bharatgraph
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
```
DATAGOV_API_KEY=register_free_at_data.gov.in_user_register
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

Run:
```bash
python -m processing.pipeline --scrapers cag,gem,pib,myneta,mca
python -m graph.loader
uvicorn api.main:app --reload
```

Open `frontend/index.html` in your browser — no server needed.

---

## Git Workflow

One long-lived branch: `main`. All branches merge directly into `main`.

```
feature/phase-N-short-name    New phase development
fix/issue-N-description        Bug fix
docs/description               Documentation only
```

Commit prefixes: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`.

---

## Reference Documents

- [Contributing Guidelines](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)
- [Phase Roadmap](PHASE_ROADMAP.md)
- [MIT License](LICENSE)
