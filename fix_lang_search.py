# fix_lang_search.py
with open('frontend/js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# LOGIC-3: preserve language in filter buttons
# Find the filter button onclick and append lang param
import re

# Pattern: onclick="Router.navigate('/search?q=${...}${...}')"
old_onclick = "onclick=\"Router.navigate('/search?q=${encodeURIComponent(query)}${t!==\"All\"?\"&type=\"+t.toLowerCase():\"\"}')\">"
new_onclick = "onclick=\"Router.navigate('/search?q=${encodeURIComponent(query)}${t!==\\'All\\'?\"&type=\"+t.toLowerCase():\"\"}'+(State.language&&State.language!=='en'?'&lang='+State.language:''))\">"

if old_onclick in content:
    content = content.replace(old_onclick, new_onclick)
    print('OK: lang param added to filter buttons')
else:
    print('WARNING: filter onclick not found, trying simpler replace...')
    # Simpler: just find the navigate call inside the filter map
    idx = content.find("Router.navigate('/search?q=${encodeURIComponent(query)}")
    if idx != -1:
        print('Found at index', idx)
        print('Context:', repr(content[idx:idx+120]))
    else:
        print('Not found at all')

# LOGIC-3: preserve language in search button
old_btn = "if (q) Router.navigate(`/search?q=${encodeURIComponent(q)}`);"
new_btn = "const _l=State.language&&State.language!=='en'?'&lang='+State.language:'';\n      if (q) Router.navigate(`/search?q=${encodeURIComponent(q)}${_l}`);"

replaced = 0
while old_btn in content:
    content = content.replace(old_btn, new_btn, 1)
    replaced += 1
print(f'OK: search button lang param added ({replaced} replacements)')

with open('frontend/js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
