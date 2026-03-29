# Security Policy

## Reporting a Vulnerability

Do not report security vulnerabilities through public GitHub issues,
pull requests, or discussions.

Use GitHub's private vulnerability reporting:
Repository page > Security tab > Advisories > Report a vulnerability.

Include in your report:
- Description of the vulnerability and its potential impact
- The file or component affected
- Steps to reproduce
- Proof of concept code if applicable

You will receive an acknowledgement within 72 hours. Confirmed
vulnerabilities targeting credentials, data exposure, or injection
will be patched within 14 days.

---

## Credential Security

No credentials are ever committed to this repository. The `.env` file
is listed in `.gitignore` and must never be staged or committed.

The `.env.example` file contains only placeholder strings. If you
discover that real credentials appear anywhere in the repository
history, report it immediately. The affected credentials must be
rotated before any other remediation step.

If a DataGov API key or Neo4j password is exposed:
1. Rotate the credential immediately at the issuing service.
2. Report the exposure via the private advisory process above.
3. The repository history will be cleaned using `git filter-repo`.

---

## Known Security Considerations

**`.env` file**: Contains the DataGov API key and Neo4j password.
This file must not be shared, committed, or included in any archive
uploaded to a public location. It is excluded by `.gitignore`.

**Scraped data in `data/`**: The `data/raw/`, `data/samples/`, and
`data/processed/` directories are git-ignored. They contain information
from official public government filings. Do not commit these directories
or share their contents outside a controlled research context.

**Neo4j AuraDB**: Uses TLS in transit. The free AuraDB instance requires
a username and password. Use a strong randomly generated password.
Rotate it if you believe it has been exposed.

**GitHub Actions secrets**: Repository secrets for `NEO4J_URI`,
`NEO4J_USER`, `NEO4J_PASSWORD`, and `DATAGOV_API_KEY` must be configured
in repository Settings > Secrets and Variables > Actions. Never echo
secrets in workflow logs.

---

## Supported Versions

Security fixes are applied to the current state of the `main` branch.
Older commits are not patched separately.
