import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class SourceDocument(BaseModel):
    institution: str
    document_title: str
    url: str
    date: Optional[str] = None
    credibility: str = "official_government"


class SearchResult(BaseModel):
    entity_id: str
    entity_type: str
    name: str
    state: Optional[str] = None
    party: Optional[str] = None
    risk_score: Optional[int] = None
    sources: List[SourceDocument] = []


class SearchResponse(BaseModel):
    query: str
    total: int
    results: List[SearchResult]
    generated_at: str


class RiskFactor(BaseModel):
    name: str
    score: float
    weight: float
    description: str
    evidence: List[str] = []


class RiskResponse(BaseModel):
    entity_id: str
    entity_name: str
    risk_score: int
    risk_level: str
    factors: List[RiskFactor]
    explanation: str
    sources: List[SourceDocument] = []
    generated_at: str


class GraphNode(BaseModel):
    id: str
    label: str
    name: str
    properties: Dict[str, Any] = {}


class GraphEdge(BaseModel):
    source: str
    target: str
    relationship: str
    properties: Dict[str, Any] = {}
    source_document: Optional[str] = None


class GraphResponse(BaseModel):
    entity_id: str
    depth: int
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    generated_at: str


class ProfileSection(BaseModel):
    section: str
    data: List[Dict[str, Any]]
    sources: List[SourceDocument] = []


class ProfileResponse(BaseModel):
    entity_id: str
    entity_type: str
    name: str
    overview: Dict[str, Any] = {}
    sections: List[ProfileSection] = []
    risk_score: Optional[int] = None
    generated_at: str


class HealthResponse(BaseModel):
    status: str
    neo4j_connected: bool
    version: str
    generated_at: str


class StatsResponse(BaseModel):
    nodes: Dict[str, int]
    relationships: Dict[str, int]
    last_pipeline_run: Optional[str]
    generated_at: str


class FeedItem(BaseModel):
    headline: str
    entity_names: List[str]
    risk_level: str
    source: str
    url: Optional[str]
    detected_at: str
    summary: str
