# BharatGraph — Complete Phase Roadmap

All branches merge directly into `main`. One branch per phase.
Branch naming: `feature/phase-N-name` or `fix/issue-N-name`.

---

## COMPLETED

### Phase 1 — Data Collection
Branch: `feature/phase-1-scrapers` | Status: MERGED
Files: `scrapers/base_scraper.py` + 6 scrapers
Result: 3,199 live records confirmed

### Phase 2 — Data Processing
Branch: `feature/phase-2-processing` | Status: MERGED
Files: `processing/cleaner.py`, `processing/entity_resolver.py`, `processing/pipeline.py`
Result: 47 records in 15 seconds confirmed

### Phase 3 — Graph Database
Branch: `feature/phase-3-graph` | Status: MERGED
Files: `graph/schema.py`, `graph/loader.py`, `graph/queries.py`
Result: Neo4j AuraDB connected

### Phase 4 — FastAPI Backend
Branch: `feature/phase-4-api` | Status: MERGED
Files: `api/main.py`, `api/models.py`, `api/dependencies.py`, `api/routes/` (4 files)
Result: v0.12.0

### Phase 5 — Risk Scoring Engine
Branch: `feature/phase-5-risk` | Status: MERGED
Files: `ai/indicators.py`, `ai/explainer.py`, `ai/risk_scorer.py`
Result: validate_language() enforced

### Phase 6 — Expanded Data Sources (13 scrapers)
Branch: `feature/phase-6-scrapers` | Status: MERGED
Files: 6 new scrapers (ICIJ, Wikidata, OpenSanctions, Lok Sabha, SEBI, Electoral Bonds)
Result: Wikidata SPARQL confirmed live

### Phase 7 — NLP Document Intelligence
Branch: `feature/phase-7-nlp` | Status: MERGED
Files: `ai/nlp_extractor.py`, `ai/benfords_analyzer.py`, `ai/multilingual_ner.py`, `ai/shadow_draft_detector.py`
Result: 93.35% shadow draft alignment confirmed

### Phase 8 — Advanced Graph Analytics
Branch: `feature/phase-8-graph-analytics` | Status: MERGED
Files: `ai/graph_analytics.py`, `ai/circular_ownership.py`, `ai/shadow_director.py`, `ai/ghost_company.py`
Result: Ghost company 100/100 confirmed

### Phase 9 — Eight New Indian Sources (21 total scrapers)
Branch: `feature/phase-9-scrapers` | Status: MERGED
Files: 8 new scrapers (NJDG, ED, CVC, NCRB, LGD, IBBI, NGO Darpan, CPPP)
Result: NJDG 39 live records confirmed

### Phase 10 — Multi-Investigator AI Engine
Branch: `feature/phase-10-multi-investigator` | Status: MERGED
Files: `ai/multi_investigator.py`, `ai/investigators/` (12 files)
Result: SHA-256 hash confirmed, synthesis working

### Phase 11 — Multilingual Platform (22 Languages)
Branch: `feature/phase-11-multilingual` | Status: MERGED
Files: `config/languages.py`, `ai/translator.py`, `ai/transliteration.py`, `api/routes/multilingual.py`
Result: 22 languages, cross-script search confirmed

### Phase 12 — PDF Dossier Generator
Branch: `feature/phase-12-pdf-dossier` | Status: MERGED
Files: `ai/report_hasher.py`, `ai/dossier_generator.py`, `templates/dossier_en.html`, `api/routes/export.py`
Result: 10,829 char HTML confirmed, SHA-256 tamper detection working

### Phase 13 — Production Frontend
Branch: `feature/phase-13-frontend` | Status: MERGED
Files: `frontend/index.html`, `frontend/css/` (2), `frontend/js/` (5)
Result: Works from file://, D3.js graph confirmed

### Phase 14 — Zero Cold-Start Deployment ✓ LIVE
Branch: `feature/phase-14-deployment` | Status: MERGED | Tag: v0.14.0
Files: `app.py`, `Dockerfile`, `frontend/sw.js`, `.github/workflows/` (static.yml),
       `graph/seed.py`, `api/routes/admin.py`
Result: Live at abinazebinoy-bharatgraph.hf.space, Frontend at abinaze.github.io/bharatgraph

---

## NEXT — Phase 15

### Phase 15 — Mathematical Intelligence Engine

**GitHub Issue:**
```
Title: feat(ai/math): mathematical intelligence engine — 6 analytical frameworks
Labels: feature, enhancement

Problem:
  Current risk scoring uses simple weighted sums. Advanced mathematical methods
  from computational topology, rough path theory, spectral graph theory, and
  information geometry surface patterns invisible to linear weights.

Scope:
  ai/math/__init__.py
  ai/math/spectral_analyzer.py       Graph Laplacian Fiedler value (bridge detection)
  ai/math/fourier_timeline.py        FFT on contract/audit date sequences
  ai/math/path_signature.py          Rough path signatures on financial sequences
  ai/math/topology_analyzer.py       Persistent homology on entity clusters
  ai/math/anomaly_scorer.py          Ensemble combining all 6 methods
  ai/math/information_gain.py        Mutual information + causal feature ranking
  ai/investigators/math_investigator.py  New 13th investigator

Frameworks:
  1. Spectral: L = D-A, Fiedler value λ₁ = algebraic connectivity
  2. Fourier: FFT on contract amount time series, detect periodic patterns
  3. Path Signature: iisignature.sig(X, level=3) on (date, amount) paths
  4. Topology: Vietoris-Rips filtration, persistent homology, loop detection
  5. Benford++: Nigrini sub-tests + Fisher combination T = -2*sum(ln(p_i))
  6. Causal: mutual_info_classif + PC algorithm Markov blanket

Acceptance Criteria:
  * spectral_analyzer returns Fiedler value for sample graph
  * fourier_timeline detects synthetic periodic pattern
  * path_signature produces consistent feature vector
  * topology_analyzer returns persistence diagram for sample cluster
  * anomaly_scorer produces ensemble score 0-100
  * math_investigator integrates with multi-investigator engine
```

Branch: `feature/phase-15-math-intelligence`

See step-by-step instructions in PHASE 15 section below.

---

## PLANNED PHASES

### Phase 16 — Evidence Connection Map + Deep Investigation Engine
Features from research: A, B, C, J, L, N

Scope:
- `ai/deep_investigator.py`: 6-layer recursive analysis engine
- `ai/connection_mapper.py`: evidence path finder between any two entities
- `api/routes/investigation.py`: GET /investigate/{id}, GET /connection-map
- `frontend/js/evidence_panel.js`: clickable side panel with WHY/HOW/SOURCE
- `frontend/js/graph.js` update: click triggers evidence panel

Graph features:
- Relationship labels: director, contract, ministry, audit, party, scheme, owner
- Source document on every edge
- Timeline order on every connection
- Hop count / connection distance
- Connection strength: strong / weak / uncertain
- Bridge entity markers
- Conflicting-source markers
- Repeated-entity detection across contexts
- "Investigate Further" button in panel
- Hidden-link suggestions (next likely entity)
- Recursive one-hop → two-hop → archive → contradiction passes

### Phase 17 — Security Hardening + Provenance Layer
Features from research: G

Scope:
- `api/middleware/rate_limiter.py`: sliding window (100/min search, 10/min export)
- `api/middleware/security_headers.py`: CSP, HSTS, X-Frame-Options
- `api/middleware/input_validator.py`: 200 char limit, parameterised queries only
- `api/middleware/audit_logger.py`: append-only SHA-256 hash chain
- `blockchain/audit_chain.py`: daily root hash in Neo4j
- Provenance fields on every node/edge: origin_url, fetch_date, parser_version,
  extraction_method, confidence_source, lineage_chain, last_validated

### Phase 18 — Self-Learning + Case Memory
Features from research: P, Q

Scope:
- `ai/self_learning/schema_learner.py`: new field detection → human review gate
- `ai/self_learning/pattern_learner.py`: weekly subgraph mining
- `ai/self_learning/source_discoverer.py`: data.gov.in catalog monitoring
- `ai/self_learning/weight_optimizer.py`: 3 confirmations minimum before update
- `ai/self_learning/self_audit.py`: weekly scraper health check + GitHub alerts
- `ai/case_memory/`: solved-case library, reusable reasoning patterns, false-positive signatures
- Human-in-the-loop: "review this merge" queue, "review this link" queue
- `.github/workflows/weekly_learn.yml`

### Phase 19 — Affidavit Wealth Trajectory Engine
Scope:
- `ai/forensics/affidavit_analyzer.py`: Kalman filter on 5 election cycles
- Expected income model vs actual growth: salary + FD returns
- Asset disappearance detection across years
- Pre-election movable asset surge detector
- `ai/investigators/affidavit_investigator.py`

### Phase 20 — Biography Engine
Scope:
- `ai/biography/timeline_builder.py`: multi-source timeline from all 28 sources
- `ai/biography/convergence_detector.py`: temporal event alignment
- `ai/biography/biography_generator.py`: neutral narrative generation
- `api/routes/biography.py`: GET /biography/{entity_id}
- `frontend/js/timeline.js`: vertical scrollable timeline component

### Phase 21 — Benami Entity Detection
Features from research: H

Scope:
- `ai/forensics/benami_detector.py`: 5-factor proxy scoring
- Node2Vec graph embeddings for similarity
- Family surname network construction
- Director age anomaly (< 22 = proxy flag)
- Address proximity clustering
- `ai/investigators/benami_investigator.py`

### Phase 22 — Procurement DNA + Cartel Detection
Scope:
- `ai/forensics/bid_dna.py`: TF-IDF structural fingerprinting
- `ai/forensics/cartel_detector.py`: price ratio, rotation, cover bid
- Bid cosine similarity between supposedly competing vendors
- Vendor co-bidding network with Louvain community detection
- Hotelling T-squared test on price ratios

### Phase 23 — Revolving Door + TBML Detection
Features from research: V

Scope:
- `ai/forensics/revolving_door.py`: career graph, cooling-off violations
- `ai/forensics/tbml_detector.py`: commodity mismatch, price anomaly vs median
- Pre-employment benefit scoring
- Post-retirement board appointment gap analysis
- `ai/investigators/conflict_investigator.py`

### Phase 24 — Linguistic Fingerprinting
Scope:
- `ai/forensics/linguistic_fingerprint.py`: Burrows' Delta authorship attribution
- Template reuse via Rabin rolling hash fingerprint
- Shadow drafting: corporate consultation vs final bill text
- Cross-document authorship clustering
- `ai/investigators/linguistic_investigator.py`

### Phase 25 — Policy-Benefit Causal Analysis
Scope:
- `ai/forensics/policy_benefit_analyzer.py`: Granger causality + transfer entropy
- Cumulative Abnormal Contract Award (CACA) event study
- Policy benefit vector: contract surge ratio around announcements
- `ai/investigators/policy_investigator.py`

### Phase 26 — Adversarial Counterevidence + Competing Hypotheses
Features from research: S

Scope:
- `ai/adversarial_engine.py`: forced disproof search for every HIGH finding
- Contra-hypothesis generation with alternative explanation library
- Hypothesis A/B/C mode with evidence scorecard
- Confidence adjustment: verified findings marked, disputed findings flagged
- `ai/investigators/adversarial_investigator.py`

### Phase 27 — Multi-Agent Debate Engine
Features from research: D, E, R

Scope:
- `ai/debate_engine.py`: iMAD-style 3-round structured debate
- Linguistic hesitation detection (41 features) → selective debate trigger
- Anti-drift via semantic similarity check (DRIFTJudge adapted)
- Dual-agent: filter agent + reasoning agent pipeline
- Consensus + dissent tracking: findings with "18 agree, 3 reject"
- Adaptive routing: simple → small panel, complex → full debate
- Personality parameters per investigator: skepticism, curiosity, strictness
- Agent profiles as JSON configs

### Phase 28 — Dark Pattern Detection
Scope:
- `ai/forensics/dark_pattern_detector.py`: PrefixSpan sequential mining
- 6 pre-defined high-risk administrative sequences
- Timing window significance test (z-score vs null distribution)
- Dark pattern score 0-100 integrated with risk engine
- `ai/investigators/dark_pattern_investigator.py`

### Phase 29 — Source-Drift + Historical Analysis
Features from research: F

Scope:
- `ai/source_credibility.py`: Wayback Machine CDX API integration
- Temporal diff: live page vs 2-year-old archive vs 4-year-old archive
- Retroactive editing detection
- Claim survival scoring: facts surviving across all time periods
- Evidence Status: Active / Modified / Removed / Archived
- First-appearance timeline per claim
- Archive-gap recovery for deleted pages
- Before/after diff view in UI

### Phase 30 — Predictive Risk + Auto-Prioritisation
Features from research: O

Scope:
- `ai/predictive_risk.py`: 3-model ensemble (linear, Random Forest, ARIMA)
- 6-month risk trajectory forecast for all tracked entities
- Lead priority score combining centrality + anomaly + recency + novelty
- Early Warning System: live feed alerts for accelerating risk
- Outcome feedback loop: model weight update on confirmed ED/CBI cases

### Phase 31 — Geospatial Verification
Features from research: U

Scope:
- `scrapers/sentinel_scraper.py`: Copernicus Open Access Hub (free Sentinel-2)
- `ai/geospatial/ndvi_analyzer.py`: NDVI change detection
- `ai/geospatial/build_verifier.py`: payment disbursed vs construction visible
- Contract location map in frontend
- Before/after satellite image comparison
- Build-completion mismatch flag

### Phase 32 — Identity Fusion + Multimedia OSINT
Features from research: W, X

Scope:
- `ai/identity/alias_resolver.py`: alias-to-email linking, credential reuse
- `ai/identity/persona_cluster.py`: cross-platform identity fusion
- `ai/osint/background_analyzer.py`: background-object extraction from images
- `ai/osint/reverse_image.py`: pattern-of-life from public image metadata
- `ai/osint/username_tracker.py`: cross-platform reuse detection
- Bridge identifier detection in identity graph

---

## Feature Index (from Research Document)

| Feature | Description | Phase |
|---------|-------------|-------|
| A | Investigation connector map | 16 |
| B | Recursive 6-layer investigation engine | 16 |
| C | Clickable evidence detail panel | 16 |
| D | Multi-agent reasoning swarm | 27 |
| E | Consensus/contradiction/uncertainty layers | 27 |
| F | Historical investigation + archive recovery | 29 |
| G | Provenance and auditability | 17 |
| H | Entity resolution and alias merging | 21 |
| I | Graph analytics features | 15 |
| J | Hidden-link suggestion engine | 16 |
| K | Evidence clustering and bridge detection | 15 |
| L | Recursive find-more mode | 16 |
| M | Report generation with evidence ranking | 12+ |
| N | Practical UI layers for analysts | 16 |
| O | Auto-prioritisation of leads | 30 |
| P | Case memory + investigation history | 18 |
| Q | Human-in-the-loop active learning | 18 |
| R | Adaptive debate routing | 27 |
| S | Competing hypotheses mode | 26 |
| T | Anomaly and suspicion modules | 15 |
| U | Geospatial verification | 31 |
| V | Revolving door + TBML detection | 23 |
| W | Multimedia investigation techniques | 32 |
| X | Identity fusion from breach data | 32 |
