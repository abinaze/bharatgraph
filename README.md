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


**India's open-source investigation intelligence platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-green.svg)](https://fastapi.tiangolo.com)
[![Version](https://img.shields.io/badge/Version-v0.31.0-blue)](PHASE_ROADMAP.md)
[![HuggingFace](https://img.shields.io/badge/Live-HuggingFace%20Spaces-orange)](https://abinazebinoly-bharatgraph.hf.space)
[![Frontend](https://img.shields.io/badge/Frontend-GitHub%20Pages-brightgreen)](https://abinaze.github.io/bharatgraph)

---

## What is BharatGraph

BharatGraph aggregates 575+ official and verified government data sources into
a Neo4j knowledge graph and runs 15 parallel AI investigators to surface
corruption patterns, procurement irregularities, conflicts of interest, proxy
ownership structures, and institutional risk indicators across Indian public life.

Every output includes a traceable citation to its primary source document. The
system never makes legal findings or accusations -- it identifies structural
patterns in public data.

---

## Live

| Service | URL |
|---------|-----|
| Frontend | https://abinaze.github.io/bharatgraph |
| API | https://abinazebinoly-bharatgraph.hf.space |
| API docs | https://abinazebinoly-bharatgraph.hf.space/docs |
| Graph DB | neo4j+s://1a34e3b8.databases.neo4j.io |
| GitHub | https://github.com/abinaze/bharatgraph |

---

## Who can use this

| User | Purpose |
|------|---------|
| Investigative journalists | Search entities, generate sourced dossiers, export PDF |
| Academic researchers | Query the knowledge graph, run pattern detection |
| Civil society organisations | Monitor procurement, track affidavit wealth trajectories |
| Government agencies | Deploy internally with full audit trails and RBAC |
| Developers | Extend via the plugin system, add new data sources |
| Students | Study the codebase -- each component has documented theory |

---

## Architecture

```
Browser (frontend/index.html -- vanilla HTML/CSS/JS, no build step)
    |
    v REST + WebSocket
FastAPI (api/main.py)
    |
    +-- 19 route modules
    +-- 15 parallel AI investigators (ThreadPoolExecutor)
    +-- 6-layer DeepInvestigator
    +-- ConnectionMapper (shortest path + WHY explanations)
    +-- RuntimeProfile (auto-detects hardware, assigns LOW/MEDIUM/HIGH)
    |
    v
Neo4j AuraDB / Custom Graph Engine (planned)
    20 node types, 12 relationship types, MERGE with SHA-256 IDs
```

---

## Data Sources (575+)

### Official Government Sources (India)

| Source | What it provides | Official URL |
|--------|-----------------|--------------|
| MyNeta / ECI | Candidate affidavits, assets, criminal cases | myneta.info |
| MCA21 | Company registrations, directorships, CIN | mca.gov.in |
| GeM | Government e-Marketplace contract awards | gem.gov.in |
| CAG | Comptroller audit reports and irregularities | cag.gov.in |
| PIB | Press Information Bureau press releases | pib.gov.in |
| Lok Sabha | Parliamentary questions, division votes | loksabha.nic.in |
| SEBI | Securities enforcement orders | sebi.gov.in |
| ED | Enforcement Directorate press releases | enforcementdirectorate.gov.in |
| CVC | Central Vigilance Commission circulars | cvc.gov.in |
| Electoral Bonds | Bond transaction data (post-SC order 2024) | eci.gov.in |
| IBBI | Insolvency and Bankruptcy Board orders | ibbi.gov.in |
| NGO Darpan | NGO registration and CSR receipts | ngodarpan.gov.in |
| CPPP | Central Public Procurement Portal tenders | eprocure.gov.in |
| NCRB | Crime statistics by state and year | ncrb.gov.in |
| LGD | Local Government Directory entity codes | lgdirectory.gov.in |
| DataGov | Unified government dataset portal | data.gov.in |
| NJDG | Court pendency statistics | njdg.ecourts.gov.in |
| RTI Online | Filed RTI applications and outcomes | rtionline.gov.in |
| SFIO | Serious Fraud Investigation Office orders | sfio.nic.in |
| DGGI | GST fraud enforcement cases | cbic.gov.in |
| RBI | Bank enforcement actions and NPA data | rbi.org.in |
| IRDAI | Insurance regulatory orders | irdai.gov.in |
| DRI | Directorate of Revenue Intelligence seizures | dri.nic.in |
| BENAMI | Benami Prohibition Unit attachment orders | incometaxindia.gov.in |
| RERA (28 states) | Real estate project registrations | varies by state |
| MOSPI | Statistical data via microdata portal | microdata.gov.in |
| Lok Sabha votes | Division vote records per MP | loksabha.nic.in/Loksabha/Divisions |
| ECI Form 24A | Audited party accounts | eci.gov.in/disclosure-of-accounts |
| CPGRAMS | Citizen grievances by ministry | pgportal.gov.in |
| Social Audit | MGNREGS wage theft, ghost worker data | socialaudit.mahatma.net.in |
| NDAP | NITI Aayog district SDG and scheme data | ndap.nic.in |
| MIB registry | Media channel license holders | mib.gov.in |
| TRAI | Telecom spectrum allocations | trai.gov.in |
| NIC eBhumi | Land records digitization | dilrmp.gov.in |
| PM Kisan | Scheme disbursement data | pmkisan.gov.in |
| MGNREGS | Wage disbursements and job cards | nrega.nic.in |
| PM Awas | Housing scheme completions | pmaymis.gov.in |

### International / Cross-Border Sources (Official)

| Source | What it provides | Official URL |
|--------|-----------------|--------------|
| ICIJ Offshore Leaks | Panama Papers, Pandora Papers, HSBC files | offshoreleaks.icij.org |
| OpenSanctions | Global sanctions and PEP lists | opensanctions.org |
| World Bank India | Project disbursements and loan data | projects.worldbank.org/en/api |
| ADB India | Asian Development Bank project portfolio | adb.org/projects/india |
| FATF India | AML/CFT risk evaluation | fatf-gafi.org |
| Wikidata | Structured biographical data for politicians | wikidata.org |
| OpenTimestamps | Bitcoin-anchored document timestamps | opentimestamps.org |

### Supplementary Sources
*These sources are used for corroboration only and are marked as
NON_OFFICIAL_RECORD in the graph. All findings from these sources
require confirmation from at least one official source before being
included in a HIGH-confidence finding.*

| Source | What it provides | Note |
|--------|-----------------|------|
| TCPD / LokDhaba | Historical election data 1962-2024 | Academic research dataset |
| github.com/tcpd/ppi | Politician biographical records | Academic, crowdsourced |
| github.com/in-rolls | Indian politician bios (8000+) | Community dataset |
| github.com/datameet | Constituency-level election data | Community dataset |
| IndiaVotes.com | Constituency results 1952-2024 | Private aggregator |
| Praja.org | Legislator attendance and questions | Civil society monitoring |
| Global Witness India | Natural resource corruption reports | NGO reports |
| India Election Affidavits | Parsed affidavit data (github) | github.com/Vonter |
| dataforindia.com | Multi-source India indicators | Aggregator |
| Wayback Machine CDX | Historical snapshots of government pages | Archive.org |

---

## Capabilities

### Knowledge Graph

The graph models 20 node types and 12 relationship types with stable
SHA-256-derived canonical IDs. All writes use MERGE semantics -- no
duplicate nodes across pipeline runs.

Node types: Politician, Company, Contract, AuditReport, Ministry, Party, Scheme,
PressRelease, Tender, RegulatoryOrder, EnforcementAction, ElectoralBond,
InsolvencyOrder, NGO, ParliamentQuestion, VigilanceCircular, ICIJEntity,
SanctionedEntity, CourtCase, LocalBody

Relationship types: MEMBER_OF, DIRECTOR_OF, CONTESTED_IN, WON_CONTRACT,
AWARDED_BY, FLAGS, MENTIONS, ISSUED_BY, ASSOCIATED_WITH, TARGETS,
AUDITS, SUBJECT_OF

### AI Investigation Engine

15 parallel investigators each query the graph independently. Findings
confirmed by 3+ independent investigators = HIGH confidence.
Findings confirmed by 2 investigators = MODERATE confidence.

| Investigator | Focus | Weight |
|-------------|-------|--------|
| Financial | Asset growth anomaly, Benford's Law | 0.12 |
| Political | Party-contract overlap, electoral proximity | 0.10 |
| Corporate | Director networks, shell company patterns | 0.10 |
| Judicial | Court cases, FIR patterns, PMLA exposure | 0.08 |
| Procurement | Bid rigging, cartel rotation, cover bids | 0.12 |
| Network | Graph centrality, bridge entities, Fiedler | 0.08 |
| Asset | Affidavit trajectory, Kalman filter | 0.10 |
| International | ICIJ links, sanctions, offshore jurisdictions | 0.10 |
| Media | PIB mentions, controversy timeline | 0.06 |
| Historical | 5-election career trajectory | 0.08 |
| Public Interest | RTI outcome, CPGRAMS complaint rate | 0.08 |
| Doubt | Forced counterevidence, adversarial probing | 0.08 |
| Math | Fourier FFT, spectral Fiedler, Benford | 0.08 |
| Affidavit | Kalman filter wealth trajectory | 0.10 |
| Benami | 5-factor proxy ownership score | 0.09 |

**6-layer deep investigation:**
1. Direct evidence (depth 1 graph traversal)
2. Relationship expansion (depth 2)
3. Structural patterns (circular ownership, ghost company)
4. Temporal investigation (timeline construction, burst detection)
5. Network influence (betweenness, authority/hub, community)
6. Cross-source validation (multi-dataset corroboration)

### Forensic Modules

**Benami proxy detection:** Director age anomaly + surname clustering +
address clustering + pre-contract formation + single-director structure.
Score >= 65 = HIGH.

**Affidavit wealth trajectory:** Kalman filter on 5-election asset series.
Expected growth = 8% FD return + 60% salary savings. Residual > 5x = VERY HIGH.

**Procurement DNA:** TF-IDF cosine >= 0.72 between bid documents from
separate vendors = cover-bid signal. Cartel detection via award rotation.

**Revolving door:** Government-to-private career moves within 365-day
cooling-off window. Pre-employment benefit scoring.

**TBML indicators:** Contract price 2.5-sigma anomaly, subcontract loop
detection, director changes within 90 days of award.

**Linguistic fingerprinting:** Burrows Delta authorship attribution,
template reuse detection, ghost-writing similarity scoring.

**Policy-benefit causal analysis:** Granger causality (lags 1-6 months),
transfer entropy, CACA cross-ministry benefit chain.

**Dark pattern detection:** PrefixSpan on administrative event sequences.
6 pre-defined high-risk sequence patterns.

### Runtime Auto-Scaling

At startup, BharatGraph detects CPU cores, RAM, GPU availability, free
disk space, Docker environment, and Neo4j URI location. It assigns one
of three profiles:

| Profile | CPU | RAM | Workers | Batch | Depth |
|---------|-----|-----|---------|-------|-------|
| LOW | 1-2 | <8GB | 2 | 25 | 2 |
| MEDIUM | 4 | 8GB | 4 | 100 | 3 |
| HIGH | 8+ | 16GB | 8 | 500 | 5 |

Force a profile: `BHARATGRAPH_PROFILE=low|medium|high`
Check active profile: `GET /runtime`

### Security

- Sliding window rate limiter: 100/min search, 30/min investigation
- IP addresses stored as SHA-256 hashes only -- never plain text
- HTTP security headers: CSP, HSTS, X-Frame-Options
- Input validator blocks Cypher injection patterns
- Append-only SHA-256 hash-chained audit log at `logs/audit.jsonl`
- CORS origins via `CORS_ORIGINS` environment variable
- All outputs pass `validate_language()` -- no accusatory vocabulary

### Multilingual

22 Indian scheduled languages supported across all API endpoints.
Language auto-detection via Unicode block analysis. Helsinki-NLP
translation models. Cross-script entity matching for all 22 languages.

---

## Quick Start

### Prerequisites

```bash
Python 3.10+
Neo4j AuraDB account (free tier: 50K nodes / 175K relationships)
```

### Local setup

```bash
git clone https://github.com/abinaze/bharatgraph.git
cd bharatgraph

pip install -r requirements.txt

# Copy environment template and fill in secrets
cp .env.example .env
# Edit .env: set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

# Start the API
uvicorn api.main:app --reload --port 8000

# Open the frontend
open frontend/index.html
# (or visit http://localhost:8000/docs for the API)
```

### Seed sample data

```bash
curl -X POST http://localhost:8000/admin/seed
```

### Run the full pipeline

```bash
curl -X POST http://localhost:8000/admin/pipeline
# Check status:
curl http://localhost:8000/admin/pipeline/status
```

---

## API Reference

### Core routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | /search?q= | Full-text + label-scan search across all 20 node types |
| GET | /profile/{id} | Complete entity profile with all linked data |
| GET | /risk/{id} | Composite 0-100 risk score with factor breakdown |
| GET | /investigate/{id} | 6-layer deep investigation report |
| GET | /affidavit/{id} | Kalman filter wealth trajectory |
| GET | /benami/{id} | 5-factor proxy ownership score |
| GET | /debate/{id} | 7-agent structured debate |
| GET | /adversarial/{id} | Forced counterevidence report |
| GET | /connection-map?a=&b= | Shortest path with WHY explanations |
| GET | /export/pdf/{id} | Download SHA-256-signed PDF dossier |
| GET | /runtime | Hardware profile and active settings |
| GET | /health | Service health check |
| GET | /stats | Node and relationship counts |
| POST | /admin/seed | Load sample data |
| POST | /admin/pipeline | Trigger full 21-scraper pipeline |
| WS | /ws/feed | Real-time high-signal entity feed |

### Search example

```bash
curl "https://abinazebinoly-bharatgraph.hf.space/search?q=Adani&limit=5"
```

### Investigation example

```bash
curl "https://abinazebinoly-bharatgraph.hf.space/investigate/pol_001"
```

---

## Project Structure

```
bharatgraph/
+-- api/
|   +-- main.py               # FastAPI app, middleware, WS feed
|   +-- routes/               # 19 route modules
|   +-- middleware/            # Rate limiter, security headers, audit logger
|   +-- models.py             # Pydantic response models
|   +-- dependencies.py       # Neo4j driver injection
+-- ai/
|   +-- multi_investigator.py # 15 parallel investigators + synthesis
|   +-- deep_investigator.py  # 6-layer recursive investigation
|   +-- risk_scorer.py        # Composite 0-100 risk score
|   +-- investigators/        # 15 specialist investigator modules
|   +-- forensics/            # Benami, TBML, cartel, linguistic, policy
|   +-- self_learning/        # Pattern learner, weight optimiser, case memory
|   +-- graph_analytics.py    # PageRank, Louvain, centrality
|   +-- explainer.py          # validate_language() enforcement
+-- config/
|   +-- settings.py           # Environment config
|   +-- runtime_profile.py    # Hardware detector + profile assignment
|   +-- model_selector.py     # Profile-aware model selection
+-- graph/
|   +-- loader.py             # Neo4j loader for all 20 node types
|   +-- schema.py             # Constraints and indexes
|   +-- seed.py               # Sample data for /admin/seed
+-- processing/
|   +-- pipeline.py           # Parallel orchestrator (20 scrapers)
|   +-- cleaner.py            # Indian name normalisation
|   +-- entity_resolver.py    # Jaccard deduplication
+-- scrapers/                 # 21 scrapers for all data sources
+-- frontend/
|   +-- index.html            # Single-page app entry point
|   +-- js/                   # app.js, api.js, components.js, timeline.js
|   +-- css/                  # main.css, themes
|   +-- sw.js                 # Service worker (cache-first)
+-- blockchain/
|   +-- audit_chain.py        # Append-only SHA-256 hash chain
+-- tests/                    # pytest test suite
+-- issues/                   # GitHub issue templates per phase
+-- .github/workflows/        # CI, daily scrape, weekly learning
```

---

## Deployment

### HuggingFace Spaces (production)

```bash
# Set these secrets in HuggingFace Space settings:
NEO4J_URI=neo4j+s://...
NEO4J_USER=neo4j
NEO4J_PASSWORD=...
CORS_ORIGINS=https://abinaze.github.io

# Deploy
git remote add hf https://huggingface.co/spaces/abinazebinoly/bharatgraph
git push hf main --force
```

### Docker

```bash
docker build -t bharatgraph .
docker run -p 8000:8000 \
  -e NEO4J_URI=... \
  -e NEO4J_PASSWORD=... \
  bharatgraph
```

---

## Legal and Ethics

BharatGraph analyses structural patterns in official public data. It does
not make legal findings, accusations, or moral judgements about any
individual or organisation.

All outputs use neutral analytical language enforced programmatically by
`validate_language()`. Forbidden words include: corrupt, guilty, criminal,
fraud, accused (as a judgement), fraudster, and similar accusatory terms.

Every finding is labelled as a "structural indicator" and includes:
- The specific data sources consulted
- The confidence level (HIGH/MODERATE/LOW/INSUFFICIENT)
- A disclaimer that this is an analytical report and not a legal finding

Users are responsible for verifying all findings through independent
research before publishing. The platform is designed to assist
investigation, not replace journalistic verification.

Data sourced from official government portals is used under the National
Data Sharing and Accessibility Policy (NDSAP) and Open Government Data
(OGD) platform terms. International data (ICIJ, OpenSanctions) is used
under their respective open-data licenses.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution guide.

Branch naming: `feature/phase-N-description` or `fix/issue-description`

Every phase has:
1. A GitHub issue created first (template in `issues/`)
2. A feature branch
3. Commits with descriptive messages referencing the issue number
4. A PR with the standard description template
5. A version tag after merge

All Python files must be pure ASCII (no Unicode in comments or strings).
Run `python3 -m py_compile <file>` before every commit.

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

**Developed by Abinaze Binoy**
