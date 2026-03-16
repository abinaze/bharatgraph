# BharatGraph Scrapers

All scrapers collect **public data only**. No private data, no logins.

## Scrapers

| File | Source | Data Collected | Status |
|------|--------|----------------|--------|
| `base_scraper.py` | - | Base class, rate limiting, logging | ✅ |
| `datagov_scraper.py` | data.gov.in | MGNREGA, PM-KISAN datasets | ✅ |
| `pib_scraper.py` | pib.gov.in | Govt press releases, cabinet decisions | ✅ |
| `myneta_scraper.py` | myneta.info | Politician assets, criminal cases, education | ✅ |
| `mca_scraper.py` | MCA / data.gov.in | Company registrations, directors | ✅ |
| `cag_scraper.py` | cag.gov.in | Audit reports, financial irregularities | ✅ |
| `gem_scraper.py` | gem.gov.in | Govt contracts, procurement orders | ✅ |

## Known Issues

| Scraper | Issue | Fix |
|---------|-------|-----|
| `datagov_scraper.py` | 403 error with default key | Register at data.gov.in for free key |
| `mca_scraper.py` | 403 error | Same - needs personal API key in .env |
| `pib_scraper.py` | 0 articles | RSS URL under investigation |

## Setup
```bash
# 1. Activate venv
source venv/Scripts/activate

# 2. Copy env file and add your API key
cp .env.example .env
# Edit .env and add DATAGOV_API_KEY=your_key

# 3. Run any scraper
python -m scrapers.cag_scraper
python -m scrapers.gem_scraper
python -m scrapers.myneta_scraper
```

## Legal Note
All data from official government portals and public civic databases.
No private data collected. See project README for full legal disclaimer.
