# BharatGraph — Complete Phase Roadmap

All branches merge into `main`. Branch naming: `feature/phase-N-name` or `fix/issue-description`.
Each phase has a GitHub Issue (see `issues/` directory) and a PR description template.

---

## COMPLETED PHASES

### Phase 1 — Data Collection
**Tag:** pre-v1 | **Branch:** `feature/phase-1-scrapers`
**Summary:** Established the base scraper class with rate limiting, retry logic, and JSON output. Delivered the first 6 live scrapers (DataGov, CAG, PIB, MyNeta, MCA, GeM). Confirmed live data: DataGov returned 3,199 MGNREGA records; CAG returned 30 audit links; PIB returned 27 press release entries. All scrapers write to `data/raw/` with ISO timestamps.

### Phase 2 — Data Processing
**Tag:** pre-v2 | **Branch:** `feature/phase-2-processing`
**Summary:** Indian name normalisation with honorific and company-prefix handling (Sh., Smt., Dr., Ltd, Pvt, LLP). Jaccard token similarity for cross-source entity resolution — prevented duplicate nodes from different datasets. Full parallel pipeline orchestrator using `concurrent.futures.ThreadPoolExecutor`. 47 records processed in 15 seconds on first run.

### Phase 3 — Graph Database
**Tag:** pre-v3 | **Branch:** `feature/phase-3-graph`
**Summary:** Designed the Neo4j AuraDB schema with 7 node types and 6 relationship types. All MERGE operations use stable MD5 IDs derived from canonical properties — no duplicate nodes across pipeline runs. 8 pre-built Cypher query templates cover the most common investigation paths. Successfully connected to `neo4j+s://1a34e3b8.databases.neo4j.io`.

### Phase 4 — FastAPI Backend
**Tag:** v0.12.0 | **Branch:** `feature/phase-4-api`
**Summary:** Launched the production API with FastAPI lifespan context, CORS middleware, Neo4j dependency injection, and Pydantic response models with typed source citations. Initial routes: search, profile, graph, risk. All responses include `generated_at` timestamp and source attribution for every data point.

### Phase 5 — Risk Scoring Engine
**Branch:** `feature/phase-5-risk`
**Summary:** Composite 0–100 structural risk score combining five weighted indicators: politician–company overlap (0.35), contract concentration (0.25), audit mention frequency (0.20), asset growth anomaly (0.15), declared criminal cases (0.05). The `validate_language()` function enforces neutral analytical vocabulary across all outputs — no accusatory language passes through any API response.

### Phase 6 — Expanded Data Sources (13 scrapers)
**Branch:** `feature/phase-6-scrapers`
**Summary:** Added ICIJ Offshore Leaks scraper using BeautifulSoup HTML parsing; Wikidata SPARQL confirmed live with Modi Q1058 and Gandhi Q10218; OpenSanctions, Lok Sabha, SEBI, Electoral Bonds. All HuggingFace models used are fully public — no gating or approval required.

### Phase 7 — NLP Document Intelligence
**Branch:** `feature/phase-7-nlp`
**Summary:** Integrated spaCy `en_core_web_sm` for English NER. Benford's Law chi-squared test on affidavit asset figures detects non-natural digit distributions. Multilingual NER via `Davlan/bert-base-multilingual-cased-ner-hrl`. Shadow draft detector achieved 93.35% cosine alignment on test corpus using `all-MiniLM-L6-v2`.

### Phase 8 — Advanced Graph Analytics
**Branch:** `feature/phase-8-graph-analytics`
**Summary:** NetworkX integration for betweenness centrality, PageRank, and Louvain community detection. Circular ownership detection using `simple_cycles` — confirmed 3-node ownership cycle. Ghost company scorer with GHOST_THRESHOLD=60 — returned 100/100 on test case. Shadow director detection maps hidden directors across corporate structures.

### Phase 9 — Eight New Indian Sources (21 total)
**Branch:** `feature/phase-9-scrapers`
**Summary:** Added NJDG (39 live court records confirmed), ED, CVC, NCRB, LGD, IBBI, NGO Darpan, CPPP. All scrapers include locally-stored fallback sample data so the system continues to work if any external source is temporarily unavailable.

### Phase 10 — Multi-Investigator AI Engine
**Tag:** v0.10.0 | **Branch:** `feature/phase-10-multi-investigator`
**Summary:** 12 parallel investigators run in `ThreadPoolExecutor`, each querying the graph independently. Synthesis logic: 3+ investigators agreeing on a finding = HIGH confidence. SHA-256 report hash is stable and unique per investigation. Forbidden-word enforcement on all text output via `validate_language()`. Investigator weights: financial (0.12), political (0.10), corporate (0.10), judicial (0.08), procurement (0.12), network (0.08), asset (0.10), international (0.10), media (0.06), historical (0.08), public_interest (0.08), doubt (0.08).

### Phase 11 — Multilingual Platform (22 Languages)
**Branch:** `feature/phase-11-multilingual`
**Summary:** All 22 Indian scheduled languages with ISO codes and Unicode script range detection. Language auto-detection via Unicode block analysis — Devanagari → hi, Tamil → ta confirmed. Helsinki-NLP/opus-mt-en-hi for translation. Cross-script entity matching: "Modi" transliterated to 5 scripts confirmed. Risk levels pre-translated in 9 languages.

### Phase 12 — PDF Dossier Generator
**Branch:** `feature/phase-12-pdf-dossier`
**Summary:** Jinja2 + WeasyPrint pipeline produces HTML-first dossiers with PDF generation on Linux production. Indian tricolour design system with 8 structured sections. SHA-256 integrity hash per report — tamper detection confirmed. 10,829-character report rendered on test case. Routes: `GET /export/pdf/{entity_id}`, `GET /verify/{hash}`.

### Phase 13 — Production Frontend
**Branch:** `feature/phase-13-frontend`
**Summary:** Vanilla HTML/CSS/JS single-page application — no React, no Node.js, no build step. Works directly from `file://` protocol for offline use. D3.js force-directed knowledge graph. Dark and light theme with CSS custom properties. 5 views: home, search, entity, live feed, about.

### Phase 14 — Zero Cold-Start Deployment
**Tag:** v0.14.0 | **Branch:** `feature/phase-14-deployment`
**Summary:** HuggingFace Spaces Docker deployment with no cold start on public spaces. Service worker cache-first strategy for static assets. GZipMiddleware achieving 60–80% compression. `POST /admin/seed` loads 10 politicians, 5 companies, 3 contracts into Neo4j. GitHub Actions workflow deploys the frontend to GitHub Pages on every push to `main`. UptimeRobot pings `/health` every 5 minutes.

### Phase 15 — Mathematical Intelligence Engine
**Tag:** v0.15.0 | **Branch:** `feature/phase-15-math-intelligence`
**Summary:** Spectral graph analysis using the Laplacian Fiedler value (λ₁) — entities near λ₁ are graph bridges. Fourier FFT on contract amount time series detects periodic patterns (e.g. systematic quarterly spikes). 13th investigator (math, weight 0.08) integrated into the multi-investigator engine.

### Phase 16 — Evidence Connection Map and Deep Investigation Engine
**Tag:** v0.16.0 | **Branch:** `feature/phase-16-evidence-map`
**Summary:** 6-layer recursive investigation: direct evidence → relationship expansion → structural patterns → temporal investigation → network influence → cross-source validation. Evidence panel shows WHY each entity is connected, the source document, confidence level, and 3 suggested next investigation leads. Connection mapper finds shortest paths between any two entities with relationship-level explanations on every edge. Routes: `GET /investigate/{id}`, `GET /connection-map`, `GET /node-evidence/{id}`.

### Phase 17 — Security Hardening and Provenance Layer
**Tag:** v0.17.0 | **Branch:** `feature/phase-17-security`
**Summary:** Sliding window rate limiter — 100/min for search, 30/min for investigation, 10/min for export, 5/min for admin. IP addresses stored as SHA-256 hashes (first 16 hex chars) — never as plain text. HTTP security headers: CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy. Input validator detects uppercase-only Cypher injection patterns. Append-only SHA-256 hash-chained audit log at `logs/audit.jsonl`. Daily root hash anchored in a Neo4j `AuditRoot` node.

### Phase 18 — Self-Learning System and Case Memory
**Branch:** `feature/phase-18-self-learning`
**Summary:** Schema learner detects new fields in scraper output and writes them to `pending_schema_additions.json` for human review — never auto-applies to production. Pattern learner runs weekly and discovers subgraph pattern candidates. Weight optimiser adjusts indicator weights by ±0.01 after every 3+ confirmed cases. Case memory persists investigation outcomes with reasoning paths for cross-case learning. Weekly GitHub Actions workflow.

### Phase 19 — Affidavit Wealth Trajectory Engine
**Tag:** v0.19.0 | **Branch:** `feature/phase-19-affidavit`
**Summary:** Kalman filter constant-velocity model on 5-election asset time series. Innovation test: |z_k − H·x̂_k| > 3√S_k = anomaly. Expected growth model: initial assets + 8% FD returns + 60% salary savings. Residual ratio >2× = HIGH, >5× = VERY_HIGH unexplained wealth. Pre-election movable asset surge detection. Test result: VERY_HIGH level, ₹42.7 Cr residual (7.1×), 3 Kalman anomalies. 14th investigator (affidavit, weight 0.10). Route: `GET /affidavit/{entity_id}`.

### Phase 20 — Biography Engine
**Branch:** `feature/phase-20-biography`
**Summary:** Chronological timeline compiled from ECI elections, GeM contracts, CAG audit mentions, NJDG court proceedings, PIB press releases, and MCA directorships. Events sorted by date, grouped by year, colour-coded by category. 5 temporal convergence window types: election+contract (90 days), election+company (180 days), audit+contract (365 days), court+company (180 days), election+audit (365 days). Neutral narrative generation with forbidden-word list and source disclaimers. Frontend: `frontend/js/timeline.js`.

### Phase 21 — Benami Entity Detection
**Branch:** `feature/phase-21-benami`
**Summary:** 5-factor composite proxy score (0–100): director age anomaly (0.25), surname network clustering (0.25), address clustering (0.20), company formed before contract awarded (0.20), single-director structure (0.10). Thresholds: HIGH ≥ 65, MODERATE ≥ 40, LOW < 40. All 5 factors have fallback paths that return graceful results when the database is unavailable. 15th investigator (benami, weight 0.09). Route: `GET /benami/{entity_id}`.

### Phase 22 — Procurement DNA, Cartel Detection, and Full Pipeline Expansion
**Branch:** `feature/phase-22-procurement`
**Summary:** TF-IDF cosine similarity ≥ 0.72 flags near-identical bid documents from different vendors. Cover-bid detection via price clustering (standard deviation test across vendor bids on same tender). Vendor cartel detection: award rotation pattern (equal share across vendors) and co-bidding network (same vendor pairs appearing repeatedly). Pipeline expanded to all 21 scrapers. `POST /admin/pipeline` triggers background ingestion. `GET /sources` returns record counts per dataset.

### Phase 23 — Revolving Door and TBML Detection
**Branch:** `feature/phase-23-conflict`
**Summary:** Career transition detector: government-to-private moves within 365-day cooling-off window = flagged. Pre-employment benefit scoring: contracts awarded to a politician's future employer before their appointment. TBML indicators: contract price anomaly (2.5σ from entity mean), subcontract loop detection via Neo4j cycle queries, director changes within 90 days of contract award.

### Phase 24 — Linguistic Fingerprinting
**Branch:** `feature/phase-24-linguistic`
**Summary:** Burrows Delta authorship attribution (Argamon's variant) using function-word frequency vectors. Template reuse detection across procurement documents via TF-IDF cosine similarity on structural elements. Ghost-writing detection by comparing speech patterns against known ministerial corpora. Route: `GET /linguistic/fingerprint/{entity_id}`.

### Phase 25 — Policy-Benefit Causal Analysis
**Branch:** `feature/phase-25-policy`
**Summary:** Granger causality test (lag 1–6 months) between policy announcement events and company valuation changes. Transfer entropy for information-theoretic causality measurement. CACA (Confound-Adjusted Causal Attribution) scoring with cross-ministry benefit chain detection. Route: `GET /policy/causal/{entity_id}`.

### Phase 26 — Adversarial Counterevidence
**Branch:** `feature/phase-26-adversarial`
**Summary:** Forced disproof methodology: the system actively searches for evidence contradicting its own findings before finalising a report. Competing hypothesis scorecard — each hypothesis is scored for and against. Uncertainty propagation: weak evidence reduces confidence of connected claims. Route: `GET /adversarial/{entity_id}`.

### Phase 27 — Multi-Agent Debate Engine
**Branch:** `feature/phase-27-debate`
**Summary:** 7-agent structured 3-round debate. iMAD hesitation detection: agents that change position mid-debate signal contested evidence. Consensus scoring with explicit support / against / uncertain counts. Minority dissent findings are preserved in the final report — not suppressed. Route: `GET /debate/{entity_id}`.

### Phase 28 — Dark Pattern Detection
**Branch:** `feature/phase-28-dark-patterns`
**Summary:** PrefixSpan sequential pattern mining on administrative event sequences. 6 pre-defined high-risk sequences including single-bidder→short-window→above-threshold and director-change→new-contract→same-buyer. Timing window significance test against baseline distribution. Route: `GET /darkpattern/{entity_id}`.

### Phase 29 — UX Overhaul, Investigation Fixes, and Full i18n
**Tag:** v0.29.0 | **Branch:** `feature/phase-29-ux-fixes`
**Summary:** Fixed critical loading bug caused by 23 invalid `\`` and 13 invalid `\${` escape sequences injected by Python string replacement during Phase 16 development — these caused silent JS parse failure, leaving the page stuck on "Loading BharatGraph..." indefinitely. Service worker cache bumped to v3 to force invalidation of all stale cached files. Evidence panel rewritten with 4 tabs: Overview, Connections, Timeline, Investigate. Deep investigator rewritten with per-layer Neo4j sessions, confidence scoring, and richer Cypher queries. Connection mapper now returns WHY/source/next-leads on every graph edge. Seed data includes DIRECTOR_OF and WON_CONTRACT relationships. Language selector expanded to 22 Indian languages. `applyLanguage()` function rewrites the full DOM including nav links, filter buttons, headings, and search placeholder. `GET /ui-labels?lang=hi` endpoint added.

### Phase 30 — Critical Bug Fix Sprint
**Tag:** v0.30.0 | **Branch:** `fix/all-bugs-phase-30`
**Summary:** Resolved 26 bugs covering: WebSocket deadlock (server now pushes heartbeat every 15s rather than waiting for client); health check now retries 5× with exponential backoff on HuggingFace cold start; investigation routes wrapped with try/except returning structured errors instead of raw 500s; export singleton no longer holds stale Neo4j driver; input validator no longer blocks legitimate searches containing words like "Union Bank" or "Call Centre"; audit logger hash stored per-process rather than a shared global that breaks multi-worker deployments; rate limiter has stale-window eviction to prevent memory leak; DeepInvestigator gives each of the 6 investigation layers its own Neo4j session; FindingItem description sanitized before innerHTML; profile.py duplicate fallback block removed; `ProfileResponse` Pydantic model now includes the `sources` field; service worker no longer caches API responses; fulltext index expanded from 8 to 16 node types; timeline builder audit events now pass `entity_name` not `entity_id` to the Cypher parameter.

---

## PLANNED PHASES — Ordered for Best Implementation Sequence

The phases below are sequenced by dependency order: infrastructure and data quality first, then intelligence, then AI reasoning, then interfaces and operations.

---

### Phase 31 — Runtime Profile and Auto-Scaling
**Branch:** `feature/phase-31-runtime-profile` | **Priority:** CRITICAL — enables all subsequent phases
**Issue:** `issues/031-runtime-profile.md`

**Summary:** Make BharatGraph self-adapting to the hardware it runs on. At startup, detect CPU cores, RAM, GPU availability, free disk, Docker environment, and whether the database is local or remote. Assign one of three runtime profiles (low / medium / high) and apply corresponding settings for `max_workers`, `batch_size`, `graph_depth`, `investigation_layers`, `cache_ttl_seconds`, and `enable_gpu`. This means the same codebase runs well on a student laptop and scales up automatically on a government server — with zero manual configuration.

**Files to create:** `config/runtime_profile.py`, `config/model_selector.py`, `api/routes/runtime.py`
**Key algorithms:** Score-based profile assignment (cpu×2 + ram×2 + gpu×2 + disk + docker + db_location), preset dictionary lookup.
**Auto-scales:** Profile decision is re-evaluated on each restart — as hardware improves, the system picks a better profile automatically.

---

### Phase 32 — Entity Resolution v2 — Canonical Identity Engine
**Branch:** `feature/phase-32-entity-resolution` | **Priority:** CRITICAL
**Issue:** `issues/032-entity-resolution.md`

**Summary:** The single most impactful bug in the current system is that the same real-world entity is stored under multiple Neo4j IDs across different scrapers, causing graph fragmentation where evidence chains break. This phase builds a canonical identity engine using multi-field string similarity (Jaro-Winkler + Jaccard token overlap + exact CIN/PAN match), embedding-based near-duplicate detection via sentence-transformers, and a deterministic canonical ID assignment protocol. Implements ordered entity-detector registry (inspired by Flowsint issue #45) so detector precedence can be controlled. Adds alias graphs that link every known variant of an entity name to a single canonical node without deleting source records.

**Files to create:** `processing/entity_resolver_v2.py`, `processing/canonical_id.py`, `processing/alias_graph.py`
**Impact:** Fixes broken evidence chains across all 16 node types. Every phase that reads from the graph becomes more reliable.

---

### Phase 33 — Custom Graph Engine (Zero Neo4j Dependency)
**Branch:** `feature/phase-33-graph-engine` | **Priority:** HIGH
**Issue:** `issues/033-graph-engine.md`

**Summary:** Eliminate the hard dependency on Neo4j AuraDB Free (which has a 50K node / 175K relationship limit) and replace it with a self-contained graph engine that can run locally, in Docker, or scale to millions of nodes. The engine stores the property graph as adjacency lists in memory with LevelDB/RocksDB persistence, implements HNSW-based approximate nearest neighbour search for semantic queries (M=16, ef_construction=200, ef_search=50), and provides a Cypher-compatible query layer so all existing routes continue to work without modification. Includes a Git-style version control system (GraphVersionControl) that writes a diff for every mutation — enabling replay, rollback, and anti-forensics detection. Temporal edge weight decay: confidence × e^(−λt) with per-source-type decay rates so stale evidence loses weight automatically.

**Files to create:** `graph_engine/store.py`, `graph_engine/hnsw.py`, `graph_engine/query_planner.py`, `graph_engine/temporal.py`, `graph_engine/version_control.py`, `graph_engine/compat_layer.py`
**Compatibility:** A `compat_layer.py` translates all existing Cypher calls to graph engine calls — no route changes required.
**Migration:** `python -m graph_engine.migrate --from neo4j --to local` exports all nodes and edges from AuraDB and imports them into the local engine.

---

### Phase 34 — Vector Search and Hybrid Retrieval
**Branch:** `feature/phase-34-vector-search` | **Priority:** HIGH
**Issue:** `issues/034-vector-search.md`

**Summary:** Add semantic search alongside keyword search using FAISS or Qdrant for vector indexing. Compute sentence-transformer embeddings for all nodes and document fields during ingestion. Hybrid query execution: vector similarity + BM25 keyword ranking merged with Reciprocal Rank Fusion (RRF). This means a search for "contract irregularities Maharashtra" can find relevant audit reports even when those exact words do not appear. Implements the cost-based query planner from the graph engine: given a query, generate 5 candidate plans (graph-first, vector-first, hybrid, path-finding, fulltext), estimate execution cost for each, and execute the cheapest.

**Files to create:** `graph_engine/vector_index.py`, `graph_engine/hybrid_search.py`, `graph_engine/query_planner.py`, `processing/embedder.py`
**Models:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (supports all 22 Indian languages).

---

### Phase 35 — Plugin System and YAML-Defined Enrichers
**Branch:** `feature/phase-35-plugins` | **Priority:** HIGH
**Issue:** `issues/035-plugin-system.md`

**Summary:** A lazy-loading plugin system (inspired by Flowsint PR #130) that lets anyone add new data sources, enrichers, or analysis modules without modifying core code. Plugins are Python packages discovered via entry-points at runtime. A YAML-based API enricher system (Flowsint issue #94) lets non-developers define new data source integrations by writing a YAML config with URL, authentication, field mappings, and rate limits — no code required. Plugins have an `EnricherABC` base class with auto-registration. Deferred Redis `connect()` avoids import-time failures.

**Files to create:** `plugins/plugin_system.py`, `plugins/enricher_base.py`, `plugins/yaml_enricher.py`, `plugins/registry.py`
**Auto-scales:** Every new data source added as a plugin is automatically discovered by the pipeline, included in `/sources`, and counted in `/stats`.

---

### Phase 36 — Sigma-Style Rule Engine
**Branch:** `feature/phase-36-rule-engine` | **Priority:** HIGH
**Issue:** `issues/036-rule-engine.md`

**Summary:** A declarative YAML rule compiler and execution engine modelled on Sigma SIEM rules, adapted for graph-based investigation. Analysts define detection rules in YAML (entity types, relationship patterns, thresholds, evidence requirements) without writing any Python. The engine compiles rules to Cypher/graph queries and evaluates them against every new investigation. Ships with 5 built-in rules: cartel pattern detection, circular ownership, ghost company formation, revolving door violation, and politician-contractor proximity. New rules are added by dropping a YAML file into `rules/` — zero code changes.

**Files to create:** `rules/rule_engine.py`, `rules/compiler.py`, `rules/built_in/cartel.yaml`, `rules/built_in/circular_ownership.yaml`, `rules/built_in/ghost_company.yaml`

---

### Phase 37 — Job Queue and Priority Worker Pool
**Branch:** `feature/phase-37-workers` | **Priority:** HIGH
**Issue:** `issues/037-workers.md`

**Summary:** Replace the current synchronous investigation pipeline with a priority job queue backed by Redis (or a lightweight in-memory queue when Redis is unavailable). Jobs have a full state machine: INIT → QUEUED → RUNNING → DONE → FAILED → DEAD_LETTER. Auto-scaler adjusts worker count based on CPU load — scales up under investigation bursts, scales down during quiet periods. Dead-letter queue holds jobs that failed 3+ times for manual review. Enables long-running investigations (multi-hop graph traversal, full 21-scraper pipeline) to run in the background without blocking the API.

**Files to create:** `workers/job_queue.py`, `workers/worker_pool.py`, `workers/auto_scaler.py`, `workers/dead_letter.py`

---

### Phase 38 — DeepSeek-R1 Reasoning Integration
**Branch:** `feature/phase-38-deepseek-r1` | **Priority:** HIGH
**Issue:** `issues/038-deepseek-r1.md`

**Summary:** Integrate DeepSeek-R1's chain-of-thought reasoning as the central synthesis engine for multi-investigator results. R1 takes the structured findings from all 15 investigators and produces a step-by-step reasoning chain that explicitly cites evidence from the graph. Anti-hallucination enforcement: R1 is constrained to reason only from verified graph evidence passed in the prompt context — it cannot invent facts. Competing hypothesis generation: R1 generates 3 competing explanations for the same evidence set and scores each. The model is accessed via the DeepSeek API (free tier available) so no GPU is required.

**Files to create:** `ai/deepseek/r1_reasoner.py`, `ai/deepseek/chain_builder.py`, `ai/deepseek/anti_hallucination.py`
**Integration:** Wraps `DeepInvestigator` and `MultiInvestigator` output through R1 before returning to the API.

---

### Phase 39 — DeepSeek-VL2 Visual Evidence Analysis
**Branch:** `feature/phase-39-deepseek-vl2` | **Priority:** MEDIUM
**Issue:** `issues/039-deepseek-vl2.md`

**Summary:** Use DeepSeek-VL2 (1B Tiny model, runs on CPU) for: (1) OCR on government document images (affidavits, audit report scans, court order photos), (2) visual inconsistency detection in submitted documents (signature mismatch, stamp placement anomalies), (3) data extraction from infographic charts in government reports. Implements DeepSeek-OCR pipeline for batch processing of PDF-attached images at ~2500 tokens/second. Cross-modal evidence linking: text findings linked to their visual source documents.

**Files to create:** `ai/deepseek/vl2_processor.py`, `ai/deepseek/document_ocr.py`, `ai/forensics/visual_validator.py`
**Route:** `POST /visual/analyze` — accepts image URL or base64.

---

### Phase 40 — DeepSeek-V3 Report Generation
**Branch:** `feature/phase-40-deepseek-v3` | **Priority:** HIGH
**Issue:** `issues/040-deepseek-v3.md`

**Summary:** Use DeepSeek-V3 to generate professional-grade investigation reports with structured sections: Executive Summary, Confirmed Evidence, Probable Indicators, Weak Signals, Risk Assessment, Timeline Reconstruction, and Legal-Safe Recommendations. Reports are generated in all 22 Indian languages using V3's multilingual capability — no separate translation step required. Report quality is graded: CONFIRMED (≥80%), PROBABLE (≥50%), WEAK (≥20%), INSUFFICIENT (<20%). All outputs are reviewed by `validate_language()` before being returned.

**Files to create:** `ai/deepseek/v3_reporter.py`, `ai/deepseek/report_grader.py`
**Integration:** Replaces and enhances `ai/dossier_generator.py`.

---

### Phase 41 — Legal Intelligence Pipeline
**Branch:** `feature/phase-41-legal-pipeline` | **Priority:** HIGH
**Issue:** `issues/041-legal-pipeline.md`

**Summary:** An end-to-end legal text analysis pipeline covering: IPC section classifier (maps incident descriptions to Indian Penal Code sections and punishment ranges), crime triple extractor (subject → action → object from FIR/charge sheet text), two-stage question-answering (ES retrieval + cosine similarity scoring), and multi-task predictor for charge framing suggestions. Integrates the CrimeKgAssitant open-source legal knowledge graph (GitHub: liuhuanyong/CrimeKgAssitant) and LawCrimeMining (GitHub: liuhuanyong/LawCrimeMining) datasets as reference corpora. OOV (out-of-vocabulary) repair using BK-tree approximate string matching. Minimum similarity thresholds: ES score ≥ 0.35, cosine ≥ 0.60.

**Files to create:** `ai/legal/legal_pipeline.py`, `ai/legal/ipc_classifier.py`, `ai/legal/crime_triple_extractor.py`, `ai/legal/qa_engine.py`

---

### Phase 42 — Forensic Content Intelligence
**Branch:** `feature/phase-42-content-intelligence` | **Priority:** HIGH
**Issue:** `issues/042-content-intelligence.md`

**Summary:** Shannon entropy content classifier distinguishes genuine documents from fabricated ones. Chi-squared test on document structure distributions (paragraph lengths, punctuation frequencies) detects template reuse. Hash classifier against known-good and known-bad document signature databases. Perceptual hash (pHash) similarity for detecting watermarked or edited government documents. Full evidence extractor using regex patterns for PAN numbers, CIN identifiers, masked Aadhaar references, cryptocurrency wallet addresses, and Indian Rupee amounts — all extracted from raw text and linked to graph nodes automatically.

**Files to create:** `ai/forensics/content_intelligence.py`, `ai/forensics/evidence_extractor.py`, `ai/forensics/hash_classifier.py`

---

### Phase 43 — Pivot Recommendation Engine
**Branch:** `feature/phase-43-pivot-engine` | **Priority:** HIGH
**Issue:** `issues/043-pivot-engine.md`

**Summary:** An AI-powered investigation pivot system that tells analysts their best next move. For any entity under investigation, compute a pivot score for every connected entity: PageRank × α + evidence_gap × β + log(risk_signals) × γ. The entity with the highest pivot score is the recommended next target. Inspired by OSINT investigation methodology where pivoting from one entity to a related one often unlocks a chain of evidence. Integrates with the job queue — high-priority pivots are automatically queued for background investigation.

**Files to create:** `ai/pivot/recommendation_engine.py`, `ai/pivot/evidence_gap_scorer.py`
**Route:** `GET /pivot/{entity_id}` — returns ranked list of recommended next investigation targets.

---

### Phase 44 — Geospatial Verification
**Branch:** `feature/phase-44-geospatial` | **Priority:** MEDIUM
**Issue:** `issues/044-geospatial.md`

**Summary:** Sentinel-2 satellite imagery analysis for verifying that claimed government construction projects exist on the ground. NDVI change detection for forest diversion and mangrove destruction near infrastructure projects. Build-completion mismatch: compare claimed % completion in contract documents against observable construction progress from satellite. Contract location validation: extract GPS coordinates from contract documents and cross-reference with satellite evidence. Free Sentinel-2 data via Copernicus Open Access Hub API.

**Files to create:** `ai/geospatial/sentinel_verifier.py`, `ai/geospatial/location_extractor.py`, `api/routes/geospatial.py`
**Route:** `GET /geospatial/verify/{contract_id}`

---

### Phase 45 — Provenance and Evidence Audit Layer
**Branch:** `feature/phase-45-provenance` | **Priority:** HIGH
**Issue:** `issues/045-provenance.md`

**Summary:** Full deterministic provenance for every node, edge, and conclusion: source, timestamp, extraction method, transformation history, confidence level, and operator. Implements W3C PROV-DM model for evidence artifacts. Claim-evidence audit panel: which evidence supports vs. weakens each finding. Evidence states: CONFIRMED, PROBABLE, WEAK, REJECTED. Evidence chain export as JSON-LD using Schema.org ontology (inspired by Flowsint issue #132) — maps entities to `schema:Person`, `schema:Organization`, `schema:MoneyTransfer`, and BharatGraph-specific types. Graph mutations use enrichment IDs with input snapshots and output diffs, enabling full replay and rollback (Flowsint Graph Conductor pattern).

**Files to create:** `ai/provenance_engine.py`, `ai/evidence_ranker.py`, `api/routes/provenance.py`
**Routes:** `GET /export/evidence-chain/{entity_id}`, `GET /export/audit/{entity_id}`, `POST /revert/{enrichment_id}`

---

### Phase 46 — Source Drift and Historical Analysis
**Branch:** `feature/phase-46-historical` | **Priority:** HIGH
**Issue:** `issues/046-historical.md`

**Summary:** Detect when government records change, disappear, or are silently modified after publication. Compare current data against Wayback Machine snapshots using the CDX API. Track first-appearance dates for all claims — when a document appears that predates the entity's known history, flag it. Evidence status lifecycle: ACTIVE → MODIFIED → REMOVED → ARCHIVED. "When did this exist?" reconstruction for pages that have been taken down. Temporal edge timestamp analysis: edges that appeared and disappeared within short windows suggest data manipulation.

**Files to create:** `ai/forensics/source_drift_detector.py`, `ai/forensics/wayback_verifier.py`, `api/routes/historical.py`
**Route:** `GET /historical/{entity_id}`

---

### Phase 47 — Predictive Risk and Lead Prioritisation
**Branch:** `feature/phase-47-predict` | **Priority:** HIGH
**Issue:** `issues/047-predict.md`

**Summary:** ARIMA time series model for 6-month risk trajectory forecasting based on historical indicator trends. Random Forest ensemble trained on confirmed/unconfirmed investigation outcomes from case memory. Lead prioritisation ranking: entities are automatically sorted by: PageRank centrality × predicted risk trajectory × evidence gap × anomaly score. Analysts see the highest-value investigation targets first. Automatic "investigate next" queue populated from the ranking. Confidence intervals on all predictions.

**Files to create:** `ai/forensics/risk_predictor.py`, `ai/lead_ranker.py`, `api/routes/predict.py`
**Route:** `GET /predict/{entity_id}`

---

### Phase 48 — Watchlist and Real-Time Alerts
**Branch:** `feature/phase-48-watchlist` | **Priority:** MEDIUM
**Issue:** `issues/048-watchlist.md`

**Summary:** Persistent watchlist: analysts add entities to a watchlist and receive WebSocket push alerts when new data appears, risk scores change, new connections are formed, or audit flags appear. Diff-based alerting: "new DIRECTOR_OF relationship added to pol_003", "risk score for co_001 increased from 42 to 67". Email and webhook notification support via configurable channels. Alert rule engine: analysts define custom alert conditions in YAML without writing code. Inspired by Flowsint event timestamps issue #106 — every mutation now records when it happened so diffing is precise.

**Files to create:** `api/routes/watchlist.py`, `ai/alert_engine.py`, `workers/alert_dispatcher.py`
**Routes:** `POST /watchlist`, `GET /watchlist`, `GET /watchlist/alerts`, `DELETE /watchlist/{entity_id}`

---

### Phase 49 — Observability and Pipeline Reliability
**Branch:** `feature/phase-49-observability` | **Priority:** HIGH
**Issue:** `issues/049-observability.md`

**Summary:** Per-stage pipeline metrics: records per scraper per run, success/failure rates, latency, last-run timestamp. Prometheus-compatible `/metrics` endpoint. Stale-data detection: alert when any source has been silent for 30+ days. Ingestion validator: schema checks before any record enters the graph — malformed records are quarantined, not silently dropped. Partial-ingestion save: if the pipeline fails halfway, completed sources are preserved. Retry with exponential backoff on all scrapers. Grafana dashboard definition file included. CI/CD hardening: Bandit static analysis, Safety dependency scanner, Trivy container scanner, all blocking PR merges.

**Files to create:** `api/middleware/metrics_collector.py`, `processing/ingestion_validator.py`, `monitoring/dashboard.py`, `deploy/ci.yml`
**Routes:** `GET /admin/metrics`, `GET /admin/pipeline-health`

---

### Phase 50 — Full 22-Language Output Engine
**Branch:** `feature/phase-50-language` | **Priority:** HIGH
**Issue:** `issues/050-language.md`

**Summary:** Complete multilingual output for all 22 Indian scheduled languages on every API endpoint — not just the search route. Domain-specific vocabulary for government, legal, and financial terminology in each language. Language auto-detection from `Accept-Language` browser header with fallback to the query-detected language. RTL layout support for Urdu, Kashmiri, and Sindhi. All 15 UI label keys including nav, filters, buttons, and headings available in 10+ languages via `/ui-labels`. Transliteration lookup table expanded to cover all entity names in the graph across all 22 scripts.

**Files to update:** `config/languages.py`, `ai/translator.py`, `frontend/js/app.js`

---

### Phase 51 — Security Hardening v2 and PII Protection
**Branch:** `feature/phase-51-security` | **Priority:** HIGH
**Issue:** `issues/051-security.md`

**Summary:** PII masking: automatic redaction of Aadhaar numbers, masked phone numbers, and personal financial details in all API output. Role-based access control (RBAC) with three roles: admin, analyst, viewer. Short-lived JWT access tokens (15-minute expiry) with refresh token rotation and revocation on sensitive events (Flowsint PR #135 pattern). DPDP Act 2023 compliance review. Defamation safeguard review — legal language enforcement audited. All injection attack surfaces hardened. Encryption at rest for the audit log. Penetration test script included.

**Files to create:** `api/middleware/auth.py`, `api/middleware/pii_masker.py`, `api/routes/auth.py`

---

### Phase 52 — Evidence Graph Frontend Upgrade
**Branch:** `feature/phase-52-evidence-graph` | **Priority:** HIGH
**Issue:** `issues/052-evidence-graph.md`

**Summary:** New investigation UI flow: entity input → data collection progress bar (live WebSocket) → graph construction (nodes appear in real time as evidence is found) → evidence-ranked results. Clustering for large graphs (>50 nodes) using force-directed community layout. Level-of-detail rendering: distant nodes shown as circles, nearby nodes expanded to show properties. Evidence strength as edge thickness. Confidence as node opacity. Time slider for temporal graph view — watch the evidence graph build over time. Evidence status badges: CONFIRMED (green), PROBABLE (orange), WEAK (grey), REJECTED (red strikethrough). File upload support for importing external documents into an investigation (Flowsint issue #137 pattern).

---

### Phase 53 — Confidence and Scoring Framework
**Branch:** `feature/phase-53-confidence` | **Priority:** HIGH
**Issue:** `issues/053-confidence.md`

**Summary:** Unified confidence engine: every claim carries a 0–100 confidence score. Confidence decay: evidence older than 6 months loses 0.5% per week. Multi-source boost: the same finding confirmed by 3+ independent sources raises confidence by 15 points per additional source. Uncertainty propagation through graph paths: weak evidence reduces confidence of downstream claims. Evidence ranker: CONFIRMED ≥ 80, PROBABLE ≥ 50, WEAK ≥ 20, REJECTED < 20. All investigator weights become dynamic — adjusted by the confidence engine based on historical accuracy of each investigator type.

**Files to create:** `ai/confidence_engine.py`, `ai/evidence_ranker.py`

---

### Phase 54 — Investigation Workspace and Case Management
**Branch:** `feature/phase-54-workspace` | **Priority:** MEDIUM
**Issue:** `issues/054-workspace.md`

**Summary:** Persistent investigation workspace: save and resume investigations. Export investigation as a shareable link with integrity hash. Bookmark entities for the watchlist. Step-by-step investigation wizard for first-time users. Investigation replay: see how conclusions were built step by step (powered by the provenance layer). Case templates: reusable investigation setups for common patterns (politician-contractor, circular ownership, electoral bond donor). Multi-user collaboration: multiple analysts can annotate the same investigation (government/organisation deployments). Undo enrichment with full revert history (Flowsint issue #109 pattern).

**Routes:** `POST /workspace`, `GET /workspace/{id}`, `GET /workspace/{id}/share`, `POST /workspace/{id}/revert/{step}`

---

### Phase 55 — Expanded Data Pipeline (367+ Sources)
**Branch:** `feature/phase-55-data-expansion` | **Priority:** CRITICAL
**Issue:** `issues/055-data-expansion.md`

**Summary:** Expand from 21 to 367+ verified real Indian government data sources. Priority additions: all 28 High Courts, all 700+ district courts via NJDG, all state CAG reports (not just central), MCA company master bulk download (6M+ companies), AGMARKNET commodity prices, PARIVESH environment clearances, TRAI telecom orders, DGFT trade data, CCI antitrust orders, EPFO payroll data, all state e-Gazette publications, 29 Pollution Control Boards, 29 state forest department portals, all PSU annual reports. Each new scraper auto-registers with the plugin system — zero changes to core code. Dataset management module: SHA-256 verification, versioning, auto-download, and retry.

**Files to create:** 30+ new scraper files, `data/dataset_manager.py`, updated `datasets/bharatgraph_sources.csv`

---

### Phase 56 — Production Launch
**Branch:** `feature/phase-56-production` | **Priority:** PLANNED
**Issue:** `issues/056-production.md`

**Summary:** Full CI/CD pipeline with automated end-to-end tests on all 25+ API routes. Load testing at 100 concurrent users. Composite Neo4j indexes on all frequently-queried property combinations. Mobile-responsive layout across all views. Progressive Web App (PWA) manifest with offline capability via service worker. Full OpenAPI 3.0 documentation. Postman collection for all endpoints. Correction request workflow: any entity can submit a correction with documentary evidence — verified corrections processed within 14 days. Public launch announcement. Dedicated documentation site.

---

## Phase Execution Order Summary

| Sequence | Phase | Reason for position |
|----------|-------|---------------------|
| 31 | Runtime Profile | Must precede all compute-intensive phases |
| 32 | Entity Resolution v2 | Fixes data quality — all later analysis depends on it |
| 33 | Custom Graph Engine | Infrastructure — decouples from Neo4j limits |
| 34 | Vector Search | Requires graph engine + embeddings |
| 35 | Plugin System | Required for data expansion phases |
| 36 | Rule Engine | Requires stable graph + plugin system |
| 37 | Job Queue | Required for async AI inference phases |
| 38–40 | DeepSeek R1/VL2/V3 | Requires job queue for background processing |
| 41–43 | Legal, Forensic, Pivot | Builds on AI reasoning from 38–40 |
| 44 | Geospatial | Independent — can run in parallel |
| 45–46 | Provenance, Historical | Requires stable entity resolution |
| 47–48 | Predict, Watchlist | Requires provenance + temporal data |
| 49 | Observability | Should precede data expansion |
| 50–51 | Language, Security | Can run in parallel |
| 52–53 | Frontend, Confidence | Requires all backend phases |
| 54 | Workspace | Requires confidence + provenance |
| 55 | Data Expansion | Requires plugin system |
| 56 | Production Launch | All phases complete |
