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

**India's open-source investigation intelligence platform — built on knowledge graphs, parallel AI analysis, and 21+ official government data sources.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-green.svg)](https://fastapi.tiangolo.com)
[![Version](https://img.shields.io/badge/Version-v0.30.0-blue)](PHASE_ROADMAP.md)

---

## Overview

BharatGraph is an investigative intelligence platform for India. It aggregates data from 21+ official government sources — Election Commission affidavits, MCA company filings, GeM procurement records, CAG audit reports, SEBI enforcement orders, Electoral Bond disclosures, NJDG court records, and international datasets including ICIJ Offshore Leaks and OpenSanctions — and links them into a unified knowledge graph.

The platform applies a team of 15 parallel AI investigators to surface corruption patterns, procurement irregularities, conflicts of interest, proxy ownership structures, financial anomalies, and institutional risk indicators. Every output includes a traceable citation to its primary source document. The system never makes legal findings or accusations — it identifies structural patterns in public data.

BharatGraph runs on any hardware from a 4 GB laptop to a dedicated government server. At startup it detects available CPU, RAM, and GPU, and automatically configures its performance profile accordingly.

---

## Who can use this

| User | Purpose |
|------|---------|
| Investigative journalists | Search entities, generate sourced dossiers, export PDF reports |
| Academic researchers | Query the knowledge graph, run pattern detection, analyse timelines |
| Civil society organisations | Monitor procurement, track affidavit wealth trajectories, follow electoral bond flows |
| Government agencies | Deploy internally with full audit trails, role-based access, and data residency controls |
| Developers | Extend via the plugin system, add new data sources, build integrations via the REST API |
| Students | Study the codebase — each component has documented theory and test cases |

---

## Capabilities

### Investigation engine

Fifteen parallel AI investigators run simultaneously and independently query the knowledge graph. Each specialist covers a distinct domain: financial indicators, corporate structure, judicial records, political connections, procurement patterns, benami proxy ownership, affidavit wealth trajectories, historical patterns, international exposure, network centrality, mathematical anomalies, media mentions, and public interest signals. Findings confirmed by three or more independent investigators are marked HIGH confidence.

A 7-agent multi-round debate engine generates a structured debate for any entity. One investigator acts as devil's advocate and is forced to produce counter-evidence for every high-risk finding before the report is finalised.

The 6-layer deep investigation engine follows evidence recursively: direct connections, second-degree relationships, structural patterns, temporal patterns, network influence, and cross-source validation. Each layer runs in its own isolated database session so a slow or failing layer does not affect the others.

### Knowledge graph

The graph currently models 16 node types and 12 relationship types. All nodes use stable MD5-derived canonical IDs computed from domain-specific properties — a politician's ID includes their name, state, and election cycle; a company's ID uses its CIN where available. MERGE semantics prevent duplicate nodes across pipeline runs.

Structural analytics include betweenness centrality, PageRank, Louvain community detection, circular ownership detection (using simple_cycles), ghost company scoring, shadow director mapping, spectral Fiedler value computation for bridge entity detection, and Fourier FFT analysis on contract amount time series for detecting periodic patterns.

### Forensic modules

**Benami proxy ownership:** 5-factor scoring model combining director age anomaly, surname network clustering, address clustering, pre-contract company formation, and single-director structure. Score ≥ 65 = HIGH.

**Affidavit wealth trajectory:** Kalman filter on 5-election asset series. Innovation test flags anomalies at 3 standard deviations. Expected growth model uses 8% fixed deposit returns plus 60% salary savings as baseline. Residual ratio > 5× expected = VERY HIGH indicator.

**Procurement DNA:** TF-IDF cosine similarity ≥ 0.72 between bid documents from different vendors flags near-identical bids — a cover-bid signal. Cartel detection via award rotation analysis and co-bidding network construction.

**Revolving door:** Career transitions from government to private sector within 365-day cooling-off window flagged. Pre-employment benefit scoring detects contracts awarded to a politician's future employer before their appointment.

**TBML indicators:** Contract price anomaly (2.5σ from entity mean), subcontract loop detection via cycle queries, director changes within 90 days of contract award.

**Linguistic fingerprinting:** Burrows Delta authorship attribution using function-word frequency vectors. Template reuse detection across procurement documents. Ghost-writing similarity scoring.

**Policy-benefit causal analysis:** Granger causality test (lags 1–6 months) between policy announcements and company valuations. Transfer entropy for information-theoretic causality. CACA scoring with cross-ministry benefit chain detection.

**Dark pattern detection:** PrefixSpan sequential pattern mining on administrative event sequences. Six pre-defined high-risk sequences covering single-bidder windows, director changes near awards, and award rotation.

### Data coverage

21+ active scrapers covering:

**Indian government:** Election Commission of India (MyNeta affidavits), Ministry of Corporate Affairs (MCA21), Government e-Marketplace (GeM contracts), Comptroller and Auditor General, Press Information Bureau, Lok Sabha parliamentary records, SEBI enforcement orders, Enforcement Directorate (PMLA), Central Vigilance Commission, Electoral Bond ECI disclosures, IBBI insolvency records, NGO Darpan, CPPP tenders, NCRB crime data, Local Government Directory, DataGov.in (MGNREGA, PM-KISAN, AGMARKNET), National Judicial Data Grid.

**International:** ICIJ Offshore Leaks (Panama Papers, Pandora Papers, Paradise Papers), OpenSanctions (global PEP and sanctions lists), Wikidata (entity enrichment and disambiguation).

### Multilingual platform

Full support for all 22 Indian scheduled languages including Hindi, Tamil, Telugu, Kannada, Malayalam, Marathi, Bengali, Gujarati, Punjabi, Odia, Assamese, Urdu, Sindhi, Konkani, Maithili, Manipuri, Santali, Kashmiri, Nepali, Dogri, Sanskrit, and English.

Language auto-detection via Unicode script range analysis. Cross-script entity matching — the same person's name in Devanagari, Tamil, Telugu, Kannada, and Malayalam is correctly resolved to a single canonical entity. Helsinki-NLP/opus-mt translation models for all supported language pairs.

### Output and provenance

Every claim in every output includes a traceable source citation. PDF dossiers are generated with SHA-256 integrity hashes — any tampering with the report file is detectable. An append-only SHA-256 hash-chained audit log records every query and pipeline event. All language output is filtered through a forbidden-word enforcement layer that prevents accusatory or legally unsafe vocabulary from reaching API responses.

---

## System requirements

### Minimum (personal use / laptop)
- Python 3.10 or later
- 4 GB RAM
- 10 GB free disk space
- Internet connection
- Neo4j AuraDB free account (https://neo4j.com/cloud/platform/aura-graph-database)

### Recommended (active research / development)
- Python 3.11
- 8 GB RAM
- 20 GB free disk space
- Neo4j AuraDB free or Professional tier

### Production (organisation / government)
- 16+ GB RAM
- 8+ CPU cores
- 100+ GB SSD storage
- Ubuntu 22.04 LTS
- Docker and Docker Compose
- Managed Neo4j instance or self-hosted Neo4j 5.x
- Redis (for job queue, Phase 37+)
- Optional: CUDA-capable GPU (for DeepSeek model inference, Phase 38+)

The system detects hardware at startup and sets `max_workers`, `batch_size`, `graph_depth`, `investigation_layers`, and `cache_ttl` automatically based on available resources.

---

## Quick start

### 1. Clone

```bash
git clone https://github.com/abinaze/bharatgraph.git
cd bharatgraph
```

### 2. Environment

```bash
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
# source venv/Scripts/activate  # Windows Git Bash

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Configuration

```bash
cp .env.example .env
```

Edit `.env` and fill in:
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` — from your AuraDB instance
- `DATAGOV_API_KEY` — free at https://data.gov.in/user/register

### 4. Seed and start

```bash
python -m graph.seed                    # load sample data
uvicorn api.main:app --reload           # start the API
```

Open `frontend/index.html` in your browser. Search for "Modi", "Adani", or "Amit Shah" to see the investigation graph.

### 5. Load live data

```bash
curl -X POST http://127.0.0.1:8000/admin/pipeline
```

For the complete deployment guide covering Docker, cloud, government, and air-gapped deployments, see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## Docker

```bash
cp .env.example .env    # fill in credentials
docker compose up --build
```

Open `http://localhost:8000`.

---

## Live deployment

| Component | URL |
|-----------|-----|
| Frontend | https://abinaze.github.io/bharatgraph |
| API | https://abinazebinoly-bharatgraph.hf.space |
| API documentation | https://abinazebinoly-bharatgraph.hf.space/docs |
| Health check | https://abinazebinoly-bharatgraph.hf.space/health |

---

## API reference

### Core endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/search?q={term}&type={type}` | Full-text search across all 16 node types |
| GET | `/profile/{id}` | Entity profile with declared properties and risk score |
| GET | `/graph/connections/{id}?depth={n}` | D3-compatible force graph neighbourhood |
| GET | `/risk/{id}` | Composite structural risk score (0–100) with factor breakdown |
| GET | `/stats` | Node and relationship counts |
| GET | `/health` | API health check (GET and HEAD) |

### Investigation

| Method | Path | Description |
|--------|------|-------------|
| GET | `/investigate/{id}` | 6-layer deep investigation with confidence scoring |
| GET | `/node-evidence/{id}` | All graph edges with WHY, source, and next-investigation leads |
| GET | `/connection-map?a={id}&b={id}` | Shortest path between two entities with relationship explanations |

### Forensic analysis

| Method | Path | Description |
|--------|------|-------------|
| GET | `/biography/{id}` | Chronological timeline with temporal convergence detection |
| GET | `/affidavit/{id}` | Kalman-filter wealth trajectory and anomaly detection |
| GET | `/benami/{id}` | 5-factor proxy ownership score |
| GET | `/adversarial/{id}` | Forced counterevidence and competing hypothesis analysis |
| GET | `/debate/{id}` | 7-agent structured debate with consensus and dissent |
| GET | `/linguistic/fingerprint/{id}` | Burrows Delta authorship attribution |
| GET | `/policy/causal/{id}` | Granger causality and CACA scoring |

### Procurement and corporate

| Method | Path | Description |
|--------|------|-------------|
| GET | `/procurement/bid-dna/{id}` | TF-IDF bid document fingerprinting |
| GET | `/procurement/cartel` | Award rotation and cover-bid cartel detection |
| GET | `/conflict/revolving-door/{id}` | Cooling-off violation scoring |
| GET | `/conflict/tbml/{id}` | Trade-based money laundering indicators |

### Export and administration

| Method | Path | Description |
|--------|------|-------------|
| GET | `/export/pdf/{id}` | SHA-256-hashed PDF or HTML dossier |
| GET | `/sources` | All active data sources with record counts |
| POST | `/admin/seed` | Load sample data (nodes + relationships) |
| POST | `/admin/pipeline?scrapers=all` | Trigger full 21-scraper background pipeline |
| GET | `/admin/pipeline/status` | Pipeline running state and last result per source |
| GET | `/languages` | All 22 supported languages |
| GET | `/ui-labels?lang={code}` | Translated UI labels for the specified language |
| GET | `/search/multilingual?q={term}&lang={code}` | Language-aware search with transliteration variants |
| GET | `/runtime` | Current hardware profile and active performance settings |

---

## Graph model

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
(EnforcementAction)-[:TARGETS]->(Politician)
(EnforcementAction)-[:TARGETS]->(Company)
```

---

## Project structure

```
bharatgraph/
  api/
    routes/          19 API route modules
    middleware/      Rate limiter, security headers, input validator, audit logger
    models.py        Pydantic request/response models
    dependencies.py  Neo4j driver management with auto-reconnect
  ai/
    investigators/   15 parallel investigators
    forensics/       Affidavit, benami, bid DNA, cartel, revolving door, TBML, linguistic, policy
    biography/       Timeline builder, convergence detector, narrative generator
    math/            Spectral (Fiedler λ₁), Fourier FFT, path signature analysis
    self_learning/   Schema learner, pattern learner, weight optimiser, self-audit
    case_memory/     Solved case library, false positive tracking
  scrapers/          22 data collectors (17 Indian + 4 international + 1 wikidata)
  graph/             Neo4j schema (16 node types), loader (15 loaders), seed, query templates
  processing/        Name normalisation, entity resolution (Jaccard), parallel pipeline orchestrator
  config/            22 language configurations, runtime profile detection
  blockchain/        SHA-256 hash-chained append-only audit log
  frontend/          Vanilla HTML/CSS/JS single-page application
  templates/         Jinja2 PDF dossier template
  deploy/            Docker Compose, CI/CD workflows, hardening configuration
  .github/workflows/ CI tests, daily scrape, weekly self-learning, static deploy
```

---

## Architecture

```
Browser (frontend/index.html)
        │
        │ REST + WebSocket
        ▼
FastAPI Application (api/main.py)
        │
        ├── Middleware stack
        │     Rate limiter → Security headers → Input validator → Audit logger
        │
        ├── Investigation routes
        │     DeepInvestigator (6 layers, isolated sessions)
        │     MultiInvestigator (15 parallel workers)
        │     ConnectionMapper (shortest path + WHY explanations)
        │
        ├── Forensic routes
        │     Affidavit, Benami, Procurement, Conflict, Biography, Policy, Linguistic
        │
        ├── Data routes
        │     Search (fulltext index + label-scan fallback)
        │     Profile, Risk, Graph, Export, Sources
        │
        └── Neo4j / Graph Engine
              Property graph with 16 node types, 12 relationship types
              MERGE semantics, stable canonical IDs, SHA-256 audit chain
```

---

## Confirmed live results

| Metric | Result |
|--------|--------|
| DataGov API | 3,199 real MGNREGA records returned |
| CAG | 30 audit report links from cag.gov.in |
| PIB | 27 press releases from pib.gov.in |
| Wikidata | Modi (Q1058), Gandhi (Q10218) confirmed live |
| NJDG | 39 court records confirmed live |
| SHA-256 hash | Stable, unique, 64 characters confirmed |
| Language detection | Devanagari → hi, Tamil → ta confirmed |
| Cross-script search | "Modi" → 5 scripts confirmed |
| Benami test case | 100/100 ghost company score confirmed |
| Affidavit test | VERY_HIGH, ₹42.7 Cr residual (7.1×), 3 Kalman anomalies |
| Shadow draft | 93.35% cosine alignment confirmed |

---

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete instructions covering:
- Personal laptop setup
- Docker and Docker Compose
- Developer environment with testing
- Organisation / enterprise deployment with Nginx and SSL
- Government / air-gapped deployment with security hardening
- Cloud deployment (AWS, GCP, Azure, DigitalOcean, Kubernetes)
- HuggingFace Spaces configuration

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request. All contributions must pass the CI test suite and follow the neutral-language standard enforced by `validate_language()`.

---

## Legal and ethical notice

BharatGraph processes only publicly available government records published by the Election Commission of India, Ministry of Corporate Affairs, Government e-Marketplace, Comptroller and Auditor General, Press Information Bureau, Parliament of India, and other official sources listed in this documentation. All outputs are statistical observations derived from official data. No claim made by this platform constitutes a legal finding, an accusation of wrongdoing, or a definitive statement of fact.

Any individual or organisation featured in this platform has the right to submit corrections. Contact the project via the GitHub issue tracker with documentary evidence. Verified corrections will be incorporated within 14 days.

---

## License

MIT License. See [LICENSE](LICENSE).

---

## Reference documents

- [DEPLOYMENT.md](DEPLOYMENT.md) — deployment guide for all environments
- [PHASE_ROADMAP.md](PHASE_ROADMAP.md) — full development roadmap with phase summaries
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution guidelines
- [SECURITY.md](SECURITY.md) — security policy and responsible disclosure

---

**Developed by Abinaze Binoly**
