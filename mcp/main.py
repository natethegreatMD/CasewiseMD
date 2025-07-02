"""
MCP-style FastAPI backend for CaseWise
Multi-Agent routing architecture
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import diagnostic, grade, config

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

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "CaseWise MCP Backend",
        "version": "1.0.0",
        "status": "active"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "mcp-backend",
        "agents": ["diagnostic", "grade", "config"]
"""
MCP-style FastAPI backend for CaseWise
Multi-Agent routing architecture
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import diagnostic, grade, config

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

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "CaseWise MCP Backend",
        "version": "1.0.0",
        "status": "active"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "mcp-backend",
        "agents": ["diagnostic", "grade", "config"]
    } 