# Security Policy

## Supported Versions

Security fixes are applied to the latest version on the `main` branch only.
Older commits are not patched.

## Reporting a Vulnerability

Do not report security vulnerabilities through public GitHub issues.

Send a description of the vulnerability to the repository owner through
GitHub's private vulnerability reporting feature:
Settings > Security > Advisories > Report a vulnerability.

Include in your report:

- A description of the vulnerability and its potential impact.
- The file or component affected.
- Steps to reproduce the issue.
- Any proof of concept code, if applicable.

You will receive an acknowledgement within 72 hours. If the vulnerability is
confirmed, a fix will be released as soon as possible, typically within 14 days
for critical issues.

## Scope

This security policy covers the BharatGraph codebase. It does not cover:

- Third-party services used by the platform (Neo4j, Render, Vercel).
- Data sources scraped by the platform (data.gov.in, pib.gov.in, etc.).
- The `.env` file, which is the user's responsibility to secure.

## Credential Security

This project never commits credentials to the repository. The `.env` file is
listed in `.gitignore` and must never be committed. The `.env.example` file
contains only placeholder values.

If you discover that real credentials were committed in the repository history,
report this immediately. The affected credentials must be rotated before any
further action.

## Known Security Considerations

**API keys in `.env`**: The DataGov API key and Neo4j password are stored in
the local `.env` file. This file must not be shared, committed, or included in
any archive uploaded to a public location.

**Scraped data in `data/`**: The `data/raw/`, `data/samples/`, and
`data/processed/` directories are git-ignored. They may contain personal
information from public government filings. Do not commit these directories or
share their contents outside your research context.

**Neo4j AuraDB**: The free AuraDB instance does not provide network-level
access controls beyond the username and password. Use a strong generated
password. Rotate it if you believe it has been exposed.
