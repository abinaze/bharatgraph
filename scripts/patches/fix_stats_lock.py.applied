# fix_stats_lock.py -- fixes BACKEND-2: add threading lock for stats cache
import re

with open('api/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# First: check what actually exists in the file around stats cache
idx = content.find('_stats_cache')
if idx == -1:
    print('ERROR: _stats_cache not found in main.py at all')
    exit()

# Show context
print('Current stats cache area:')
print(repr(content[idx-10:idx+200]))
print()

# Add threading import + lock after _stats_cache = None line
# Find the module-level _stats_cache declaration
import_added = False
if '_stats_lock' not in content:
    # Add threading lock after _STATS_TTL line
    old_ttl = '_STATS_TTL       = 60.0'
    if old_ttl in content:
        content = content.replace(
            old_ttl,
            old_ttl + '\nimport threading as _th\n_stats_lock = _th.Lock()'
        )
        import_added = True
        print('OK: _stats_lock added after _STATS_TTL')
    else:
        # Try alternate TTL variable name
        for candidate in ['_STATS_TTL = 60.0', '_STATS_TTL=60.0']:
            if candidate in content:
                content = content.replace(
                    candidate,
                    candidate + '\nimport threading as _th\n_stats_lock = _th.Lock()'
                )
                import_added = True
                print(f'OK: lock added after {candidate}')
                break
        if not import_added:
            print('WARNING: could not find _STATS_TTL -- adding lock near _stats_cache')
            content = content.replace(
                '_stats_cache     = None',
                '_stats_cache     = None\nimport threading as _th\n_stats_lock = _th.Lock()',
                1
            )
            import_added = True

# Add double-check pattern inside get_stats
# Find the early return and add lock before the Neo4j call
old_early_return = '    if _stats_cache is not None and'
if old_early_return in content:
    # Find the full early-return block
    start = content.find(old_early_return)
    # Find end of that if block (the return statement)
    end = content.find('\n', content.find('return _stats_cache', start)) + 1
    early_block = content[start:end]
    print('Found early return block:')
    print(repr(early_block))

    # After the early return, add lock + double-check
    old_driver_line = '    driver      = get_driver()'
    if old_driver_line in content:
        content = content.replace(
            old_driver_line,
            '    # BACKEND-2 FIX: lock prevents two concurrent requests both\n'
            '    # seeing _stats_cache is None and both running the full graph scan\n'
            '    with _stats_lock:\n'
            '        import time as _tc\n'
            '        if _stats_cache is not None and (_tc.monotonic() - _stats_cached_at) < _STATS_TTL:\n'
            '            return _stats_cache\n'
            '    driver      = get_driver()',
            1
        )
        print('OK: double-check lock added before get_driver()')
    else:
        print('WARNING: "driver = get_driver()" not found in get_stats')
else:
    print('WARNING: early return not found')

with open('api/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify syntax
import ast
try:
    ast.parse(content)
    print('SYNTAX OK')
except SyntaxError as e:
    print(f'SYNTAX ERROR at line {e.lineno}: {e.msg}')
