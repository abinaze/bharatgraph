import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.main import app

__all__ = ["app"]
