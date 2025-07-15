# Hardcoded URLs Audit

This document contains all hardcoded URLs and configuration values found in the codebase that need to be replaced with environment variables.

## Backend (MCP)

### mcp/main.py
- **Line 27-29**: CORS origins
  ```python
  "https://casewisemd.org",
  "https://app.casewisemd.org",
  "https://www.casewisemd.org"
  ```

### mcp/tools/viewer_tools.py
- **Line 21**: OHIF base URL
  ```python
  self.ohif_base_url = "https://viewer.casewisemd.org/viewer"
  ```
- **Line 24**: DICOMweb endpoint
  ```python
  self.dicomweb_endpoint = "https://api.casewisemd.org/orthanc/dicom-web"
  ```

### mcp/Dockerfile
- **Line 27**: Health check
  ```
  CMD curl -f http://localhost:8000/health || exit 1
  ```
- **Line 30**: Uvicorn command
  ```
  CMD ["uvicorn", "mcp.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```

## Frontend

### frontend/src/DiagnosticWorkflow.tsx
- **Line 129**: API URL fallback
  ```typescript
  const API_URL = `${import.meta.env.VITE_API_URL || 'https://api.casewisemd.org'}/api/v1`;
  ```
- **Line 185**: Hardcoded viewer URL
  ```typescript
  setViewerUrl('https://viewer.casewisemd.org/viewer');
  ```
- **Line 201**: Another hardcoded viewer URL
  ```typescript
  setViewerUrl('https://viewer.casewisemd.org/viewer');
  ```

### frontend/src/components/OhifIframeViewer.tsx
- **Line 18**: Viewer URL fallback
  ```typescript
  const VIEWER_URL = viewerUrl || import.meta.env.VITE_VIEWER_URL || 'https://viewer.casewisemd.org';
  ```

### frontend/vite.config.ts
- **Line 15-20**: Server allowed hosts
  ```typescript
  'casewisemd.org',
  'www.casewisemd.org',
  'app.casewisemd.org',
  'api.casewisemd.org',
  'viewer.casewisemd.org',
  'dicom.casewisemd.org'
  ```
- **Line 24**: Development server host
  ```typescript
  host: 'app.casewisemd.org'
  ```

## Docker Configuration

### docker-compose.yml
- **Line 15**: MCP health check
  ```yaml
  test: ["CMD-SHELL", "curl --fail http://localhost:8000/health || exit 1"]
  ```
- **Line 37**: Orthanc health check
  ```yaml
  test: ["CMD-SHELL", "curl --fail http://localhost:8042/system || exit 1"]
  ```

## Scripts

### deploy-frontend.sh
- **Line 21**: Success message
  ```bash
  echo "🌐 Changes are now live at https://casewisemd.org"
  ```

## Documentation Files

### Multiple documentation files contain references:
- OHIF-Configuration-Changes.md
- SYSTEM_FLOW_DETAILED.md
- ohif-working-config-backup.js
- current-context.md
- DNS Configuration
- readme/README.md
- readme/DEVNET_USAGE.md
- readme/commands.md
- memory-bank/*.md files

These documentation files contain URLs for reference purposes and don't need to be updated with environment variables.

## Port References

### Production Ports (need environment variables):
- **8000**: MCP API port (mcp/Dockerfile, docker-compose.yml)
- **8042**: Orthanc port (docker-compose.yml, memory-bank/techContext.md)

### Development Port:
- **5173**: Vite dev server (referenced in claude.md)

## Summary of Required Changes

### Backend Files to Update:
1. `mcp/main.py` - CORS origins
2. `mcp/tools/viewer_tools.py` - OHIF and DICOMweb URLs
3. `mcp/Dockerfile` - Port reference

### Frontend Files to Update:
1. `frontend/src/DiagnosticWorkflow.tsx` - API and viewer URLs
2. `frontend/src/components/OhifIframeViewer.tsx` - Viewer URL
3. `frontend/vite.config.ts` - Allowed hosts and dev server host

### Docker/Scripts to Update:
1. `docker-compose.yml` - Port references in health checks
2. `deploy-frontend.sh` - Success message URL

### Total Files Requiring Changes: 8 files (excluding documentation)