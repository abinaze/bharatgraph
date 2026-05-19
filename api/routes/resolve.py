"""
BharatGraph - Phase 32: Entity Resolution API
GET /resolve?name=Sh.+Ram+Kumar&kind=person
  -> canonical_id, normalised_name, score, aliases

GET /resolve/alias?name=Ram+Kumar
  -> canonical_id from alias graph (O(1) lookup)

POST /resolve/batch
  -> resolve a list of names against each other (cross-dataset matching)

Pure ASCII.
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel
from loguru import logger

from processing.entity_resolver_v2 import EntityResolverV2, normalise_indian_name
from processing.canonical_id import canonical_id
from processing.alias_graph import AliasGraph

router = APIRouter(prefix="/resolve", tags=["resolve"])

# Module-level resolver (shared across requests)
_resolver = EntityResolverV2(threshold=0.82)


# ---- Pydantic models ---------------------------------------------------

class ResolveRecord(BaseModel):
    name: str
    kind: str = "person"  # "person" or "company"
    cin:  Optional[str] = None
    pan:  Optional[str] = None
    gstin: Optional[str] = None
    source: Optional[str] = None


class BatchResolveRequest(BaseModel):
    records: List[ResolveRecord]
    threshold: float = 0.82
    name_field: str = "name"


class ResolveResponse(BaseModel):
    input_name:      str
    normalised_name: str
    canonical_id:    str
    kind:            str
    aliases:         List[dict] = []
    score:           float = 1.0
    note:            str = ""


class AliasLookupResponse(BaseModel):
    input_name:   str
    canonical_id: str
    found:        bool


# ---- Routes ------------------------------------------------------------

@router.get("", response_model=ResolveResponse)
def resolve_name(
    name: str = Query(..., min_length=1, max_length=300,
                      description="Name to resolve (person or company)"),
    kind: str = Query("person", description="'person' or 'company'"),
):
    """
    Normalise and canonicalise a single name.
    Returns the normalised form, canonical SHA-256 ID, and any aliases
    found in the current in-memory resolver state.

    Example:
      GET /resolve?name=Sh.+Ram+Kumar&kind=person
    """
    if kind not in ("person", "company"):
        raise HTTPException(status_code=400,
                            detail="kind must be 'person' or 'company'")
    try:
        norm = normalise_indian_name(name, kind)
        cid  = canonical_id(norm)
        return ResolveResponse(
            input_name      = name,
            normalised_name = norm,
            canonical_id    = cid,
            kind            = kind,
            score           = 1.0,
            note            = "Direct normalisation -- no cross-record matching performed",
        )
    except Exception as e:
        logger.error(f"[Resolve] Error: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Resolution failed")


@router.get("/alias", response_model=AliasLookupResponse)
def alias_lookup(
    name: str = Query(..., min_length=1, max_length=300,
                      description="Name variant to look up in alias graph"),
):
    """
    O(1) lookup in the pre-built alias graph.
    Returns the canonical_id if this name variant has been seen before,
    empty string if not found.

    The alias graph is built by the pipeline after each run and loaded
    at startup. Fast for any name seen during ingestion.

    Example:
      GET /resolve/alias?name=RAHUL+KUMAR
    """
    try:
        # Import the singleton from main to share state
        from api.main import _alias_graph
        cid = _alias_graph.resolve(name)
        return AliasLookupResponse(
            input_name   = name,
            canonical_id = cid,
            found        = bool(cid),
        )
    except ImportError:
        return AliasLookupResponse(
            input_name   = name,
            canonical_id = "",
            found        = False,
        )
    except Exception as e:
        logger.error(f"[Resolve/alias] Error: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Alias lookup failed")


@router.post("/batch")
def batch_resolve(body: BatchResolveRequest):
    """
    Resolve a list of records against each other.
    Identifies duplicates and assigns canonical IDs.
    Maximum 500 records per request (HuggingFace CPU limit).

    Returns merged canonical records with alias lists.
    """
    if len(body.records) > 500:
        raise HTTPException(status_code=400,
                            detail="Maximum 500 records per batch request")
    try:
        resolver = EntityResolverV2(threshold=body.threshold)
        raw = []
        for rec in body.records:
            d = {"name": rec.name, "kind": rec.kind}
            if rec.cin:    d["cin"]    = rec.cin
            if rec.pan:    d["pan"]    = rec.pan
            if rec.gstin:  d["gstin"]  = rec.gstin
            if rec.source: d["_source"] = rec.source
            raw.append(d)

        resolved = resolver.resolve_dataset(raw, name_field="name")
        merged   = len(body.records) - len(resolved)

        return {
            "input_count":     len(body.records),
            "canonical_count": len(resolved),
            "merged_count":    merged,
            "threshold":       body.threshold,
            "records":         resolved,
        }
    except Exception as e:
        logger.error(f"[Resolve/batch] Error: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Batch resolution failed")


@router.get("/stats")
def resolve_stats():
    """
    Return alias graph statistics: how many aliases are indexed,
    how many unique canonical IDs, avg aliases per entity.
    """
    try:
        from api.main import _alias_graph
        return {"alias_graph": _alias_graph.stats()}
    except ImportError:
        return {"alias_graph": {"total_aliases": 0, "unique_canonical_ids": 0}}
