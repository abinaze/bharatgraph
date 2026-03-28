# 🇮🇳 BharatGraph

**AI-powered Public Transparency & Relationship Mapping Platform for India**

> A civic-tech platform that aggregates public government data, maps relationships 
> between politicians, companies and contracts using graph AI, and generates 
> evidence-backed risk scores — helping journalists and citizens hold power accountable.

## ⚠️ Legal Disclaimer
This platform uses ONLY publicly available government data (MyNeta, data.gov.in, MCA, 
GeM, court records, official press releases). It provides statistical relationship 
analysis and risk scores — NOT accusations. All claims link to original source documents.

## 🏗️ Project Structure
```
bharatgraph/
├── scrapers/        # Data collection scripts
├── processing/      # Data cleaning & entity resolution
├── graph/           # Neo4j graph database logic
├── ai/              # Risk scoring & anomaly detection
├── api/             # FastAPI backend
├── frontend/        # React dashboard
├── blockchain/      # Audit logging
├── data/            # Raw and processed data
├── docs/            # Documentation
├── tests/           # Test files
└── config/          # Configuration
```

## 📊 Data Sources
- Election Commission / MyNeta — candidate affidavits
- data.gov.in — government open datasets
- MCA21 — company directors
- GeM — procurement contracts
- PIB / e-Gazette — official announcements
- CAG reports, court judgments, ADR, PRS

## 🚀 Quick Start
```bash
git clone https://github.com/abinaze/bharatgraph.git
cd bharatgraph
pip install -r requirements.txt
cp .env.example .env
# edit .env with your keys
python scrapers/datagov_scraper.py
```

## 📅 Development Phases
- Phase 1 : Data collection & graph setup
- Phase 2 : AI risk scoring
- Phase 3 : Dashboard & API
- Phase 4 : Live monitoring & deployment


## 🤝 Contributing
Open source. PRs welcome. See docs/CONTRIBUTING.md

## 📜 License
MIT License
