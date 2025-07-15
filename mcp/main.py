"""
MCP-style FastAPI backend for CaseWise
Multi-Agent routing architecture
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import diagnostic, grade, config, case_viewer
from .config import settings

# Load environment variables from .env file
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="CaseWise MCP Backend",
    version="1.0.0",
    description="Multi-Agent routing backend for CaseWise",
)

# Add CORS middleware with environment-based origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api/v1 prefix
app.include_router(diagnostic.router, prefix="/api/v1", tags=["diagnostic"])
app.include_router(grade.router, prefix="/api/v1", tags=["grade"])
app.include_router(config.router, prefix="/api/v1", tags=["config"])
app.include_router(case_viewer.router, prefix="/api/v1", tags=["case-viewer"])

# Startup event to log configuration
@app.on_event("startup")
async def startup_event():
    config_summary = settings.get_config_summary()
    print(f"Starting MCP Backend in {config_summary['environment']} mode")
    print(f"Configuration: {config_summary}")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "CaseWise MCP Backend",
        "version": "1.0.0",
        "status": "active",
        "environment": settings.ENVIRONMENT,
        "ai_grading_enabled": os.getenv("AI_GRADING_ENABLED", "true").lower() == "true"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "mcp-backend",
        "environment": settings.ENVIRONMENT,
        "agents": ["diagnostic", "grade", "config", "case-viewer"],
        "ai_grading_status": "enabled" if os.getenv("AI_GRADING_ENABLED", "true").lower() == "true" else "disabled"
    } 