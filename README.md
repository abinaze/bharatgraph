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

AI-powered public transparency and institutional intelligence platform for India.

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

## Architecture

```
bharatgraph/
  scrapers/          21 data collectors (17 Indian + 4 international)
  processing/        Name normalisation, entity resolution, parallel pipeline
  graph/             Neo4j schema, loader, Cypher queries, seed data
  ai/
    investigators/   14 parallel investigators (Phase 10 + affidavit + benami + math)
    forensics/       Affidavit, benami, bid DNA, cartel, revolving door, TBML
    biography/       Timeline builder, convergence detector, narrative generator
    math/            Spectral, Fourier, path signature analysis
    self_learning/   Schema learner, pattern learner, weight optimiser, self audit
    case_memory/     Solved case library, false positive tracking
  config/            22 language configurations
  api/
    routes/          14 API route modules
    middleware/       Rate limiter, security headers, input validator, audit logger
    models.py         Pydantic request/response models
  blockchain/        SHA-256 hash-chained audit log
  frontend/          HTML/CSS/JS dashboard (no build step required)
  templates/         Jinja2 PDF dossier template
  .github/workflows/ CI test, daily scrape, weekly learning, static deploy
```

---

## Deployment Stack

| Component | Service | Free Allowance |
|-----------|---------|----------------|
| Source code | GitHub | Unlimited public repos |
| Backend API | Hugging Face Spaces Docker | No cold start on public spaces |
| Frontend | GitHub Pages via Actions | Static HTML workflow |
| Graph database | Neo4j AuraDB Free | 50K nodes, 175K relationships |
| CDN / DDoS | Cloudflare Free | Unlimited caching |
| CI/CD | GitHub Actions | 2,000 min/month |
| Uptime monitor | UptimeRobot Free | 5-min health check intervals |

---

## Data Sources

### Indian Government (17 scrapers)

| Source | Institution | Data |
|--------|-------------|------|
| MyNeta / ECI | Election Commission | Assets, criminal cases, affidavits |
| MCA21 | Corporate Affairs | Directors, company registration |
| data.gov.in | Open Data Platform | MGNREGA, PM-KISAN |
| GeM | Government e-Marketplace | Procurement contracts |
| PIB | Press Information Bureau | Cabinet decisions |
| CAG | Comptroller and Auditor General | Audit reports, irregularities |
| Lok Sabha | Parliament | Questions, debates |
| NJDG | eCourts | Case status, court records |
| ED | Enforcement Directorate | PMLA press releases |
| SEBI | Securities Exchange Board | Enforcement orders |
| Electoral Bonds | ECI / SC disclosure | Donor-party mapping |
| CVC | Central Vigilance Commission | Vigilance advisories |
| NCRB | Crime Records Bureau | Crime statistics |
| LGD | Panchayati Raj | Local government data |
| IBBI | Insolvency Board | Corporate insolvency records |
| NGO Darpan | NITI Aayog | NGO registration and funding |
| CPPP | Procurement Portal | Procurement transparency |

### International (4 scrapers)

| Source | Data |
|--------|------|
| OpenSanctions | Global PEP and sanctions list |
| ICIJ Offshore Leaks | Panama, Pandora, Paradise Papers |
| Wikidata | Entity enrichment, career data |

---

## Completed Phases

### Phase 1 — Data Collection
7 scrapers. Confirmed live: 3,199 MGNREGA records, 30 CAG links, 27 PIB articles.
Base scraper with load_dotenv, rate limiting, JSON output.

### Phase 2 — Data Processing
Indian name normalisation with honorific and company prefix handling.
Jaccard token similarity for cross-source entity resolution. Full pipeline orchestrator.

### Phase 3 — Graph Database
Neo4j schema: 7 node types, 6 relationship types, 10 constraint queries.
MERGE with stable MD5 IDs. 8 pre-built Cypher query templates.
Connected to Neo4j AuraDB Free: neo4j+s://1a34e3b8.databases.neo4j.io

### Phase 4 — FastAPI Backend
FastAPI with lifespan context manager, CORS, 6 initial route modules.
Pydantic models with typed source citations. Neo4j dependency injection. Version 0.12.0.

### Phase 5 — Risk Scoring Engine
Composite 0-100 score. Five weighted indicators: politician_company_overlap (0.35),
contract_concentration (0.25), audit_frequency (0.20), asset_anomaly (0.15),
criminal_case (0.05). validate_language() enforces neutral analytical output.

### Phase 6 — Expanded Data Sources (13 scrapers)
ICIJ HTML scraping via BeautifulSoup. Wikidata SPARQL confirmed live.
All public HuggingFace models, no access approval required.

### Phase 7 — NLP Document Intelligence
spaCy en_core_web_sm NER. Benford's Law chi-squared test on affidavit asset figures.
Multilingual NER via Davlan/bert-base-multilingual-cased-ner-hrl.
Shadow draft detector via all-MiniLM-L6-v2: 93.35% alignment confirmed.

### Phase 8 — Advanced Graph Analytics
NetworkX: betweenness centrality, PageRank, Louvain community detection.
Circular ownership via simple_cycles: 3-node cycle confirmed.
Ghost company scorer with GHOST_THRESHOLD=60: 100/100 confirmed.

### Phase 9 — Eight New Indian Sources (21 total scrapers)
NJDG (39 live records confirmed), ED, CVC, NCRB, LGD, IBBI, NGO Darpan, CPPP.
All scrapers include sample fallback data when live source is unavailable.

### Phase 10 — Multi-Investigator AI Engine
12 parallel investigators in ThreadPoolExecutor. SHA-256 report hash: confirmed stable.
Synthesis: 3+ investigators agreeing = HIGH confidence.
FakeSession for offline unit testing. validate_language() on all output.

Investigators: financial (0.12), political (0.10), corporate (0.10), judicial (0.08),
procurement (0.12), network (0.08), asset (0.10), international (0.10), media (0.06),
historical (0.08), public_interest (0.08), doubt (0.08)

### Phase 11 — Multilingual Platform (22 Languages)
All 22 Indian scheduled languages with ISO codes and Unicode script ranges.
Language detection via Unicode block analysis confirmed: Devanagari to hi, Tamil to ta.
Helsinki-NLP/opus-mt-en-hi (public model, no gating).
Cross-script transliteration: Modi to five scripts confirmed.
Risk levels pre-translated in 9 languages. UI labels in 6 languages.

### Phase 12 — PDF Dossier Generator
SHA-256 integrity hash per report. Tamper detection confirmed.
Jinja2 + WeasyPrint (HTML fallback on Windows, PDF on Linux production).
Indian tricolour design, 8 report sections. 10,829 chars rendered confirmed.
Routes: GET /export/pdf/{entity_id}, GET /verify/{hash}

### Phase 13 — Production Frontend
HTML/CSS/JS with no React, no Node.js, no build step. Works from file:// protocol.
D3.js force-directed knowledge graph. Dark and light theme toggle.
5 views: home, search, entity, feed, about. CSS custom properties token layer.

### Phase 14 — Zero Cold-Start Deployment
Hugging Face Spaces Docker SDK. No cold start on public spaces.
Service worker cache-first for static assets. GZipMiddleware for 60-80% compression.
POST /admin/seed loads 10 politicians, 5 companies, 3 contracts into Neo4j.
GitHub Pages static deployment via Actions workflow.
UptimeRobot health check every 5 minutes to prevent Neo4j AuraDB pause.

### Phase 15 — Mathematical Intelligence Engine
Spectral graph analysis: Laplacian Fiedler value (lambda-1) for bridge entity detection.
Fourier timeline analysis: FFT on contract amount sequences for periodic pattern detection.
13th investigator (math, weight 0.08) integrated with multi-investigator engine.

### Phase 16 — Evidence Connection Map and Deep Investigation Engine
6-layer recursive investigation engine (direct, expansion, patterns, timeline,
influence, validation). Clickable graph node evidence panel showing WHY connected,
source document, confidence, and next investigation leads.
Connection mapper finds all paths between any two entities with relationship labels
(director, contract, ministry, audit, party), strength (strong/weak/uncertain),
and WHY/HOW/SOURCE on every edge.
Routes: GET /investigate/{id}, GET /connection-map, GET /node-evidence/{id}

### Phase 17 — Security Hardening and Provenance Layer
Sliding window rate limiter: 100/min search, 30/min investigate, 10/min export, 5/min admin.
IP stored as SHA-256 hash for privacy. Returns 429 with Retry-After header.
HTTP security headers: CSP, HSTS, X-Frame-Options, nosniff, Referrer-Policy.
Input validator: 200-char max, Cypher injection detection, Indian script Unicode allowlist.
Append-only SHA-256 hash-chained audit log in logs/audit.jsonl.
Daily root hash anchored in Neo4j AuditRoot node via blockchain/audit_chain.py.

### Phase 18 — Self-Learning System and Case Memory
Schema learner: detects new fields in scraper output, writes to pending_schema_additions.json
for human review. Never auto-applies changes to production schema.
Pattern learner: weekly subgraph pattern candidate discovery via known pattern queries
and high-directorship motif detection. Writes to pattern_candidates_YYYYMMDD.json.
Weight optimiser: records confirmed and unconfirmed investigation outcomes.
Adjusts indicator weights by delta 0.01/0.005 after minimum 3 confirmed cases.
Self-audit: imports all 20 scrapers, verifies expected class exists, flags failures as
GitHub Actions warnings. Weekly workflow: .github/workflows/weekly_learn.yml.
Case memory: saves investigation findings with outcome and reasoning path.
find_similar() retrieves past cases with overlapping finding types.

### Phase 19 — Affidavit Wealth Trajectory Engine
Kalman filter constant-velocity model on affidavit time series across 5 election cycles.
Innovation |z_k - H*x_hat_k| > 3*sqrt(S_k) = anomaly flag.
Expected growth model: initial + 8% FD returns + 60% salary savings.
Residual ratio: > 2x = HIGH, > 5x = VERY_HIGH unexplained wealth level.
Asset disappearance detection across years. Pre-election movable asset surge detection.
Test result: VERY_HIGH level, Rs 42.7 Cr residual (7.1x), 3 Kalman anomalies, 4 findings.
14th investigator (affidavit, weight 0.10). Route: GET /affidavit/{entity_id}

### Phase 20 — Biography Engine
Chronological life timeline from elections (ECI), contracts (GeM), audit mentions (CAG),
court proceedings (NJDG), press releases (PIB), and corporate directorships (MCA).
Events sorted by date, grouped by year, colour-coded by category.
Temporal convergence detection across 5 window types: election+contract (90d),
election+company (180d), audit+contract (365d), court+company (180d), election+audit (365d).
Severity: HIGH/MODERATE/LOW based on proximity within window.
Neutral narrative generation with FORBIDDEN word enforcement and source disclaimers.
Route: GET /biography/{entity_id}. Frontend: frontend/js/timeline.js.

### Phase 21 — Benami Entity Detection
5-factor composite proxy scoring (0-100): director age anomaly (0.25), surname network
(0.25), address clustering (0.20), company formed before contract (0.20), single-director
structure (0.10). Level: HIGH >= 65, MODERATE >= 40, LOW < 40.
All 5 factors fallback-safe when database unavailable.
15th investigator (benami, weight 0.09). Route: GET /benami/{entity_id}

### Phase 22 — Procurement DNA and Cartel Detection
Bid document fingerprinting via TF-IDF cosine similarity.
Similarity threshold 0.72 flags near-identical bids from different vendors.
Cover-bid detection via price clustering analysis (standard deviation test).
Vendor cartel detection: award rotation (equal share pattern), co-bidding network
(same vendor pairs appearing together across multiple tenders).
Routes: GET /procurement/bid-dna/{id}, GET /procurement/cartel?ministry=...

### Phase 22 (continued) — Full Pipeline Expansion
Pipeline expanded from 5 to all 20 scrapers with parallel ThreadPoolExecutor execution.
POST /admin/pipeline triggers full pipeline in background on HF Space.
GET /admin/pipeline/status shows running state and last result per source.
GET /sources shows record count per dataset loaded into Neo4j.
GET /sources/{dataset} shows sample records from a specific dataset.

### Phase 23 — Revolving Door and TBML Detection
Revolving door: career transition detector with cooling-off violation scoring.
Flags government-to-private transitions within 365-day cooling-off window.
Pre-employment benefit scoring: contracts awarded to future employer before appointment.
TBML indicators: contract price anomaly (2.5 sigma from entity mean), subcontract loop
detection via Neo4j cycle queries, director-change-near-award window detection (90 days).
Routes: GET /conflict/revolving-door/{id}, GET /conflict/tbml/{id}

---

## Upcoming Phases

| Phase | Title | Key Capability |
|-------|-------|----------------|
| 24 | Linguistic Fingerprinting | Burrows Delta authorship attribution, template reuse |
| 25 | Policy-Benefit Causal Analysis | Granger causality, transfer entropy, CACA |
| 26 | Adversarial Counterevidence | Forced disproof, competing hypothesis scorecard |
| 27 | Multi-Agent Debate Engine | iMAD hesitation detection, 3-round structured debate |
| 28 | Dark Pattern Detection | PrefixSpan sequential mining, 6 high-risk patterns |
| 29 | Source-Drift and Historical Analysis | Wayback Machine credibility, claim survival scoring |
| 30 | Predictive Risk and Auto-Prioritisation | ARIMA + Random Forest trajectory, 6-month forecast |
| 31 | Geospatial Verification | Sentinel-2 NDVI, build-completion mismatch detection |
| 32 | Identity Fusion and Multimedia OSINT | Alias-email linking, persona clustering |

Full detail in [Phase Roadmap](PHASE_ROADMAP.md).

---

## Confirmed Live Results

```
DataGov API         3,199 real MGNREGA records
CAG                 30 audit report links from cag.gov.in
PIB                 27 press releases from pib.gov.in
Wikidata            Modi (Q1058), Gandhi (Q10218) confirmed live
NJDG                39 court records confirmed live
Pipeline            28 nodes loaded on first run
SHA-256 hash        Stable, unique, 64 chars confirmed
Language detection  Devanagari to hi, Tamil to ta confirmed
Cross-script search Modi to 5 scripts confirmed
Search              Working on production HF Space
Frontend            Live at abinaze.github.io/bharatgraph
API                 Live at abinazebinoy-bharatgraph.hf.space
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
# Edit .env with your NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, DATAGOV_API_KEY
python -m processing.pipeline
python -m graph.loader
uvicorn api.main:app --reload
```

Open frontend/index.html in your browser. No server required.

To seed the production database when running locally is not possible:

```bash
curl -X POST https://abinazebinoy-bharatgraph.hf.space/admin/seed
curl -X POST "https://abinazebinoy-bharatgraph.hf.space/admin/pipeline?scrapers=all"
```

---

## Git Workflow

One long-lived branch: main. All feature branches merge directly into main.

```
feature/phase-N-short-name    New phase development
fix/issue-description          Bug fix
docs/description               Documentation only
```

Commit prefixes: feat, fix, docs, test, chore, refactor.
Never resolve merge conflicts using the GitHub web editor. Resolve locally then push.

---

## Reference Documents

- [Contributing Guidelines](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)
- [Phase Roadmap](PHASE_ROADMAP.md)
- [MIT License](LICENSE)
