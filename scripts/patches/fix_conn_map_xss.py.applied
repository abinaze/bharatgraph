# fix_conn_map_xss.py
with open('frontend/js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the exact pattern using a simpler anchor
old = "onclick=\"EvidencePanel.open('${sanitize(e.connected_id||'')}','${sanitize(e.connected_to||'')}')\">"
new = "data-eid=\"${sanitize(e.connected_id||'')}\"\n             data-ename=\"${sanitize(e.connected_to||'')}\"\n             onclick=\"EvidencePanel.open(this.getAttribute('data-eid'),this.getAttribute('data-ename'))\">"

if old in content:
    content = content.replace(old, new)
    print('OK: connection map evidence onclick fixed with data-* attrs')
else:
    print('WARNING: trying alternate search...')
    # Try finding just a portion
    if "EvidencePanel.open('${sanitize(e.connected_id" in content:
        print('Found partial -- the exact quoting is different in your file')
        print('Showing context around EvidencePanel.open in connection map:')
        idx = content.find("EvidencePanel.open('${sanitize(e.connected_id")
        print(repr(content[idx-50:idx+150]))
    else:
        print('Pattern not found at all')

# Fix data-eid on Find Shortest Path button (unsanitized entityId)
old2 = 'data-eid="${entityId}"'
new2 = 'data-eid="${sanitize(entityId)}"'
if old2 in content:
    content = content.replace(old2, new2)
    print('OK: path-finder data-eid sanitized')
else:
    print('INFO: path-finder data-eid pattern not found (may already be sanitized)')

with open('frontend/js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
