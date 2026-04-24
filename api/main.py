import os, sys
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from api.dependencies import get_driver, close_driver
from api.routes import (
    search, profile, graph, risk, multilingual, export, admin,
    investigation, affidavit, biography, benami, sources,
    procurement, conflict, linguistic, policy, adversarial, debate
)
from api.models import HealthResponse, StatsResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[API] Starting up — attempting Neo4j connection")
    driver = get_driver()
    if driver:
        logger.success("[API] Neo4j ready")
    else:
        logger.warning("[API] Starting without Neo4j — set secrets to enable")
    yield
    logger.info("[API] Shutting down")
    close_driver()


app = FastAPI(
    title="BharatGraph API",
    description=(
        "Public transparency and institutional intelligence platform for India. "
        "All data sourced from official government records. "
        "Outputs are structural indicators, not legal findings."
    ),
    # BUG-28 FIX: bumped version string from stale 0.29.0 → 0.30.0
    version="0.30.0",
    lifespan=lifespan,
)

# BUG-15 FIX: CORS origins now read from CORS_ORIGINS env var (comma-separated).
# Defaults to localhost for local dev. Set CORS_ORIGINS=https://abinaze.github.io
# in HuggingFace secrets for production.
_cors_origins_raw = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000,https://abinaze.github.io"
)
_cors_origins = [o.strip() for o in _cors_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

from fastapi.middleware.gzip import GZipMiddleware
from api.middleware.rate_limiter import SlidingWindowRateLimiter
from api.middleware.security_headers import SecurityHeadersMiddleware
from api.middleware.input_validator import InputValidatorMiddleware
from api.middleware.audit_logger import AuditLoggerMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(SlidingWindowRateLimiter)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(InputValidatorMiddleware)
app.add_middleware(AuditLoggerMiddleware)

app.include_router(search.router,        tags=["Search"])
app.include_router(profile.router,       tags=["Profile"])
app.include_router(graph.router,         tags=["Graph"])
app.include_router(risk.router,          tags=["Risk"])
app.include_router(multilingual.router,  tags=["Multilingual"])
app.include_router(export.router,        tags=["Export"])
app.include_router(admin.router,         tags=["Admin"])
app.include_router(investigation.router, tags=["Investigation"])
app.include_router(affidavit.router,     tags=["Affidavit"])
app.include_router(biography.router,     tags=["Biography"])
app.include_router(benami.router,        tags=["Benami"])
app.include_router(sources.router,       tags=["Sources"])
app.include_router(procurement.router,   tags=["Procurement"])
app.include_router(conflict.router,      tags=["Conflict"])
app.include_router(linguistic.router,    tags=["Linguistic"])
app.include_router(policy.router,        tags=["Policy"])
app.include_router(adversarial.router,   tags=["Adversarial"])
app.include_router(debate.router,        tags=["Debate"])


@app.get("/")
def root():
    return {
        "name":        "BharatGraph API",
        "version":     "0.30.0",
        "status":      "running",
        "docs":        "/docs",
        "health":      "/health",
        "description": "Public transparency intelligence platform for India. All data from official government records.",
    }

@app.api_route("/health", methods=["GET", "HEAD"], response_model=HealthResponse)
def health_check():
    driver    = get_driver()
    connected = driver is not None
    try:
        if driver:
            driver.verify_connectivity()
    except Exception:
        connected = False
    return HealthResponse(
        status="ok" if connected else "degraded",
        neo4j_connected=connected,
        version="0.30.0",
        generated_at=datetime.now().isoformat(),
    )


@app.get("/stats", response_model=StatsResponse)
def get_stats():
    driver      = get_driver()
    node_counts = {}
    rel_counts  = {}
    last_run    = None
    if driver:
        try:
            with driver.session() as session:
                n_rows = session.run(
                    "MATCH (n) RETURN labels(n)[0] AS t, count(n) AS c"
                ).data()
                node_counts = {r["t"]: r["c"] for r in n_rows if r["t"]}
                r_rows = session.run(
                    "MATCH ()-[r]->() RETURN type(r) AS t, count(r) AS c"
                ).data()
                rel_counts = {r["t"]: r["c"] for r in r_rows if r["t"]}
                meta = session.run(
                    "MATCH (m:PipelineMeta) "
                    "RETURN m.last_run AS ts ORDER BY m.last_run DESC LIMIT 1"
                ).single()
                last_run = meta["ts"] if meta else None
        except Exception as e:
            logger.debug(f"[Stats] Query error: {e}")

    return StatsResponse(
        nodes=node_counts,
        relationships=rel_counts,
        last_pipeline_run=last_run,
        generated_at=datetime.now().isoformat(),
    )


# High-signal node types to surface in the live feed
_FEED_LABELS = [
    "AuditReport", "EnforcementAction", "RegulatoryOrder",
    "ElectoralBond", "Contract", "VigilanceCircular",
]


@app.websocket("/ws/feed")
async def websocket_feed(websocket: WebSocket):
    """
    BUG-5 FIX: now pushes real recent nodes instead of a static heartbeat.
    BUG-9 FIX: finally block guarantees the socket is always closed on exit.
    """
    import asyncio
    await websocket.accept()
    logger.info("[WS] Feed client connected")
    try:
        while True:
            driver = get_driver()
            payload: dict = {
                "type": "feed",
                "at":   datetime.now().isoformat(),
            }

            if driver:
                try:
                    with driver.session() as s:
                        # Real data: most recent high-signal nodes
                        feed_rows = s.run(
                            """
                            MATCH (n)
                            WHERE labels(n)[0] IN $labels
                              AND n.scraped_at IS NOT NULL
                            RETURN labels(n)[0] AS label,
                                   coalesce(n.name, n.title, n.company_name, n.id) AS name,
                                   n.scraped_at  AS scraped_at,
                                   n.id          AS id,
                                   n.source      AS source
                            ORDER BY n.scraped_at DESC
                            LIMIT 8
                            """,
                            labels=_FEED_LABELS
                        ).data()

                        if feed_rows:
                            payload["items"] = feed_rows
                            payload["message"] = (
                                f"{feed_rows[0].get('label','Entity')}: "
                                f"{feed_rows[0].get('name','—')}"
                            )
                        else:
                            # Fallback: at least show node counts
                            rows = s.run(
                                "MATCH (n) RETURN labels(n)[0] AS t, count(n) AS c"
                            ).data()
                            payload["stats"]   = {r["t"]: r["c"] for r in rows if r["t"]}
                            payload["message"] = "BharatGraph feed active — run /admin/pipeline to ingest data"
                except Exception as db_err:
                    logger.debug(f"[WS] DB query error: {db_err}")
                    payload["message"] = "Feed active — database query pending"
            else:
                payload["message"] = "Feed active — no database connection"

            await websocket.send_json(payload)
            await asyncio.sleep(15)

    except WebSocketDisconnect:
        logger.info("[WS] Feed client disconnected")
    except Exception as e:
        logger.warning(f"[WS] Feed error: {e}")
    finally:
        # BUG-9 FIX: always close — prevents hanging socket on unexpected exception
        try:
            await websocket.close()
        except Exception:
            pass


@app.get("/debug/env")
def debug_env():
    import os
    return {
        "neo4j_uri_set":      bool(os.getenv("NEO4J_URI")),
        "neo4j_user_set":     bool(os.getenv("NEO4J_USER")),
        "neo4j_password_set": bool(os.getenv("NEO4J_PASSWORD")),
        "neo4j_uri_prefix":   (os.getenv("NEO4J_URI","")[:15] + "...") if os.getenv("NEO4J_URI") else "NOT SET",
    }

@app.get("/debug/neo4j")
def debug_neo4j():
    import os
    from neo4j import GraphDatabase
    uri      = os.getenv("NEO4J_URI", "")
    user     = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        driver.close()
        return {"status": "connected", "uri_prefix": uri[:20]}
    except Exception as e:
        logger.warning(f"[Debug] Neo4j connection test failed: {e.__class__.__name__}")
        return {
            "status":     "failed",
            "error":      "Connection failed — check environment secrets",
            "uri_prefix": uri[:20] if uri else "NOT SET",
        }
