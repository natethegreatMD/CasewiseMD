# Environment Variable Refactor Changelog

## Date: 2025-07-15

### Overview
Refactored the entire codebase to use environment variables instead of hardcoded URLs and configuration values. This enables running development (devnet) and production environments simultaneously on the same VPS.

### Files Created
- `/mcp/config/__init__.py` - Config module initialization
- `/mcp/config/settings.py` - Centralized settings management
- `frontend/.env.example` - Frontend environment template
- `.env.example` - Updated backend environment template
- `docker-compose.dev.yml` - Development Docker configuration
- `deploy-frontend-dev.sh` - Development frontend deployment script
- `scripts/deploy-prod.sh` - Production deployment script
- `scripts/deploy-dev.sh` - Development deployment script
- `DEVNET_SETUP.md` - Complete devnet setup guide
- `hardcoded_urls_audit.md` - Audit of all hardcoded values
- `env_var_mapping.md` - Environment variable mapping
- `ports_and_services.md` - Port and service configuration

### Files Modified

#### Backend Changes
- `mcp/main.py`
  - Added import for settings module
  - Replaced hardcoded CORS origins with `settings.ALLOWED_ORIGINS`
  - Added startup event logging
  - Added environment info to root and health endpoints

- `mcp/tools/viewer_tools.py`
  - Added import for settings module
  - Replaced hardcoded `ohif_base_url` with `settings.OHIF_BASE_URL`
  - Replaced hardcoded `dicomweb_endpoint` with `settings.DICOMWEB_ENDPOINT`

- `mcp/Dockerfile`
  - Added `MCP_PORT` environment variable
  - Updated EXPOSE to use `${MCP_PORT}`
  - Updated healthcheck to use `${MCP_PORT}`
  - Updated CMD to use environment variable for port

#### Frontend Changes
- `frontend/src/DiagnosticWorkflow.tsx`
  - Added `VIEWER_BASE_URL` from environment
  - Replaced hardcoded viewer URLs with environment variable

- `frontend/src/components/OhifIframeViewer.tsx`
  - Already correctly using environment variables (no changes needed)

#### Infrastructure Changes
- `docker-compose.yml`
  - Added environment variable support for container names
  - Added environment variable support for ports
  - Updated healthcheck to use environment variables
  - Added logs volume mapping

- `deploy-frontend.sh`
  - Fixed URL in success message to use app.casewisemd.org

### Environment Variables Added

#### Backend
- `ENVIRONMENT` - production/development
- `ALLOWED_ORIGINS` - CORS allowed origins
- `API_BASE_URL` - Base URL for API
- `MCP_PORT` - MCP service port
- `OHIF_BASE_URL` - OHIF viewer base URL
- `DICOMWEB_ENDPOINT` - DICOMweb endpoint
- `ORTHANC_URL` - Internal Orthanc URL
- `ORTHANC_PORT` - Orthanc service port

#### Frontend (VITE_ prefix)
- `VITE_API_URL` - API endpoint
- `VITE_VIEWER_URL` - OHIF viewer URL
- `VITE_APP_URL` - Frontend application URL
- `VITE_DICOM_URL` - DICOM server URL
- `VITE_ENVIRONMENT` - Environment name

#### Docker
- `COMPOSE_PROJECT_NAME` - Docker project name
- `DOCKER_MCP_PORT` - External MCP port
- `DOCKER_ORTHANC_PORT` - External Orthanc port
- `DOCKER_MCP_CONTAINER` - MCP container name
- `DOCKER_ORTHANC_CONTAINER` - Orthanc container name

### Port Assignments

#### Production
- MCP API: 8000
- Orthanc: 8042

#### Development
- MCP API: 8001
- Orthanc: 8043

### Next Steps for VPS

1. Create `.env.dev` file on VPS
2. Update nginx configuration for dev-* domains
3. Create SSL certificates for dev-* domains
4. Deploy development environment using `scripts/deploy-dev.sh`

### Testing Instructions

1. Create `.env` file with production values
2. Run `docker-compose up -d`
3. Verify services are running with correct environment
4. Test API endpoints return correct environment info
5. Verify frontend builds with correct URLs

### Breaking Changes
None - all existing functionality preserved with production defaults

### Migration Notes
- Existing deployments will continue to work without changes
- To enable devnet, follow DEVNET_SETUP.md guide
- Environment variables default to production values if not set