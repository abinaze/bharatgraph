#!/usr/bin/env python3
"""CI check: verify all route modules in api/main.py exist on disk."""
import re, os, sys

def verify_routes():
    try:
        with open('api/main.py', 'r', encoding='utf-8') as f:
            main = f.read()
    except FileNotFoundError:
        print("ERROR: api/main.py not found")
        sys.exit(1)

    m = re.findall(r'from api\.routes import (.*)', main)
    if not m:
        print("PASS: no route imports found")
        return

    mods = [x.strip() for x in m[0].split(',')]
    missing = [x for x in mods if not os.path.exists(f'api/routes/{x}.py')]
    if missing:
        print('MISSING ROUTE FILES:', missing)
        sys.exit(1)
    print(f'PASS: All {len(mods)} route files present')

if __name__ == '__main__':
    verify_routes()
