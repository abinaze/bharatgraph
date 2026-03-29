# Contributing to BharatGraph

Thank you for your interest in contributing. This document explains the
contribution workflow, code standards, and pull request process.

---

## Before You Start

- Read the README to understand the project scope and architecture.
- Check the issue tracker to see if your idea or bug is already being discussed.
- For significant changes, open an issue first to discuss the approach before
  writing code.

---

## Branch Strategy

There is one long-lived branch: `main`. All work happens on short-lived
branches that merge directly into `main`. There is no develop branch.

Branch naming:

```
feature/phase-N-short-description     New functionality for a phase
fix/issue-N-short-description          Bug fix referencing an issue number
docs/short-description                 Documentation only changes
test/short-description                 Test additions or improvements
```

Create your branch from the latest `main`:

```bash
git checkout main
git pull origin main
git checkout -b feature/phase-5-risk-scoring
```

---

## Commit Messages

Use the conventional commits format:

```
type(scope): short description in present tense

Optional longer explanation. Wrap at 72 characters.
Reference issues: Closes #12
```

Types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`, `style`.

Examples:

```
feat(api): add entity search endpoint with pagination
fix(scraper): handle 403 response from data.gov.in
docs(readme): update quick start instructions
test(processing): add unit tests for name cleaner edge cases
```

---

## Code Standards

**Python**

- Python 3.10 or higher.
- Follow PEP 8. Line length maximum 88 characters.
- No inline comments that explain what the code does. Write code that is
  self-explanatory. Comments explain why, not what.
- No print statements in library code. Use `loguru` for all logging.
- Type hints on all function signatures.
- Every class and public method has a docstring.
- No hardcoded credentials or API keys anywhere in the codebase.
- All file reads and writes specify `encoding="utf-8"`.
- Use `os.getenv()` for all environment variables via `python-dotenv`.

**File encoding**

All Python files are ASCII-safe. No Unicode symbols (currency, special
characters) embedded in source code strings. Use plain text equivalents
where needed (e.g. `Rs` instead of the rupee symbol).

**No dead code**

Do not commit commented-out code blocks or unused imports.

---

## Testing

Before opening a pull request, verify all syntax checks pass:

```bash
for f in scrapers/*.py processing/*.py graph/*.py api/*.py; do
    python -m py_compile $f && echo "OK: $f"
done
```

If tests exist in `tests/`, run them:

```bash
python -m pytest tests/
```

---

## Pull Request Process

1. Push your branch to the remote:
   ```bash
   git push origin feature/phase-5-risk-scoring
   ```

2. Open a pull request on GitHub from your branch into `main`.

3. Use this PR title format:
   ```
   feat(scope): short description
   ```

4. In the PR description, include:
   - What the change does
   - How to test it
   - Any issues it closes (`Closes #N`)

5. Do not merge your own pull request. Wait for a review.

6. Do not use the GitHub web editor to resolve merge conflicts.
   Always resolve conflicts locally:
   ```bash
   git checkout main
   git pull origin main
   git checkout your-branch
   git merge main
   # resolve conflicts in your editor
   git add .
   git commit -m "chore: resolve merge conflicts"
   git push origin your-branch
   ```

---

## What Not to Contribute

- Scrapers that access login-protected pages or private APIs.
- Any code that stores or logs personally identifiable information beyond
  what is in official public government filings.
- Features that produce output language accusing named individuals of
  criminal activity without a court judgment.
- Dependencies with GPL licences (this project uses MIT).

---

## Data Sources Policy

All data collected must come from official, publicly accessible government
sources. The full list of approved sources is in the README. If you want to
add a new data source, open an issue first and describe the source, its
legal basis for public use, and the data it provides.

---

## Questions

Open a GitHub issue with the `question` label.
