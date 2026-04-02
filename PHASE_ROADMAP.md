# BharatGraph — Complete Phase Roadmap

All branches merge directly into `main`. One branch per phase.
Branch naming: `feature/phase-N-name` or `fix/issue-N-name`.

---

## COMPLETED

### Phase 1 — Data Collection
Branch: `feature/phase-1-scrapers`
Files: `scrapers/base_scraper.py`, `scrapers/datagov_scraper.py`, `scrapers/pib_scraper.py`,
`scrapers/myneta_scraper.py`, `scrapers/mca_scraper.py`, `scrapers/cag_scraper.py`,
`scrapers/gem_scraper.py`
Status: MERGED — 3,199 live records confirmed

### Phase 2 — Data Processing
Branch: `feature/phase-2-processing`
Files: `processing/cleaner.py`, `processing/entity_resolver.py`, `processing/pipeline.py`
Status: MERGED — 47 records in 15 seconds confirmed

### Phase 3 — Graph Database
Branch: `feature/phase-3-graph`
Files: `graph/schema.py`, `graph/loader.py`, `graph/queries.py`
Status: MERGED — Neo4j AuraDB connected

### Phase 4 — FastAPI Backend
Branch: `feature/phase-4-api`
Files: `api/main.py`, `api/models.py`, `api/dependencies.py`,
`api/routes/search.py`, `api/routes/profile.py`, `api/routes/graph.py`,
`api/routes/risk.py`
Status: MERGED — v0.12.0

### Phase 5 — Risk Scoring Engine
Branch: `feature/phase-5-risk`
Files: `ai/indicators.py`, `ai/explainer.py`, `ai/risk_scorer.py`
Status: MERGED — validate_language() enforced

### Phase 6 — Expanded Data Sources (13 scrapers)
Branch: `feature/phase-6-scrapers`
Files: `scrapers/icij_scraper.py`, `scrapers/wikidata_scraper.py`,
`scrapers/opensanctions_scraper.py`, `scrapers/loksabha_scraper.py`,
`scrapers/sebi_scraper.py`, `scrapers/electoral_bond_scraper.py`
Status: MERGED — Wikidata SPARQL confirmed live

### Phase 7 — NLP Document Intelligence
Branch: `feature/phase-7-nlp`
Files: `ai/nlp_extractor.py`, `ai/benfords_analyzer.py`,
`ai/multilingual_ner.py`, `ai/shadow_draft_detector.py`
Status: MERGED — 93.35% shadow draft alignment confirmed

### Phase 8 — Advanced Graph Analytics
Branch: `feature/phase-8-graph-analytics`
Files: `ai/graph_analytics.py`, `ai/circular_ownership.py`,
`ai/shadow_director.py`, `ai/ghost_company.py`
Status: MERGED — Ghost company 100/100 confirmed

### Phase 9 — Eight New Indian Sources (21 total scrapers)
Branch: `feature/phase-9-scrapers`
Files: `scrapers/njdg_scraper.py`, `scrapers/ed_scraper.py`,
`scrapers/cvc_scraper.py`, `scrapers/ncrb_scraper.py`, `scrapers/lgd_scraper.py`,
`scrapers/ibbi_scraper.py`, `scrapers/ngo_darpan_scraper.py`, `scrapers/cppp_scraper.py`
Status: MERGED — NJDG 39 live records confirmed

### Phase 10 — Multi-Investigator AI Engine
Branch: `feature/phase-10-multi-investigator`
Files: `ai/multi_investigator.py`, `ai/investigators/__init__.py`,
`ai/investigators/financial_investigator.py` (×12 total)
Status: MERGED — SHA-256 hash confirmed, synthesis working

### Phase 11 — Multilingual Platform
Branch: `feature/phase-11-multilingual`
Files: `config/languages.py`, `ai/translator.py`, `ai/transliteration.py`,
`api/routes/multilingual.py`
Status: MERGED — 22 languages, cross-script search confirmed

### Phase 12 — PDF Dossier Generator
Branch: `feature/phase-12-pdf-dossier`
Files: `ai/report_hasher.py`, `ai/dossier_generator.py`,
`templates/dossier_en.html`, `api/routes/export.py`
Status: MERGED — 10,829 char HTML confirmed, SHA-256 tamper detection working

### Phase 13 — Production Frontend
Branch: `feature/phase-13-frontend`
Files: `frontend/index.html`, `frontend/css/design-system.css`,
`frontend/css/components.css`, `frontend/js/router.js`,
`frontend/js/api.js`, `frontend/js/components.js`,
`frontend/js/graph.js`, `frontend/js/app.js`
Status: MERGED — works from file:// protocol, D3.js graph confirmed

---

## NEXT — Phase 14

### Phase 14 — Zero Cold-Start Deployment
Branch: `feature/phase-14-deployment`

**Problem:** Render free tier sleeps after 15 minutes. Users get 30-60 second
delays. Hugging Face Spaces with Docker SDK do not sleep on public spaces.

**Files to create:**
```
app.py                              HF Space ASGI entry point
Dockerfile                          Docker SDK config (port 7860)
frontend/sw.js                      Service worker (offline-first)
.github/workflows/deploy_hf.yml     Auto-deploy to HF on main push
.github/workflows/daily_scrape.yml  Cron 02:00 IST daily scrape
.github/workflows/test.yml          CI on every push/PR
```

**Changes to existing files:**
```
api/main.py        Add GZipMiddleware + Cache-Control headers
frontend/index.html  Register service worker, add preconnect hints
```

See step-by-step instructions below.

---

## PLANNED

### Phase 15 — Mathematical Intelligence Engine
6 analytical frameworks: Spectral graph (Fiedler value), Fourier timeline,
Path signatures (rough path theory), Persistent homology (topological),
Expanded Benford (Nigrini sub-tests), Mutual information (causal ranking).
Files: `ai/math/` (6 modules), `ai/investigators/math_investigator.py`

### Phase 16 — Evidence Connection Map + Deep Investigation
6-layer recursive investigation engine. Clickable graph nodes open evidence
detail panel showing WHY connected, source, confidence, timeline, next leads.
Files: `ai/deep_investigator.py`, `ai/connection_mapper.py`,
`api/routes/investigation.py`, `frontend/js/evidence_panel.js`

### Phase 17 — Security Hardening
Sliding window rate limiter (100/min search, 10/min export).
Input validation, HTTP security headers (CSP, HSTS, X-Frame-Options).
SHA-256 hash-chained audit log. Cloudflare free DDoS.
Files: `api/middleware/rate_limiter.py`, `api/middleware/security_headers.py`,
`api/middleware/input_validator.py`, `api/middleware/audit_logger.py`,
`blockchain/audit_chain.py`

### Phase 18 — Self-Learning System
Schema learner (new field detection with human review gate).
Weekly pattern candidate discovery via subgraph mining.
data.gov.in catalog monitoring for new datasets.
Evidence-based weight optimiser (3 confirmed outcomes minimum).
Weekly self-audit of all 21 scrapers with GitHub alerts.
Files: `ai/self_learning/` (5 modules),
`.github/workflows/weekly_learn.yml`

### Phase 19 — Affidavit Wealth Trajectory Engine
Kalman filter on affidavit time series across 5 election cycles.
Unexplained wealth residual scoring. Asset disappearance detection.
Pre-election movable asset surge detector.
File: `ai/forensics/affidavit_analyzer.py`

### Phase 20 — Biography Engine
Complete chronological life timeline from all 28 sources.
Temporal convergence detection (election + contract within 90 days).
Neutral narrative generation with full source citations.
Files: `ai/biography/timeline_builder.py`, `api/routes/biography.py`,
`frontend/js/timeline.js`

### Phase 21 — Benami Entity Detection
Node2Vec graph embeddings + surname/age/address similarity.
Family network construction. Director proxy scoring.
File: `ai/forensics/benami_detector.py`

### Phase 22 — Procurement DNA + Cartel Detection
Bid document fingerprinting (TF-IDF + cosine similarity).
Price ratio analysis (Hotelling T-squared). Cover bid detection.
Vendor co-bidding network with community detection.
Files: `ai/forensics/bid_dna.py`, `ai/forensics/cartel_detector.py`

### Phase 23 — Revolving Door Tracker
Career graph: regulator → private sector transitions.
Cooling-off period violation detection. Pre-employment benefit scoring.
File: `ai/forensics/revolving_door.py`

### Phase 24 — Linguistic Fingerprinting
Burrows' Delta authorship attribution on government documents.
Template reuse via Rabin fingerprint. Shadow drafting detection.
File: `ai/forensics/linguistic_fingerprint.py`

### Phase 25 — Policy-Benefit Causal Analysis
Granger causality test (policy → entity benefit).
Transfer entropy for causal direction. Event study: Cumulative Abnormal
Contract Award scoring.
File: `ai/forensics/policy_benefit_analyzer.py`

### Phase 26 — Adversarial Counterevidence Engine
For every HIGH finding: auto-generate contra-hypothesis and search for
disproving evidence. Confidence adjustment based on counterevidence strength.
File: `ai/adversarial_engine.py`

### Phase 27 — Multi-Agent Debate Engine
iMAD architecture: linguistic hesitation detection (41 features) triggers
structured 3-round debate. Anti-drift via semantic similarity check.
Dual-agent: filter agent + reasoning agent.
File: `ai/debate_engine.py`

### Phase 28 — Dark Pattern Detection
PrefixSpan sequential pattern mining on administrative event histories.
6 pre-defined high-risk patterns. Timing window significance test.
File: `ai/forensics/dark_pattern_detector.py`

### Phase 29 — Source-Drift Triangulation
Wayback Machine CDX API for historical source comparison.
Credibility score: age + consistency + multi-source.
Retroactive editing detection.
File: `ai/source_credibility.py`

### Phase 30 — Predictive Risk Engine
3-model ensemble: linear trajectory, Random Forest, ARIMA.
6-month risk forecast for all tracked entities.
Early Warning System with live feed alerts.
File: `ai/predictive_risk.py`
