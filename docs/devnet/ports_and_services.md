# Ports and Services Configuration

This document outlines the port assignments and service names for both production and development environments.

## Production Environment

### Ports
| Service | Port | Description |
|---------|------|-------------|
| MCP API | 8000 | FastAPI backend server |
| Orthanc DICOM | 8042 | Medical imaging server |
| Frontend (dev) | 5173 | Vite development server (local only) |
| Nginx HTTP | 80 | Web server (redirects to HTTPS) |
| Nginx HTTPS | 443 | Secure web server |

### Container Names
| Service | Container Name | Description |
|---------|---------------|-------------|
| MCP API | mcp | Backend API container |
| Orthanc | casewise_orthanc | DICOM server container |

### URLs
| Service | URL | Proxies To |
|---------|-----|------------|
| Frontend | https://app.casewisemd.org | /var/www/frontend/ |
| API | https://api.casewisemd.org | localhost:8000 |
| Viewer | https://viewer.casewisemd.org | /var/www/viewer/ |
| DICOM | https://dicom.casewisemd.org | localhost:8042 |

## Development Environment (Devnet)

### Ports
| Service | Port | Description | Conflicts |
|---------|------|-------------|-----------|
| MCP API | 8001 | FastAPI backend server | No conflict |
| Orthanc DICOM | 8043 | Medical imaging server | No conflict |
| Frontend (dev) | 5173 | Vite development server | Shared with prod |
| Nginx HTTP | 80 | Web server (shared) | Shared with prod |
| Nginx HTTPS | 443 | Secure web server (shared) | Shared with prod |

### Container Names
| Service | Container Name | Description |
|---------|---------------|-------------|
| MCP API | mcp-dev | Backend API container |
| Orthanc | casewise_orthanc-dev | DICOM server container |

### URLs
| Service | URL | Proxies To |
|---------|-----|------------|
| Frontend | https://dev-app.casewisemd.org | /var/www/frontend-dev/ |
| API | https://dev-api.casewisemd.org | localhost:8001 |
| Viewer | https://dev-viewer.casewisemd.org | /var/www/viewer-dev/ |
| DICOM | https://dev-dicom.casewisemd.org | localhost:8043 |

## Docker Compose Project Names
- **Production**: `casewise`
- **Development**: `casewise-dev`

## Port Conflict Analysis

### No Conflicts
- MCP API: 8000 (prod) vs 8001 (dev) ✓
- Orthanc: 8042 (prod) vs 8043 (dev) ✓
- Container names are different ✓
- Docker networks are isolated by project name ✓

### Shared Resources
- Nginx (ports 80/443) - Single nginx instance handles both environments
- VPS filesystem - Different directories for each environment
- System resources (CPU, memory) - Both environments run simultaneously

## Nginx Configuration Strategy

### Production
```nginx
upstream mcp_backend {
    server localhost:8000;
}

upstream orthanc_backend {
    server localhost:8042;
}
```

### Development
```nginx
upstream mcp_backend_dev {
    server localhost:8001;
}

upstream orthanc_backend_dev {
    server localhost:8043;
}
```

## Service Dependencies

### MCP API
- Depends on: Orthanc (for DICOM queries)
- Environment vars needed: ORTHANC_URL

### Orthanc
- Standalone service
- Stores DICOM files in volume

### Frontend
- Depends on: MCP API
- Build-time env vars: VITE_API_URL, VITE_VIEWER_URL

### OHIF Viewer
- Depends on: Orthanc (via DICOMweb)
- Configuration: Static JavaScript file

## Health Check Endpoints

### Production
- MCP API: http://localhost:8000/health
- Orthanc: http://localhost:8042/system

### Development
- MCP API: http://localhost:8001/health
- Orthanc: http://localhost:8043/system

## Volume Mappings

### Production
- Orthanc data: `orthanc_data:/var/lib/orthanc/db`
- MCP logs: `./logs:/app/logs`

### Development
- Orthanc data: `orthanc_data_dev:/var/lib/orthanc/db`
- MCP logs: `./logs-dev:/app/logs`

## Network Configuration

### Production
- Network name: `casewise_default`
- All containers on same network

### Development
- Network name: `casewise-dev_default`
- All containers on same network
- Isolated from production network