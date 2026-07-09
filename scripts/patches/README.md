# Applied patch scripts (archive)

These were one-off scripts used to patch specific bugs during earlier
sprints. They have already been run against the codebase and are kept
here (renamed `.applied`) purely as a record of what was changed and
why -- do NOT re-run them, they are not idempotent and some (see
fix_lang_search.py.applied) contain the literal source of a bug that
was fixed in a later commit.

If you need to make a similar fix in the future, write a fresh patch
script, test it with `node --check` / `python3 -m py_compile` before
committing, and archive it here afterward the same way.
