from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class AnalysisResponse(BaseModel):
    """Response from CSV analysis endpoint."""
    session_id: str
    summary: str
    insights: List[str]
    charts: List[str]  # base64 encoded PNG images
    raw_stats: Dict[str, Any]


class ChatRequest(BaseModel):
    """Request for chat endpoint."""
    session_id: str
    message: str


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    session_id: str
    response: str
    charts: Optional[List[str]] = None


class HealthResponse(BaseModel):
    """Response from health check endpoint."""
    status: str
    version: str = "1.0.0"
    ollama_status: str = "unknown"
