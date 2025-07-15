FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY ./mcp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create mcp directory and copy the MCP application
RUN mkdir -p mcp
COPY ./mcp/ ./mcp/

# Copy demo cases
COPY demo_cases /app/demo_cases

# Set default port
ENV MCP_PORT=8000

# Expose port (will be overridden by docker-compose)
EXPOSE ${MCP_PORT}

# Health check using environment variable
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${MCP_PORT}/health || exit 1

# Run the application with port from environment
CMD uvicorn mcp.main:app --host 0.0.0.0 --port ${MCP_PORT} 