---
title: BharatGraph
emoji: 🔍
colorFrom: red
colorTo: green
sdk: docker
app_file: app.py
pinned: false
---

# BharatGraph — Public Transparency Intelligence Platform

[![API Health](https://img.shields.io/badge/API-Live-brightgreen)](https://abinazebinoly-bharatgraph.hf.space/health)
[![Frontend](https://img.shields.io/badge/Frontend-Live-blue)](https://abinaze.github.io/bharatgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.29.0-orange)](PHASE_ROADMAP.md)

BharatGraph aggregates official Indian government records — corporate filings, audit reports, parliamentary data, procurement contracts, court judgments, and international investigative datasets — into a unified Neo4j knowledge graph. It applies entity resolution, graph analytics, and multi-agent AI reasoning to surface structural relationships between politicians, companies, contracts, ministries, and public schemes.

**Every output is traceable to a primary source document. The platform does not make accusations — it identifies structural patterns and governance anomalies derived from publicly available information.**

---

## Live Deployment

| Layer | URL |
|-------|-----|
| 🌐 Frontend | https://abinaze.github.io/bharatgraph |
| ⚡ API | https://abinazebinoly-bharatgraph.hf.space |
| 🏥 Health | https://abinazebinoly-bharatgraph.hf.space/health |
| 📖 API Docs | https://abinazebinoly-bharatgraph.hf.space/docs |
| 📦 Source | https://github.com/abinaze/bharatgraph |

---

## API Reference (v0.29.0)

### Core Search & Profiles
| Method | Path | Description |
|--------|------|-------------|
| GET | `/search?q={term}&type={type}` | Full-text search across all 16 node types |
| GET | `/profile/{id}` | Entity profile with declared assets, risk score, sections |
| GET | `/graph/{id}` | D3-compatible force graph neighbourhood |
| GET | `/risk/{id}` | Composite structural risk indicators (0–100) |
| GET | `/stats` | Node and relationship counts from Neo4j |
| GET | `/health` | API health check (GET + HEAD) |

### Investigation Engine
| Method | Path | Description |
|--------|------|-------------|
| GET | `/investigate/{id}` | 6-layer deep investigation (direct → expansion → patterns → timeline → influence → validation) |
| GET | `/node-evidence/{id}` | All edges with WHY / source / next-leads explanations |
| GET | `/connection-map?a={id}&b={id}` | Shortest path with relationship explanations |

### Forensic Analysis Modules
| Method | Path | Description |
|--------|------|-------------|
| GET | `/biography/{id}` | AI-generated chronological timeline with temporal convergence detection |
| GET | `/affidavit/{id}` | Kalman-filter wealth trajectory + anomaly detection |
| GET | `/benami/{id}` | 5-factor proxy ownership scoring (0–100) |
| GET | `/adversarial/{id}` | Competing hypotheses — forced counterevidence analysis |
| GET | `/debate/{id}` | 7-agent structured debate with consensus and dissent |
| GET | `/linguistic/fingerprint/{id}` | Burrows Delta authorship attribution |
| GET | `/policy/causal/{id}` | Granger causality + transfer entropy (CACA) |

### Procurement & Corporate
| Method | Path | Description |
|--------|------|-------------|
| GET | `/procurement/bid-dna/{id}` | TF-IDF bid document fingerprinting (≥0.72 = flag) |
| GET | `/procurement/cartel` | Award rotation + cover-bid cartel detection |
| GET | `/conflict/revolving-door/{id}` | 365-day cooling-off violation scoring |
| GET | `/conflict/tbml/{id}` | Trade-based money laundering indicators |

### Export & Admin
| Method | Path | Description |
|--------|------|-------------|
| GET | `/export/{id}` | PDF/HTML dossier with SHA-256 integrity hash |
| GET | `/sources` | All 21 data sources with record counts |
| POST | `/admin/seed` | Seed sample politicians, companies, contracts + relationships |
| POST | `/admin/pipeline?scrapers=all` | Trigger full 21-scraper background pipeline |
| GET | `/admin/pipeline/status` | Pipeline running state and last result per source |

---

## Architecture

```
bharatgraph/
  scrapers/          22 data collectors (17 Indian + 4 international + 1 wikidata)
  graph/             Neo4j schema (16 node types), loader (15 loaders), seed, queries
  processing/        Name normalisation, entity resolution (Jaccard), parallel pipeline
  ai/
    investigators/   15 parallel investigators
    forensics/       Affidavit, benami, bid DNA, cartel, revolving door, TBML, linguistic, policy
    biography/       Timeline builder, convergence detector, narrative generator
    math/            Spectral (Fiedler), Fourier FFT, path signature analysis
    self_learning/   Schema learner, pattern learner, weight optimiser, self-audit
    case_memory/     Solved case library, false positive tracking
  config/            22 language configurations (all Indian scheduled languages)
  api/
    routes/          19 route modules
    middleware/       Rate limiter, security headers, input validator, audit logger
    models.py         Pydantic request/response models
  blockchain/        SHA-256 hash-chained append-only audit log
  frontend/          Vanilla HTML/CSS/JS (no build step)
  templates/         Jinja2 PDF dossier template
  .github/workflows/ CI test, daily scrape, weekly learning, static deploy
```

---

## Data Sources (21 total)

### Indian Government (17 scrapers)

| # | Source | Records Type | Investigation Use |
|---|--------|--------------|-------------------|
| 1 | MyNeta / ECI | `Politician` | Assets, criminal cases, affidavits |
| 2 | MCA21 | `Company` | Directors, incorporation, status |
| 3 | GeM | `Contract` | Procurement, amounts, buyers |
| 4 | CAG | `AuditReport` | Audit flags, financial irregularities |
| 5 | PIB | `PressRelease` | Cabinet decisions, policy announcements |
| 6 | Lok Sabha | `ParliamentQuestion` | Questions, debates, members |
| 7 | SEBI | `RegulatoryOrder` | Securities enforcement orders |
| 8 | ED | `EnforcementAction` | PMLA press releases, attachments |
| 9 | CVC | `VigilanceCircular` | Vigilance advisories |
| 10 | Electoral Bonds | `ElectoralBond` | Donor-to-party transaction mapping |
| 11 | IBBI | `InsolvencyOrder` | Corporate insolvency records |
| 12 | NGO Darpan | `NGO` | NGO registration and funding |
| 13 | CPPP | `Tender` | Procurement transparency |
| 14 | NCRB | `CrimeReport` | Crime statistics by state |
| 15 | LGD | `LocalBody` | Local government directory |
| 16 | DataGov | `Document` | Multi-schema open datasets |
| 17 | NJDG | `CourtCase` | eCourts case status records |

### International (4 scrapers)

| # | Source | Records Type | Investigation Use |
|---|--------|--------------|-------------------|
| 18 | ICIJ Offshore Leaks | `ICIJEntity` | Panama, Pandora, Paradise Papers |
| 19 | OpenSanctions | `SanctionedEntity` | Global PEP and sanctions lists |
| 20 | Wikidata | Enriches `Politician` | Career data, entity disambiguation |
| 21 | UN SDG | `Document` | Development scheme tracking |

---

## Investigation Graph Model

```
(Politician)-[:MEMBER_OF]->(Party)
(Politician)-[:DIRECTOR_OF]->(Company)
(Politician)-[:CONTESTED_IN]->(Election)
(Company)-[:WON_CONTRACT]->(Contract)
(Contract)-[:AWARDED_BY]->(Ministry)
(AuditReport)-[:FLAGS]->(Scheme)
(AuditReport)-[:MENTIONS]->(Ministry)
(PressRelease)-[:ISSUED_BY]->(Ministry)
(Company)-[:ASSOCIATED_WITH]->(ICIJEntity)
(Politician)-[:ASSOCIATED_WITH]->(SanctionedEntity)
```

---

## Completed Phases (1–28)

### Phase 1 — Data Collection
**Files:** `scrapers/base_scraper.py` + 6 scrapers  
**Summary:** Base scraper class with rate limiting and JSON output. First 6 live scrapers confirmed. MGNREGA: 3,199 records; CAG: 30 links; PIB: 27 articles.

### Phase 2 — Data Processing
**Files:** `processing/cleaner.py`, `processing/entity_resolver.py`, `processing/pipeline.py`  
**Summary:** Indian name normalisation (honorifics, company prefixes). Jaccard token similarity for cross-source entity resolution. Parallel pipeline orchestrator. 47 records processed in 15 seconds.

### Phase 3 — Graph Database
**Files:** `graph/schema.py`, `graph/loader.py`, `graph/queries.py`  
**Summary:** Neo4j AuraDB connected. 7 node types, 6 relationship types, 10 Cypher constraint queries. MERGE with stable MD5 IDs. Connected to: `neo4j+s://1a34e3b8.databases.neo4j.io`

### Phase 4 — FastAPI Backend
**Files:** `api/main.py`, `api/models.py`, `api/dependencies.py`, 4 route modules  
**Summary:** FastAPI with lifespan context, CORS, Pydantic models with source citations, Neo4j dependency injection. Version 0.12.0.

### Phase 5 — Risk Scoring Engine
**Files:** `ai/indicators.py`, `ai/explainer.py`, `ai/risk_scorer.py`  
**Summary:** Composite 0–100 structural risk score. Five weighted indicators: politician_company_overlap (0.35), contract_concentration (0.25), audit_frequency (0.20), asset_anomaly (0.15), criminal_case (0.05). `validate_language()` enforces neutral analytical output on all routes.

### Phase 6 — Expanded Data Sources (13 scrapers)
**Files:** `icij_scraper.py`, `wikidata_scraper.py`, `opensanctions_scraper.py`, `loksabha_scraper.py`, `sebi_scraper.py`, `electoral_bond_scraper.py`  
**Summary:** ICIJ HTML parsing via BeautifulSoup. Wikidata SPARQL live confirmed. All public HuggingFace models, no gating required.

### Phase 7 — NLP Document Intelligence
**Files:** `ai/nlp_extractor.py`, `ai/benfords_analyzer.py`, `ai/multilingual_ner.py`, `ai/shadow_draft_detector.py`  
**Summary:** spaCy `en_core_web_sm` NER. Benford's Law chi-squared test on affidavit asset figures. Multilingual NER via `Davlan/bert-base-multilingual-cased-ner-hrl`. Shadow draft detector: 93.35% alignment confirmed.

### Phase 8 — Advanced Graph Analytics
**Files:** `ai/graph_analytics.py`, `ai/circular_ownership.py`, `ai/shadow_director.py`, `ai/ghost_company.py`  
**Summary:** NetworkX: betweenness centrality, PageRank, Louvain community detection. Circular ownership via `simple_cycles`: 3-node cycle confirmed. Ghost company scorer with GHOST_THRESHOLD=60: 100/100 confirmed.

### Phase 9 — Eight New Indian Sources (21 total)
**Files:** `njdg_scraper.py`, `ed_scraper.py`, `cvc_scraper.py`, `ncrb_scraper.py`, `lgd_scraper.py`, `ibbi_scraper.py`, `ngo_darpan_scraper.py`, `cppp_scraper.py`  
**Summary:** NJDG: 39 live court records confirmed. All scrapers include sample fallback data when live source is rate-limited or unavailable.

### Phase 10 — Multi-Investigator AI Engine
**Files:** `ai/multi_investigator.py`, `ai/investigators/` (12 files)  
**Summary:** 12 parallel investigators in `ThreadPoolExecutor`. SHA-256 report hash stable. Synthesis: 3+ investigators agreeing = HIGH confidence. 12 specialists: financial (0.12), political (0.10), corporate (0.10), judicial (0.08), procurement (0.12), network (0.08), asset (0.10), international (0.10), media (0.06), historical (0.08), public_interest (0.08), doubt (0.08).

### Phase 11 — Multilingual Platform (22 Languages)
**Files:** `config/languages.py`, `ai/translator.py`, `ai/transliteration.py`, `api/routes/multilingual.py`  
**Summary:** All 22 Indian scheduled languages with ISO codes and Unicode script ranges. Language detection via Unicode block analysis confirmed. Helsinki-NLP/opus-mt-en-hi for translation. Cross-script transliteration: "Modi" to five scripts confirmed.

### Phase 12 — PDF Dossier Generator
**Files:** `ai/report_hasher.py`, `ai/dossier_generator.py`, `templates/dossier_en.html`, `api/routes/export.py`  
**Summary:** SHA-256 integrity hash per report with tamper detection. Jinja2 + WeasyPrint (HTML fallback on Windows). Indian tricolour design, 8 report sections. 10,829 chars rendered confirmed.

### Phase 13 — Production Frontend
**Files:** `frontend/index.html`, `frontend/css/` (2 files), `frontend/js/` (5 files)  
**Summary:** Vanilla HTML/CSS/JS — no React, no Node.js, no build step. Works from `file://` protocol. D3.js force-directed knowledge graph. Dark/light theme toggle. 5 views: home, search, entity, feed, about.

### Phase 14 — Zero Cold-Start Deployment
**Files:** `app.py`, `Dockerfile`, `frontend/sw.js`, `.github/workflows/static.yml`, `graph/seed.py`, `api/routes/admin.py`  
**Summary:** Hugging Face Spaces Docker (no cold start on public spaces). Service worker cache-first for static assets. GZipMiddleware (60–80% compression). `POST /admin/seed` loads sample data. GitHub Pages deploy via Actions.

### Phase 15 — Mathematical Intelligence Engine
**Files:** `ai/math/__init__.py`, `ai/math/spectral_analyzer.py`, `ai/math/fourier_timeline.py`, `ai/investigators/math_investigator.py`  
**Summary:** Spectral graph analysis: Laplacian Fiedler value (λ₁) for bridge entity detection. Fourier timeline analysis: FFT on contract amount sequences for periodic pattern detection. 13th investigator (math, weight 0.08).

### Phase 16 — Evidence Connection Map and Deep Investigation Engine
**Files:** `ai/deep_investigator.py`, `ai/connection_mapper.py`, `api/routes/investigation.py`, `frontend/js/evidence_panel.js`  
**Summary:** 6-layer recursive investigation (direct → expansion → patterns → timeline → influence → validation). Evidence panel shows WHY each entity is connected, source document, confidence, and next investigation leads. Connection mapper finds shortest paths with relationship-level explanations. Routes: `/investigate/{id}`, `/connection-map`, `/node-evidence/{id}`.

### Phase 17 — Security Hardening and Provenance Layer
**Files:** `api/middleware/rate_limiter.py`, `api/middleware/security_headers.py`, `api/middleware/input_validator.py`, `api/middleware/audit_logger.py`, `blockchain/audit_chain.py`  
**Summary:** Sliding window rate limiter: 100/min search, 30/min investigate, 10/min export, 5/min admin. IPs stored as SHA-256 hash. HTTP security headers (CSP, HSTS, X-Frame-Options). Input validator: 200-char max, Cypher injection detection. Append-only SHA-256 hash-chained audit log.

### Phase 18 — Self-Learning System and Case Memory
**Files:** `ai/self_learning/`, `ai/case_memory/`, `.github/workflows/weekly_learn.yml`  
**Summary:** Schema learner detects new fields in scraper output, writes to `pending_schema_additions.json` for human review. Pattern learner discovers subgraph candidates weekly. Weight optimiser adjusts indicator weights (±0.01/0.005) after 3+ confirmed cases. Case memory saves investigation findings with outcome and reasoning path.

### Phase 19 — Affidavit Wealth Trajectory Engine
**Files:** `ai/forensics/affidavit_analyzer.py`, `ai/investigators/affidavit_investigator.py`, `api/routes/affidavit.py`  
**Summary:** Kalman filter constant-velocity model across 5 election cycles. Innovation |z_k − H·x̂_k| > 3√S_k = anomaly flag. Expected growth: 8% FD returns + 60% salary savings. Residual ratio >2x = HIGH, >5x = VERY_HIGH. Pre-election movable asset surge detection. Test: VERY_HIGH level, ₹42.7 Cr residual (7.1×), 3 Kalman anomalies.

### Phase 20 — Biography Engine
**Files:** `ai/biography/biography_generator.py`, `ai/biography/timeline_builder.py`, `ai/biography/convergence_detector.py`, `frontend/js/timeline.js`  
**Summary:** Chronological timeline from ECI, GeM, CAG, NJDG, PIB, MCA. Events sorted by date, grouped by year, colour-coded by category. 5 temporal convergence window types: election+contract (90d), election+company (180d), audit+contract (365d), court+company (180d), election+audit (365d). Neutral narrative generation with forbidden-word enforcement.

### Phase 21 — Benami Entity Detection
**Files:** `ai/forensics/benami_detector.py`, `ai/investigators/benami_investigator.py`, `api/routes/benami.py`  
**Summary:** 5-factor proxy scoring (0–100): director age anomaly (0.25), surname network (0.25), address clustering (0.20), company-before-contract (0.20), single-director structure (0.10). Threshold: HIGH ≥65, MODERATE ≥40. All 5 factors fallback-safe when database is unavailable.

### Phase 22 — Procurement DNA, Cartel Detection, and Full Pipeline Expansion
**Files:** `ai/forensics/bid_dna.py`, `ai/forensics/cartel_detector.py`, `api/routes/procurement.py`  
**Summary:** TF-IDF cosine similarity: ≥0.72 flags near-identical bids from different vendors. Cover-bid detection via price clustering (standard deviation test). Vendor cartel detection: award rotation + co-bidding network analysis. Pipeline expanded to all 20 scrapers with `ThreadPoolExecutor`. `POST /admin/pipeline` triggers background ingestion. `GET /sources` shows record counts.

### Phase 23 — Revolving Door and TBML Detection
**Files:** `ai/forensics/revolving_door.py`, `ai/forensics/tbml_detector.py`, `api/routes/conflict.py`  
**Summary:** Career transition detector with 365-day cooling-off violation scoring. Pre-employment benefit scoring: contracts to future employer before appointment. TBML: price anomaly (2.5σ), subcontract loop detection via Neo4j cycle queries, director-change-near-award (90-day window).

### Phase 24 — Linguistic Fingerprinting
**Files:** `ai/forensics/linguistic_fingerprint.py`, `api/routes/linguistic.py`  
**Summary:** Burrows Delta authorship attribution (Argamon's variant). Function-word frequency analysis. Template reuse detection across procurement documents. Ghost-writing similarity scoring against known ministerial speech corpora.

### Phase 25 — Policy-Benefit Causal Analysis
**Files:** `ai/forensics/policy_benefit_analyzer.py`, `api/routes/policy.py`  
**Summary:** Granger causality test (lag 1–6 months) between policy announcements and company valuations. Transfer entropy for information-theoretic causality. CACA (Confound-Adjusted Causal Attribution) scoring. Cross-ministry benefit chain detection.

### Phase 26 — Adversarial Counterevidence
**Files:** `ai/adversarial_engine.py`, `api/routes/adversarial.py`  
**Summary:** Forced disproof methodology: system actively searches for evidence that contradicts its own findings. Competing hypothesis scorecard: each hypothesis scored for/against evidence. Uncertainty propagation across multi-hop paths.

### Phase 27 — Multi-Agent Debate Engine
**Files:** `ai/debate_engine.py`, `api/routes/debate.py`  
**Summary:** 7-agent structured 3-round debate. iMAD hesitation detection (agents that change position signal contested evidence). Consensus scoring with explicit support/against/uncertain counts. Dissent preservation: minority findings retained in final report.

### Phase 28 — Dark Pattern Detection
**Files:** `ai/dark_pattern_detector.py`  
**Summary:** PrefixSpan sequential pattern mining on procurement sequences. 6 pre-defined high-risk administrative sequences (single-bidder → short-window → above-threshold). Timing window significance test. Route: `GET /darkpattern/{entity_id}`.

### Phase 29 — UX Overhaul + Investigation Fixes (v0.29.0)
**Files:** `frontend/js/app.js`, `frontend/js/evidence_panel.js`, `frontend/index.html`, `frontend/sw.js`, `ai/deep_investigator.py`, `ai/connection_mapper.py`, `graph/seed.py`, `api/routes/admin.py`  
**Summary:** Fixed critical loading bug (23 invalid `\`` sequences from Python string injection caused silent JS parse failure). Fixed 13 `\${` blocking template substitution. Bumped SW cache to v3 to force old-cache invalidation. Evidence panel rewritten with 4 tabs (Overview, Connections, Timeline, Investigate). Deep investigator rewritten with confidence scoring and richer Cypher queries. Connection mapper returns WHY/source/next-leads on every edge. Seed data now includes DIRECTOR_OF and WON_CONTRACT relationships. Language selector (22 Indian languages). Connection map route with D3 interactive graph.

---

## Upcoming Phases

See [PHASE_ROADMAP.md](PHASE_ROADMAP.md) for full detail.

| Phase | Title | Priority |
|-------|-------|----------|
| 30 | Source-Drift + Historical Analysis | HIGH |
| 31 | Predictive Risk + Lead Prioritisation | HIGH |
| 32 | Entity Resolution v2 (canonical IDs) | CRITICAL |
| 33 | Contradiction Engine | HIGH |
| 34 | Multi-Agent Orchestration | HIGH |
| 35 | Graph Intelligence (anomaly, link prediction) | HIGH |
| 36 | Provenance + Evidence Audit Layer | HIGH |
| 37 | Watchlist + Alerts | MEDIUM |
| 38 | Full Data Pipeline (367+ sources) | CRITICAL |
| 39 | Geospatial Verification (Sentinel-2) | MEDIUM |
| 40 | DeepSeek-R1 Reasoning Integration | HIGH |
| 41 | DeepSeek-VL2 Visual Evidence Analysis | MEDIUM |
| 42 | DeepSeek-V3 Report Generation | HIGH |
| 43 | Observability + Pipeline Reliability | HIGH |
| 44 | Report Export + Legal-Safe Output | HIGH |
| 45 | Full 22-Language Output Engine | HIGH |
| 46 | Security Hardening + PII Protection | HIGH |
| 47 | Evidence Graph Frontend Upgrade | HIGH |
| 48 | Confidence + Scoring Framework | HIGH |
| 49 | User Workflows + Investigation Workspace | MEDIUM |
| 50 | Production Launch | PLANNED |

---

## Deployment Stack

| Component | Service | Free Allowance |
|-----------|---------|----------------|
| Source code | GitHub | Unlimited public repos |
| Backend API | Hugging Face Spaces Docker | No cold start on public spaces |
| Frontend | GitHub Pages via Actions | Static HTML workflow |
| Graph database | Neo4j AuraDB Free | 50K nodes, 175K relationships |
| CI/CD | GitHub Actions | 2,000 min/month |
| Uptime monitor | UptimeRobot Free | 5-min health check intervals |

---

## Quick Start

```bash
git clone https://github.com/abinaze/bharatgraph.git
cd bharatgraph
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, DATAGOV_API_KEY

# Seed sample data (nodes + relationships)
python -m graph.seed

# OR start the API and seed via HTTP
uvicorn api.main:app --reload
curl -X POST http://localhost:8000/admin/seed
curl -X POST http://localhost:8000/admin/pipeline

# Open frontend
open frontend/index.html
```

**Production seeding:**
```bash
curl -X POST https://abinazebinoly-bharatgraph.hf.space/admin/seed
curl -X POST "https://abinazebinoly-bharatgraph.hf.space/admin/pipeline?scrapers=all"
```

---

## Confirmed Live Results

```
DataGov API          3,199 real MGNREGA records
CAG                  30 audit report links from cag.gov.in
PIB                  27 press releases from pib.gov.in
Wikidata             Modi (Q1058), Gandhi (Q10218) confirmed live
NJDG                 39 court records confirmed live
Pipeline             28 nodes loaded on first run
SHA-256 hash         Stable, unique, 64 chars confirmed
Language detection   Devanagari → hi, Tamil → ta confirmed
Cross-script search  "Modi" → 5 scripts confirmed
Frontend             Live at abinaze.github.io/bharatgraph
API                  Live at abinazebinoly-bharatgraph.hf.space
```

---

## Reference Documents

- [Phase Roadmap](PHASE_ROADMAP.md) — All 50 phases with summaries
- [Contributing Guidelines](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)
- [MIT License](LICENSE)
