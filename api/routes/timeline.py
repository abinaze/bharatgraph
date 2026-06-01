"""
BharatGraph - Phase 33: Timeline API
GET /timeline/{entity_id}            -- chronological event feed for an entity
GET /timeline/{entity_id}/by-year    -- same events bucketed by year

The EvidencePanel timeline tab calls /profile/{entity_id} and gets no events.
This route queries the graph directly for time-stamped activity across all
node types connected to the entity.

Pure ASCII.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from loguru import logger

from api.dependencies import get_db

router = APIRouter(prefix="/timeline", tags=["Timeline"])


def _label_to_category(label: str) -> str:
    """Map Neo4j node label to a timeline event category."""
    mapping = {
        "Contract":         "contract",
        "AuditReport":      "audit",
        "EnforcementAction":"enforcement",
        "ElectoralBond":    "financial",
        "CourtCase":        "legal",
        "PressRelease":     "political",
        "Affidavit":        "electoral",
        "RegulatoryOrder":  "regulatory",
        "VigilanceCircular":"vigilance",
        "Company":          "corporate",
        "Ministry":         "corporate",
        "Tender":           "contract",
        "InsolvencyOrder":  "legal",
        "NGO":              "corporate",
        "Politician":       "political",
    }
    return mapping.get(label, "other")


def _extract_date(props: dict) -> Optional[str]:
    """Find the most reliable date field from a node properties dict."""
    for field in ("order_date", "date", "filing_date", "registered_at",
                  "case_date", "issue_date", "scraped_at", "year"):
        val = props.get(field)
        if val:
            return str(val)
    return None


@router.get("/{entity_id}")
def entity_timeline(
    entity_id: str,
    limit:      int      = Query(100, ge=1, le=500),
    category:   Optional[str] = Query(None,
                    description="Filter: contract, audit, legal, financial, ..."),
    driver=Depends(get_db),
):
    """
    Return all time-stamped events connected to an entity, sorted
    newest first. This feeds the EvidencePanel timeline tab.

    Categories: contract, audit, enforcement, financial, legal,
                political, electoral, regulatory, vigilance, corporate, other.

    Example:
      GET /timeline/pol_abc123?category=contract&limit=20
    """
    logger.info(f"[Timeline] entity={entity_id[:8]} limit={limit}")
    events = []

    with driver.session() as session:
        # Fetch all connected nodes that have any date field
        rows = session.run(
            """
            MATCH (e {id: })-[r]-(n)
            WHERE n.scraped_at IS NOT NULL
               OR n.order_date  IS NOT NULL
               OR n.date        IS NOT NULL
               OR n.filing_date IS NOT NULL
               OR n.year        IS NOT NULL
            RETURN labels(n)[0]   AS node_label,
                   type(r)        AS rel_type,
                   properties(n)  AS props,
                   n.id           AS nid
            LIMIT 
            """,
            id=entity_id, limit=limit * 3  # over-fetch so filtering doesn't starve
        ).data()

        for row in rows:
            label    = row.get("node_label", "Unknown")
            cat      = _label_to_category(label)
            if category and cat != category.lower():
                continue
            props    = row.get("props") or {}
            date_str = _extract_date(props)
            events.append({
                "date":       date_str,
                "category":   cat,
                "label":      label,
                "rel_type":   row.get("rel_type", ""),
                "node_id":    row.get("nid", ""),
                "title":      props.get("title", props.get("name",
                                props.get("order_id", row.get("nid", ""))))[:120],
                "detail":     props.get("summary", props.get("description",
                                props.get("item_desc", "")))[:300],
                "amount_crore": props.get("amount_crore",
                                  props.get("total_assets_crore")),
                "source":     props.get("source", ""),
            })

    # Sort by date descending (None dates go to the end)
    events.sort(
        key=lambda x: x["date"] or "0000-00-00",
        reverse=True,
    )
    events = events[:limit]

    return {
        "entity_id":    entity_id,
        "total_events": len(events),
        "category":     category,
        "events":       events,
        "generated_at": datetime.now().isoformat(),
    }


@router.get("/{entity_id}/by-year")
def entity_timeline_by_year(
    entity_id: str,
    driver=Depends(get_db),
):
    """
    Same as /{entity_id} but events are bucketed by year.
    Useful for rendering a bar chart or year-selector UI.
    """
    result = entity_timeline(entity_id, limit=500, category=None, driver=driver)
    by_year = {}
    for ev in result["events"]:
        date = ev.get("date") or ""
        year = date[:4] if len(date) >= 4 and date[:4].isdigit() else "unknown"
        by_year.setdefault(year, []).append(ev)

    # Sort years descending
    sorted_years = sorted(
        [k for k in by_year if k != "unknown"],
        reverse=True
    ) + (["unknown"] if "unknown" in by_year else [])

    return {
        "entity_id":  entity_id,
        "total_years": len(by_year),
        "by_year":     {yr: by_year[yr] for yr in sorted_years},
        "generated_at": datetime.now().isoformat(),
    }
