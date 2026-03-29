import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from api.dependencies import get_driver, close_driver
from api.routes import search, profile, graph, risk
from api.models import HealthResponse, StatsResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[API] Starting up — initialising Neo4j driver")
    get_driver()
    yield
    logger.info("[API] Shutting down — closing Neo4j driver")
    close_driver()


app = FastAPI(
    title="BharatGraph API",
    description=(
        "Public transparency and institutional intelligence platform for India. "
        "All data sourced from official government records. "
        "Outputs are structural indicators, not legal findings."
    ),
    version="0.4.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(search.router,  tags=["Search"])
app.include_router(profile.router, tags=["Profile"])
app.include_router(graph.router,   tags=["Graph"])
app.include_router(risk.router,    tags=["Risk"])


@app.get("/health", response_model=HealthResponse)
def health_check():
    driver = get_driver()
    connected = driver is not None
    try:
        if driver:
            driver.verify_connectivity()
    except Exception:
        connected = False
    return HealthResponse(
        status="ok" if connected else "degraded",
        neo4j_connected=connected,
        version="0.4.0",
        generated_at=datetime.now().isoformat(),
    )


@app.get("/stats", response_model=StatsResponse)
def get_stats():
    driver = get_driver()
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

    return StatsResponse(
        nodes=node_counts,
        relationships=rel_counts,
        last_pipeline_run=None,
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
