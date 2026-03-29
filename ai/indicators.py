import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger


WEIGHTS = {
    "politician_company_overlap": 0.35,
    "contract_concentration":     0.25,
    "audit_mention_frequency":    0.20,
    "asset_growth_anomaly":       0.15,
    "criminal_case_presence":     0.05,
}

MAX_SCORE = 100


def indicator_politician_company_overlap(entity_id: str, session) -> dict:
    row = session.run(
        """
        MATCH (p {id: $id})-[:DIRECTOR_OF]->(c:Company)-[:WON_CONTRACT]->(ct:Contract)
        RETURN count(ct) AS cnt, sum(ct.amount_crore) AS total
        """,
        id=entity_id
    ).single()

    cnt   = row["cnt"]   if row and row["cnt"]   else 0
    total = row["total"] if row and row["total"] else 0.0

    raw   = min(int(cnt * 10), 35)
    return {
        "name":        "politician_company_overlap",
        "raw_score":   raw,
        "weight":      WEIGHTS["politician_company_overlap"],
        "weighted":    round(raw * WEIGHTS["politician_company_overlap"], 2),
        "description": (
            f"Entity linked to {cnt} contract(s) totalling Rs {total:.1f} Cr "
            "through company directorships."
        ),
        "evidence": [
            f"{cnt} contract(s) found via DIRECTOR_OF -> WON_CONTRACT path",
            f"Total contract value: Rs {round(total, 2)} Cr",
            "Source: Government e-Marketplace procurement records",
        ],
        "source_institution": "Government e-Marketplace",
        "source_url":         "https://gem.gov.in",
    }


def indicator_contract_concentration(entity_id: str, session) -> dict:
    row = session.run(
        """
        MATCH (c {id: $id})-[:WON_CONTRACT]->(ct:Contract)
        RETURN count(ct) AS cnt, sum(ct.amount_crore) AS total
        """,
        id=entity_id
    ).single()

    cnt   = row["cnt"]   if row and row["cnt"]   else 0
    total = row["total"] if row and row["total"] else 0.0

    raw   = min(int(cnt * 8), 25)
    return {
        "name":        "contract_concentration",
        "raw_score":   raw,
        "weight":      WEIGHTS["contract_concentration"],
        "weighted":    round(raw * WEIGHTS["contract_concentration"], 2),
        "description": (
            f"Entity awarded {cnt} government contract(s) totalling Rs {total:.1f} Cr. "
            "Repeated awards to the same entity indicate concentration."
        ),
        "evidence": [
            f"{cnt} contract(s) via WON_CONTRACT relationships",
            f"Total value: Rs {round(total, 2)} Cr",
            "Source: Government e-Marketplace procurement records",
        ],
        "source_institution": "Government e-Marketplace",
        "source_url":         "https://gem.gov.in",
    }


def indicator_audit_mention_frequency(entity_id: str, entity_name: str,
                                       session) -> dict:
    row = session.run(
        """
        MATCH (a:AuditReport)
        WHERE toLower(a.title) CONTAINS toLower($name)
        RETURN count(a) AS cnt, sum(a.amount_crore) AS total
        """,
        name=entity_name
    ).single()

    cnt   = row["cnt"]   if row and row["cnt"]   else 0
    total = row["total"] if row and row["total"] else 0.0

    raw   = min(int(cnt * 10), 20)
    return {
        "name":        "audit_mention_frequency",
        "raw_score":   raw,
        "weight":      WEIGHTS["audit_mention_frequency"],
        "weighted":    round(raw * WEIGHTS["audit_mention_frequency"], 2),
        "description": (
            f"Entity or associated names appear in {cnt} CAG audit report(s). "
            f"Total amount flagged in those reports: Rs {total:.1f} Cr."
        ),
        "evidence": [
            f"{cnt} CAG report mention(s)",
            f"Total flagged amount: Rs {round(total, 2)} Cr",
            "Source: Comptroller and Auditor General of India, cag.gov.in",
        ],
        "source_institution": "Comptroller and Auditor General of India",
        "source_url":         "https://cag.gov.in/en/audit-report",
    }


def indicator_asset_growth_anomaly(entity_id: str, session) -> dict:
    row = session.run(
        """
        MATCH (p:Politician {id: $id})
        RETURN p.total_assets AS assets
        """,
        id=entity_id
    ).single()

    assets_str = row["assets"] if row else ""
    raw = 0
    description = "Insufficient asset declaration data for growth analysis."

    if assets_str and any(c.isdigit() for c in str(assets_str)):
        raw = 5
        description = (
            "Asset declaration data available from election affidavit. "
            "Multi-cycle comparison requires affidavit data from consecutive elections."
        )

    return {
        "name":        "asset_growth_anomaly",
        "raw_score":   raw,
        "weight":      WEIGHTS["asset_growth_anomaly"],
        "weighted":    round(raw * WEIGHTS["asset_growth_anomaly"], 2),
        "description": description,
        "evidence": [
            f"Declared assets: {assets_str or 'not available'}",
            "Source: Election Commission of India candidate affidavit",
        ],
        "source_institution": "Election Commission of India",
        "source_url":         "https://myneta.info",
    }


def indicator_criminal_case_presence(entity_id: str, session) -> dict:
    row = session.run(
        """
        MATCH (p:Politician {id: $id})
        RETURN toInteger(p.criminal_cases) AS cases
        """,
        id=entity_id
    ).single()

    cases = row["cases"] if row and row["cases"] else 0
    raw   = min(int(cases * 3), 5)

    return {
        "name":        "criminal_case_presence",
        "raw_score":   raw,
        "weight":      WEIGHTS["criminal_case_presence"],
        "weighted":    round(raw * WEIGHTS["criminal_case_presence"], 2),
        "description": (
            f"Entity has declared {cases} criminal case(s) in their "
            "Election Commission of India candidate affidavit."
        ),
        "evidence": [
            f"{cases} declared criminal case(s)",
            "Source: Election Commission of India candidate affidavit (self-declared)",
        ],
        "source_institution": "Election Commission of India",
        "source_url":         "https://eci.gov.in",
    }


ALL_INDICATORS = [
    indicator_politician_company_overlap,
    indicator_contract_concentration,
    indicator_audit_mention_frequency,
    indicator_asset_growth_anomaly,
    indicator_criminal_case_presence,
]
