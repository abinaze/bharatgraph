"""
BharatGraph - Base Scraper
All scrapers inherit from this class.
"""
import time
import os
import requests
from loguru import logger
from dotenv import load_dotenv

# Load .env file automatically for ALL scrapers that inherit this class
load_dotenv()

class BaseScraper:
    def __init__(self, name, delay=2.0):
        self.name = name
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "BharatGraph Civic Research Tool (public data only)"
        })
        os.makedirs("logs", exist_ok=True)  # BUG-29 FIX: ensure logs/ exists
        logger.add(f"logs/{name}.log", rotation="10 MB", enqueue=True, catch=True)

    def get_json(self, url, params=None):
        try:
            logger.info(f"[{self.name}] Fetching: {url}")
            resp = self.session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            time.sleep(self.delay)
            return resp.json()
        except Exception as e:
            logger.error(f"[{self.name}] Error: {e}")
            return None

    def get_html(self, url, params=None):
        try:
            logger.info(f"[{self.name}] Fetching HTML: {url}")
            resp = self.session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            time.sleep(self.delay)
            return resp.text
        except Exception as e:
            logger.error(f"[{self.name}] Error: {e}")
            return None

    def save_json(self, data, filepath):
        import json
        # M-09 FIX: dirname("output.json") returns "" -- makedirs("") crashes.
        # Guard with: only call makedirs if there is actually a directory component.
        dir_path = os.path.dirname(filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"[{self.name}] Saved: {filepath}")

if __name__ == "__main__":
    s = BaseScraper("test")
    print("BaseScraper ready.")
