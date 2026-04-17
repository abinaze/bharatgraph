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
from api.routes import search, profile, graph, risk, multilingual, export, admin, investigation, affidavit, biography, benami, sources, procurement, conflict, linguistic, policy, adversarial, debate
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
    version="0.29.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

app.include_router(search.router,      tags=["Search"])
app.include_router(profile.router,     tags=["Profile"])
app.include_router(graph.router,       tags=["Graph"])
app.include_router(risk.router,        tags=["Risk"])
app.include_router(multilingual.router,tags=["Multilingual"])
app.include_router(export.router,      tags=["Export"])
app.include_router(admin.router,         tags=["Admin"])
app.include_router(investigation.router, tags=["Investigation"])
app.include_router(affidavit.router,     tags=["Affidavit"])
app.include_router(biography.router,     tags=["Biography"])
app.include_router(benami.router,       tags=["Benami"])
app.include_router(sources.router,      tags=["Sources"])
app.include_router(procurement.router,   tags=["Procurement"])
app.include_router(conflict.router,       tags=["Conflict"])
app.include_router(linguistic.router,     tags=["Linguistic"])
app.include_router(policy.router,         tags=["Policy"])
app.include_router(adversarial.router,     tags=["Adversarial"])
app.include_router(debate.router,          tags=["Debate"])



@app.get("/")
def root():
    """API root — returns version and link to docs."""
    return {
        "name": "BharatGraph API",
        "version": "0.29.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
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
        version="0.29.0",
        generated_at=datetime.now().isoformat(),
    )


@app.get("/stats", response_model=StatsResponse)
def get_stats():
    driver      = get_driver()
    node_counts = {}
    rel_counts  = {}
    if driver:
        with driver.session() as session:
            rows = session.run(
                "MATCH (n) RETURN labels(n)[0] AS t, count(n) AS c"
            ).data()
            node_counts = {r["t"]: r["c"] for r in rows if r["t"]}
            rows = session.run(
                "MATCH ()-[r]->() RETURN type(r) AS t, count(r) AS c"
            ).data()
            rel_counts = {r["t"]: r["c"] for r in rows if r["t"]}
    # Read last pipeline timestamp from Neo4j if stored
    last_run = None
    try:
        if driver:
            with driver.session() as session:
                row = session.run(
                    "MATCH (m:PipelineMeta) "
                    "RETURN m.last_run AS ts ORDER BY m.last_run DESC LIMIT 1"
                ).single()
                last_run = row["ts"] if row else None
    except Exception:
        pass

    return StatsResponse(
        nodes=node_counts,
        relationships=rel_counts,
        last_pipeline_run=last_run,
        generated_at=datetime.now().isoformat(),
    )


@app.websocket("/ws/feed")
async def websocket_feed(websocket: WebSocket):
    await websocket.accept()
    logger.info("[WS] Feed client connected")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({
                "type":    "ping",
                "message": "Feed active. Updates broadcast on new data ingestion.",
                "at":      datetime.now().isoformat(),
            })
    except WebSocketDisconnect:
        logger.info("[WS] Feed client disconnected")

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
        logger.warning(f"[Debug] Neo4j connection test failed: {type(e).__name__}")
        return {"status": "failed",
                "error": "Connection failed — check environment secrets",
                "uri_prefix": uri[:20] if uri else "NOT SET"}
