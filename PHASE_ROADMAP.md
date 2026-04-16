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


### Phase 29 — Full UX Overhaul: Evidence Panel + Connection Map + Language UI (v0.29.0)
Branch: feature/phase-29-ux-evidence | Priority: IMMEDIATE
Status: COMPLETE (this session)
Files changed:
  frontend/js/evidence_panel.js — Complete rewrite. 4-tab panel:
    Tab 1 Overview: risk indicator, summary stats, top 5 connections
    Tab 2 Connections: all edges grouped by relationship type, clickable to open chain
    Tab 3 Timeline: event reconstruction from profile API, date-sorted
    Tab 4 Investigate: 6-layer investigation, contradiction search, connection map button
  frontend/js/app.js — Added:
    Language selector dropdown (22 Indian scheduled languages)
    Connection Map route: /connection-map?entity=X&name=Y
    Path Finder: find shortest path between any two entities
    D3 interactive evidence graph rendering for connection map
    Router.register("/connection-map", ...) registered
  frontend/index.html — Fixed:
    Health check retries 3× at 5-second intervals (HF Space cold-start handling)
    API status shows neo4j_connected state and version
  api/main.py — Added: GET / root route returning version, status, links
Result: Loading screen bug resolved. Language selector live. Evidence panel fully tabbed.
  Connection map available. API offline indicator handles cold-starts correctly.

### Phase 30 — Source-Drift and Historical Analysis Engine (v0.30.0)
Branch: feature/phase-30-historical | Priority: HIGH
Files to create:
  ai/forensics/source_drift_detector.py
    compare_versions(url, entity_id) → detect added/removed/modified claims
    first_appearance(claim_text) → earliest Wayback cache date
    drift_report(entity_id) → timeline of claim changes with diff
    evidence_status: ACTIVE | MODIFIED | REMOVED | ARCHIVED
  ai/forensics/event_reconstructor.py
    reconstruct_from_artifacts(entity_id) → event timeline from documents
    temporal_truth_store(entity_id) → versioned fact graph: Fact_v1, Fact_v2
    archive_gap_recovery(url) → Wayback Machine integration for deleted pages
  api/routes/historical.py — GET /historical/{entity_id}
    Returns: drift_events[], first_appearances[], archive_gaps[], evidence_timeline
  api/main.py — register historical router, bump to v0.30.0

### Phase 31 — Predictive Risk and Lead Prioritisation (v0.31.0)
Branch: feature/phase-31-predict | Priority: HIGH
Files to create:
  ai/forensics/risk_predictor.py
    predict_trajectory(entity_id) → 6-month risk trajectory
    ensemble_model() → gradient boost + random forest + logistic regression
    lead_prioritiser(graph) → rank entities by centrality, community, anomaly score
    anomaly_scorer(subgraph) → detect unusual patterns vs peer group
  api/routes/predict.py — GET /predict/{entity_id}
    Returns: risk_6month, trajectory_direction, high_priority_leads[], confidence
  graph/queries.py — add get_peer_group(), get_anomaly_candidates()
  api/main.py — register predict router, bump to v0.31.0

### Phase 32 — Entity Resolution and Deduplication Engine (v0.32.0)
Branch: feature/phase-32-entity-resolution | Priority: CRITICAL
Files to create:
  processing/entity_resolver_v2.py
    resolve(name_a, name_b, context) → merge confidence score
    alias_index(entity_id) → all known aliases, transliterations
    bridge_identifier_detect(graph) → cross-dataset linking keys
    global_id_assign(record) → stable UUID for every resolved entity
    near_duplicate_detect(embeddings) → cosine similarity threshold
  processing/name_normaliser.py
    normalise_indian_name(name) → handle transliterations, honorifics
    ministry_canonical_map() → maps common abbreviations to full names
    company_name_clean(name) → strips Ltd/Pvt/LLP variants
  frontend/js/app.js — add resolution-aware toggle in search results
  api/routes/admin.py — POST /admin/resolve endpoint for manual merges
  api/main.py — bump to v0.32.0

### Phase 33 — Contradiction Engine and Counterevidence Search (v0.33.0)
Branch: feature/phase-33-contradiction | Priority: HIGH
Files to create:
  ai/forensics/contradiction_detector.py
    scan(entity_id) → find contradicting claims across sources
    confidence_decay(evidence, age_days) → reduce weight of old evidence
    counter_investigate(claim) → search for evidence against a claim
    uncertainty_propagate(graph, node) → flow uncertainty through edges
  ai/investigators/adversarial_investigator.py
    investigate(entity_id) → counter-investigator challenging all claims
    hypothesis_rank(hypotheses[]) → score competing explanations
    debate_verdict(for_evidence[], against_evidence[]) → weighted consensus
  api/routes/adversarial.py — already exists, EXTEND with:
    GET /adversarial/{entity_id}/contradict
    GET /adversarial/{entity_id}/hypotheses
  api/main.py — bump to v0.33.0

### Phase 34 — Multi-Agent Orchestration and Consensus Engine (v0.34.0)
Branch: feature/phase-34-multiagent | Priority: HIGH
Files to create:
  ai/agents/agent_orchestrator.py
    route_task(entity_id, task_type) → select specialist agents
    parallel_investigate(entity_id) → run 12 agents in parallel
    consensus_build(agent_outputs[]) → weighted vote with dissent preservation
    adaptive_debate(evidence, controversy_score) → scale to 3/6/12 agents
    consensus_format: {"agree":N, "uncertain":M, "disagree":K, "verdict":"..."}
  ai/agents/agent_profile.py
    profile: name, role, expertise, memory, reputation_score
    memory_recall(entity_id) → past investigation patterns
    reputation_update(outcome) → agent trust score update
  ai/agents/investigator_roles.py
    ROLES: financial, procurement, judicial, political, corporate,
           geographic, temporal, linguistic, network, adversarial,
           public_interest, synthesis
  api/routes/debate.py — already exists, EXTEND with consensus output format
  api/main.py — bump to v0.34.0

### Phase 35 — Graph Intelligence: Anomaly Detection and Link Prediction (v0.35.0)
Branch: feature/phase-35-graph-intelligence | Priority: HIGH
Files to create:
  ai/graph_intelligence.py
    centrality_rank(graph) → betweenness, eigenvector, PageRank
    community_detect(graph) → Louvain clustering
    bridge_detect(graph) → cut nodes connecting separate clusters
    link_predict(node_a, node_b) → Jaccard, Adamic-Adar, common-neighbor
    anomaly_detect_subgraph(subgraph) → compare to peer cluster
    hidden_link_suggest(entity_id) → top 5 links to investigate next
  ai/graph_analytics.py — extend existing with:
    cluster_explain(community) → plain-language story about a cluster
    lead_rank(candidates[]) → prioritise by graph position + evidence strength
  graph/queries.py — add:
    get_centrality_candidates(), get_bridge_nodes(), get_anomalous_edges()
  api/routes/graph.py — extend with:
    GET /graph/anomalies/{entity_id}
    GET /graph/leads/{entity_id}
    GET /graph/bridge-nodes
  api/main.py — bump to v0.35.0

### Phase 36 — Provenance and Evidence Audit Layer (v0.36.0)
Branch: feature/phase-36-provenance | Priority: HIGH
Files to create:
  ai/provenance_engine.py
    stamp(evidence, source, method, timestamp) → full provenance record
    claim_audit(claim_id) → all evidence supporting + opposing
    evidence_rank(evidence[]) → CONFIRMED / PROBABLE / WEAK / REJECTED
    chain_export(entity_id) → legal-style evidence chain JSON
    confidence_score(claim) → multi-source confidence calculation
  graph/schema.py — add Provenance node:
    {claim_id, source, timestamp, method, confidence, status}
  graph/loader.py — stamp every loaded record with provenance
  api/routes/export.py — extend with:
    GET /export/evidence-chain/{entity_id} → ranked JSON
    GET /export/audit/{entity_id} → full provenance export
  frontend/js/evidence_panel.js — add provenance tab to panel
  api/main.py — bump to v0.36.0

### Phase 37 — Watchlist and Alerting System (v0.37.0)
Branch: feature/phase-37-watchlist | Priority: MEDIUM
Files to create:
  api/routes/watchlist.py
    POST /watchlist — add entity to watchlist
    GET /watchlist — list watched entities
    GET /watchlist/alerts — new events since last check
    DELETE /watchlist/{entity_id} — remove from watchlist
  ai/alert_engine.py
    diff_check(entity_id, last_seen) → what changed since last visit
    new_source_detect(entity_id) → new mentions in any source
    risk_change_alert(entity_id) → risk score crossed threshold
  frontend/js/app.js — add watchlist icon on entity cards
    Views["watchlist"]: watchlist management UI
    Router.register("/watchlist", Views.watchlist)
  api/main.py — register watchlist router, bump to v0.37.0

### Phase 38 — Full Data Pipeline for 367+ Sources (v0.38.0)
Branch: feature/phase-38-data-expansion | Priority: CRITICAL
Files to create/extend:
  scrapers/ — add scrapers for all priority sources:
    scraper_ecourts.py — eCourts NJDG data
    scraper_cag.py — extend existing with all CAG report types
    scraper_ncrb.py — NCRB crime statistics by IPC section
    scraper_sebi_orders.py — SEBI enforcement orders database
    scraper_ed_pmla.py — ED PMLA press releases
    scraper_cvc.py — CVC vigilance circulars (extend existing)
    scraper_mca_bulk.py — MCA company master bulk download
    scraper_agmarknet.py — AGMARKNET daily mandi prices
    scraper_parivesh.py — PARIVESH clearance database
    scraper_trai.py — TRAI orders and tariff data
    scraper_dgft.py — DGFT IEC and trade data
    scraper_cci.py — CCI antitrust orders
    scraper_njdg.py — Court pendency data
    scraper_epfo.py — EPFO payroll data
    scraper_isro_transfer.py — ISRO technology transfer records
  graph/loader.py — add 14 new loaders for above scrapers
  datasets/bharatgraph_sources.csv — 367-source verified catalog (DONE this session)
  api/main.py — bump to v0.38.0

### Phase 39 — Geospatial Verification Engine (v0.39.0)
Branch: feature/phase-39-geospatial | Priority: MEDIUM
Files to create:
  ai/geospatial/sentinel_verifier.py
    verify_site(lat, lon, project_name) → satellite before/after comparison
    ndvi_change(lat, lon, date_range) → vegetation loss detection
    construction_detect(lat, lon) → built structure change detection
    contract_validate(contract_id) → verify claimed construction exists
  ai/geospatial/location_extractor.py
    extract_coords(text) → NER-based location extraction
    geocode_india(location_text) → India-specific geocoding
  api/routes/geospatial.py — GET /geospatial/verify/{contract_id}
  frontend/js/app.js — map view in entity profile for geo-tagged contracts
  api/main.py — register geospatial router, bump to v0.39.0

### Phase 40 — Identity Fusion and Multimedia OSINT (v0.40.0)
Branch: feature/phase-40-identity | Priority: MEDIUM
Files to create:
  ai/identity/identity_fuser.py
    fuse(records[]) → merge identity across all sources
    cross_source_match(entity_a, entity_b) → identity probability
    alias_graph(entity_id) → all known identities, aliases, spellings
  ai/identity/osint_collector.py
    collect_media_mentions(name) → news, social, documents
    face_entity_link(image_url, entity_id) → facial recognition match
    document_owner_detect(doc_url) → extract owner from metadata
  api/routes/identity.py — GET /identity/{entity_id}
  api/main.py — register identity router, bump to v0.40.0

### Phase 41 — Observability and Pipeline Reliability (v0.41.0)
Branch: feature/phase-41-observability | Priority: HIGH
Files to create:
  api/middleware/metrics_collector.py
    track(endpoint, latency, status) → Prometheus-compatible metrics
    pipeline_health() → per-scraper success rate
    neo4j_health() → query latency, node count trends
  processing/ingestion_validator.py
    validate_schema(record, schema) → catch malformed records early
    retry_failed(source_key) → retry up to 3× with exponential backoff
    partial_ingestion_save(completed_sources) → don't lose completed work
  api/routes/admin.py — extend with:
    GET /admin/pipeline-health — per-source ingestion status
    GET /admin/metrics — JSON metrics dump
  api/main.py — bump to v0.41.0

### Phase 42 — Report Export and Legal-Safe Output (v0.42.0)
Branch: feature/phase-42-reports | Priority: HIGH
Files to create:
  ai/report_generator.py
    generate(entity_id, format) → ranked dossier report
    evidence_ranking(findings[]) → CONFIRMED / PROBABLE / WEAK / REJECTED
    legal_safe_rewrite(text) → enforce allegation vs verified labeling
    chapter_structure() → identity, relationships, contracts, risk, timeline
  api/routes/export.py — extend with:
    GET /export/dossier/{entity_id}?format=pdf|json|md
    Evidence-ranked output with confidence scores
    Legal disclaimer on every output
  frontend/js/app.js — download report button on entity profile
  api/main.py — bump to v0.42.0

### Phase 43 — Caching and Async Job Processing (v0.43.0)
Branch: feature/phase-43-performance | Priority: MEDIUM
Files to create:
  api/cache.py
    get(key) → Redis or in-memory lookup
    set(key, value, ttl) → store with TTL
    invalidate(entity_id) → clear on data update
  api/job_queue.py
    submit(task_fn, entity_id) → queue long-running task
    status(job_id) → running | done | failed
    result(job_id) → fetch result when ready
  api/routes/investigation.py — return job_id immediately for long tasks
  frontend/js/api.js — add pollJob(job_id) function
  frontend/js/app.js — show progress bar for running investigations
  api/main.py — bump to v0.43.0

### Phase 44 — Full India Language Output Engine (v0.44.0)
Branch: feature/phase-44-language | Priority: HIGH
Files to extend:
  config/languages.py — already has 22 languages, EXTEND:
    add domain-specific vocabulary for all 22 languages
    risk level translations for all 22 (currently only 9)
    UI labels for all 22 (currently only 5)
  ai/translator.py — ensure all 22 scheduled languages produce output
  ai/transliteration.py — add transliteration for:
    hi, ta, te, kn, ml, mr, bn, gu, pa, or, as, ur, sd, kok, mai, mni, sat, ks, ne, doi, sa
  api/routes/multilingual.py — test all 22 language outputs
  frontend/js/app.js — language selector already in (Phase 29)
    Add: auto-detect browser language on load
    Add: search in selected language, show results in same language
  api/main.py — bump to v0.44.0

### Phase 45 — Security Hardening and PII Protection (v0.45.0)
Branch: feature/phase-45-security | Priority: HIGH
Files to create/extend:
  api/middleware/pii_filter.py
    mask_aadhaar(text) → mask Aadhaar numbers in output
    mask_phone(text) → mask phone numbers
    strip_sensitive(record) → remove personally sensitive fields
  api/middleware/input_validator.py — extend with:
    injection_detect(query) → Cypher injection prevention
    payload_size_limit(body) → block oversized requests
    rate_limit_by_ip(request) → sliding window per IP
  api/routes/export.py — add integrity hash to all exports
  .github/workflows/ — add:
    codeql.yml — static analysis
    dependency-check.yml — vulnerable package scan
  api/main.py — bump to v0.45.0

### Phase 46 — Evidence Intelligence Graph Frontend (v0.46.0)
Branch: feature/phase-46-evidence-graph | Priority: HIGH
Files to create:
  frontend/js/app.js — new investigation flow:
    Step 1: Input entity search
    Step 2: Multi-source data collection progress
    Step 3: Graph construction with live nodes appearing
    Step 4: Evidence ranked results with tabs
  frontend/js/graph.js — upgrade:
    Clustering for large graphs (> 50 nodes)
    Level-of-detail rendering (zoom in = more detail)
    Evidence strength as edge thickness
    Confidence as node opacity
    Time slider for temporal graph view
  frontend/css/design-system.css — add:
    .evidence-confirmed (green border)
    .evidence-probable (orange border)
    .evidence-weak (grey border)
    .evidence-rejected (red border strikethrough)
  api/main.py — bump to v0.46.0

### Phase 47 — Dataset Sources Integration (v0.47.0)
Branch: feature/phase-47-sources-integration | Priority: MEDIUM
Files to create:
  datasets/bharatgraph_sources.csv — DONE this session (367 sources)
  scrapers/source_registry.py
    SOURCE_REGISTRY: full dict of all 367 verified sources
    get_by_category(category) → filtered source list
    get_priority_sources() → top 30 most investigation-relevant
    check_availability(url) → test if source is live
  api/routes/sources.py — extend SCRAPER_META with all new sources
    Sources page now shows all 367+ sources with category filter
  frontend/js/app.js — sources page UI with:
    Category tabs (Core, Finance, Environment, Defence, etc.)
    Live status indicator per source
    Link to source + data type
  api/main.py — bump to v0.47.0

### Phase 48 — Investigation Scoring and Confidence Framework (v0.48.0)
Branch: feature/phase-48-confidence | Priority: HIGH
Files to create:
  ai/confidence_engine.py
    score_claim(claim, evidence[]) → 0-100 confidence
    propagate(graph, node) → uncertainty flows to connected nodes
    decay(evidence, age_days) → older evidence loses weight
    multi_source_boost(claim) → confirmed by 3+ sources = higher confidence
  ai/evidence_ranker.py
    rank(findings[]) → CONFIRMED > PROBABLE > WEAK > REJECTED
    explain_rank(finding) → why this ranking was assigned
    threshold: CONFIRMED >= 80, PROBABLE >= 50, WEAK >= 20, REJECTED < 20
  graph/schema.py — add confidence field to all relationship types
  api/routes/risk.py — extend with confidence breakdown
  api/main.py — bump to v0.48.0

### Phase 49 — Open Investigation Platform and User Workflows (v0.49.0)
Branch: feature/phase-49-workflows | Priority: MEDIUM
Files to create:
  frontend/js/app.js — add:
    Investigation workspace (save current state to storage API)
    Resume investigation from saved state
    Export investigation as shareable link
    Bookmark entities for later
  api/routes/investigation.py — extend with:
    POST /investigation/save — save investigation state
    GET /investigation/{id} — resume
    GET /investigation/{id}/share — public shareable summary
  api/main.py — bump to v0.49.0

### Phase 50 — Full Production Hardening and Public Launch (v0.50.0)
Branch: feature/phase-50-production | Priority: PLANNED
Tasks:
  Infrastructure:
    CI/CD pipeline with automated testing
    End-to-end test suite covering all 21 API routes
    Load testing with 100 concurrent users
    Graph query optimization: add composite indexes
    Auto-restart scraper pipeline on schedule
  Frontend:
    Mobile responsive layout for all views
    Accessibility: keyboard navigation, screen reader support
    Progressive Web App (PWA) with offline capability
    Error boundary components for graceful degradation
  Documentation:
    Full API documentation with examples
    Data source citation guide
    Contribution guide for new scrapers
    Investigation methodology guide
  Legal:
    Comprehensive disclaimer on all entity pages
    Correction request workflow (14-day processing)
    DPDP Act 2023 compliance review
    Defamation safeguard review
  api/main.py — bump to v0.50.0 — Production Release

---

## CONTINUOUS IMPROVEMENT BACKLOG

### CI-1 — Indian Name Normalisation
  processing/name_normaliser.py
  Handle: honorifics (Sh., Smt., Dr.), transliterations across scripts,
  ministry abbreviations, company name variants (Ltd/Pvt/LLP)

### CI-2 — Government Ontology
  config/india_ontology.py
  Ministry hierarchy, department → ministry mapping,
  PSU → ministry mapping, court → jurisdiction mapping

### CI-3 — Pipeline Scheduler
  Implement daily, weekly, monthly refresh schedules per source
  Stale-detection alerts when source goes silent > 30 days

### CI-4 — Graph Versioning
  Snapshot graph state on every pipeline run
  Allow time-travel queries: "what did the graph look like on date X"

### CI-5 — Reproducibility Guarantee
  Deterministic investigation IDs
  Same entity + same date + same sources = same result hash

### CI-6 — Edge Intelligence
  Every graph edge should carry: source, date, confidence, method, raw_url
  Edges without provenance flagged as UNVERIFIED

### CI-7 — Mobile App
  React Native or PWA wrapper for iOS and Android
  Push notifications for watchlist alerts

### CI-8 — API Public Documentation
  OpenAPI spec with examples for every endpoint
  Postman collection export
  SDK in Python and JavaScript

---

## PHASE SUMMARY TABLE

| Phase | Name | Status | Version |
|-------|------|--------|---------|
| 1-12 | Core Infrastructure | ✅ Complete | v0.12.0 |
| 13-18 | Production + ML | ✅ Complete | v0.18.0 |
| 19-28 | Investigation Modules | ✅ Complete | v0.28.0 |
| 29 | UX Overhaul + Evidence Panel | ✅ Complete | v0.29.0 |
| 30 | Source-Drift + Historical | 🔜 Next | v0.30.0 |
| 31 | Predictive Risk + Lead Rank | 🔜 Planned | v0.31.0 |
| 32 | Entity Resolution v2 | 🔜 Planned | v0.32.0 |
| 33 | Contradiction Engine | 🔜 Planned | v0.33.0 |
| 34 | Multi-Agent Orchestration | 🔜 Planned | v0.34.0 |
| 35 | Graph Intelligence | 🔜 Planned | v0.35.0 |
| 36 | Provenance + Audit Layer | 🔜 Planned | v0.36.0 |
| 37 | Watchlist + Alerts | 🔜 Planned | v0.37.0 |
| 38 | Data Pipeline 367+ Sources | 🔜 Planned | v0.38.0 |
| 39 | Geospatial Verification | 🔜 Planned | v0.39.0 |
| 40 | Identity Fusion + OSINT | 🔜 Planned | v0.40.0 |
| 41 | Observability + Reliability | 🔜 Planned | v0.41.0 |
| 42 | Report Export + Legal-Safe | 🔜 Planned | v0.42.0 |
| 43 | Caching + Async Jobs | 🔜 Planned | v0.43.0 |
| 44 | Full 22-Language Output | 🔜 Planned | v0.44.0 |
| 45 | Security Hardening + PII | 🔜 Planned | v0.45.0 |
| 46 | Evidence Graph Frontend | 🔜 Planned | v0.46.0 |
| 47 | 367+ Source Integration | 🔜 Planned | v0.47.0 |
| 48 | Confidence Framework | 🔜 Planned | v0.48.0 |
| 49 | User Workflows + Workspace | 🔜 Planned | v0.49.0 |
| 50 | Production Launch | 🔜 Future | v0.50.0 |
