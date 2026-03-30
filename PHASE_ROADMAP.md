# BharatGraph — Complete Phase Roadmap
# GitHub Issue and Pull Request reference for phases 7 through 21
# One issue per phase. One branch per phase. All merge directly into main.
# Branch naming: feature/phase-N-name or fix/issue-N-name


# ================================================================
# PHASE 7 — NLP Document Intelligence
# ================================================================

ISSUE_TITLE: "feat(ai): NLP pipeline — entity extraction, Benford analysis, Hindi NER"
ISSUE_LABELS: ["enhancement"]
ISSUE_DESCRIPTION: |
  Add NLP to extract structured intelligence from government documents.
  All models are free and run locally — no paid APIs.

  Files to create:
    ai/nlp_extractor.py          spaCy English NER on CAG and PIB text
    ai/benfords_analyzer.py      Statistical anomaly on declared asset figures
    ai/multilingual_ner.py       Hindi NER via AI4Bharat IndicNER (HuggingFace)
    ai/shadow_draft_detector.py  Semantic similarity: bill text vs corporate submissions

  benfords_analyzer.py: Chi-squared test on first-digit distribution of declared
  assets in election affidavits. If figures cluster around thresholds such as
  Rs 99 lakh rather than Rs 1 crore, it flags possible manipulation to stay
  below disclosure triggers.

  shadow_draft_detector.py: sentence-transformers cosine similarity comparing
  corporate lobby submissions against bill text. Score above 65 flagged as
  high semantic alignment indicating potential policy capture.

  New requirements: spacy>=3.7.0, sentence-transformers>=2.6.0

BRANCH: "feature/phase-7-nlp"
PR_TITLE: "feat(ai): NLP pipeline — entity extraction, Benford, Hindi NER, shadow drafting"
PR_DESCRIPTION: |
  Four NLP modules using only free locally-executable models.
  Benford's Law catches manipulation of asset figures.
  Hindi NER extends coverage to PIB Hindi releases.
  Closes #ISSUE_NUMBER


# ================================================================
# PHASE 8 — Advanced Graph Analytics
# ================================================================

ISSUE_TITLE: "feat(ai): graph analytics — centrality, community detection, circular ownership"
ISSUE_LABELS: ["enhancement"]
ISSUE_DESCRIPTION: |
  Structural analysis of the knowledge graph using NetworkX (free).

  Files to create:
    ai/graph_analytics.py      Betweenness centrality, PageRank, Louvain community detection
    ai/circular_ownership.py   Cycle detection in shareholding graph
    ai/shadow_director.py      De facto controllers not on formal board
    ai/ghost_company.py        Shell companies activated before tenders

  ghost_company.py flags: registered within 90 days before first contract,
  no prior CAG or SEBI mentions, single director, contract value more than
  10x paid-up capital. Results written back to Neo4j as node properties.

  New requirement: networkx>=3.2.0

BRANCH: "feature/phase-8-graph-analytics"
PR_TITLE: "feat(ai): centrality, community detection, circular ownership, ghost company detector"
PR_DESCRIPTION: |
  NetworkX-powered structural analysis. Results written to Neo4j.
  Ghost company detector catches shell entities activated for specific tenders.
  Closes #ISSUE_NUMBER


# ================================================================
# PHASE 9 — Eight New Indian Data Sources
# ================================================================

ISSUE_TITLE: "feat(scrapers): NJDG, ED, CVC, NCRB, LGD, IBBI, NGO Darpan, CPPP"
ISSUE_LABELS: ["enhancement"]
ISSUE_DESCRIPTION: |
  Eight new Indian government sources. Total scrapers becomes 21.

  Files to create:
    scrapers/njdg_scraper.py       National Judicial Data Grid — case pendency and history
    scrapers/ed_scraper.py         Enforcement Directorate press releases and actions
    scrapers/cvc_scraper.py        Central Vigilance Commission complaint statistics
    scrapers/ncrb_scraper.py       NCRB Crime in India district-wise annual statistics
    scrapers/lgd_scraper.py        Local Government Directory — 782 districts, 676,497 villages
    scrapers/ibbi_scraper.py       Insolvency and Bankruptcy Board corporate filings
    scrapers/ngo_darpan_scraper.py NGO Darpan registered NGO and CSR recipient list
    scrapers/cppp_scraper.py       Central Public Procurement Portal tender awards

  New graph nodes:
    CourtCase, EDAction, VigilanceCase, InsolventEntity, NGO, Tender

BRANCH: "feature/phase-9-eight-sources"
PR_TITLE: "feat(scrapers): NJDG, ED, CVC, NCRB, LGD, IBBI, NGO Darpan, CPPP"
PR_DESCRIPTION: |
  8 new scrapers: judiciary, enforcement, crime, administration,
  insolvency, NGO, and procurement. Total: 21 scrapers.
  Closes #ISSUE_NUMBER


# ================================================================
# PHASE 10 — Multi-Investigator AI Engine
# ================================================================

ISSUE_TITLE: "feat(ai): 12-investigator parallel analysis engine with synthesis and doubt section"
ISSUE_LABELS: ["enhancement"]
ISSUE_DESCRIPTION: |
  The core differentiating capability. 12 specialist investigators run in
  parallel, each analysing the entity from a different professional angle.
  Findings are synthesised. Where 3+ investigators agree, confidence is HIGH.

  Files to create:
    ai/investigators/financial_investigator.py    Money flows, contract values, asset anomalies
    ai/investigators/political_investigator.py    Party funding, voting records, affiliations
    ai/investigators/corporate_investigator.py    Directorships, company health, compliance
    ai/investigators/judicial_investigator.py     Court cases, convictions, pending litigation
    ai/investigators/procurement_investigator.py  Contract patterns, bid behaviour
    ai/investigators/network_investigator.py      Graph centrality, community membership
    ai/investigators/asset_investigator.py        Declared vs probable assets, growth
    ai/investigators/international_investigator.py Offshore entities, sanctions, ICIJ
    ai/investigators/media_investigator.py         PIB mentions, press release patterns
    ai/investigators/historical_investigator.py    Timeline reconstruction over time
    ai/investigators/public_interest_investigator.py Scheme data, development indicators
    ai/investigators/doubt_investigator.py         Unexplained anomalies, hypotheses
    ai/multi_investigator.py                       Parallel runner and synthesis

  Output per report:
    entity_biography: full public life timeline from all sources
    agreed_findings: patterns confirmed by 3 or more investigators
    individual_findings: all findings by source investigator
    doubts: suspicious patterns that cannot be confirmed, stated as hypotheses
    positive_contributions: good governance actions found (balanced view)
    unique_report_hash: SHA-256 of entity_id + data snapshot timestamp
    evidence_locker: all source documents across all findings

  Language rules: structural indicator, governance anomaly, pattern.
  Never: corrupt, guilty, criminal, fraud, suspect.

BRANCH: "feature/phase-10-multi-investigator"
PR_TITLE: "feat(ai): 12-investigator parallel engine with synthesis, doubts, and unique hash"
PR_DESCRIPTION: |
  The core intelligence layer. 12 specialised investigators run concurrently.
  Synthesis identifies agreed patterns and raises confidence.
  Doubt section surfaces unexplained anomalies as investigative hypotheses.
  Every report has a unique SHA-256 hash for integrity verification.
  Closes #ISSUE_NUMBER


# ================================================================
# PHASE 11 — Multilingual Platform (22 Indian Languages)
# ================================================================

ISSUE_TITLE: "feat(ai): multilingual support for all 22 Indian scheduled languages"
ISSUE_LABELS: ["enhancement"]
ISSUE_DESCRIPTION: |
  Every citizen regardless of language can query and read reports.

  Files to create:
    ai/translator.py             Language detection and translation via IndicTrans2
    ai/transliteration.py        Roman to Devanagari, Tamil, Telugu scripts etc.
    api/routes/multilingual.py   Language-aware endpoints with ?lang= parameter
    config/languages.py          ISO codes for all 22 scheduled languages

  Uses AI4Bharat IndicTrans2 (free HuggingFace model, runs locally).
  Supports: hi, ta, te, kn, ml, mr, bn, gu, pa, or, as, ur, sd, kok,
  mai, mni, sat, ks, ne, bho, doi, sa

  Name transliteration ensures search works across scripts:
  "Modi" = "मोदी" = "மோடி" = "మోదీ" all resolve to the same entity.

  All 14 dossier sections translated. Risk explanations in native language.

BRANCH: "feature/phase-11-multilingual"
PR_TITLE: "feat(ai): multilingual support — 22 Indian languages via IndicTrans2"
PR_DESCRIPTION: |
  Every citizen can now use the platform in their native language.
  AI4Bharat IndicTrans2 runs locally at no cost.
  Transliteration ensures consistent entity matching across scripts.
  Closes #ISSUE_NUMBER


# ================================================================
# PHASE 12 — PDF Dossier Generator
# ================================================================

ISSUE_TITLE: "feat(ai): PDF dossier generator with SHA-256 integrity hash per report"
ISSUE_LABELS: ["enhancement"]
ISSUE_DESCRIPTION: |
  Professional PDF investigation dossiers submittable to courts and journalists.

  Files to create:
    ai/dossier_generator.py    14-section PDF assembly
    ai/report_hasher.py        SHA-256 hash per report
    templates/dossier_en.html  English Jinja2 template
    templates/dossier_hi.html  Hindi template
    api/routes/export.py       GET /export/pdf/{entity_id}

  14 sections: Cover, Identity, Career Timeline, Corporate Associations,
  Government Contracts, Audit Mentions, Court Records, International
  Connections, Asset Declarations, Risk Summary, Analytical Findings,
  Doubts and Unexplained Patterns, Positive Contributions, Evidence Locker.

  Hash printed on cover page. Stored in Neo4j for future verification.
  GET /verify/{hash} confirms a report has not been tampered with.

  New requirements: weasyprint>=60.0, jinja2>=3.1.0

BRANCH: "feature/phase-12-pdf-dossier"
PR_TITLE: "feat(ai): PDF dossier generator — 14 sections, SHA-256 hash, multilingual templates"
PR_DESCRIPTION: |
  Court-grade PDF dossiers with unique integrity hash.
  14-section structure covering every analytical dimension.
  Verify endpoint allows anyone to confirm report authenticity.
  Closes #ISSUE_NUMBER


# ================================================================
# PHASE 13 — React Frontend with Patriotic Design
# ================================================================

ISSUE_TITLE: "feat(frontend): patriotic React dashboard with dark/light theme and D3.js graph"
ISSUE_LABELS: ["enhancement"]
ISSUE_DESCRIPTION: |
  Complete frontend. Patriotic Indian design. Dark and light themes.
  Deployed free on Vercel.

  Technology: Next.js 14, TypeScript, Tailwind CSS, D3.js, Leaflet, Recharts.

  Design system:
    Colour palette: saffron (#FF9933), white (#FFFFFF), India green (#138808),
    Ashoka blue (#000080) as accent.
    Dark theme: deep navy background (#0A0F2E), saffron and white typography.
    Light theme: white background, deep green accents, saffron highlights.
    No gradients, no decorative clutter, every element is functional.
    WCAG AA contrast ratios throughout.

  Pages: /, /search, /entity/[id], /risk-dashboard, /graph-explorer,
  /live-feed, /watchlist, /report/[id], /about, /verify/[hash]

  Graph nodes coloured by type:
    Politician: saffron | Company: India green | Contract: Ashoka blue
    AuditReport: red | Ministry: navy | PressRelease: grey

BRANCH: "feature/phase-13-frontend"
PR_TITLE: "feat(frontend): patriotic React dashboard — Indian tricolour design system"
PR_DESCRIPTION: |
  Professional patriotic design using Indian tricolour palette.
  Dark navy and saffron dark mode. Clean white light mode.
  D3.js graph, Leaflet map, Sankey diagrams, full PDF download.
  Closes #ISSUE_NUMBER


# ================================================================
# PHASE 14 — Live Monitoring and GitHub Actions
# ================================================================

ISSUE_TITLE: "feat(pipeline): GitHub Actions automation, alert engine, live feed generation"
ISSUE_LABELS: ["enhancement"]
ISSUE_DESCRIPTION: |
  Automate all data collection using GitHub Actions free 2,000 min/month.

  Files to create:
    .github/workflows/daily_scrape.yml    02:00 IST daily
    .github/workflows/weekly_load.yml     Neo4j refresh
    .github/workflows/test.yml            CI on every push and PR
    ai/alert_engine.py                    Diff-based alerts
    ai/headline_generator.py              Neutral NLG for live feed

  alert_engine.py detects: new CAG report mentioning known entity,
  new contract for company linked to politician, new ED action,
  new court filing. Each alert generates a live feed headline.

BRANCH: "feature/phase-14-monitoring"
PR_TITLE: "feat(pipeline): GitHub Actions automation, diff alerts, live feed headlines"
PR_DESCRIPTION: |
  Automated daily scraping, weekly Neo4j refresh, CI tests on every PR.
  Alert engine generates neutral analytical headlines for the live feed.
  Closes #ISSUE_NUMBER


# ================================================================
# PHASE 15 — LLM Chatbot and Hypothesis Testing
# ================================================================

ISSUE_TITLE: "feat(ai): multilingual chatbot with multi-hop hypothesis testing"
ISSUE_LABELS: ["enhancement"]
ISSUE_DESCRIPTION: |
  Conversational interface to the knowledge graph. Free Hugging Face only.
  Supports all 22 Indian languages via Phase 11 translator.

  Files to create:
    ai/chatbot.py            Intent classification and Cypher template generation
    ai/hypothesis_tester.py  Multi-hop connection tester between two entities
    api/routes/chat.py       POST /chat endpoint

  hypothesis_tester.py: finds shortest path between any two entities in the
  graph up to 5 hops. Returns full path with every edge's source document.
  Useful for journalists testing specific investigative theories.

BRANCH: "feature/phase-15-chatbot"
PR_TITLE: "feat(ai): multilingual chatbot with Cypher generation and hypothesis testing"
PR_DESCRIPTION: |
  Conversational interface in all 22 Indian languages.
  Rule-based Cypher generation prevents hallucinated graph queries.
  Closes #ISSUE_NUMBER


# ================================================================
# PHASE 16 — Geospatial Infrastructure Verification
# ================================================================

ISSUE_TITLE: "feat(ai): Sentinel-2 satellite verification of infrastructure progress"
ISSUE_LABELS: ["enhancement"]
ISSUE_DESCRIPTION: |
  Verify physical construction progress using free Copernicus satellite data.

  Files to create:
    ai/geospatial_verifier.py    NDVI change detection on Sentinel-2
    scrapers/project_locator.py  GPS geocoding of GeM contract locations

  Flags discrepancy when final payment is disbursed but satellite imagery
  shows less than 30 percent visual change at the contract location.

  New .env variables: COPERNICUS_USER, COPERNICUS_PASSWORD
  New requirements: sentinelsat>=1.3.0, rasterio>=1.3.0, numpy>=1.24.0

BRANCH: "feature/phase-16-geospatial"
PR_TITLE: "feat(ai): Sentinel-2 satellite verification of infrastructure progress"
PR_DESCRIPTION: |
  Free Copernicus satellite data objectively verifies project progress.
  Progress discrepancy flag triggers when payment is complete but
  satellite evidence shows limited physical change.
  Closes #ISSUE_NUMBER


# ================================================================
# PHASE 17 — Revolving Door and TBML Detection
# ================================================================

ISSUE_TITLE: "feat(ai): revolving door indicator, TBML red flags, electoral cycle analysis"
ISSUE_LABELS: ["enhancement"]
ISSUE_DESCRIPTION: |
  Three advanced institutional risk pattern detectors using existing graph data.

  Files to create:
    ai/revolving_door.py            Career regulatory-to-private transition analysis
    ai/tbml_detector.py             Five FATF Trade-Based Money Laundering flags
    ai/electoral_cycle_analyzer.py  Contract timing vs election calendar

  TBML flags: commodity_mismatch, single_bid_contract, price_anomaly,
  rapid_director_change, subcontracting_loop.

BRANCH: "feature/phase-17-revolving-door"
PR_TITLE: "feat(ai): revolving door, TBML detection, electoral cycle analysis"
PR_DESCRIPTION: |
  Three advanced corruption pattern detectors using data already in graph.
  FATF-aligned TBML flags cover five distinct laundering patterns.
  Closes #ISSUE_NUMBER


# ================================================================
# PHASE 18 — Security Hardening
# ================================================================

ISSUE_TITLE: "feat(security): rate limiting, DDoS protection, input validation, audit chain"
ISSUE_LABELS: ["enhancement", "security"]
ISSUE_DESCRIPTION: |
  Industry-grade security for a long-running public transparency platform.

  Files to create:
    api/middleware/rate_limiter.py      Sliding window per IP
    api/middleware/input_validator.py   Strict sanitisation, no Cypher injection
    api/middleware/security_headers.py  CSP, HSTS, X-Frame-Options
    api/middleware/audit_logger.py      Immutable append-only request log
    blockchain/audit_chain.py          SHA-256 hash chain on audit log
    docs/security_architecture.md      Threat model and incident response

  rate_limiter.py: 100 req/min for search, 10 req/min for PDF export.
  audit_chain.py: each log entry includes hash of previous entry.
  Daily root hash stored in Neo4j. Optional public anchor available.

BRANCH: "feature/phase-18-security"
PR_TITLE: "feat(security): rate limiting, input validation, security headers, tamper-evident audit log"
PR_DESCRIPTION: |
  Production-grade security hardening. Rate limiting prevents DDoS.
  Parameterised queries prevent injection. Hash-chained audit log
  provides tamper evidence for all platform activity.
  Closes #ISSUE_NUMBER


# ================================================================
# PHASE 19 — Self-Learning System
# ================================================================

ISSUE_TITLE: "feat(ai): self-learning system — schema adaptation, pattern discovery, health monitoring"
ISSUE_LABELS: ["enhancement"]
ISSUE_DESCRIPTION: |
  Platform improves itself as data grows and new fraud patterns emerge.
  All automatic changes require human review before taking effect.

  Files to create:
    ai/schema_learner.py      Detects new entity types in incoming data
    ai/pattern_learner.py     Identifies candidate structural patterns weekly
    ai/source_discoverer.py   Monitors data.gov.in for new published datasets
    ai/weight_optimizer.py    Adjusts indicator weights based on confirmed outcomes
    ai/self_audit.py          Weekly health check of all 21 scrapers

  source_discoverer.py checks weekly for new government datasets and
  creates draft scraper templates for human review and approval.

  weight_optimizer.py: when court conviction or ED chargesheet confirms
  a pattern, back-traces which indicators predicted it and adjusts weights.

BRANCH: "feature/phase-19-self-learning"
PR_TITLE: "feat(ai): self-learning system — schema adaptation, pattern discovery, weight optimisation"
PR_DESCRIPTION: |
  Platform adapts to new data sources and confirmed outcomes.
  All automatic changes gated by human review.
  Weekly self-audit ensures all scrapers remain operational.
  Closes #ISSUE_NUMBER


# ================================================================
# PHASE 20 — Free Production Deployment
# ================================================================

ISSUE_TITLE: "feat(deploy): zero-cost production deployment — Render, Vercel, Neo4j AuraDB"
ISSUE_LABELS: ["enhancement"]
ISSUE_DESCRIPTION: |
  Full production deployment at zero monthly cost.

  Files to create:
    render.yaml          Render.com web service definition
    vercel.json          Vercel deployment configuration
    Procfile             uvicorn process definition
    docs/deployment.md   Step-by-step deployment guide

  UptimeRobot free tier monitors /health every 5 minutes and keeps
  the Render free tier awake with periodic pings.

  GitHub Actions deploy hook triggers Render redeploy on every
  merge to main.

BRANCH: "feature/phase-20-deployment"
PR_TITLE: "feat(deploy): Render backend, Vercel frontend, Neo4j AuraDB, UptimeRobot monitoring"
PR_DESCRIPTION: |
  Zero-cost production deployment. All environment variables in
  Render and Vercel dashboards. UptimeRobot keeps free tier awake.
  Closes #ISSUE_NUMBER


# ================================================================
# PHASE 21 — Court and Law Enforcement Intelligence Pack
# ================================================================

ISSUE_TITLE: "feat(ai): court-grade intelligence pack for law enforcement and judicial use"
ISSUE_LABELS: ["enhancement"]
ISSUE_DESCRIPTION: |
  Professional-grade investigation outputs suitable for courts, police,
  CBI, ED, CVC, and parliamentary committees.

  Files to create:
    ai/case_builder.py             Structured case file assembly
    ai/evidence_chain.py           Formal evidence chain with legal citations
    ai/crime_classifier.py         Maps findings to IPC, PCA, PMLA sections
    ai/timeline_reconstructor.py   Forensic chronological event mapping
    api/routes/legal_export.py     GET /legal/case-file/{entity_id}

  crime_classifier.py maps structural patterns to potentially relevant
  legal sections using neutral language: "pattern may be relevant to
  section X" — never asserts guilt. Sections: IPC 420/409, PCA 13,
  PMLA 3/4, FEMA, Companies Act 2013.

  timeline_reconstructor.py builds forensic timeline combining all
  data sources: registrations, contracts, asset declarations, audit
  filings, court cases, ED actions, electoral bonds.

  legal_export.py produces: PDF case file + JSON + evidence index.
  Unique case file hash. Methodology note for court admissibility.

BRANCH: "feature/phase-21-court-intelligence"
PR_TITLE: "feat(ai): court and law enforcement intelligence pack with formal evidence chain"
PR_DESCRIPTION: |
  Professional investigation outputs for courts, police, CBI, ED, CVC.
  Formal evidence chain, crime section mapping, forensic timeline.
  Never asserts guilt — provides structured analytical framework only.
  Closes #ISSUE_NUMBER
