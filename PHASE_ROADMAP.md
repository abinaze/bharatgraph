# BharatGraph — Complete Phase Roadmap

All branches merge into `main`. Branch naming: `feature/phase-N-name` or `fix/issue-name`.

---

## COMPLETED PHASES

### Phase 1 — Data Collection
**Branch:** `feature/phase-1-scrapers` | **Tag:** (pre-tagging)  
**Files:** `scrapers/base_scraper.py` + 6 scrapers  
**Summary:** Base scraper class with load_dotenv, configurable rate limiting, JSON output, and retry logic. First 6 live scrapers. Confirmed live: DataGov (3,199 MGNREGA records), CAG (30 links), PIB (27 articles).

### Phase 2 — Data Processing
**Branch:** `feature/phase-2-processing`  
**Files:** `processing/cleaner.py`, `processing/entity_resolver.py`, `processing/pipeline.py`  
**Summary:** Indian name normalisation (honorifics: Sh./Smt./Dr., company prefixes: Ltd/Pvt/LLP). Jaccard token similarity for cross-source entity resolution. Full parallel pipeline orchestrator. 47 records in 15 seconds confirmed.

### Phase 3 — Graph Database
**Branch:** `feature/phase-3-graph`  
**Files:** `graph/schema.py`, `graph/loader.py`, `graph/queries.py`  
**Summary:** Neo4j AuraDB connected: `neo4j+s://1a34e3b8.databases.neo4j.io`. 7 node types, 6 relationship types, 10 constraint queries. MERGE with stable MD5 IDs prevents duplicates. 8 pre-built Cypher query templates.

### Phase 4 — FastAPI Backend
**Branch:** `feature/phase-4-api`  
**Files:** `api/main.py`, `api/models.py`, `api/dependencies.py`, 4 route modules  
**Summary:** FastAPI with lifespan context manager, CORS, 6 initial route modules. Pydantic models with typed source citations. Neo4j dependency injection. Version 0.12.0.

### Phase 5 — Risk Scoring Engine
**Branch:** `feature/phase-5-risk`  
**Files:** `ai/indicators.py`, `ai/explainer.py`, `ai/risk_scorer.py`  
**Summary:** Composite 0–100 risk score. Five weighted indicators: politician_company_overlap (0.35), contract_concentration (0.25), audit_frequency (0.20), asset_anomaly (0.15), criminal_case (0.05). `validate_language()` enforces neutral analytical output on every route.

### Phase 6 — Expanded Data Sources (13 scrapers)
**Branch:** `feature/phase-6-scrapers`  
**Files:** `icij_scraper.py`, `wikidata_scraper.py`, `opensanctions_scraper.py`, `loksabha_scraper.py`, `sebi_scraper.py`, `electoral_bond_scraper.py`  
**Summary:** ICIJ HTML scraping via BeautifulSoup. Wikidata SPARQL confirmed live. All public HuggingFace models, no access approval required.

### Phase 7 — NLP Document Intelligence
**Branch:** `feature/phase-7-nlp`  
**Files:** `ai/nlp_extractor.py`, `ai/benfords_analyzer.py`, `ai/multilingual_ner.py`, `ai/shadow_draft_detector.py`  
**Summary:** spaCy `en_core_web_sm` NER. Benford's Law chi-squared test on affidavit figures. Multilingual NER via Davlan/bert-base-multilingual-cased-ner-hrl. Shadow draft detector: 93.35% alignment confirmed.

### Phase 8 — Advanced Graph Analytics
**Branch:** `feature/phase-8-graph-analytics`  
**Files:** `ai/graph_analytics.py`, `ai/circular_ownership.py`, `ai/shadow_director.py`, `ai/ghost_company.py`  
**Summary:** NetworkX betweenness centrality, PageRank, Louvain community detection. Circular ownership via `simple_cycles` (3-node cycle confirmed). Ghost company scorer: GHOST_THRESHOLD=60, 100/100 confirmed.

### Phase 9 — Eight New Indian Sources (21 total)
**Branch:** `feature/phase-9-scrapers`  
**Files:** `njdg_scraper.py`, `ed_scraper.py`, `cvc_scraper.py`, `ncrb_scraper.py`, `lgd_scraper.py`, `ibbi_scraper.py`, `ngo_darpan_scraper.py`, `cppp_scraper.py`  
**Summary:** NJDG: 39 live records confirmed. All scrapers include sample fallback data when live source is unavailable.

### Phase 10 — Multi-Investigator AI Engine
**Branch:** `feature/phase-10-multi-investigator`  
**Files:** `ai/multi_investigator.py`, `ai/investigators/` (12 files)  
**Summary:** 12 parallel investigators in ThreadPoolExecutor. SHA-256 report hash stable. Synthesis: 3+ agreeing = HIGH confidence. 12 specialists with calibrated weights summing to 1.0.

### Phase 11 — Multilingual Platform (22 Languages)
**Branch:** `feature/phase-11-multilingual`  
**Files:** `config/languages.py`, `ai/translator.py`, `ai/transliteration.py`, `api/routes/multilingual.py`  
**Summary:** All 22 Indian scheduled languages. Language detection via Unicode block analysis. Helsinki-NLP/opus-mt-en-hi translation. Cross-script transliteration: "Modi" → 5 scripts confirmed.

### Phase 12 — PDF Dossier Generator
**Branch:** `feature/phase-12-pdf-dossier`  
**Files:** `ai/report_hasher.py`, `ai/dossier_generator.py`, `templates/dossier_en.html`, `api/routes/export.py`  
**Summary:** SHA-256 integrity hash per report. Tamper detection confirmed. Jinja2 + WeasyPrint. Indian tricolour design, 8 report sections. 10,829 chars rendered confirmed.

### Phase 13 — Production Frontend
**Branch:** `feature/phase-13-frontend`  
**Files:** `frontend/index.html`, `frontend/css/` (2 files), `frontend/js/` (5 files)  
**Summary:** Vanilla HTML/CSS/JS — no build step required. Works from `file://`. D3.js force-directed graph. Dark/light theme. 5 views: home, search, entity, feed, about.

### Phase 14 — Zero Cold-Start Deployment
**Branch:** `feature/phase-14-deployment` | **Tag:** `v0.14.0`  
**Files:** `app.py`, `Dockerfile`, `frontend/sw.js`, `.github/workflows/static.yml`, `graph/seed.py`, `api/routes/admin.py`  
**Summary:** Hugging Face Spaces Docker SDK. Service worker cache-first. GZipMiddleware (60–80% compression). `POST /admin/seed` loads sample data. GitHub Pages static deployment.

### Phase 15 — Mathematical Intelligence Engine
**Branch:** `feature/phase-15-math-intelligence` | **Tag:** `v0.15.0`  
**Files:** `ai/math/__init__.py`, `ai/math/spectral_analyzer.py`, `ai/math/fourier_timeline.py`, `ai/investigators/math_investigator.py`  
**Summary:** Spectral graph analysis: Laplacian Fiedler value (λ₁) for bridge entity detection. Fourier FFT on contract amount sequences. 13th investigator (math, weight 0.08).

### Phase 16 — Evidence Connection Map and Deep Investigation Engine
**Branch:** `feature/phase-16-evidence-map` | **Tag:** `v0.16.0`  
**Files:** `ai/deep_investigator.py`, `ai/connection_mapper.py`, `api/routes/investigation.py`, `frontend/js/evidence_panel.js`  
**Summary:** 6-layer recursive investigation engine. Clickable evidence panel: WHY connected, source, confidence, next leads. Connection mapper with relationship-level explanations on every edge.

### Phase 17 — Security Hardening and Provenance Layer
**Branch:** `feature/phase-17-security` | **Tag:** `v0.17.0`  
**Files:** `api/middleware/rate_limiter.py`, `api/middleware/security_headers.py`, `api/middleware/input_validator.py`, `api/middleware/audit_logger.py`, `blockchain/audit_chain.py`  
**Summary:** Sliding window rate limiter. IP SHA-256 hashing. HTTP security headers. Input validator with Cypher injection detection. Append-only SHA-256 hash-chained audit log.

### Phase 18 — Self-Learning System and Case Memory
**Branch:** `feature/phase-18-self-learning`  
**Files:** `ai/self_learning/`, `ai/case_memory/`, `.github/workflows/weekly_learn.yml`  
**Summary:** Schema learner detects new fields for human review. Pattern learner discovers subgraph candidates weekly. Weight optimiser adjusts indicator weights. Case memory saves investigation outcomes.

### Phase 19 — Affidavit Wealth Trajectory Engine
**Branch:** `feature/phase-19-affidavit` | **Tag:** `v0.19.0`  
**Files:** `ai/forensics/affidavit_analyzer.py`, `ai/investigators/affidavit_investigator.py`, `api/routes/affidavit.py`  
**Summary:** Kalman filter on 5-election asset time series. Expected growth model (8% FD + 60% salary). Residual ratio >2x = HIGH, >5x = VERY_HIGH. Test: VERY_HIGH, ₹42.7 Cr residual (7.1×), 3 anomalies.

### Phase 20 — Biography Engine
**Branch:** `feature/phase-20-biography`  
**Files:** `ai/biography/biography_generator.py`, `ai/biography/timeline_builder.py`, `ai/biography/convergence_detector.py`, `frontend/js/timeline.js`  
**Summary:** Chronological timeline from all 21 sources. 5 temporal convergence window types with severity scoring. Neutral narrative generation with forbidden-word enforcement.

### Phase 21 — Benami Entity Detection
**Branch:** `feature/phase-21-benami`  
**Files:** `ai/forensics/benami_detector.py`, `ai/investigators/benami_investigator.py`, `api/routes/benami.py`  
**Summary:** 5-factor proxy scoring (0–100): director age (0.25), surname network (0.25), address clustering (0.20), company-before-contract (0.20), single-director (0.10). HIGH ≥65, MODERATE ≥40.

### Phase 22 — Procurement DNA, Cartel Detection, Full Pipeline Expansion
**Branch:** `feature/phase-22-procurement`  
**Files:** `ai/forensics/bid_dna.py`, `ai/forensics/cartel_detector.py`, `api/routes/procurement.py`  
**Summary:** TF-IDF cosine similarity ≥0.72 = near-identical bid flag. Cover-bid price clustering. Cartel: award rotation + co-bidding network. Pipeline expanded to all 21 scrapers.

### Phase 23 — Revolving Door and TBML Detection
**Branch:** `feature/phase-23-conflict`  
**Files:** `ai/forensics/revolving_door.py`, `ai/forensics/tbml_detector.py`, `api/routes/conflict.py`  
**Summary:** 365-day cooling-off violation detection. Pre-employment benefit scoring. TBML: price anomaly (2.5σ), subcontract loop, director-change-near-award (90-day window).

### Phase 24 — Linguistic Fingerprinting
**Branch:** `feature/phase-24-linguistic`  
**Files:** `ai/forensics/linguistic_fingerprint.py`, `api/routes/linguistic.py`  
**Summary:** Burrows Delta authorship attribution (Argamon's variant). Function-word frequency analysis. Template reuse detection across procurement documents.

### Phase 25 — Policy-Benefit Causal Analysis
**Branch:** `feature/phase-25-policy`  
**Files:** `ai/forensics/policy_benefit_analyzer.py`, `api/routes/policy.py`  
**Summary:** Granger causality test (lag 1–6 months). Transfer entropy. CACA scoring. Cross-ministry benefit chain detection.

### Phase 26 — Adversarial Counterevidence
**Branch:** `feature/phase-26-adversarial`  
**Files:** `ai/adversarial_engine.py`, `api/routes/adversarial.py`  
**Summary:** Forced disproof methodology. Competing hypothesis scorecard. Uncertainty propagation across multi-hop paths.

### Phase 27 — Multi-Agent Debate Engine
**Branch:** `feature/phase-27-debate`  
**Files:** `ai/debate_engine.py`, `api/routes/debate.py`  
**Summary:** 7-agent 3-round structured debate. iMAD hesitation detection. Consensus with support/against/uncertain counts. Minority findings preserved.

### Phase 28 — Dark Pattern Detection
**Branch:** `feature/phase-28-dark-patterns`  
**Files:** `ai/dark_pattern_detector.py`  
**Summary:** PrefixSpan sequential pattern mining. 6 high-risk administrative sequences. Timing window significance test.

### Phase 29 — UX Overhaul + Investigation Fixes
**Branch:** `feature/phase-29-ux-fixes` | **Tag:** `v0.29.0`  
**Files:** `frontend/js/app.js`, `frontend/js/evidence_panel.js`, `frontend/index.html`, `frontend/sw.js`, `ai/deep_investigator.py`, `ai/connection_mapper.py`, `graph/seed.py`, `api/routes/admin.py`  
**Summary:** Fixed critical loading bug (23 `\`` + 13 `\${` from Python string injection → silent JS parse failure). SW cache bumped to v3. Evidence panel: 4 tabs (Overview / Connections / Timeline / Investigate). Deep investigator: confidence scoring + 6 richer Cypher layers. Connection mapper: WHY/source/next-leads on every edge. Seed data now includes DIRECTOR_OF + WON_CONTRACT relationships. 22-language selector. Connection map D3 graph route.

---

## PLANNED PHASES

### Phase 30 — Source-Drift and Historical Analysis
**Branch:** `feature/phase-30-historical` | **Priority:** HIGH  
**Summary:** Detect when government records change, disappear, or are silently modified. Compare current data against Wayback Machine snapshots. Track first-appearance timelines for claims. Evidence status states: ACTIVE / MODIFIED / REMOVED / ARCHIVED. Reconstruct "what existed" when pages are taken down.  
**Files to create:** `ai/forensics/source_drift_detector.py`, `ai/forensics/event_reconstructor.py`, `api/routes/historical.py`  
**Route:** `GET /historical/{entity_id}`

### Phase 31 — Predictive Risk and Lead Prioritisation
**Branch:** `feature/phase-31-predict` | **Priority:** HIGH  
**Summary:** ARIMA + Random Forest ensemble for 6-month risk trajectory forecasting. Lead prioritisation by centrality, community structure, link prediction, and anomaly scores. Automatic "investigate next" ranking so analysts focus on highest-value targets first.  
**Files to create:** `ai/forensics/risk_predictor.py`, `api/routes/predict.py`  
**Route:** `GET /predict/{entity_id}`

### Phase 32 — Entity Resolution v2 (Canonical IDs)
**Branch:** `feature/phase-32-entity-resolution` | **Priority:** CRITICAL  
**Summary:** Fix the root cause of fragmented graphs — same entity stored under multiple Neo4j IDs. Canonical ID assignment using company CIN, Aadhaar-masked hash, or stable name+state key. Alias merging with near-duplicate detection via embedding cosine similarity. Indian name normalisation for transliteration variants. Bridge-identifier detection across datasets.  
**Files to create:** `processing/entity_resolver_v2.py`, `processing/name_normaliser.py`, `api/routes/admin.py` (merge endpoint)  
**Impact:** Fixes broken evidence chains across all 16 node types.

### Phase 33 — Contradiction Engine
**Branch:** `feature/phase-33-contradiction` | **Priority:** HIGH  
**Summary:** Scan all findings for contradictions across independent sources. Confidence decay — older evidence loses weight. Counter-investigation mode: search for evidence that challenges each finding. Uncertainty propagation model across graph edges. Competing hypotheses ranked by evidence weight.  
**Files to create:** `ai/forensics/contradiction_detector.py`  
**Route:** `GET /adversarial/{entity_id}/contradict`

### Phase 34 — Multi-Agent Orchestration
**Branch:** `feature/phase-34-multiagent` | **Priority:** HIGH  
**Summary:** Proper orchestration layer for the 15 parallel investigators. Adaptive routing: simple cases → 3 agents; complex/contradictory → 12 agents. Agent memory and reputation scoring. Consensus builder outputs "N agree / M uncertain / K disagree" format. Agent profile: name, role, expertise, memory, reputation.  
**Files to create:** `ai/agents/agent_orchestrator.py`, `ai/agents/agent_profile.py`, `ai/agents/investigator_roles.py`

### Phase 35 — Graph Intelligence
**Branch:** `feature/phase-35-graph-intelligence` | **Priority:** HIGH  
**Summary:** Centrality ranking (betweenness, eigenvector, PageRank). Community detection via Louvain with plain-language cluster explanations. Bridge node detection — entities connecting otherwise separate clusters. Link prediction (Jaccard, Adamic-Adar, common-neighbour). Graph anomaly detection on nodes, edges, and subgraphs. Auto-surfaced "hidden link suggestions".  
**Files to create:** `ai/graph_intelligence.py`  
**Routes:** `GET /graph/anomalies/{entity_id}`, `GET /graph/leads/{entity_id}`, `GET /graph/bridge-nodes`

### Phase 36 — Provenance and Evidence Audit Layer
**Branch:** `feature/phase-36-provenance` | **Priority:** HIGH  
**Summary:** Full provenance for every node, edge, and conclusion: source, timestamp, extraction method, transformation history, confidence. Deterministic IDs for evidence artifacts. Claim-evidence audit panel: which evidence supports vs. weakens each finding. Evidence ranking: CONFIRMED / PROBABLE / WEAK / REJECTED. Evidence chain export in legal-safe format.  
**Files to create:** `ai/provenance_engine.py`  
**Routes:** `GET /export/evidence-chain/{entity_id}`, `GET /export/audit/{entity_id}`

### Phase 37 — Watchlist and Alerting
**Branch:** `feature/phase-37-watchlist` | **Priority:** MEDIUM  
**Summary:** Persistent watchlist of entities. WebSocket alerts when new data appears for a watched entity. Diff-based alerting: "new connection added", "risk score changed", "audit flag appeared". Email or webhook notification support.  
**Files to create:** `api/routes/watchlist.py`, `ai/alert_engine.py`  
**Routes:** `POST /watchlist`, `GET /watchlist`, `GET /watchlist/alerts`

### Phase 38 — Full Data Pipeline (367+ Sources)
**Branch:** `feature/phase-38-data-expansion` | **Priority:** CRITICAL  
**Summary:** Expand from 21 to 367+ verified real Indian government sources. Priority scrapers: eCourts NJDG, all CAG report types, NCRB IPC section-wise, SEBI enforcement orders DB, ED PMLA press releases, MCA company master bulk download, AGMARKNET mandi prices, PARIVESH clearances, TRAI orders, DGFT trade data, CCI antitrust orders, EPFO payroll, ISRO technology transfers.  
**Files to create:** 14+ new scraper files, extended `graph/loader.py`, updated `datasets/bharatgraph_sources.csv`

### Phase 39 — Geospatial Verification
**Branch:** `feature/phase-39-geospatial` | **Priority:** MEDIUM  
**Summary:** Sentinel-2 satellite imagery for verifying claimed government projects physically exist on the ground. NDVI change detection for forest diversion and mangrove destruction. Construction progress detection. Contract-location validation: compare claimed construction site against satellite data.  
**Files to create:** `ai/geospatial/sentinel_verifier.py`, `ai/geospatial/location_extractor.py`, `api/routes/geospatial.py`  
**Route:** `GET /geospatial/verify/{contract_id}`

### Phase 40 — DeepSeek-R1 Reasoning Integration
**Branch:** `feature/phase-40-deepseek-r1` | **Priority:** HIGH  
**Summary:** Integrate DeepSeek-R1 chain-of-thought reasoning as the central investigation synthesis engine. R1 produces evidence-backed, step-by-step reasoning chains instead of simple pattern matches. Multi-hop explanation engine: "A is connected to B because: Step 1 → Step 2 → Step 3". Anti-hallucination enforcement: R1 only reasons from verified graph evidence. Competing hypothesis generation and scoring via R1's logical decomposition.  
**Files to create:** `ai/deepseek/r1_reasoner.py`, `ai/deepseek/reasoning_chain.py`  
**Integration:** Wraps DeepInvestigator and ConnectionMapper output through R1 for natural-language explanation generation.

### Phase 41 — DeepSeek-VL2 Visual Evidence Analysis
**Branch:** `feature/phase-41-deepseek-vl2` | **Priority:** MEDIUM  
**Summary:** Use DeepSeek-VL2 for: (1) OCR on government document images (affidavits, audit reports, court orders), (2) visual inconsistency detection in submitted documents, (3) satellite image analysis for geospatial verification, (4) infographic and chart data extraction from government reports. Cross-modal evidence: link text evidence with visual document evidence.  
**Files to create:** `ai/deepseek/vl2_processor.py`, `ai/deepseek/document_vision.py`  
**Route:** `POST /visual/analyze` (accepts image URL or base64)

### Phase 42 — DeepSeek-V3 Report Generation
**Branch:** `feature/phase-42-deepseek-v3` | **Priority:** HIGH  
**Summary:** Use DeepSeek-V3 for professional-quality investigation report generation. Structured reports with: Executive Summary, Evidence Sections (CONFIRMED / PROBABLE / WEAK), Risk Assessment, Timeline Reconstruction, Connection Map Description, Legal-Safe Language Enforcement. Reports generated in all 22 Indian languages via V3's multilingual capability.  
**Files to create:** `ai/deepseek/v3_report_generator.py`  
**Integration:** Replaces/enhances `ai/dossier_generator.py`

### Phase 43 — Observability and Pipeline Reliability
**Branch:** `feature/phase-43-observability` | **Priority:** HIGH  
**Summary:** Per-stage pipeline logging with success/failure rates. Metrics per scraper (records/run, latency, error rate). Prometheus-compatible metrics endpoint. Stale-data detection (alert when source silent >30 days). Ingestion validator: schema checks before any record enters Neo4j. Retry with exponential backoff for all scrapers. Partial-ingestion save: completed sources not lost on failure.  
**Files to create:** `api/middleware/metrics_collector.py`, `processing/ingestion_validator.py`  
**Route:** `GET /admin/metrics`, `GET /admin/pipeline-health`

### Phase 44 — Report Export and Legal-Safe Output
**Branch:** `feature/phase-44-reports` | **Priority:** HIGH  
**Summary:** Evidence-ranked final reports: CONFIRMED ≥80%, PROBABLE ≥50%, WEAK ≥20%, REJECTED <20%. Legal disclaimer enforcement on every output. "Allegation vs verified" labelling. Multi-format export: PDF, JSON audit log, markdown. Evidence chain export with source traceability. Shareable report links with integrity hash.  
**Files to create:** `ai/report_generator.py`, `api/routes/export.py` (extended)

### Phase 45 — Full 22-Language Output Engine
**Branch:** `feature/phase-45-language` | **Priority:** HIGH  
**Summary:** Complete multilingual output for all 22 Indian scheduled languages. Domain-specific vocabulary for risk levels, legal terms, and government entities in each language. Language auto-detection from browser headers. Search results and investigation output in the user's selected language. Transliteration for all person/organisation names across all 22 scripts.

### Phase 46 — Security Hardening and PII Protection
**Branch:** `feature/phase-46-security` | **Priority:** HIGH  
**Summary:** PII masking: Aadhaar number redaction, phone number masking in all output. Role-based access control (RBAC): admin, analyst, viewer. DPDP Act 2023 compliance review. Defamation safeguard review. Rate limiting per entity lookup. Injection attack hardening across all 19 route modules.

### Phase 47 — Evidence Graph Frontend Upgrade
**Branch:** `feature/phase-47-evidence-graph` | **Priority:** HIGH  
**Summary:** New investigation flow: Input → Collection progress → Graph construction (live nodes appearing) → Evidence-ranked results. Clustering for large graphs (>50 nodes). Level-of-detail rendering. Evidence strength as edge thickness. Confidence as node opacity. Time slider for temporal graph view. Evidence status badges: CONFIRMED (green), PROBABLE (orange), WEAK (grey), REJECTED (red strikethrough).

### Phase 48 — Confidence and Scoring Framework
**Branch:** `feature/phase-48-confidence` | **Priority:** HIGH  
**Summary:** Unified confidence engine: 0–100 score for every claim. Confidence decay for older evidence. Multi-source boost: confirmed by 3+ independent sources → higher confidence. Uncertainty propagation: weak evidence reduces confidence of connected claims. Evidence ranker: CONFIRMED ≥80, PROBABLE ≥50, WEAK ≥20, REJECTED <20.  
**Files to create:** `ai/confidence_engine.py`, `ai/evidence_ranker.py`

### Phase 49 — User Workflows and Investigation Workspace
**Branch:** `feature/phase-49-workflows` | **Priority:** MEDIUM  
**Summary:** Save/resume investigations in persistent storage. Export investigation as shareable link. Bookmark entities for watchlist. Step-by-step investigation wizard for new users. Investigation replay: see how conclusions were built step by step.  
**Routes:** `POST /investigation/save`, `GET /investigation/{id}`, `GET /investigation/{id}/share`

### Phase 50 — Production Launch
**Branch:** `feature/phase-50-production` | **Priority:** PLANNED  
**Summary:** Full CI/CD with automated end-to-end tests on all 21 API routes. Load testing (100 concurrent users). Graph query optimisation with composite indexes. Mobile-responsive layout for all views. Progressive Web App (PWA) with offline capability. Full API documentation with Postman collection. Correction request workflow (14-day processing). Public launch announcement.

---

## Continuous Improvement Backlog

| ID | Topic | Description |
|----|-------|-------------|
| CI-1 | Indian Name Normalisation | Honorifics, transliterations, ministry abbreviations |
| CI-2 | Government Ontology | Ministry hierarchy, PSU → ministry, court → jurisdiction |
| CI-3 | Pipeline Scheduler | Daily/weekly/monthly refresh schedules per source |
| CI-4 | Graph Versioning | Snapshot graph state; time-travel queries |
| CI-5 | Reproducibility | Same input + date + sources = same result hash |
| CI-6 | Edge Intelligence | Every edge must carry: source, date, confidence, method, raw_url |
| CI-7 | Mobile App | React Native / PWA wrapper with push notification alerts |
| CI-8 | OpenAPI SDK | Python + JavaScript SDKs with Postman collection |
| CI-9 | Deduplication | Document-level hash deduplication to prevent duplicate records |
| CI-10 | Cost Optimisation | Cache agent results; reuse multi-investigator outputs |

---

## Phase Summary Table

| Phase | Name | Status | Version |
|-------|------|--------|---------|
| 1–12 | Core Infrastructure + ML | ✅ Complete | v0.12.0 |
| 13–14 | Frontend + Deployment | ✅ Complete | v0.14.0 |
| 15–16 | Math Engine + Evidence Map | ✅ Complete | v0.16.0 |
| 17–18 | Security + Self-Learning | ✅ Complete | v0.18.0 |
| 19–23 | Forensic Modules | ✅ Complete | v0.23.0 |
| 24–28 | Advanced Analysis | ✅ Complete | v0.28.0 |
| 29 | UX Overhaul + Investigation Fixes | ✅ Complete | v0.29.0 |
| 30 | Source-Drift + Historical | 🔜 Next | v0.30.0 |
| 31 | Predictive Risk + Lead Rank | 🔜 Planned | v0.31.0 |
| 32 | Entity Resolution v2 | 🔜 **CRITICAL** | v0.32.0 |
| 33 | Contradiction Engine | 🔜 Planned | v0.33.0 |
| 34 | Multi-Agent Orchestration | 🔜 Planned | v0.34.0 |
| 35 | Graph Intelligence | 🔜 Planned | v0.35.0 |
| 36 | Provenance + Audit Layer | 🔜 Planned | v0.36.0 |
| 37 | Watchlist + Alerts | 🔜 Planned | v0.37.0 |
| 38 | 367+ Source Pipeline | 🔜 **CRITICAL** | v0.38.0 |
| 39 | Geospatial Verification | 🔜 Planned | v0.39.0 |
| 40 | DeepSeek-R1 Reasoning | 🔜 Planned | v0.40.0 |
| 41 | DeepSeek-VL2 Visual Evidence | 🔜 Planned | v0.41.0 |
| 42 | DeepSeek-V3 Report Generation | 🔜 Planned | v0.42.0 |
| 43 | Observability + Reliability | 🔜 Planned | v0.43.0 |
| 44 | Report Export + Legal-Safe | 🔜 Planned | v0.44.0 |
| 45 | Full 22-Language Output | 🔜 Planned | v0.45.0 |
| 46 | Security + PII Protection | 🔜 Planned | v0.46.0 |
| 47 | Evidence Graph Frontend | 🔜 Planned | v0.47.0 |
| 48 | Confidence + Scoring | 🔜 Planned | v0.48.0 |
| 49 | User Workflows + Workspace | 🔜 Planned | v0.49.0 |
| 50 | Production Launch | 🔜 Future | v0.50.0 |
