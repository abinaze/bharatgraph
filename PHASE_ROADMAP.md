# BharatGraph -- Complete Phase Roadmap

All branches merge into `main`. Branch naming: `feature/phase-N-name` or `fix/description`.
Each phase has a GitHub Issue (see `issues/` directory) and a PR description template.

---

## COMPLETED PHASES (1-31)

### Phase 1 -- Data Collection
**Tag:** pre-v1 | 6 scrapers, 3,199+ records, base scraper with rate limiting and retry

### Phase 2 -- Data Processing
**Tag:** pre-v2 | Indian name normalisation, Jaccard entity resolution, parallel pipeline

### Phase 3 -- Graph Database
**Tag:** pre-v3 | Neo4j schema, 7 node types, stable MD5 IDs, 8 Cypher templates

### Phase 4 -- FastAPI Backend
**Tag:** v0.12.0 | FastAPI + Pydantic + Neo4j dependency injection, source citations

### Phase 5 -- Risk Scoring Engine
5-indicator composite score, validate_language() forbidden-word enforcement

### Phase 6 -- Expanded Data Sources (13 scrapers)
ICIJ, Wikidata, OpenSanctions, Lok Sabha, SEBI, Electoral Bonds added

### Phase 7 -- NLP Document Intelligence
spaCy NER, Benford Law chi-squared, multilingual BERT NER, shadow draft detector

### Phase 8 -- Advanced Graph Analytics
NetworkX betweenness/PageRank/Louvain, circular ownership, ghost company scorer

### Phase 9 -- Eight New Indian Sources (21 total)
NJDG, ED, CVC, NCRB, LGD, IBBI, NGO Darpan, CPPP added with fallback samples

### Phase 10 -- Multi-Investigator AI Engine
**Tag:** v0.10.0 | 12 parallel investigators, SHA-256 report hash, synthesis engine

### Phase 11 -- Multilingual Platform (22 Languages)
All 22 Indian scheduled languages, auto-detection, Helsinki-NLP translation

### Phase 12 -- PDF Dossier Generator
Jinja2 + WeasyPrint, SHA-256 integrity hash, GET /export/pdf/{id}

### Phase 13 -- Production Frontend
Vanilla JS/HTML/CSS, D3.js force graph, 5 views, works offline from file://

### Phase 14 -- Zero Cold-Start Deployment
**Tag:** v0.14.0 | HuggingFace Spaces Docker, service worker cache, GitHub Pages CI/CD

### Phase 15 -- Mathematical Intelligence Engine
**Tag:** v0.15.0 | Spectral Fiedler value, Fourier FFT, 13th investigator (math)

### Phase 16 -- Evidence Connection Map and Deep Investigation
**Tag:** v0.16.0 | 6-layer recursive investigation, connection mapper, WHY explanations

### Phase 17 -- Security Hardening and Provenance Layer
**Tag:** v0.17.0 | Rate limiter, CSP/HSTS headers, input validator, SHA-256 audit log

### Phase 18 -- Self-Learning System and Case Memory
Schema learner, pattern learner, weight optimiser (+-0.01 per 3 confirmed cases)

### Phase 19 -- Affidavit Wealth Trajectory Engine
**Tag:** v0.19.0 | Kalman filter, 5-election series, 14th investigator (affidavit)

### Phase 20 -- Biography Engine
Chronological timeline, 5 temporal convergence window types, neutral narrative

### Phase 21 -- Benami Entity Detection
5-factor proxy score, thresholds HIGH>=65 MODERATE>=40, 15th investigator

### Phase 22 -- Procurement DNA, Cartel Detection, Full Pipeline
TF-IDF cosine >=0.72, award rotation, co-bidding network, 21 scrapers

### Phase 23 -- Revolving Door and TBML Detection
365-day cooling-off, pre-employment benefit, 2.5-sigma TBML, subcontract loops

### Phase 24 -- Linguistic Fingerprinting
Burrows Delta authorship, template reuse detection, ghost-writing detection

### Phase 25 -- Policy-Benefit Causal Analysis
Granger causality (lags 1-6), transfer entropy, CACA cross-ministry chain

### Phase 26 -- Adversarial Counterevidence
Forced disproof, competing hypotheses, uncertainty propagation

### Phase 27 -- Multi-Agent Debate Engine
7-agent 3-round debate, iMAD hesitation detection, minority dissent preserved

### Phase 28 -- Dark Pattern Detection
PrefixSpan sequential mining, 6 pre-defined high-risk sequences

### Phase 29 -- UX Overhaul and i18n
Evidence panel (4 tabs), D3 graph redesign, 22-language UI, timeline view

### Phase 30 -- Bug Fix Sprint
**Tag:** v0.30.0 | 26 bugs resolved including BUG-1 (search crash), BUG-2 (7 missing loaders)

### Phase 31 -- Runtime Profile and Auto-Scaling
**Tag:** v0.31.0 | Hardware detector, LOW/MEDIUM/HIGH profiles, GET /runtime endpoint
**Branch:** `feature/phase-31-runtime-profile`
**Files:** config/runtime_profile.py, config/model_selector.py, api/routes/runtime.py
**Tests:** 15 unit tests in tests/test_runtime_profile.py
**Profile assignment:** cpu*2 + ram*2 + gpu*2 + disk + docker + db_local (max 9)

---

## PLANNED PHASES

---

### Phase 32 -- Entity Resolution v2: Canonical Identity Engine
**Branch:** `feature/phase-32-entity-resolution`
**Priority:** CRITICAL -- fixes broken evidence chains across all phases

**Problem:** Jaccard token similarity misses transliteration variants, honorific
variations ("Sh. Ram Kumar" vs "Shri Ramkumar"), and cross-script name forms.
The same person stored under 3+ IDs = broken evidence chains.

**Algorithms:**
- Jaro-Winkler (weight 0.30) -- character-level typo and transliteration
- Jaccard token overlap (weight 0.20) -- word-order variations
- Sentence-transformers cosine (weight 0.35) -- multilingual name variants
- Exact PAN/CIN/GSTIN match (weight 1.0, overrides all) -- deterministic keys

**New files:**
- `processing/entity_resolver_v2.py` -- CanonicalIdentityEngine class
- `processing/canonical_id.py` -- stable SHA-256 ID generation functions
- `processing/alias_graph.py` -- AliasGraph: alias_name -> canonical_id lookup

**Indian name normalisation added:**
- Remove honorifics: Sh., Smt., Dr., Late, Sri, Shri, Er., Adv., Col.
- Normalise suffixes: Private Limited -> Pvt Ltd, LLP, Ltd
- Script-aware: Devanagari -> Latin transliteration for comparison

**Integration:** pipeline.py resolve_dataset() upgraded to use v2 engine

---

### Phase 33 -- Custom Graph Engine: Eliminate Neo4j 50K Limit
**Branch:** `feature/phase-33-custom-graph-engine`
**Priority:** HIGH -- AuraDB free tier caps at 50K nodes / 175K relationships

**Architecture:**
```
graph_engine/
+-- store.py          -- LevelDB key-value backing store
+-- hnsw.py           -- HNSW vector index (M=16, ef=200)
+-- query_planner.py  -- Cypher-to-native query translator
+-- temporal.py       -- Time-weighted edge decay by relationship type
+-- version_control.py -- Git-style diff log for graph mutations
+-- compat_layer.py   -- Translates all existing Cypher to native calls
```

**Temporal edge decay lambdas:**
- court_order: 0.00005 (slowest -- court records are permanent)
- cag_audit: 0.0002
- government_portal: 0.0005
- director_of: 0.0003
- member_of: 0.0005
- news_article: 0.001
- social_media: 0.01 (fastest decay)

**Version control:** Every graph mutation is recorded as a diff with before/after
hashes. Detects when government portals silently modify records post-publication.
Anti-forensics pattern: commit A -> commit B (change) -> commit C (reverts to A) = flag

---

### Phase 34 -- Vector Search and Hybrid Retrieval
**Branch:** `feature/phase-34-vector-search`

**Problem:** Keyword search misses semantically similar documents. Searching
"Maharashtra road contract irregularity" does not find CAG reports about
"highway construction irregularity in Pune" even though they are the same topic.

**Algorithms:**
- FAISS (cpu) or Qdrant for vector index
- BM25 for keyword ranking
- Reciprocal Rank Fusion (k=60): RRF = sum(1 / (60 + rank))
- Query classifier routes to appropriate retrieval strategy

**Query routing:**
| Query type | Keywords | Retrieval mix |
|-----------|---------|--------------|
| factual | who is, what is, when did | BM25 70% + vector 30% |
| relational | connected to, path from | Graph 80% + vector 20% |
| temporal | before, after, election, contract date | Graph 60% + BM25 40% |
| exploratory | similar to, pattern, cluster | Vector 60% + community 40% |

**Embedding model:** paraphrase-multilingual-MiniLM-L12-v2 (covers all 22 languages)

---

### Phase 35 -- Plugin System and YAML Enrichers
**Branch:** `feature/phase-35-plugins`

**Lazy-loading plugin architecture** -- new data sources added by dropping
a YAML file in `enrichers/` with no code changes.

**Plugin registry also covers algorithms** -- new detection algorithms
registered as plugins, enabling Phase 57 A/B testing.

---

### Phase 36 -- Sigma-Style YAML Rule Engine
**Branch:** `feature/phase-36-rule-engine`

**Problem:** Adding a new detection rule requires writing Python + Cypher.
Non-developer investigators cannot contribute detection logic.

**YAML -> Cypher compiler** -- a rule file specifies conditions, thresholds,
and actions. The engine compiles it to Cypher at startup.

**10 built-in rules shipped:**
1. `cartel_rotation.yaml` -- same vendor group rotates wins
2. `electoral_bond_proximity.yaml` -- bond + contract within 12 months (CRITICAL)
3. `family_directorship_web.yaml` -- politician's family = company director
4. `audit_contract_overlap.yaml` -- continued contracts after CAG audit flag
5. `shell_company_age_contract.yaml` -- company < 6 months old + large contract
6. `single_bidder_high_value.yaml` -- single bid above district average
7. `circular_ownership_3node.yaml` -- 3-node corporate ownership cycle
8. `revolving_door_365day.yaml` -- government to private within 1 year
9. `address_cluster_directors.yaml` -- 3+ companies same registered address
10. `pre_election_contract_surge.yaml` -- contract spend spike 90 days before poll

---

### Phase 37 -- Job Queue and Worker Pool
**Branch:** `feature/phase-37-job-queue`

**Redis-backed job queue** with state machine: INIT -> QUEUED -> RUNNING -> DONE

**Algorithm job priorities:**
- Priority 1 (immediate): entity_resolution, neurosymbolic_risk, rule_engine
- Priority 2 (30s): gnn_tbml, election_burst, shap_explanation, graphrag_summary
- Priority 3 (5min): corruption_dna, metapath_walk, community_detection, topic_modeling
- Priority 4 (off-peak): fingerprint_index, gcpal_pretraining, wayback_drift

---

### Phase 38 -- DeepSeek-R1 Chain-of-Thought Reasoning
**Branch:** `feature/phase-38-deepseek-r1`

**Problem:** Current synthesis logic (3+ investigators agreeing = HIGH) is a
vote count, not reasoning. No audit trail of how a conclusion was reached.

**DeepSeek-R1 integration:**
- Receives: graph findings + SHAP explanations + TruthChain evidence IDs
- Generates: step-by-step reasoning chain citing specific evidence node IDs
- Produces: 2 competing hypotheses with scores, then a final verdict
- Verdict levels: CONFIRMED (>=80), PROBABLE (>=50), WEAK (>=20), INSUFFICIENT

**Anti-hallucination enforcement:**
- Every R1 claim must cite a TruthChain node_id (format: [EVIDENCE-XXXX])
- Post-generation validation: regex check for invented node IDs
- Invalid citations are stripped before the report is returned

**Fallback:** When DeepSeek API is unavailable, the existing multi-investigator
synthesis provides the output. R1 augments -- it does not replace.

---

### Phase 38B -- GraphRAG: Graph-Guided LLM Retrieval (NEW)
**Branch:** `feature/phase-38b-graphrag`

**Problem:** R1 cannot answer global questions like "What are the main corruption
themes across all 5,000 CAG audit reports?" Standard RAG retrieves isolated chunks.

**GraphRAG approach:**
1. Run Leiden clustering over all scraped documents and graph nodes
2. For each community > 3 nodes, R1 generates a community summary
3. At query time: embed query -> retrieve top-k community summaries by cosine
4. Feed summaries + relevant subgraph as structured context to R1

**New files:**
- `ai/graphrag/community_indexer.py` -- builds community summaries offline
- `ai/graphrag/graphrag_retriever.py` -- query-time retrieval

**Integration with Phase 38:** R1 receives GraphRAG community summaries instead
of raw graph fragments -- dramatically reduces hallucination.

---

### Phase 39 -- DeepSeek-VL2 Visual Evidence Analysis
**Branch:** `feature/phase-39-deepseek-vl2`

Analyse scanned affidavit PDFs, audit report images, and newspaper clippings.
Signature mismatch detection. Document image authenticity via Shannon entropy.
OCR pipeline for non-digital government documents.

---

### Phase 40 -- DeepSeek-V3 Multilingual Dossier Generation
**Branch:** `feature/phase-40-deepseek-v3`

Generate full investigation reports in all 22 Indian languages.
CONFIRMED/PROBABLE/WEAK/INSUFFICIENT grading on every finding.
Length: 800-1200 words per report. Export to PDF with trilingual header.

---

### Phase 41 -- Legal Intelligence Pipeline
**Branch:** `feature/phase-41-legal`

**IPC Section Classifier:**
- Algorithm: TF-IDF + OneVsRestClassifier(LogisticRegression) -- multi-label
- 8 corruption-relevant IPC sections: 420, 409, 13, 7, 120B, 467, 468, 471
- Keyword fallback when model not trained

**Crime triple extractor:**
- Pattern: Subject -> Action -> Object from legal text
- Store as directed evidence edges: (Company)-[:BRIBED]->(Official)

**Semantic Role Labelling (SRL):**
- ARG0 (agent) -> entity who acted
- ARG2 (recipient) -> entity who benefited
- V (predicate) -> action type: BRIBED, APPROVED, AWARDED

**BK-tree** for out-of-vocabulary legal term repair.

---

### Phase 42 -- Forensic Content Intelligence
**Branch:** `feature/phase-42-forensic-content`

**Shannon entropy classifier:**
| Document type | Expected range |
|--------------|----------------|
| government_order | 3.8 -- 5.2 bits |
| cag_report | 4.0 -- 5.4 bits |
| tender_document | 3.5 -- 5.0 bits |
| court_order | 3.9 -- 5.3 bits |

Documents outside expected range flagged as SUSPICIOUS or LIKELY_FABRICATED.

**Perceptual hash (pHash)** for image-based document copy detection.
**PAN/CIN/Aadhaar regex extraction** from document text.
**Lexical diversity score** -- repetitive templates have diversity < 0.3.

---

### Phase 43 -- Pivot Recommendation Engine
**Branch:** `feature/phase-43-pivot`

**Problem:** After finding a suspicious entity, the next best investigation
target is unclear. The pivot engine scores all connected entities.

**6-factor scoring:**
| Factor | Weight | Description |
|--------|--------|-------------|
| pagerank | 0.20 | How central is this entity? |
| evidence_gap | 0.25 | How much do we NOT know? |
| risk_signals | 0.20 | log(risk_signals + 1) |
| connection_strength | 0.15 | Edge weight to current entity |
| temporal_recency | 0.10 | Recently active? |
| unexplored_depth | 0.10 | Unexplored 2-hop nodes |

**Route:** `GET /pivot/{entity_id}?already_investigated=id1,id2`

---

### Phase 44 -- Geospatial Verification via Satellite
**Branch:** `feature/phase-44-satellite`

Sentinel-2 L2A time series for project verification.
NDVI change detection for forest diversion claims.
NDBI (built-up index) for construction completion verification.
SAR (Sentinel-1) for flood infrastructure claims.
Compare contract completion claims vs satellite-observable progress.

---

### Phase 45 -- W3C PROV-DM Provenance and TruthChain
**Branch:** `feature/phase-45-provenance`

**TruthChain algorithm:**
- Each evidence node has: SHA-256 ID, source_type, content_hash, timestamp, status
- Merkle tree over all evidence: root_hash changes if ANY evidence changes
- Temporal decay: weight(E,t) = base_weight * exp(-lambda_type * days)
- Status propagation: MODIFIED evidence propagates DEPENDS_ON_MODIFIED to descendants
- Aggregate confidence = active_weight / total_weight

**Decay rates by source:**
- court_order: 0.0001 (permanent)
- cag_audit: 0.0002
- government_portal: 0.0005
- news_article: 0.001
- social_media: 0.01

**Export:** JSON-LD using W3C PROV-DM ontology + Schema.org
**Blockchain anchor:** Merkle root stored in audit_chain.py (Bitcoin via OpenTimestamps)

---

### Phase 46 -- Source Drift and Historical Record Analysis
**Branch:** `feature/phase-46-source-drift`

**Wayback CDX API** to detect when government records are silently modified.
**7 fault types** (ISWC 2024 taxonomy):
- node_disappearance: entity removed from portal
- edge_rewiring: director change silently backdated
- attribute_drift: contract amount modified post-publication
- cluster_split: formerly linked entities disconnected
- cluster_merge: separate networks joined
- temporal_burst: sudden new relationship creation
- isolation: previously connected entity becomes isolated

**Anti-forensics detection:** commit A -> commit B (change) -> commit C (reverts) = SUPPRESS_ATTEMPT

---

### Phase 47 -- Predictive Risk Trajectory
**Branch:** `feature/phase-47-predictive`

**ARIMA(2,1,1) risk prediction:**
- Fits on monthly risk score history (min 12 data points)
- Forecasts 6 months ahead with 80% confidence intervals
- Alert when predicted score crosses HIGH threshold

**GCPAL contrastive pre-training for label scarcity:**
- India's 1:707 confirmed-corruption ratio makes traditional supervised ML difficult
- GCPAL mines supervised signals from the unlabelled relationship graph
- Three augmented views: node feature dropout + edge dropout + KNN view
- NT-Xent contrastive loss (temperature = 0.07)
- Fine-tunes on confirmed cases from case_memory (min 5 needed)

---

### Phase 48 -- Watchlist, Alerts, and ARIMA Prediction
**Branch:** `feature/phase-48-watchlist`

WebSocket push alerts when risk score changes for watched entities.
YAML alert rules (same format as Phase 36).
Webhook support for journalist notification systems.

---

### Phase 49 -- Observability and Reliability
**Branch:** `feature/phase-49-observability`

Prometheus /metrics endpoint.
Stale-data alerts when pipeline has not run in >7 days.
Ingestion validator checks all 20 node types have recent data.
/health upgraded to return per-source freshness status.

---

### Phase 50 -- Security v2: RBAC and JWT
**Branch:** `feature/phase-50-security-v2`

Role-based access control: Lead Investigator, Contributor, Reviewer, Observer.
JWT authentication with refresh tokens.
DPDP Act compliance (India Data Protection).
Entity-level access control for sensitive investigations.

---

### Phase 51 -- Electoral Bond Causal Graph Engine
**Branch:** `feature/phase-51-electoral-bond-causal`

**Critical missing feature.** The data exists but the causal chain is not mapped.

**Full graph path:**
Corporate donor -> ElectoralBond -> Party -> Ministry -> Policy -> Contract -> Company

**Algorithm:** Granger causality (from Phase 25) + Difference-in-Differences
to establish whether policy changes statistically follow bond purchases.

**New node type:** PolicyChange (date, ministry, beneficiaries)
**New relationship:** FOLLOWED_BOND (lag_days, p_value, granger_f_stat)

**New route:** `GET /electoral-bond/causal/{company_id}`

---

### Phase 52 -- Parliament Performance Analytics
**Branch:** `feature/phase-52-parliament`

**New data sources:** Lok Sabha division votes (loksabha.nic.in/Loksabha/Divisions),
Rajya Sabha Q&A archive, Praja.org legislator data.

**MP accountability score:**
- Attendance rate (0.30 weight)
- Questions asked per session (0.25 weight)
- Vote consistency with party line vs independent votes (0.20 weight)
- Bills sponsored (0.15 weight)
- Starred questions with substantive follow-up (0.10 weight)

**New route:** `GET /parliament/performance/{politician_id}`
**New node type:** DivisionVote, ParliamentSession
**New relationship:** VOTED_IN, ASKED_STARRED_QUESTION

---

### Phase 53 -- Media Ownership Graph
**Branch:** `feature/phase-53-media-ownership`

**New data sources:** MIB media license registry, TRAI spectrum allocations.

**Graph paths:**
- Channel -> Corporate parent -> Promoter -> Political donor
- Channel -> Editorial stance correlation (NLP) -> Political entity

**Editorial bias detection:** NLP sentiment analysis comparing coverage of
political entities across channels with known ownership structures.

**New node types:** MediaChannel, SpectrumLicense, EditorialEntity
**New route:** `GET /media/ownership/{channel_id}`

---

### Phase 54 -- Constituency Development Index
**Branch:** `feature/phase-54-constituency`

**Data sources:** NDAP district SDG scores, MGNREGS employment data,
PM Kisan disbursements, PM Awas completions, Swachh Bharat ODF data.

**Algorithm:** Regression analysis -- does the constituency improve during
the politician's tenure vs comparison period?

**Pre-election spending surge detection:** CUSUM on district spending in
90 days before election vs annual baseline.

**New route:** `GET /constituency/{id}/development`
**Satellite verification:** Sentinel-2 images corroborate claimed completions.

---

### Phase 55 -- Family Dynasty and Nepotism Graph
**Branch:** `feature/phase-55-dynasty`

**Data source:** FAMILY_OF edges extracted from MyNeta affidavit declarations
("Spouse: X", "Dependent 1: Y"). Already partially available in existing data.

**Dynasty depth score:**
- Count of family members in government positions
- Count of family-controlled companies with government contracts
- Count of elections won by family members across generations
- Geographic concentration (same constituency or district)

**New relationship:** FAMILY_OF (role: spouse/child/sibling/parent)
**New route:** `GET /dynasty/{politician_id}`

---

### Phase 56 -- RTI Intelligence Engine
**Branch:** `feature/phase-56-rti`

**RTI auto-filer:** System detects evidence gaps in any investigation and
drafts the exact RTI application to fill them.

**Gap detection algorithm:**
- For each HIGH-risk finding: check if primary source data is available
- If data missing: identify the correct Public Information Officer
- Generate RTI draft citing the specific provisions (RTI Act 2005, Sections 6-8)

**RTI outcome tracker:** Index filed RTI applications from RTI Online portal.
Map outcomes to graph: PIOs who deny information for high-risk entities = flag.

**New route:** `GET /rti/draft/{entity_id}` (generates RTI text)
**New node type:** RTIApplication, PublicInformationOfficer

---

### Phase 57 -- A/B Algorithm Testing Framework (NEW)
**Branch:** `feature/phase-57-ab-testing`

**Multi-armed bandit (Thompson Sampling) for algorithm selection:**
- Each algorithm arm has Beta(alpha, beta) prior over performance
- alpha = times algorithm was "preferred" by human review
- beta = times algorithm was "not preferred"
- Select arm with highest sampled value at each request

**Use case:** When upgrading from static risk scorer -> ML ensemble ->
NeuroSymbolic, verify the new algorithm actually improves outcomes.

**New route:** `GET /admin/algorithm-performance`

---

### Phase 58 -- Real-Time Stream Processing (NEW)
**Branch:** `feature/phase-58-streaming`

**Problem:** Pipeline runs in batches. Breaking leads appear hours late.

**Redis Streams** (Kafka fallback) for real-time event ingestion.
**CUSUM online anomaly detection** on the stream (no batch needed).
**Sliding window aggregation** for real-time indicator updates.

**Events processed in real-time:**
- new_contract: immediate CUSUM check on contract value
- new_audit_report: check if any tracked entities are mentioned
- new_enforcement_action: update risk scores for named entities
- source_modification: detect when a scraped page changes

---

### Phase 59 -- CorruptionDNA Fingerprint (NEW)
**Branch:** `feature/phase-59-corruption-dna`

**Problem:** Two entities in the same corruption network may have no direct
graph edge -- different states, different directors, but identical patterns.

**512-dim fingerprint = concat(:**
- Node2Vec structural embedding (128d)
- TF-IDF document vector (128d)
- Benford's Law digit distribution (9d, padded to 16d)
- Temporal burst vector (64d)
- Linguistic fingerprint -- Burrows Delta (64d)
- Entity type one-hot (16d)
- Risk indicator vector (16d)
- CAG audit TF-IDF (64d)
- Institutional path vector (32d)

**MinHash LSH** for efficient similarity search (cosine > 0.82 = same network).
**New route:** `GET /dna/{entity_id}` and `GET /dna/similar/{entity_id}`

---

### Phase 60 -- ElectionProximityBurst Detector (NEW)
**Branch:** `feature/phase-60-election-burst`

**The only corruption detection algorithm that encodes the Indian electoral
calendar as a statistical regression variable.**

**Algorithm:**
1. Load full Indian electoral calendar (Lok Sabha + 28 state assemblies)
2. ARIMA(2,1,1) on monthly metric aggregates
3. PELT changepoint detection on ARIMA residuals
4. Match changepoints to election proximity (within 180 days)
5. CUSUM control chart with k=0.5, h=5.0
6. Granger causality: does election_proximity_days Granger-cause the metric?

**Output:** burst_score (0-100), election_burst_flags, cusum_alerts,
Granger p-value, interpretation in plain language.

**Integrated as 16th investigator** (temporal, weight 0.10)

---

### Phase 61 -- BennamiGNN: Heterogeneous Graph Neural Network (NEW)
**Branch:** `feature/phase-61-benami-gnn`

**Problem:** 5-factor heuristic misses multi-hop benami: politician's cousin
is director (not the politician), company has legitimate small contracts before
being used for a large fraudulent one.

**H-GNN architecture:**
- 8 relation types: DIRECTOR_OF, WON_CONTRACT, SHARES_ADDRESS, RELATED_TO,
  AWARDED_BY, FAMILY_MEMBER_OF, APPEARS_IN_AUDIT, SANCTIONED_BY
- Layer 0: Per-type linear projection to d=64
- Layer 1: Relation-aware message passing
- Layer 2: Entity-type attention
- Layer 3: Classification head -> benami_score in [0,1]

**Fallback:** Always falls back to existing 5-factor heuristic when:
- PyTorch not installed
- Subgraph has < 5 nodes
- Model not trained yet

**Training:** Fine-tunes on confirmed benami cases from case_memory.

---

### Phase 62 -- CartelDNA Sequential Mining (NEW)
**Branch:** `feature/phase-62-cartel-dna`

**Problem:** Current cartel detector checks single-tender award rotation.
Temporal cartels rotate wins across months and across ministries to avoid
statistical detection within any one ministry.

**CartelDNA = PrefixSpan + HITS + DBSCAN:**
1. PrefixSpan on bid event sequences (company, category, month, rank)
2. Detect alternating rank order patterns (length 2-6, min support 3)
3. HITS on co-bidding network: authority = real winners, hub = fake competitors
4. DBSCAN geographic clustering (epsilon = 50km, min_samples = 3)
5. Cartel confidence = 0.35*pattern + 0.25*alternation + 0.20*geo + 0.20*HITS

**New route:** `GET /cartel/dna/{entity_id}`

---

### Phase 63 -- SHAP and LIME Explainability Layer (NEW)
**Branch:** `feature/phase-63-explainability`

**Problem:** Every risk score has no explanation. Journalists cannot publish
"score: 67" without "why: politician_overlap drove +24 points."

**SHAP TreeExplainer** on the ML ensemble from Phase 19 upgrade:
- Feature contributions for each of the 5 indicators
- Counterfactual: "If contract_concentration were 0, score would be 43"
- Baseline score (expected value)

**LIME** locally linear approximation for non-tree models.

**New fields added to all risk responses:**
- shap_top_drivers: [{feature, shap_value, direction}]
- shap_counterfactual: plain-language minimum change to flip risk level
- shap_baseline: expected value before any features

**New route:** `GET /risk/explain/{entity_id}`

---

### Phase 64 -- Cross-Language Entity Disambiguation (NEW)
**Branch:** `feature/phase-64-cross-lingual`

**Problem:** "Modi" / "modi" / "modii" appear in 22 scripts -- potentially
stored as separate graph nodes. Cross-lingual entity linker maps all variants
to a single canonical node using Wikidata Q-numbers.

**XLM-RoBERTa** zero-shot entity linking.
**Wikidata SPARQL** for canonical Q-number lookup (existing scraper extended).
**Transliteration confidence score** per script pair.

---

### Phase 65 -- Knowledge Graph Completion (Missing Link Prediction) (NEW)
**Branch:** `feature/phase-65-kg-completion`

**TransE** link prediction: h + r = t in d-dimensional space.
Missing edge score: ||h + r - t|| (lower = more probable edge).

**Use cases:**
- (Politician, DIRECTOR_OF, ?) -- suggest companies likely controlled
- (?, RELATED_TO, KnownShellCompany) -- find hidden associates
- (Company, WON_CONTRACT, ?) -- predict future contract awards

**Output:** List of probable missing edges with confidence scores,
presented as "Suggested next investigation targets."

---

### Phase 66 -- LAS-GNN Temporal TBML Detection (NEW)
**Branch:** `feature/phase-66-las-gnn`

**Problem:** Current TBML detector uses threshold rules. Temporal money
laundering (pre-election scatter-gather, below-threshold smurfing) is
invisible to structural analysis.

**LAS-GNN:** LSTM aggregator on directed transaction graphs.
Learns sequential order of edges imposed by timestamps.
Detects motifs: scatter-gather, fan-in/fan-out, layering, pre-election burst.

**Indian-specific motifs:**
- Pre-election scatter: funds split to many accounts < 6 months before election
- Post-contract layering: payment -> N shell companies -> reconsolidated
- Smurfing below threshold: many transactions < Rs 2 lakh (PMLA threshold)
- Circular director rotation: A appoints X -> X at B -> B pays A

---

### Phase 67 -- NeuroSymbolic Risk Reasoning (NEW)
**Branch:** `feature/phase-67-neurosymbolic`

**Fuses three reasoning modes into one coherent system:**

Stage 1 -- DEDUCTIVE (Phase 36 YAML rules):
- Rules fire with certainty = 1.0 (logical certainty)
- CRITICAL rule match -> score forced >= 75

Stage 2 -- INDUCTIVE (Phase 19 ML ensemble + SHAP):
- GNN/ML soft score in [0,1]
- SHAP feature contributions

Stage 3 -- ABDUCTIVE (Phase 38 DeepSeek-R1):
- Chain-of-thought synthesis citing TruthChain evidence IDs
- 2 competing hypotheses with scores

Stage 4 -- Integration:
- final_score = 0.40*rule_certainty + 0.35*gnn_score + 0.25*r1_confidence
- Adversarial override: if adversarial engine finds contradicting evidence -> cap at PROBABLE

---

### Phase 68 -- InstitutionMetapath2Vec Embeddings (NEW)
**Branch:** `feature/phase-68-metapath`

**5 Indian-specific metapaths** for structured random walks:
1. politician_enrichment: Politician-DIRECTOR_OF-Company-WON_CONTRACT-Contract
2. circular_enrichment: Politician-MEMBER_OF-Party-CONTROLS-Ministry-...-DIRECTOR_OF-Politician
3. audit_flag_circular: Company-WON_CONTRACT-Contract-MENTIONED_IN-AuditReport-AUDITS-Ministry
4. shell_address_cluster: Director-DIRECTOR_OF-Company-SHARES_ADDRESS-Company
5. constituency_benefit: Politician-REPRESENTS-Constituency-LOCATED_IN-District-HAS_PROJECT-Contract

**128-dim entity embeddings** trained via Word2Vec skip-gram on guided walks.
**find_similar_by_metapath()** finds entities with the same institutional role
across different states -- invisible to structural graph analysis.

---

### Phase 69 -- Geospatial Risk Clustering (NEW)
**Branch:** `feature/phase-69-geospatial`

**Moran's I** spatial autocorrelation on district-level risk scores.
I > 0 = spatial corruption hotspots cluster together.

**LISA** (Local Indicators of Spatial Association):
- High-High cluster: high-risk district surrounded by high-risk districts
- Low-High outlier: low-risk district in high-risk region (potential evasion)
- High-Low outlier: targeted corruption in otherwise clean district

**Output:** District-level choropleth with cluster classification.
**New route:** `GET /geospatial/risk-clusters`

---

### Phase 70 -- Dynamic Knowledge Graph Anomaly Detection (NEW)
**Branch:** `feature/phase-70-dynamic-kg`

Continuously monitors graph for unexpected structural changes.
7 fault types (ISWC 2024): node_disappearance, edge_rewiring,
attribute_drift, cluster_split, cluster_merge, temporal_burst, isolation.

**Contextual anomaly detection:** entity that was HIGH-risk 3 months ago
is now suddenly LOW-risk = possible evidence suppression.

---

### Phase 71 -- GCPAL Contrastive Pre-Training (NEW)
**Branch:** `feature/phase-71-gcpal`

**Label scarcity problem:** India has very few confirmed corruption cases
relative to the total number of entities (estimated 1:707 ratio).
Standard supervised ML cannot train on this imbalance.

**GCPAL solution:** NT-Xent contrastive loss on 3 augmented views:
- View 1: node feature dropout (20%)
- View 2: edge dropout (20%)
- View 3: KNN implicit interactions (k=5)

Pre-trains on unlabelled graph. Fine-tunes on case_memory confirmed cases.

---

### Phase 72 -- Automated Source Credibility Scoring (NEW)
**Branch:** `feature/phase-72-source-credibility`

Bayesian credibility model per source:
- institutional_authority: government > NGO > news > social
- historical_accuracy: confirmed vs denied past claims
- methodology_transparency: does source explain collection method?
- timeliness: freshness decay
- cross_source_corroboration: independent corroboration count

Bayesian update after each confirmed/denied case.

---

### Phase 73 -- Investigative RAG Over Case Memory (NEW)
**Branch:** `feature/phase-73-rag-cases`

**RAG over all past investigation reports** in case_memory.
Query: "Past investigations involving electoral bonds and road contracts"
-> Dense retrieval -> Top-k case summaries as context
-> DeepSeek-R1 synthesizes commonalities and suggests strategy.

---

### Phase 74 -- Continuous Model Drift Detection (NEW)
**Branch:** `feature/phase-74-drift`

**Population Stability Index (PSI):**
- PSI < 0.10: stable
- PSI 0.10-0.25: monitor closely
- PSI > 0.25: retrain required

**ADWIN (Adaptive Windowing):** streaming concept drift detection.
Auto-triggers GCPAL retraining job when drift detected.

---

### Phase 75 -- Ethics and Bias Audit System (NEW)
**Branch:** `feature/phase-75-ethics`

**Fairness metrics:**
- Demographic parity: P(HIGH_RISK | party=A) approx= P(HIGH_RISK | party=B)
- Equal opportunity: TPR equal across entity types
- Predictive parity: PPV equal across geographic regions

**Bias detection:** chi-squared test, disparate impact ratio, SHAP fairness.
**Mitigation:** Reweighing, adversarial debiasing, calibration.

**New route:** `GET /admin/bias-audit`

---

## BRANCH WORKFLOW

```bash
# Before each new phase:
git checkout main && git pull origin main
git checkout -b feature/phase-N-name

# After all commits:
git push origin feature/phase-N-name
# Open PR on GitHub -> merge -> pull main -> tag

# Tag every completed phase:
git tag -a vN.0.0 -m "Phase N: description"
git push origin vN.0.0

# Deploy to HuggingFace after every merge:
git push hf main --force

# Reseed after every deploy:
curl -X POST https://abinazebinoly-bharatgraph.hf.space/admin/seed
```

---

## VERSION HISTORY

| Version | Phase | Key addition |
|---------|-------|--------------|
| v0.30.0 | 30 | Bug fix sprint -- 26 bugs resolved |
| v0.31.0 | 31 | Runtime profile auto-scaling |
| v0.32.0 | 32 | Entity resolution v2 (planned) |
| v0.33.0 | 33 | Custom graph engine (planned) |
| v0.40.0 | 40 | DeepSeek-V3 multilingual reports (planned) |
| v0.50.0 | 50 | Security v2 RBAC (planned) |
| v1.0.0 | 75 | Full production launch (planned) |

---

## Developed by Abinaze Binoy
