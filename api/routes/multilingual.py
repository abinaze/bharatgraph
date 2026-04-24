import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body
from loguru import logger

from api.dependencies import get_db
from config.languages import (
    SCHEDULED_LANGUAGES,
    get_language_name,
    get_risk_translation,
    get_ui_label,
)
from ai.translator import Translator
from ai.transliteration import Transliterator

router          = APIRouter()
_translator     = None
_transliterator = None


def get_translator() -> Translator:
    global _translator
    if _translator is None:
        _translator = Translator()
    return _translator


def get_transliterator() -> Transliterator:
    global _transliterator
    if _transliterator is None:
        _transliterator = Transliterator()
    return _transliterator


@router.get("/languages")
def list_languages():
    return {
        "supported_languages": [
            {"code": code, "name": info["name"],
             "native": info["native"], "script": info["script"]}
            for code, info in SCHEDULED_LANGUAGES.items()
        ],
        "total":        len(SCHEDULED_LANGUAGES),
        "default":      "en",
        "generated_at": datetime.now().isoformat(),
    }


@router.get("/search/multilingual")
def multilingual_search(
    q:    str           = Query(..., min_length=1),
    lang: Optional[str] = Query("en"),
    driver                = Depends(get_db),
):
    logger.info(f"[Multilingual] Search: '{q}' lang={lang}")
    translator     = get_translator()
    transliterator = get_transliterator()

    detected_lang = translator.detect_language(q)
    if detected_lang != "en":
        lang = detected_lang

    search_variants = transliterator.normalize_for_search(q)

    # BUG-31 FIX: added 6 previously missing node types:
    # ParliamentQuestion, VigilanceCircular, ICIJEntity,
    # SanctionedEntity, CourtCase, LocalBody
    INDEXED_QUERIES = [
        ("Politician",        "MATCH (n:Politician) WHERE toLower(n.name) CONTAINS toLower($q) OR any(a IN coalesce(n.aliases,[]) WHERE toLower(a) CONTAINS toLower($q)) RETURN n.id AS id, 'Politician' AS type, n.name AS name, n.state AS state, n.source AS source LIMIT 5"),
        ("Company",           "MATCH (n:Company) WHERE toLower(n.name) CONTAINS toLower($q) OR toLower(coalesce(n.cin,'')) CONTAINS toLower($q) RETURN n.id AS id, 'Company' AS type, n.name AS name, n.state AS state, n.source AS source LIMIT 5"),
        ("AuditReport",       "MATCH (n:AuditReport) WHERE toLower(coalesce(n.title,'')) CONTAINS toLower($q) OR toLower(coalesce(n.ministry,'')) CONTAINS toLower($q) RETURN n.id AS id, 'AuditReport' AS type, n.title AS name, n.state AS state, n.source AS source LIMIT 3"),
        ("Contract",          "MATCH (n:Contract) WHERE toLower(coalesce(n.item_desc,'')) CONTAINS toLower($q) OR toLower(coalesce(n.buyer_org,'')) CONTAINS toLower($q) RETURN n.id AS id, 'Contract' AS type, coalesce(n.item_desc,n.order_id) AS name, null AS state, n.source AS source LIMIT 3"),
        ("Ministry",          "MATCH (n:Ministry) WHERE toLower(n.name) CONTAINS toLower($q) RETURN n.id AS id, 'Ministry' AS type, n.name AS name, null AS state, n.source AS source LIMIT 3"),
        ("Party",             "MATCH (n:Party) WHERE toLower(n.name) CONTAINS toLower($q) RETURN n.id AS id, 'Party' AS type, n.name AS name, null AS state, n.source AS source LIMIT 3"),
        ("PressRelease",      "MATCH (n:PressRelease) WHERE toLower(coalesce(n.title,'')) CONTAINS toLower($q) RETURN n.id AS id, 'PressRelease' AS type, n.title AS name, null AS state, n.source AS source LIMIT 3"),
        ("ElectoralBond",     "MATCH (n:ElectoralBond) WHERE toLower(coalesce(n.purchaser_name,'')) CONTAINS toLower($q) OR toLower(coalesce(n.redeemed_by,'')) CONTAINS toLower($q) RETURN n.id AS id, 'ElectoralBond' AS type, coalesce(n.purchaser_name,n.redeemed_by) AS name, null AS state, n.source AS source LIMIT 3"),
        ("NGO",               "MATCH (n:NGO) WHERE toLower(coalesce(n.ngo_name,'')) CONTAINS toLower($q) RETURN n.id AS id, 'NGO' AS type, n.ngo_name AS name, n.state AS state, n.source AS source LIMIT 3"),
        # BUG-31 FIX: 6 new types added below
        ("ParliamentQuestion","MATCH (n:ParliamentQuestion) WHERE toLower(coalesce(n.subject,'')) CONTAINS toLower($q) OR toLower(coalesce(n.member_name,'')) CONTAINS toLower($q) RETURN n.id AS id, 'ParliamentQuestion' AS type, n.subject AS name, null AS state, n.source AS source LIMIT 3"),
        ("VigilanceCircular", "MATCH (n:VigilanceCircular) WHERE toLower(coalesce(n.title,'')) CONTAINS toLower($q) OR toLower(coalesce(n.subject,'')) CONTAINS toLower($q) RETURN n.id AS id, 'VigilanceCircular' AS type, n.title AS name, null AS state, n.source AS source LIMIT 3"),
        ("ICIJEntity",        "MATCH (n:ICIJEntity) WHERE toLower(coalesce(n.name,'')) CONTAINS toLower($q) OR toLower(coalesce(n.jurisdiction,'')) CONTAINS toLower($q) RETURN n.id AS id, 'ICIJEntity' AS type, n.name AS name, null AS state, n.source AS source LIMIT 3"),
        ("SanctionedEntity",  "MATCH (n:SanctionedEntity) WHERE toLower(coalesce(n.name,'')) CONTAINS toLower($q) RETURN n.id AS id, 'SanctionedEntity' AS type, n.name AS name, null AS state, n.source AS source LIMIT 3"),
        ("CourtCase",         "MATCH (n:CourtCase) WHERE toLower(coalesce(n.court_name,'')) CONTAINS toLower($q) OR toLower(coalesce(n.state,'')) CONTAINS toLower($q) RETURN n.id AS id, 'CourtCase' AS type, n.court_name AS name, n.state AS state, n.source AS source LIMIT 3"),
        ("LocalBody",         "MATCH (n:LocalBody) WHERE toLower(coalesce(n.name,'')) CONTAINS toLower($q) OR toLower(coalesce(n.district,'')) CONTAINS toLower($q) RETURN n.id AS id, 'LocalBody' AS type, n.name AS name, n.state AS state, n.source AS source LIMIT 3"),
    ]

    results  = []
    seen_ids = set()
    with driver.session() as session:
        for variant in search_variants[:3]:
            for label, cypher in INDEXED_QUERIES:
                try:
                    rows = session.run(cypher, q=variant).data()
                    for r in rows:
                        rid = r.get("id", "")
                        if rid and rid not in seen_ids:
                            seen_ids.add(rid)
                            results.append(r)
                except Exception as qe:
                    logger.debug(f"[Multilingual] {label} query skipped: {qe}")

    disclaimer = get_ui_label("legal_disclaimer", lang)

    return {
        "query":             q,
        "detected_language": detected_lang,
        "display_language":  lang,
        "search_variants":   search_variants,
        "results":           results,
        "total":             len(results),
        "disclaimer":        disclaimer,
        "generated_at":      datetime.now().isoformat(),
    }


@router.get("/risk/multilingual/{entity_id}")
def multilingual_risk(
    entity_id: str,
    lang: Optional[str] = Query("en"),
    driver               = Depends(get_db),
):
    logger.info(f"[Multilingual] Risk for {entity_id} in {lang}")
    translator = get_translator()

    with driver.session() as session:
        row = session.run(
            "MATCH (n {id: $id}) RETURN n.name AS name, "
            "n.risk_score AS score, n.risk_level AS level",
            id=entity_id
        ).single()

    if not row:
        return {
            "error":   "Entity not found",
            "message": translator.get_no_data_message(lang),
        }

    name  = row["name"]  or entity_id
    score = row["score"] or 0
    level = row["level"] or "UNKNOWN"

    translated_level = get_risk_translation(level, lang)
    explanation      = translator.translate_risk_explanation(name, score, translated_level, lang)
    risk_label       = get_ui_label("risk_indicator", lang)
    disclaimer       = get_ui_label("legal_disclaimer", lang)

    return {
        "entity_id":          entity_id,
        "entity_name":        name,
        "risk_score":         score,
        "risk_level":         level,
        "risk_level_display": translated_level,
        "risk_label":         risk_label,
        "explanation":        explanation,
        "language":           lang,
        "language_name":      get_language_name(lang),
        "disclaimer":         disclaimer,
        "generated_at":       datetime.now().isoformat(),
    }


# BUG-7 FIX: translate now accepts text from EITHER query param (short text)
# OR JSON request body (long text). The frontend sends query params for text
# < 400 chars and a JSON body for longer text to avoid 414 URI Too Long.
@router.post("/translate")
def translate_text(
    source_lang: str = Query("en"),
    target_lang: str = Query("hi"),
    text:        str = Query(None),         # short text via query string
    body:        dict = Body(default={}),   # long text via JSON body
):
    # Prefer body.text if present, fall back to query param
    actual_text = (body.get("text") or text or "").strip()
    if not actual_text:
        return {"error": "No text provided", "original": "", "translated": ""}

    logger.info(f"[Multilingual] Translate {source_lang}->{target_lang} "
                f"({len(actual_text)} chars)")
    translator = get_translator()
    translated = translator.translate(actual_text, source_lang, target_lang)
    return {
        "original":     actual_text,
        "translated":   translated,
        "source_lang":  source_lang,
        "target_lang":  target_lang,
        "lang_name":    get_language_name(target_lang),
        "generated_at": datetime.now().isoformat(),
    }


# BUG-32 FIX: duplicate @router.get("/ui-labels") definition — Python
# silently registers only the SECOND one, so the first implementation
# (using get_ui_label) was always shadowed. Merged into one handler using
# the more complete get_all_labels_for_lang implementation.
@router.get("/ui-labels")
def get_ui_labels(lang: str = "en"):
    """Return all UI labels translated into the requested language."""
    from config.languages import get_all_labels_for_lang, SCHEDULED_LANGUAGES
    labels = get_all_labels_for_lang(lang)
    return {
        "language":      lang,
        "language_name": SCHEDULED_LANGUAGES.get(lang, {}).get("name", "English"),
        "native_name":   SCHEDULED_LANGUAGES.get(lang, {}).get("native", "English"),
        "labels":        labels,
        "generated_at":  datetime.now().isoformat(),
    }
