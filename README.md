---
title: BharatGraph
emoji: 🔍
colorFrom: red
colorTo: green
sdk: docker
app_file: app.py
pinned: false
---
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

## Live Deployment

| Layer | URL |
|-------|-----|
| Frontend | https://abinaze.github.io/bharatgraph |
| API | https://abinazebinoy-bharatgraph.hf.space |
| Health | https://abinazebinoy-bharatgraph.hf.space/health |
| API Docs | https://abinazebinoy-bharatgraph.hf.space/docs |

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
  graph/          Neo4j schema, loader, Cypher queries, seed data
  ai/             Risk scoring, NLP, graph analytics, 12 investigators
  config/         22 language configs, settings
  api/            FastAPI REST + WebSocket (6 routes + admin)
  frontend/       HTML/CSS/JS dashboard, D3.js graph, dark/light theme
  templates/      Jinja2 dossier template (PDF/HTML)
  blockchain/     Audit log
  .github/        CI/CD workflows (test, deploy, daily scrape)
```

---

## Deployment Stack (Zero Cost)

| Component      | Service             | Free Allowance                     |
|----------------|---------------------|------------------------------------|
| Source code    | GitHub              | Unlimited public repos             |
| Backend API    | Hugging Face Spaces | Docker SDK — no cold start         |
| Frontend       | GitHub Pages        | Static HTML Actions workflow       |
| Graph database | Neo4j AuraDB Free   | 50K nodes, 175K relationships      |
| CDN + DDoS     | Cloudflare Free     | Unlimited caching + DDoS           |
| CI/CD          | GitHub Actions      | 2,000 min/month                    |
| Uptime monitor | UptimeRobot Free    | 5-min interval health checks       |

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

### Phase 4 — FastAPI Backend
FastAPI with lifespan, CORS, 6 route modules registered after `app = FastAPI()`,
WebSocket feed. Version 0.12.0.

### Phase 5 — Risk Scoring Engine
Composite 0–100 score. Weights: politician_company_overlap (0.35),
contract_concentration (0.25), audit_frequency (0.20), asset_anomaly (0.15),
criminal_case (0.05). `validate_language()` enforces neutral output.

### Phase 6 — Expanded Data Sources (13 scrapers)
ICIJ HTML mode (BeautifulSoup). Wikidata SPARQL confirmed. Public HF models only.

### Phase 7 — NLP Document Intelligence
spaCy `en_core_web_sm` NER. Benford's Law chi-squared test on affidavit assets.
Shadow draft detector: `all-MiniLM-L6-v2`, 93.35% alignment confirmed.

### Phase 8 — Advanced Graph Analytics
NetworkX: betweenness centrality, PageRank, Louvain community detection.
Circular ownership `simple_cycles()`. Ghost company scorer: 100/100 confirmed.

### Phase 9 — Eight New Indian Sources (21 Total Scrapers)
NJDG (39 live records confirmed), ED, CVC, NCRB, LGD, IBBI, NGO Darpan, CPPP.

### Phase 10 — Multi-Investigator AI Engine
12 parallel investigators. SHA-256 report hash: stable, unique, 64 chars.
Synthesis: 3+ investigators agreeing = HIGH confidence. `FakeSession` for offline testing.

### Phase 11 — Multilingual Platform (22 Languages)
All 22 Indian scheduled languages. Unicode detection confirmed.
Helsinki-NLP public model. Modi→मोदी/தமிழ்/తెలుగు/ಕನ್ನಡ/മലയാളം confirmed.

### Phase 12 — PDF Dossier Generator
SHA-256 integrity hash. Jinja2 + WeasyPrint (HTML fallback on Windows).
Indian tricolour design, 8 sections. 10,829 chars rendered confirmed.

### Phase 13 — Production Frontend
HTML/CSS/JS — no React, no Node.js, no build step. Works from `file://`.
D3.js force-directed graph. Dark/light theme. 5 views: home/search/entity/feed/about.

### Phase 14 — Zero Cold-Start Deployment ✓ LIVE
Hugging Face Spaces Docker SDK. No cold start on public spaces.
Service worker cache-first for static assets. GZipMiddleware (60-80% compression).
`POST /admin/seed` endpoint loads 10 politicians, 5 companies, 3 contracts.
Frontend on GitHub Pages via GitHub Actions static workflow.

---

## Upcoming Phases

| Phase | Title | Key Capability |
|-------|-------|----------------|
| **15** | **Mathematical Intelligence Engine** | Spectral graph analysis, Fourier timeline, path signatures, persistent homology, expanded Benford, mutual information + causal ranking |
| **16** | **Evidence Connection Map + Deep Investigation** | Investigation connector map with relationship labels/strength/source, 6-layer recursive engine, clickable evidence panel, hidden-link suggestions, recursive find-more button |
| **17** | **Security Hardening + Provenance** | Rate limiting, CSP/HSTS headers, SHA-256 audit chain, full provenance layer on every node/edge, deterministic artifact IDs |
| **18** | **Self-Learning + Case Memory** | Schema adaptation, pattern candidate discovery, case memory library, human-in-the-loop merge queue, investigation replay |
| **19** | **Affidavit Wealth Trajectory** | Kalman filter across 5 election cycles, unexplained wealth residual scoring, asset disappearance detection |
| **20** | **Biography Engine** | Complete chronological life timeline from all 28 sources, temporal convergence detection, narrative generation |
| **21** | **Benami Detection** | Graph embeddings, proxy network analysis, family name matching, director age anomaly |
| **22** | **Procurement DNA + Cartel Detection** | Bid document fingerprinting, price ratio analysis, cover bid detection, vendor co-bidding network |
| **23** | **Revolving Door + TBML Detection** | Career graph, cooling-off violations, trade-based money laundering flags |
| **24** | **Linguistic Fingerprinting** | Burrows' Delta authorship attribution across govt documents, template reuse detection |
| **25** | **Policy-Benefit Causal Analysis** | Granger causality, transfer entropy, Cumulative Abnormal Contract Award |
| **26** | **Adversarial Counterevidence + Competing Hypotheses** | Forced disproof search, hypothesis A/B/C mode, evidence scorecard |
| **27** | **Multi-Agent Debate Engine** | iMAD hesitation detection, 3-round structured debate, anti-drift, adaptive routing, consensus + dissent tracking |
| **28** | **Dark Pattern Detection** | PrefixSpan sequential pattern mining, 6 pre-defined high-risk patterns |
| **29** | **Source-Drift + Historical Analysis** | Wayback Machine credibility, archive-gap recovery, temporal slice viewer, claim survival scoring |
| **30** | **Predictive Risk + Auto-Prioritisation** | ARIMA + Random Forest trajectory, 6-month forecast, lead priority scores |
| **31** | **Geospatial Verification** | Sentinel-2 satellite imagery, NDVI change detection, build-completion mismatch |
| **32** | **Identity Fusion + Multimedia OSINT** | Alias-to-email linking, credential reuse detection, persona clustering, background-object analysis |

Full detail in [Phase Roadmap](PHASE_ROADMAP.md).

---

## Confirmed Live Results

```
DataGov API    3,199 real MGNREGA records
CAG            30 audit report links from cag.gov.in
PIB            27 press releases from pib.gov.in
Wikidata       Modi (Q1058), Gandhi (Q10218) confirmed live
NJDG           39 court records confirmed live
Pipeline       28 nodes loaded — 2 politicians, 2 companies, 20 audits, 4 press
SHA-256        Stable, unique, 64 chars — confirmed
Language det.  Devanagari→hi, Tamil→ta, Latin→en — confirmed
Search         Working on production HF Space
Frontend       Live at abinaze.github.io/bharatgraph
API            Live at abinazebinoy-bharatgraph.hf.space
```

---

## Quick Start

```bash
git clone https://github.com/abinaze/bharatgraph.git
cd bharatgraph
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Neo4j URI, user, password and DATAGOV_API_KEY
python -m processing.pipeline --scrapers cag,gem,pib,myneta,mca
python -m graph.loader
uvicorn api.main:app --reload
```

Open `frontend/index.html` — no server needed.

---

## Git Workflow

```
feature/phase-N-short-name    New phase development
fix/issue-N-description        Bug fix
docs/description               Documentation only
```

Commit prefixes: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`.

Never resolve merge conflicts in the GitHub web editor. Resolve locally then push.

---

## Reference Documents

- [Contributing Guidelines](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)
- [Phase Roadmap](PHASE_ROADMAP.md)
- [MIT License](LICENSE)
- [Phase Roadmap](PHASE_ROADMAP.md)
- [MIT License](LICENSE)
