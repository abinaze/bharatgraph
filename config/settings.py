import os
import warnings
from dotenv import load_dotenv

load_dotenv()

# Project Info
PROJECT_NAME = "BharatGraph"
VERSION      = "0.32.0"   # NEW-A7 FIX: bumped from 0.31.0 after 3 bug sprints
DESCRIPTION  = "AI-powered public transparency platform for India"

# Database
NEO4J_URI      = os.getenv("NEO4J_URI", "")
NEO4J_USER     = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

# BUG-16 FIX: removed OPENAI_API_KEY -- no code in the repo uses it.
# It was dead config that misled contributors into adding an unused secret.

# Scraper settings
DEFAULT_DELAY   = 2.0
MAX_RETRIES     = 3
REQUEST_TIMEOUT = 30

# Data paths
DATA_RAW_PATH       = "data/raw/"
DATA_PROCESSED_PATH = "data/processed/"
DATA_SAMPLES_PATH   = "data/samples/"
LOGS_PATH           = "logs/"

# Data Sources URLs
DATAGOV_BASE_URL = "https://api.data.gov.in/resource/"
# BUG-27 FIX: warn at import time if DATAGOV_API_KEY is missing so the silent
# HTTP 403 errors from datagov_scraper.py are visible in startup logs
DATAGOV_API_KEY  = os.getenv("DATAGOV_API_KEY", "")
if not DATAGOV_API_KEY:
    warnings.warn(
        "DATAGOV_API_KEY is not set -- datagov_scraper will fail with HTTP 403. "
        "Add it to .env or GitHub Secrets.",
        stacklevel=1,
    )

NEWSAPI_KEY      = os.getenv("NEWSAPI_KEY", "")
PIB_RSS_URL      = "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3"
MYNETA_BASE_URL  = "https://myneta.info"
MCA_BASE_URL     = "https://www.mca.gov.in"
GEM_BASE_URL     = "https://mkp.gem.gov.in"
LOKSABHA_URL     = "https://loksabha.nic.in"
RAJYASABHA_URL   = "https://rajyasabha.nic.in"
ECOURTS_URL      = "https://judgments.ecourts.gov.in"
PRS_URL          = "https://prsindia.org"
CAG_URL          = "https://cag.gov.in"
ADR_URL          = "https://adrindia.org"
