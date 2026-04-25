import os
from dotenv import load_dotenv

load_dotenv()

# Project Info
PROJECT_NAME = "BharatGraph"
VERSION = "0.30.0"
DESCRIPTION = "AI-powered public transparency platform for India"

# Database
NEO4J_URI      = os.getenv("NEO4J_URI", "")
NEO4J_USER     = os.getenv("NEO4J_USER", "neo4j")
# BUG-14 FIX: was defaulting to literal "password" — changed to empty string
# so a missing secret fails loudly instead of silently using wrong credentials.
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

# API Keys (free ones)
NEWSAPI_KEY    = os.getenv("NEWSAPI_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

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
DATAGOV_API_KEY  = os.getenv("DATAGOV_API_KEY", "")
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
