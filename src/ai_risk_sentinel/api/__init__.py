"""
AI Risk Sentinel API
====================

FastAPI application for the AI Risk Sentinel system.
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import structlog
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ai_risk_sentinel import __version__
from ai_risk_sentinel.core.gap_detector import GapDetector
from ai_risk_sentinel.core.compliance_checker import ComplianceChecker
from ai_risk_sentinel.models.risk import MITCategory, Risk, RiskCreate
from ai_risk_sentinel.models.metrics import BlindSpotIndex, CoverageReport, SystemMetrics

logger = structlog.get_logger(__name__)

# Global instances
gap_detector: Optional[GapDetector] = None
compliance_checker: Optional[ComplianceChecker] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global gap_detector, compliance_checker
    
    logger.info("Starting AI Risk Sentinel API", version=__version__)
    
    # Initialize components
    gap_detector = GapDetector(use_reference_data=True)
    compliance_checker = ComplianceChecker()
    
    yield
    
    logger.info("Shutting down AI Risk Sentinel API")


# Create FastAPI app
app = FastAPI(
    title="AI Risk Sentinel",
    description="Multi-Agent System for Proactive AI Risk Documentation Analysis",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Health & Info Endpoints
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": __version__
    }


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "AI Risk Sentinel",
        "version": __version__,
        "description": "Multi-Agent System for AI Risk Analysis",
        "docs": "/docs",
        "health": "/health"
    }


# =============================================================================
# Metrics Endpoints
# =============================================================================

class BSIResponse(BaseModel):
    """Response model for Blind Spot Index."""
    global_bsi: float
    by_category: dict[str, float]
    high_risk_categories: list[str]
    documentation_quality_score: float
    analysis_date: str


@app.get("/api/v1/metrics/blind-spot-index", response_model=BSIResponse)
async def get_blind_spot_index(
    model_type: Optional[str] = Query(None, description="Filter by model type")
):
    """
    Get the current Blind Spot Index metrics.
    
    The BSI measures gaps between documented risks and real-world incidents.
    A higher BSI indicates larger blind spots in risk documentation.
    """
    if not gap_detector:
        raise HTTPException(status_code=503, detail="Gap detector not initialized")
    
    report = gap_detector.analyze(model_type=model_type)
    
    return BSIResponse(
        global_bsi=report.global_bsi,
        by_category={
            cat.category.value: cat.blind_spot_index 
            for cat in report.by_category
        },
        high_risk_categories=[cat.value for cat in report.high_risk_categories],
        documentation_quality_score=report.documentation_quality_score,
        analysis_date=report.analysis_date.isoformat()
    )


@app.get("/api/v1/metrics/priority-gaps")
async def get_priority_gaps(
    limit: int = Query(5, ge=1, le=20, description="Number of gaps to return")
):
    """
    Get the most critical documentation gaps that need attention.
    """
    if not gap_detector:
        raise HTTPException(status_code=503, detail="Gap detector not initialized")
    
    gaps = gap_detector.get_priority_gaps(limit=limit)
    return {"priority_gaps": gaps, "count": len(gaps)}


@app.get("/api/v1/metrics/system", response_model=SystemMetrics)
async def get_system_metrics():
    """Get overall system metrics and agent status."""
    return SystemMetrics(
        total_risks=2863,
        risks_pending_validation=0,
        active_agents=3,
        api_requests_24h=0,
        avg_response_time_ms=50.0,
    )


# =============================================================================
# Risk Endpoints
# =============================================================================

@app.get("/api/v1/risks")
async def list_risks(
    category: Optional[str] = Query(None, description="Filter by MIT category"),
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List risks from the catalog."""
    return {
        "risks": [],
        "total": 2863,
        "limit": limit,
        "offset": offset,
        "filters": {"category": category, "source": source}
    }


@app.get("/api/v1/risks/categories")
async def get_risk_categories():
    """Get all MIT risk categories with descriptions."""
    categories = [
        {
            "id": cat.value,
            "name": cat.value.replace("_", " ").title(),
            "documented_pct": GapDetector.REFERENCE_DOCUMENTED.get(cat, 0),
            "incident_pct": GapDetector.REFERENCE_INCIDENTS.get(cat, 0)
        }
        for cat in MITCategory
    ]
    return {"categories": categories}


@app.post("/api/v1/risks", status_code=201)
async def create_risk(risk: RiskCreate):
    """Create a new risk entry."""
    return {
        "message": "Risk created",
        "risk_id": "placeholder-uuid",
        "validation_status": "pending"
    }


# =============================================================================
# Analysis Endpoints
# =============================================================================

class ModelAnalysisRequest(BaseModel):
    """Request for model analysis."""
    model_id: str
    frameworks: list[str] = ["EU_AI_ACT", "NIST_AI_RMF"]


@app.post("/api/v1/analyze/model")
async def analyze_model(request: ModelAnalysisRequest):
    """Perform comprehensive risk analysis on a model."""
    if not compliance_checker:
        raise HTTPException(status_code=503, detail="Compliance checker not initialized")
    
    report = compliance_checker.check_model(
        model_id=request.model_id,
        frameworks=request.frameworks
    )
    
    return report.model_dump()


@app.get("/api/v1/analyze/model/{model_id}/gaps")
async def get_model_gaps(model_id: str):
    """Get documentation gaps for a specific model."""
    if not compliance_checker:
        raise HTTPException(status_code=503, detail="Compliance checker not initialized")
    
    report = compliance_checker.check_model(model_id)
    
    return {
        "model_id": model_id,
        "coverage_ratio": report.coverage_ratio,
        "missing_categories": [cat.value for cat in report.categories_missing],
        "priority_gaps": report.priority_gaps
    }


# =============================================================================
# Compliance Endpoints
# =============================================================================

@app.post("/api/v1/compliance/check")
async def check_compliance(request: ModelAnalysisRequest):
    """Check model compliance against regulatory frameworks."""
    if not compliance_checker:
        raise HTTPException(status_code=503, detail="Compliance checker not initialized")
    
    report = compliance_checker.check_model(
        model_id=request.model_id,
        frameworks=request.frameworks
    )
    
    return {
        "model_id": request.model_id,
        "frameworks_checked": request.frameworks,
        "compliance_status": {
            "EU_AI_ACT": report.eu_ai_act_compliant,
            "NIST_AI_RMF": report.nist_ai_rmf_compliant
        },
        "coverage_ratio": report.coverage_ratio,
        "recommendations": report.priority_gaps[:3]
    }


# =============================================================================
# Agent Endpoints
# =============================================================================

@app.get("/api/v1/agents/status")
async def get_agents_status():
    """Get status of all AgenticX5 agents."""
    agents = [
        {"name": "HF_Crawler", "level": 1, "status": "idle", "items_processed": 0},
        {"name": "Incident_Monitor", "level": 1, "status": "idle", "items_processed": 0},
        {"name": "Regulatory_Tracker", "level": 1, "status": "idle", "items_processed": 0},
        {"name": "Gap_Detector", "level": 3, "status": "running", "items_processed": 2863},
        {"name": "Compliance_Checker", "level": 4, "status": "running", "items_processed": 0},
        {"name": "RiskDoc_Filler", "level": 5, "status": "idle", "items_processed": 0},
    ]
    return {"agents": agents, "active": 2, "total": 6}


@app.post("/api/v1/agents/{agent_name}/trigger")
async def trigger_agent(agent_name: str):
    """Manually trigger an agent run."""
    valid_agents = ["HF_Crawler", "Incident_Monitor", "Regulatory_Tracker"]
    
    if agent_name not in valid_agents:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent. Valid agents: {valid_agents}"
        )
    
    return {
        "message": f"Agent {agent_name} triggered",
        "status": "queued",
        "task_id": "placeholder-task-id"
    }


# =============================================================================
# Error Handlers
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
