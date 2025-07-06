"""
MCP-style FastAPI backend for CaseWise
Multi-Agent routing architecture
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import diagnostic, grade, config, case_viewer, case_management

# Load environment variables from .env file
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="CaseWise MCP Backend",
    version="1.0.0",
    description="Multi-Agent routing backend for CaseWise",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://casewisemd.org",
        "https://app.casewisemd.org",
        "https://www.casewisemd.org"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api/v1 prefix
app.include_router(diagnostic.router, prefix="/api/v1", tags=["diagnostic"])
app.include_router(grade.router, prefix="/api/v1", tags=["grade"])
app.include_router(config.router, prefix="/api/v1", tags=["config"])
app.include_router(case_viewer.router, prefix="/api/v1", tags=["case-viewer"])
app.include_router(case_management.router, prefix="/api/v1", tags=["case-management"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "CaseWise MCP Backend",
        "version": "1.0.0",
        "status": "active",
        "ai_grading_enabled": os.getenv("AI_GRADING_ENABLED", "true").lower() == "true",
        "case_management_enabled": True
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "mcp-backend",
        "agents": ["diagnostic", "grade", "config", "case-viewer", "case-management"],
        "ai_grading_status": "enabled" if os.getenv("AI_GRADING_ENABLED", "true").lower() == "true" else "disabled"
    } 