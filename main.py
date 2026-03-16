"""
BharatGraph - Main entry point
Run scrapers from project root to avoid import issues.
Usage: python main.py
"""

import sys
import os

# This ensures all imports work from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("BharatGraph is ready.")
    print("Run scrapers like: python -m scrapers.datagov_scraper")

