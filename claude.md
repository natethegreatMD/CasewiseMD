# Casewise VPS - AI Assistant Guide

## Working Context
- **Ask for location**: Always ask "Are we working locally or on the VPS?" at session start
- **Cursor Integration**: User codes with Cursor (AI editor) - provide specific, detailed tasks
- **Task Style**: Break down work into small, explicit steps like for a junior developer
- **VPS vs Local**: 
  - VPS (143.244.154.89): nginx, docker, production/devnet deployments
  - Local: development, code editing with Cursor

## Project Overview
- **What**: AI-powered medical education platform for radiology residents
- **Status**: Production system live with real users, 1 case (TCGA-09-0364)
- **Key Feature**: Real-time AI grading using GPT-4o for medical diagnostic accuracy
- **Architecture**: FastAPI backend, React frontend, OHIF viewer, Orthanc DICOM server
- **Current Focus**: Environment variable refactor completed, ready for devnet deployment

## Environment Setup (COMPLETED 2025-07-15)

### What Was Done
The entire codebase has been refactored to use environment variables instead of hardcoded URLs. This enables running development (devnet) and production environments simultaneously on the same VPS.

### Key Changes Made
1. **Backend**: Created `/mcp/config/settings.py` for centralized configuration
2. **Frontend**: Updated to use `import.meta.env.VITE_*` variables
3. **Docker**: Both `docker-compose.yml` and `docker-compose.dev.yml` use env vars
4. **Scripts**: Created deployment scripts for both environments
5. **Documentation**: Created comprehensive setup guides

### Environment Structure
```
Production (Current):
- Ports: 8000 (MCP), 8042 (Orthanc)
- URLs: *.casewisemd.org
- Config: .env files

Development (Ready to Deploy):
- Ports: 8001 (MCP), 8043 (Orthanc)  
- URLs: dev-*.casewisemd.org
- Config: .env.dev files
```

## Directory Structure
```
casewise-vps/
├── frontend/               # React 19 + TypeScript + Vite
│   ├── src/               # Source code
│   ├── .env               # Production environment
│   └── .env.dev           # Development environment
├── mcp/                   # FastAPI backend
│   ├── config/            # NEW: Settings module
│   │   └── settings.py    # Centralized env var config
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic (AI grading)
│   └── tools/             # MCP tools (viewer config)
├── scripts/               # Deployment scripts
│   ├── deploy-prod.sh     # Production deployment
│   ├── deploy-dev.sh      # Development deployment
│   └── test-env-setup.sh  # Environment verification
├── docs/                  # Documentation
│   ├── devnet/           # Environment setup docs
│   └── technical/        # System documentation
├── docker/               # Docker configurations
├── demo_cases/           # Case data and DICOM files
├── rubrics/              # AI grading criteria
├── .env                  # Production backend config
├── .env.dev              # Development backend config
├── docker-compose.yml     # Production Docker
└── docker-compose.dev.yml # Development Docker
```

## Current URLs

### Production (LIVE)
- Frontend: https://app.casewisemd.org
- API: https://api.casewisemd.org
- Viewer: https://viewer.casewisemd.org
- DICOM: https://dicom.casewisemd.org

### Development (DNS Ready, Nginx Pending)
- Frontend: https://dev-app.casewisemd.org
- API: https://dev-api.casewisemd.org
- Viewer: https://dev-viewer.casewisemd.org
- DICOM: https://dev-dicom.casewisemd.org

## Quick Start Commands

### Local Development
```bash
# Start production environment
docker-compose up -d

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Check services
docker ps

# View logs
docker logs mcp          # Production
docker logs mcp-dev      # Development
```

### VPS Deployment
```bash
# SSH to VPS
ssh root@143.244.154.89

# Deploy production
cd /root/casewise-vps
./scripts/deploy-prod.sh

# Deploy development (after nginx setup)
./scripts/deploy-dev.sh
```

## Environment Variables

### Backend Core Variables
- `ENVIRONMENT`: production/development
- `MCP_PORT`: API port (8000/8001)
- `ORTHANC_PORT`: DICOM port (8042/8043)
- `ALLOWED_ORIGINS`: CORS allowed origins
- `OPENAI_API_KEY`: Required for AI grading

### Frontend Variables (VITE_ prefix required)
- `VITE_API_URL`: Backend API endpoint
- `VITE_VIEWER_URL`: OHIF viewer URL
- `VITE_ENVIRONMENT`: Environment name

### Docker Variables
- `DOCKER_MCP_PORT`: External MCP port
- `DOCKER_ORTHANC_PORT`: External Orthanc port
- `COMPOSE_PROJECT_NAME`: Docker project name

## Next Steps for Devnet Deployment

### On VPS (One-time Setup)
1. **Pull latest code**: `git pull origin main`
2. **Copy env file**: Ensure `.env.dev` has OpenAI key
3. **Create nginx configs** for dev-* domains
4. **Get SSL certificates**: `certbot --nginx -d dev-*.casewisemd.org`
5. **Create frontend directory**: `mkdir -p /var/www/frontend-dev`
6. **Run deployment**: `./scripts/deploy-dev.sh`

### Nginx Configuration Needed
```nginx
# For dev-api.casewisemd.org
upstream mcp_backend_dev {
    server localhost:8001;
}

# For dev-app.casewisemd.org  
root /var/www/frontend-dev;
```

## Critical Files & Their Purpose

### Backend
- `/mcp/config/settings.py`: All environment variables loaded here
- `/mcp/main.py`: FastAPI app with CORS configuration
- `/mcp/services/ai_grading.py`: GPT-4o integration for grading
- `/mcp/tools/viewer_tools.py`: OHIF viewer URL generation

### Frontend
- `/frontend/src/DiagnosticWorkflow.tsx`: Main workflow component
- `/frontend/src/components/OhifIframeViewer.tsx`: DICOM viewer iframe

### Configuration
- `.env` / `.env.dev`: Backend environment variables
- `frontend/.env` / `frontend/.env.dev`: Frontend build variables
- `docker-compose*.yml`: Docker service definitions

## Common Issues & Solutions

### CORS Errors
- Check `ALLOWED_ORIGINS` in backend .env includes frontend URL
- Restart MCP container after changes

### Viewer Not Loading
- Verify `VITE_VIEWER_URL` is set correctly
- Check nginx proxy configuration
- Ensure Orthanc is running

### AI Grading Fails
- Verify `OPENAI_API_KEY` is set and valid
- Check API rate limits
- Review logs: `docker logs mcp`

## Testing the Setup

Run the test script:
```bash
./scripts/test-env-setup.sh
```

This verifies:
- All required files exist
- Environment variables are set
- Docker configurations are valid
- Python imports work correctly

## Important Notes

### Production Considerations
- **Live System**: Real medical residents use this daily
- **AI Costs**: Each grading call costs money (GPT-4o)
- **Medical Accuracy**: Critical for educational value
- **DICOM Files**: Large files, handle with care

### Development Best Practices
- Always test in devnet before production
- Keep `.env.dev` updated with latest variables
- Monitor both environments - they share VPS resources
- Document any nginx or infrastructure changes

## Current Limitations
- Single case (TCGA-09-0364) hardcoded
- No user authentication system
- No database (filesystem only)
- Manual case creation process
- Basic error handling

## Planned Improvements
1. MCP Case Loader Refactor
  - **Current**: Hardcoded case001, basic filesystem scanning
  - **Goal**: Dynamic, cached, modular case loading
  - **New structure**: `/mcp/case_loader/`
  - **Features**:
    - Pluggable loader classes (demo_cases, TCGA, custom)
    - In-memory caching
    - Dynamic file watching
    - Case filtering by subspecialty/difficulty
2. Core MCP Refactor  
- **Current**: Monolithic services (ai_grading.py has 923 lines)
- **Goal**: Modular components for grading, questions, feedback
- **New structure**: 
  - `/mcp/grading/` - Rubric and AI grading modules
  - `/mcp/questions/` - Question generation and prompts
  - `/mcp/core/` - Shared interfaces and base classes


3. **Database Integration**: PostgreSQL for user/case management
4. **Authentication**: JWT-based auth system
5. **More Cases**: Expand beyond single case
6. **Enhanced Analytics**: Track student performance

## For New Claude Sessions

When starting a new session:
1. Ask if working locally or on VPS
2. Check `git status` for any uncommitted changes
3. Review recent commits for context
4. Check docker container status
5. Verify which environment (prod/dev) is being worked on

Key context to remember:
- Environment variable refactor is COMPLETE
- Both .env and .env.dev files contain the OpenAI API key
- Frontend uses Vite, requires VITE_ prefix for env vars
- Deployment scripts handle environment switching
- Nginx configuration on VPS still needs dev-* setup

---
*Last updated: 2025-07-15 - Environment Variable Refactor Complete, Ready for Devnet Deployment*