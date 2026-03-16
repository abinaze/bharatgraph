cat > scrapers/README.md << 'EOF'
# BharatGraph Scrapers

All scrapers collect **public data only**. No private data, no logins.

## Scrapers

| File | Source | Data Collected |
|------|--------|----------------|
| `base_scraper.py` | - | Base class, rate limiting, logging |
| `datagov_scraper.py` | data.gov.in | MGNREGA, PM-KISAN datasets |
| `pib_scraper.py` | pib.gov.in | Govt press releases, cabinet decisions |
| `myneta_scraper.py` | myneta.info | Politician assets, criminal cases, education |
| `mca_scraper.py` | MCA / data.gov.in | Company registrations, directors |

## How to run
```bash
# Always activate venv first
source venv/Scripts/activate

# Run any scraper
python -m scrapers.datagov_scraper
python -m scrapers.pib_scraper
python -m scrapers.myneta_scraper
python -m scrapers.mca_scraper
```

## Legal Note
All data collected is from official government portals and public civic
databases. No private data is collected. See project README for full
legal disclaimer.
EOF
