# CaseWise VPS

AI-powered medical education platform for radiology residents.

## Quick Start

### Environment Setup

1. **Copy environment files**:
   ```bash
   cp .env.example .env
   cp frontend/.env.example frontend/.env
   ```

2. **Set your OpenAI API key** in `.env`:
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   ```

3. **Start services**:
   ```bash
   docker-compose up -d
   ```

## Environment Variables

The application now uses environment variables for all configuration. This allows running multiple environments on the same server.

### Key Files
- `.env.example` - Backend environment template
- `frontend/.env.example` - Frontend environment template
- `docker-compose.yml` - Production Docker configuration
- `docker-compose.dev.yml` - Development Docker configuration

### Important Variables
- `MCP_PORT` - Backend API port (8000 for prod, 8001 for dev)
- `ORTHANC_PORT` - DICOM server port (8042 for prod, 8043 for dev)
- `ALLOWED_ORIGINS` - CORS allowed origins
- `VITE_API_URL` - Frontend API endpoint
- `VITE_VIEWER_URL` - OHIF viewer URL

## Development Environment (Devnet)

To run a development environment alongside production:

1. Create `.env.dev` from `.env.example`
2. Update ports and URLs for dev environment
3. Run: `docker-compose -f docker-compose.dev.yml up -d`

See `DEVNET_SETUP.md` for complete instructions.

## Deployment

### Production
```bash
./scripts/deploy-prod.sh
```

### Development
```bash
./scripts/deploy-dev.sh
```

## Documentation

- `DEVNET_SETUP.md` - Development environment setup
- `CHANGELOG_CURRENT.md` - Recent changes
- `claude.md` - AI assistant instructions
- `hardcoded_urls_audit.md` - Hardcoded values audit
- `env_var_mapping.md` - Environment variable reference
- `ports_and_services.md` - Port assignments

## URLs

### Production
- Frontend: https://app.casewisemd.org
- API: https://api.casewisemd.org
- Viewer: https://viewer.casewisemd.org

### Development (when configured)
- Frontend: https://dev-app.casewisemd.org
- API: https://dev-api.casewisemd.org
- Viewer: https://dev-viewer.casewisemd.org

## Testing

Run the environment setup test:
```bash
./scripts/test-env-setup.sh
```

## Architecture

- **Frontend**: React 19 + TypeScript + Vite
- **Backend**: Python FastAPI
- **DICOM**: Orthanc server
- **Viewer**: OHIF medical imaging viewer
- **AI**: OpenAI GPT-4o for grading