"""
BharatGraph - Phase 31: Model Selector
Picks the right AI model variant based on the runtime profile.
LOW  -> smallest/fastest models (CPU-only, fits in 2GB RAM)
HIGH -> larger/more accurate models (GPU or high-RAM server)
Pure ASCII.
"""
from config.runtime_profile import PROFILE


MODEL_VARIANTS = {
    "ner": {
        "low":    "xx_ent_wiki_sm",
        "medium": "en_core_web_sm",
        "high":   "en_core_web_trf",
    },
    "embeddings": {
        "low":    "sentence-transformers/paraphrase-MiniLM-L3-v2",
        "medium": "sentence-transformers/all-MiniLM-L6-v2",
        "high":   "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    },
    "translation": {
        "low":    "Helsinki-NLP/opus-mt-en-hi",
        "medium": "Helsinki-NLP/opus-mt-en-hi",
        "high":   "Helsinki-NLP/opus-mt-en-ROMANCE",
    },
}


def get_model(task: str) -> str:
    """Return the model name for a task given the current runtime profile."""
    profile_name = PROFILE.name
    variants     = MODEL_VARIANTS.get(task, {})
    model        = variants.get(profile_name, variants.get("medium", ""))
    return model


def get_max_workers() -> int:
    return PROFILE["max_workers"]


def get_batch_size() -> int:
    return PROFILE["batch_size"]


def get_graph_depth() -> int:
    return PROFILE["graph_depth"]


def get_investigation_layers() -> int:
    return PROFILE["investigation_layers"]


def get_cache_ttl() -> int:
    return PROFILE["cache_ttl_seconds"]
