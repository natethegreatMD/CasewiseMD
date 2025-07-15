# Environment Variable Mapping

This document maps all hardcoded values to their corresponding environment variables for both production and development environments.

## Backend Environment Variables

| Variable Name | Production Value | Development Value | Description |
|--------------|------------------|-------------------|-------------|
| `ALLOWED_ORIGINS` | `https://app.casewisemd.org,https://casewisemd.org,https://www.casewisemd.org` | `https://dev-app.casewisemd.org,http://localhost:5173` | CORS allowed origins |
| `API_BASE_URL` | `https://api.casewisemd.org` | `https://dev-api.casewisemd.org` | Base URL for API |
| `OHIF_BASE_URL` | `https://viewer.casewisemd.org/viewer` | `https://dev-viewer.casewisemd.org/viewer` | OHIF viewer base URL |
| `DICOMWEB_ENDPOINT` | `https://api.casewisemd.org/orthanc/dicom-web` | `https://dev-api.casewisemd.org/orthanc/dicom-web` | DICOMweb endpoint |
| `ORTHANC_URL` | `http://localhost:8042` | `http://localhost:8043` | Internal Orthanc URL |
| `MCP_PORT` | `8000` | `8001` | MCP API port |
| `ORTHANC_PORT` | `8042` | `8043` | Orthanc server port |
| `ENVIRONMENT` | `production` | `development` | Environment name |
| `OPENAI_API_KEY` | `sk-...` | `sk-...` | OpenAI API key (same for both) |

## Frontend Environment Variables (VITE_ prefix required)

| Variable Name | Production Value | Development Value | Description |
|--------------|------------------|-------------------|-------------|
| `VITE_API_URL` | `https://api.casewisemd.org` | `https://dev-api.casewisemd.org` | API base URL |
| `VITE_VIEWER_URL` | `https://viewer.casewisemd.org` | `https://dev-viewer.casewisemd.org` | OHIF viewer URL |
| `VITE_APP_URL` | `https://app.casewisemd.org` | `https://dev-app.casewisemd.org` | Frontend app URL |
| `VITE_DICOM_URL` | `https://dicom.casewisemd.org` | `https://dev-dicom.casewisemd.org` | DICOM server URL |
| `VITE_ENVIRONMENT` | `production` | `development` | Environment name |

## Docker Environment Variables

| Variable Name | Production Value | Development Value | Description |
|--------------|------------------|-------------------|-------------|
| `COMPOSE_PROJECT_NAME` | `casewise` | `casewise-dev` | Docker Compose project name |
| `DOCKER_MCP_PORT` | `8000` | `8001` | MCP container port |
| `DOCKER_ORTHANC_PORT` | `8042` | `8043` | Orthanc container port |
| `DOCKER_MCP_CONTAINER` | `mcp` | `mcp-dev` | MCP container name |
| `DOCKER_ORTHANC_CONTAINER` | `casewise_orthanc` | `casewise_orthanc-dev` | Orthanc container name |

## Usage Examples

### Backend (.env)
```bash
# Production
ALLOWED_ORIGINS=https://app.casewisemd.org,https://casewisemd.org,https://www.casewisemd.org
API_BASE_URL=https://api.casewisemd.org
OHIF_BASE_URL=https://viewer.casewisemd.org/viewer
DICOMWEB_ENDPOINT=https://api.casewisemd.org/orthanc/dicom-web
ORTHANC_URL=http://localhost:8042
MCP_PORT=8000
ORTHANC_PORT=8042
ENVIRONMENT=production
OPENAI_API_KEY=sk-your-key-here
```

### Backend (.env.dev)
```bash
# Development
ALLOWED_ORIGINS=https://dev-app.casewisemd.org,http://localhost:5173
API_BASE_URL=https://dev-api.casewisemd.org
OHIF_BASE_URL=https://dev-viewer.casewisemd.org/viewer
DICOMWEB_ENDPOINT=https://dev-api.casewisemd.org/orthanc/dicom-web
ORTHANC_URL=http://localhost:8043
MCP_PORT=8001
ORTHANC_PORT=8043
ENVIRONMENT=development
OPENAI_API_KEY=sk-your-key-here
```

### Frontend (.env)
```bash
# Production
VITE_API_URL=https://api.casewisemd.org
VITE_VIEWER_URL=https://viewer.casewisemd.org
VITE_APP_URL=https://app.casewisemd.org
VITE_DICOM_URL=https://dicom.casewisemd.org
VITE_ENVIRONMENT=production
```

### Frontend (.env.dev)
```bash
# Development
VITE_API_URL=https://dev-api.casewisemd.org
VITE_VIEWER_URL=https://dev-viewer.casewisemd.org
VITE_APP_URL=https://dev-app.casewisemd.org
VITE_DICOM_URL=https://dev-dicom.casewisemd.org
VITE_ENVIRONMENT=development
```

### Docker (.env)
```bash
# Production
COMPOSE_PROJECT_NAME=casewise
DOCKER_MCP_PORT=8000
DOCKER_ORTHANC_PORT=8042
DOCKER_MCP_CONTAINER=mcp
DOCKER_ORTHANC_CONTAINER=casewise_orthanc
```

### Docker (.env.dev)
```bash
# Development
COMPOSE_PROJECT_NAME=casewise-dev
DOCKER_MCP_PORT=8001
DOCKER_ORTHANC_PORT=8043
DOCKER_MCP_CONTAINER=mcp-dev
DOCKER_ORTHANC_CONTAINER=casewise_orthanc-dev
```

## Implementation Notes

1. **Backend**: All backend environment variables should be loaded in `/mcp/config/settings.py`
2. **Frontend**: Vite requires the `VITE_` prefix for environment variables to be accessible in the browser
3. **Docker**: Use `${VARIABLE:-default}` syntax in docker-compose.yml for defaults
4. **Build Time vs Runtime**: Frontend environment variables are set at BUILD TIME, not runtime