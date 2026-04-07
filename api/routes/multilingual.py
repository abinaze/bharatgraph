import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
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

router     = APIRouter()
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
            {
                "code":   code,
                "name":   info["name"],
                "native": info["native"],
                "script": info["script"],
            }
            for code, info in SCHEDULED_LANGUAGES.items()
        ],
        "total":        len(SCHEDULED_LANGUAGES),
        "default":      "en",
        "generated_at": datetime.now().isoformat(),
    }


@router.get("/search/multilingual")
def multilingual_search(
    q:    str            = Query(..., min_length=1),
    lang: Optional[str]  = Query("en"),
    driver                = Depends(get_db),
):
    logger.info(f"[Multilingual] Search: '{q}' lang={lang}")
    translator     = get_translator()
    transliterator = get_transliterator()

    detected_lang = translator.detect_language(q)
    if detected_lang != "en":
        lang = detected_lang

    search_variants = transliterator.normalize_for_search(q)
    logger.info(f"[Multilingual] Search variants: {search_variants}")

    results = []
    with driver.session() as session:
        for variant in search_variants[:3]:
            rows = session.run(
                """
                MATCH (n)
                WHERE (n:Politician OR n:Company OR n:AuditReport OR
                       n:Contract OR n:Ministry OR n:Party OR
                       n:Scheme OR n:PressRelease)
                  AND (
                    toLower(coalesce(n.name,''))        CONTAINS toLower($q) OR
                    toLower(coalesce(n.title,''))       CONTAINS toLower($q) OR
                    toLower(coalesce(n.item_desc,''))   CONTAINS toLower($q) OR
                    toLower(coalesce(n.buyer_org,''))   CONTAINS toLower($q) OR
                    any(a IN coalesce(n.aliases,[])
                        WHERE toLower(a) CONTAINS toLower($q))
                  )
                RETURN n.id AS id, labels(n)[0] AS type,
                       coalesce(n.name, n.title) AS name,
                       n.state AS state, n.source AS source
                LIMIT 15
                """,
                q=variant
            ).data()
            for r in rows:
                if r.get("id") and not any(x.get("id") == r["id"] for x in results):
                    results.append(r)

    disclaimer = get_ui_label("legal_disclaimer", lang)

    return {
        "query":            q,
        "detected_language":detected_lang,
        "display_language": lang,
        "search_variants":  search_variants,
        "results":          results,
        "total":            len(results),
        "disclaimer":       disclaimer,
        "generated_at":     datetime.now().isoformat(),
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
            """
            MATCH (n {id: $id})
            RETURN n.name AS name, n.risk_score AS score,
                   n.risk_level AS level
            """,
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
    explanation      = translator.translate_risk_explanation(
        name, score, translated_level, lang
    )
    risk_label = get_ui_label("risk_indicator", lang)
    disclaimer = get_ui_label("legal_disclaimer", lang)

    return {
        "entity_id":         entity_id,
        "entity_name":       name,
        "risk_score":        score,
        "risk_level":        level,
        "risk_level_display":translated_level,
        "risk_label":        risk_label,
        "explanation":       explanation,
        "language":          lang,
        "language_name":     get_language_name(lang),
        "disclaimer":        disclaimer,
        "generated_at":      datetime.now().isoformat(),
    }


@router.post("/translate")
def translate_text(
    text:        str,
    source_lang: str = Query("en"),
    target_lang: str = Query("hi"),
):
    logger.info(f"[Multilingual] Translate {source_lang}->{target_lang}")
    translator   = get_translator()
    translated   = translator.translate(text, source_lang, target_lang)
    return {
        "original":     text,
        "translated":   translated,
        "source_lang":  source_lang,
        "target_lang":  target_lang,
        "lang_name":    get_language_name(target_lang),
        "generated_at": datetime.now().isoformat(),
    }
