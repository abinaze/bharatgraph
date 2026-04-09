# BharatGraph — Complete Phase Roadmap

All branches merge directly into main. Branch naming: feature/phase-N-name or fix/issue-name.

---

## COMPLETED

### Phase 1 — Data Collection
Branch: feature/phase-1-scrapers | Tag: (pre-tagging)
Files: scrapers/base_scraper.py + 6 scrapers
Result: 3,199 live records confirmed

### Phase 2 — Data Processing
Branch: feature/phase-2-processing
Files: processing/cleaner.py, processing/entity_resolver.py, processing/pipeline.py
Result: 47 records in 15 seconds confirmed

### Phase 3 — Graph Database
Branch: feature/phase-3-graph
Files: graph/schema.py, graph/loader.py, graph/queries.py
Result: Neo4j AuraDB connected: neo4j+s://1a34e3b8.databases.neo4j.io

### Phase 4 — FastAPI Backend
Branch: feature/phase-4-api
Files: api/main.py, api/models.py, api/dependencies.py, api/routes/ (4 files)
Result: v0.12.0

### Phase 5 — Risk Scoring Engine
Branch: feature/phase-5-risk
Files: ai/indicators.py, ai/explainer.py, ai/risk_scorer.py
Result: validate_language() enforced on all output

### Phase 6 — Expanded Data Sources (13 scrapers)
Branch: feature/phase-6-scrapers
Files: icij_scraper.py, wikidata_scraper.py, opensanctions_scraper.py,
       loksabha_scraper.py, sebi_scraper.py, electoral_bond_scraper.py
Result: Wikidata SPARQL confirmed live

### Phase 7 — NLP Document Intelligence
Branch: feature/phase-7-nlp
Files: ai/nlp_extractor.py, ai/benfords_analyzer.py, ai/multilingual_ner.py,
       ai/shadow_draft_detector.py
Result: 93.35% shadow draft alignment confirmed

### Phase 8 — Advanced Graph Analytics
Branch: feature/phase-8-graph-analytics
Files: ai/graph_analytics.py, ai/circular_ownership.py, ai/shadow_director.py,
       ai/ghost_company.py
Result: Ghost company 100/100 confirmed

### Phase 9 — Eight New Indian Sources (21 total scrapers)
Branch: feature/phase-9-scrapers
Files: njdg_scraper.py, ed_scraper.py, cvc_scraper.py, ncrb_scraper.py,
       lgd_scraper.py, ibbi_scraper.py, ngo_darpan_scraper.py, cppp_scraper.py
Result: NJDG 39 live records confirmed

### Phase 10 — Multi-Investigator AI Engine
Branch: feature/phase-10-multi-investigator
Files: ai/multi_investigator.py, ai/investigators/ (12 investigator files)
Result: SHA-256 report hash confirmed, synthesis working

### Phase 11 — Multilingual Platform (22 Languages)
Branch: feature/phase-11-multilingual
Files: config/languages.py, ai/translator.py, ai/transliteration.py,
       api/routes/multilingual.py
Result: 22 languages, cross-script search confirmed

### Phase 12 — PDF Dossier Generator
Branch: feature/phase-12-pdf-dossier
Files: ai/report_hasher.py, ai/dossier_generator.py, templates/dossier_en.html,
       api/routes/export.py
Result: 10,829 char HTML confirmed, SHA-256 tamper detection working

### Phase 13 — Production Frontend
Branch: feature/phase-13-frontend
Files: frontend/index.html, frontend/css/ (2 files), frontend/js/ (5 files)
Result: Works from file:// protocol, D3.js graph confirmed

### Phase 14 — Zero Cold-Start Deployment
Branch: feature/phase-14-deployment | Tag: v0.14.0
Files: app.py, Dockerfile, frontend/sw.js, .github/workflows/static.yml,
       graph/seed.py, api/routes/admin.py
Result: Live at abinazebinoy-bharatgraph.hf.space

### Phase 15 — Mathematical Intelligence Engine
Branch: feature/phase-15-math-intelligence | Tag: v0.15.0
Files: ai/math/__init__.py, ai/math/spectral_analyzer.py,
       ai/math/fourier_timeline.py, ai/investigators/math_investigator.py
Result: Spectral Fiedler value and Fourier pattern detection confirmed

### Phase 16 — Evidence Connection Map and Deep Investigation Engine
Branch: feature/phase-16-evidence-map | Tag: v0.16.0
Files: ai/deep_investigator.py, ai/connection_mapper.py,
       api/routes/investigation.py, frontend/js/evidence_panel.js
Result: 6-layer investigation engine confirmed, node click panel working

### Phase 17 — Security Hardening and Provenance Layer
Branch: feature/phase-17-security | Tag: v0.17.0
Files: api/middleware/rate_limiter.py, api/middleware/security_headers.py,
       api/middleware/input_validator.py, api/middleware/audit_logger.py,
       blockchain/audit_chain.py
Result: Rate limiting, CSP headers, SHA-256 audit chain confirmed

### Phase 18 — Self-Learning System and Case Memory
Branch: feature/phase-18-self-learning | Tag: v0.18.0
Files: ai/self_learning/ (5 files), ai/case_memory/case_store.py,
       .github/workflows/weekly_learn.yml
Result: Schema learner, pattern learner, weight optimiser, self-audit confirmed

### Phase 19 — Affidavit Wealth Trajectory Engine
Branch: feature/phase-19-affidavit-trajectory | Tag: v0.19.0
Files: ai/forensics/affidavit_analyzer.py,
       ai/investigators/affidavit_investigator.py, api/routes/affidavit.py
Result: VERY_HIGH level, Rs 42.7 Cr residual (7.1x), 3 Kalman anomalies confirmed

### Phase 20 — Biography Engine
Branch: feature/phase-20-biography-engine | Tag: v0.20.0
Files: ai/biography/timeline_builder.py, ai/biography/convergence_detector.py,
       ai/biography/biography_generator.py, api/routes/biography.py,
       frontend/js/timeline.js
Result: 8-event timeline, 5-type convergence detection confirmed

### Phase 21 — Benami Entity Detection
Branch: feature/phase-21-benami-detection | Tag: v0.21.0
Files: ai/forensics/benami_detector.py,
       ai/investigators/benami_investigator.py, api/routes/benami.py
Result: 5-factor proxy scoring confirmed

### Phase 22 — Procurement DNA, Cartel Detection, and Full Pipeline Expansion
Branch: feature/phase-22-procurement | Tag: v0.22.0
Files: ai/forensics/bid_dna.py, ai/forensics/cartel_detector.py,
       api/routes/procurement.py, api/routes/sources.py,
       processing/pipeline.py (expanded to 20 scrapers)
Also: admin.py updated with POST /admin/pipeline background trigger
Result: TF-IDF bid similarity, rotation detection, all 20 scrapers confirmed

### Phase 23 — Revolving Door and TBML Detection
Branch: feature/phase-23-revolving-door | Tag: v0.23.0
Files: ai/forensics/revolving_door.py, ai/forensics/tbml_detector.py,
       api/routes/conflict.py
Result: Cooling-off detection, price anomaly, director-change window confirmed

---

## CURRENT — Phase 24

### Phase 24 — Linguistic Fingerprinting

GitHub Issue:
```
Title: feat(ai/forensics): linguistic fingerprinting — authorship attribution,
       template reuse, shadow drafting detection

Labels: feature, enhancement

Scope:
  ai/forensics/linguistic_fingerprint.py  Burrows Delta + TF-IDF template reuse
  api/routes/linguistic.py                GET /linguistic/fingerprint/{entity_id}
  api/main.py                             Register linguistic router

Acceptance Criteria:
  * Burrows Delta correctly identifies closest authorship cluster for test docs
  * Template reuse detects structurally identical documents from different dates
  * Shadow drafting similarity score matches known corporate-bill text pairs
  * Route returns structured findings with evidence
```

Branch: feature/phase-24-linguistic-fingerprinting

See Phase 24 step-by-step below.

---

## PLANNED

### Phase 25 — Policy-Benefit Causal Analysis
Scope:
  ai/forensics/policy_benefit_analyzer.py: Granger causality on policy+contract pairs.
  Transfer entropy for directional causality. Cumulative Abnormal Contract Award (CACA).
  api/routes/policy.py: GET /policy/causal/{entity_id}

### Phase 26 — Adversarial Counterevidence and Competing Hypotheses
Scope:
  ai/adversarial_engine.py: forced disproof search for every HIGH finding.
  Hypothesis A/B/C mode with evidence-for/evidence-against scorecard.
  Confidence adjustment on verified vs disputed findings.
  api/routes/adversarial.py: GET /adversarial/{entity_id}

### Phase 27 — Multi-Agent Debate Engine
Scope:
  ai/debate_engine.py: iMAD-style 3-round structured debate with anti-drift.
  Linguistic hesitation detection (41 features) triggers selective debate.
  Consensus + dissent tracking per finding. Adaptive routing by complexity.
  Agent profiles: JSON configs with skepticism, curiosity, strictness knobs.

### Phase 28 — Dark Pattern Detection
Scope:
  ai/forensics/dark_pattern_detector.py: PrefixSpan sequential pattern mining.
  6 pre-defined high-risk administrative sequences. Timing window significance test.
  api/routes/darkpattern.py: GET /darkpattern/{entity_id}

### Phase 29 — Source-Drift and Historical Analysis
Scope:
  ai/source_credibility.py: Wayback Machine CDX API, retroactive edit detection.
  Claim survival scoring across time versions. Archive-gap recovery.
  Before/after diff view. Evidence status: Active/Modified/Removed/Archived.

### Phase 30 — Predictive Risk and Auto-Prioritisation
Scope:
  ai/predictive_risk.py: 3-model ensemble (linear, Random Forest, ARIMA).
  6-month risk trajectory forecast. Lead priority score combining centrality,
  anomaly, recency, and novelty. Early Warning System live feed alerts.

### Phase 31 — Geospatial Verification
Scope:
  scrapers/sentinel_scraper.py: Copernicus Open Access Hub (free Sentinel-2).
  ai/geospatial/ndvi_analyzer.py: NDVI change detection.
  ai/geospatial/build_verifier.py: payment vs visible construction cross-check.
  Contract location map in frontend with before/after satellite image comparison.

### Phase 32 — Identity Fusion and Multimedia OSINT
Scope:
  ai/identity/alias_resolver.py: alias-to-email linking, credential reuse.
  ai/identity/persona_cluster.py: cross-platform identity fusion.
  ai/osint/background_analyzer.py: background-object extraction from images.
  ai/osint/reverse_image.py: pattern-of-life from public image metadata.
  ai/osint/username_tracker.py: cross-platform reuse detection.

---

## Feature Index

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
| M | Report generation with evidence ranking | 12 |
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
