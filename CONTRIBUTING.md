# Contributing to BharatGraph

Read this before opening a pull request.

---

## Before You Start

Check the open issues before writing code. For any change that adds a new
file, modifies the graph schema, or adds a dependency, open an issue first
to discuss the approach. Small bug fixes can go straight to a pull request.

---

## Branch Strategy

One long-lived branch: `main`. All work happens on short-lived branches
that merge directly into `main`. There is no develop branch.

Naming:

```
feature/phase-N-short-name    New phase functionality
fix/issue-N-short-name        Bug fix referencing an issue number
docs/short-name               Documentation only
test/short-name               Tests only
```

Always branch from the latest `main`:

```bash
git checkout main
git pull origin main
git checkout -b feature/phase-5-risk-scoring
```

---

## Commit Messages

Format:

```
type(scope): imperative description under 72 characters

Optional body. Wrap at 72 characters. Explain why, not what.
Closes #12
```

Types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`.

---

## Python Code Standards

**Style**
Python 3.10 minimum. PEP 8. Maximum line length 88 characters.

**Comments**
No inline comments that describe what the code does. Write self-explanatory
code. Use comments only to explain non-obvious decisions or constraints.
Do not commit commented-out code blocks.

**Logging**
No `print` statements in any module except `__main__` blocks. Use `loguru`
for all diagnostic output.

**Type hints**
All function signatures have type hints. Return types are always annotated.

**Docstrings**
Every class and every public method has a one-line docstring. Multi-line
docstrings use the Google format.

**Environment variables**
All credentials and configuration via `os.getenv()` loaded by `python-dotenv`.
No hardcoded values for any API key, password, or URL that changes between
environments.

**Encoding**
All file reads and writes specify `encoding="utf-8"`. All Python files are
ASCII-safe in their source text. No Unicode currency symbols or special
characters embedded in string literals.

**Imports**
Standard library imports first, then third-party, then local. One import
per line. No wildcard imports.

---

## Adding a New Scraper

Place the file in `scrapers/`. Inherit from `BaseScraper`. The class must
implement a method named `fetch_and_save` that saves to `data/samples/`
and returns the list of records. Add the scraper to `processing/pipeline.py`
under the appropriate method name. Document the source in the README data
sources table.

---

## Adding a New Dependency

Add to `requirements.txt` with a minimum version constraint using `>=`.
Never pin to an exact version with `==` unless there is a specific
incompatibility reason documented in a comment. Verify the package is
available under a licence compatible with MIT.

---

## Pull Request Process

1. Push your branch:
   ```bash
   git push origin feature/phase-5-risk-scoring
   ```

2. Open a pull request on GitHub targeting `main`.

3. Title format: `type(scope): description`

4. Description must include:
   - What the change does
   - How to test it locally
   - Issues it closes: `Closes #N`

5. Do not merge your own pull request without a review unless you are the
   sole contributor.

6. Resolve merge conflicts locally, never in the GitHub web editor:
   ```bash
   git checkout main && git pull origin main
   git checkout your-branch && git merge main
   # resolve conflicts in your editor
   git add . && git commit -m "chore: resolve merge conflicts"
   git push origin your-branch
   ```

---

## What Not to Contribute

- Scrapers targeting login-protected pages, private APIs, or sources not
  listed in the approved data sources section of the README.
- Any code that stores personally identifiable information beyond what
  appears in official public government filings.
- Language in any output that accuses a named individual of a crime without
  a court judgment as the source.
- Dependencies under GPL, AGPL, or other copyleft licences.
- Paid API calls. Every external service used must have a usable free tier.

---

## Questions

Open a GitHub issue with the label `question`.
