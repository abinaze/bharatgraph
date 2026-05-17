import ast, os
errors = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'data', 'logs', 'venv')]
    for f in files:
        if not f.endswith('.py'):
            continue
        path = os.path.join(root, f)
        # Try UTF-8 first, then latin-1 as fallback
        for enc in ('utf-8', 'latin-1', 'cp1252'):
            try:
                src = open(path, encoding=enc).read()
                ast.parse(src)
                break
            except UnicodeDecodeError:
                continue
            except SyntaxError as e:
                errors.append(f'{path}:{e.lineno}: {e.msg}')
                break
print(f'Syntax: {len(errors)} errors' if errors else 'OK: all Python files clean')
for e in errors:
    print(' ', e)
