"""
BharatGraph - Canonical ID Generation
Single source of truth for deterministic entity IDs.
Every node in the graph derives its ID from its most stable
real-world identifier (CIN, constituency+name, etc.).
Identical to make_id() in graph/loader.py for full compatibility.
Pure ASCII.
"""
import hashlib
import re


def canonical_id(*parts) -> str:
    """
    20-char SHA-256-derived ID from canonical entity properties.
    Same algorithm as make_id() in loader.py for full compatibility.

    Examples:
        canonical_id("narendra modi", "gujarat")        -> stable ID
        canonical_id("L51100GJ1993PLC019067")            -> company by CIN
        canonical_id("adani enterprises", "gujarat")    -> same every run
    """
    combined = "|".join(str(p).lower().strip() for p in parts)
    return hashlib.sha256(combined.encode()).hexdigest()[:20]


def canonical_id_for_politician(name: str, state: str,
                                  election: str = "") -> str:
    return canonical_id(name, state, election)


def canonical_id_for_company(cin: str = "", name: str = "",
                               state: str = "") -> str:
    if cin:
        return canonical_id(cin)
    return canonical_id(name, state)


def canonical_id_for_contract(order_id: str) -> str:
    return canonical_id(order_id)


def canonical_id_for_ngo(darpan_id: str = "", name: str = "") -> str:
    if darpan_id:
        return canonical_id("ngo", darpan_id)
    return canonical_id("ngo", name)
