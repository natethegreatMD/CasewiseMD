# Casewise VPS - AI Assistant Guide

## Working Context
- **Ask for location**: Always ask "Are we working locally or on the VPS?" at session start
- **Cursor Integration**: User codes with Cursor (AI editor) - provide specific, detailed tasks
- **Task Style**: Break down work into small, explicit steps like for a junior developer
- **VPS vs Local**: 
  - VPS (143.244.154.89): nginx, docker, production/devnet deployments
  - Local: development, code editing with Cursor

## Quick Start
- **Project**: AI-powered medical education platform for radiology residents
- **Status**: Production system with 1 case, planning major refactors
- **Key Achievement**: Real AI grading with GPT-4o (replaced fake scoring)
- **Production URLs**: 
  - Frontend: https://app.casewisemd.org
  - API: https://api.casewisemd.org
  - Viewer: https://viewer.casewisemd.org
  - DICOM: https://dicom.casewisemd.org
- **Devnet URLs** (DNS records created, nginx pending):
  - Frontend: https://dev-app.casewisemd.org
  - API: https://dev-api.casewisemd.org
  - Viewer: https://dev-viewer.casewisemd.org
  - DICOM: https://dev-dicom.casewisemd.org

## Current Architecture

### System Components
- **Frontend**: React 19 + TypeScript + Vite (deployed)
- **Backend**: Python FastAPI with MCP pattern (deployed) 
- **Viewer**: OHIF medical image viewer (deployed)
- **DICOM**: Orthanc server (deployed)
- **AI**: OpenAI GPT-4o integration (active)

### Directory Structure
```
/Users/newuser/Documents/casewise/casewise-vps/
├── frontend/           # React application
├── mcp/               # Backend API with routes, services, tools
├── memory-bank/       # Project documentation and context
├── rubrics/           # Grading criteria JSON files
├── source-documents/  # Medical case data
├── case generator/    # Tools for creating new cases
└── docker/            # Docker configuration files
```

## CURRENT ACTIVE GOAL: Environment Variable Refactor
**Status**: Planning phase
**Reason**: Need to support devnet without maintaining two branches with different hardcoded URLs

### Detailed Task List:

#### Phase 1: Discovery and Planning
1. [ ] Run search for all hardcoded URLs and save to `hardcoded_urls_audit.md`
   - Search for: "casewisemd.org", "localhost", "8000", "8042", "https://", "http://"
   - Include file path and line numbers
   - Group by component (backend, frontend, config)

2. [ ] Create environment variable mapping document `env_var_mapping.md`
   - Map each hardcoded value to proposed env var name
   - Include default values for production
   - Include devnet values

3. [ ] Identify all ports and services in `ports_and_services.md`
   - Current production ports
   - Proposed devnet ports (must not conflict)
   - Docker container names

#### Phase 2: Backend Updates
4. [ ] Create `/mcp/config/settings.py` for centralized configuration
   - Import os and load all env vars
   - Provide defaults matching current production

5. [ ] Update `mcp/main.py`
   - Import settings from config/settings.py
   - Replace CORS origins with settings.ALLOWED_ORIGINS
   - Replace any other hardcoded values

6. [ ] Update `mcp/tools/viewer_tools.py`
   - Import settings
   - Replace OHIF base URL with settings.OHIF_BASE_URL
   - Replace DICOMweb endpoint with settings.DICOMWEB_ENDPOINT

7. [ ] Update any other backend files identified in step 1
   - Check all route files
   - Check service files

#### Phase 3: Frontend Updates
8. [ ] Update frontend environment usage
   - Check all uses of import.meta.env
   - Ensure proper fallbacks
   - Document required VITE_ prefixed variables

9. [ ] Create `.env.example` for frontend
   - Include all VITE_ variables
   - Add comments explaining each

#### Phase 4: Configuration Files
10. [ ] Create backend `.env.example`
    - Include all backend environment variables
    - Add detailed comments
    - Include both production and devnet examples

11. [ ] Update `docker-compose.yml`
    - Add env_file directive
    - Ensure environment variables are passed to containers

12. [ ] Create `docker-compose.dev.yml` 
    - Override ports for devnet
    - Override container names (add -dev suffix)
    - Override environment variables

#### Phase 5: Testing and Documentation
13. [ ] Test with production values
    - Create `.env` with current production values
    - Verify nothing breaks
    - Test all endpoints

14. [ ] Update documentation
    - Update README.md with env setup instructions
    - Update this claude.md file
    - Create `DEVNET_SETUP.md` guide

15. [ ] Create devnet setup checklist
    - DNS records to create
    - Nginx configs needed
    - Environment files to configure

### Output Documents to Create:
- `hardcoded_urls_audit.md` - All hardcoded values found
- `env_var_mapping.md` - Mapping of hardcoded values to env vars
- `ports_and_services.md` - Port assignments for prod/dev
- `.env.example` - Backend environment template
- `frontend/.env.example` - Frontend environment template
- `docker-compose.dev.yml` - Devnet Docker configuration
- `DEVNET_SETUP.md` - Complete devnet setup guide

## Planned Development Goals (Priority Order)

### 1. Devnet Setup
- **Goal**: Isolated development environment
- **Blocked by**: Environment variable refactor (hardcoded URLs)
- **Tasks**:
  - Create dev.*.casewisemd.org DNS records
  - Configure separate Docker environments
  - Set up `.env.dev` files
  - Separate nginx configurations
  - Use different ports to avoid conflicts

### 2. MCP Case Loader Refactor
- **Current**: Hardcoded case001, basic filesystem scanning
- **Goal**: Dynamic, cached, modular case loading
- **New structure**: `/mcp/case_loader/`
- **Features**:
  - Pluggable loader classes (demo_cases, TCGA, custom)
  - In-memory caching
  - Dynamic file watching
  - Case filtering by subspecialty/difficulty

### 3. Core MCP Refactor  
- **Current**: Monolithic services (ai_grading.py has 923 lines)
- **Goal**: Modular components for grading, questions, feedback
- **New structure**: 
  - `/mcp/grading/` - Rubric and AI grading modules
  - `/mcp/questions/` - Question generation and prompts
  - `/mcp/core/` - Shared interfaces and base classes

## Key Files & Locations

### Configuration
- **Docker**: `docker-compose.yml`
- **Nginx**: On VPS at `/etc/nginx/sites-available/`
- **Environment**: `.env` files (use `.env.dev` for devnet)
- **Orthanc Config**: `/docker/orthanc-config.json`

### Nginx Configuration (VPS Only)
- **Location**: `/etc/nginx/sites-available/` and `/etc/nginx/sites-enabled/`
- **Current sites**: casewisemd.org (all subdomains)
- **SSL Certificates**: Managed by Certbot, located at `/etc/letsencrypt/`
- **Upstream blocks**: Point to Docker containers on localhost ports
- **To reload**: `sudo nginx -t && sudo systemctl reload nginx`

#### Nginx Devnet Setup Tasks:
1. Copy existing config files with dev- prefix
2. Update server_name to dev- domains
3. Update upstream ports to devnet Docker containers
4. Create SSL certificates: `sudo certbot --nginx -d dev-app.casewisemd.org -d dev-api.casewisemd.org -d dev-viewer.casewisemd.org -d dev-dicom.casewisemd.org`
5. Enable sites: `sudo ln -s /etc/nginx/sites-available/dev-* /etc/nginx/sites-enabled/`
6. Test and reload: `sudo nginx -t && sudo systemctl reload nginx`

#### Production Nginx Ports:
- MCP API: localhost:8000
- Orthanc: localhost:8042
- Frontend: /var/www/casewise/dist

#### Devnet Nginx Ports (proposed):
- MCP API: localhost:8001
- Orthanc: localhost:8043
- Frontend: /var/www/casewise-dev/dist

### Critical Code
- **AI Grading**: `/mcp/services/ai_grading.py`
- **Diagnostic Flow**: `/mcp/routes/diagnostic.py`
- **Grade Route**: `/mcp/routes/grade.py`
- **Frontend Workflow**: `/frontend/src/DiagnosticWorkflow.tsx`
- **Main App**: `/frontend/src/App.tsx`

### Data Files
- **Current Case**: TCGA-09-0364 (ovarian cancer)
- **Rubric**: `/rubrics/TCGA-09-0364_rubric_detailed.json`
- **Case Reports**: `/source-documents/excel-reports/TCGA-case-reports.csv`

## Common Tasks

### Local Development
```bash
# Backend
cd mcp
python main.py

# Frontend  
cd frontend
npm run dev

# Docker (all services)
docker-compose up -d

# View logs
docker logs mcp
docker logs casewise_orthanc
```

### Deployment
```bash
# Frontend deployment
./deploy-frontend.sh

# Backend deployment (via Docker)
docker-compose down
docker-compose build
docker-compose up -d

# Check deployment
curl https://api.casewisemd.org/health
```

### Check Services
```bash
# All Docker services
docker ps

# API health
curl https://api.casewisemd.org/health

# Test diagnostic endpoint
curl https://api.casewisemd.org/api/v1/diagnostic-session?case_id=case001
```

## Architecture Patterns

### API Endpoints
- **Base URL**: `/api/v1/`
- **Pattern**: RESTful with JSON responses
- **Main Routes**:
  - `/diagnostic-*` - Case delivery and answers
  - `/grade*` - AI grading and feedback
  - `/config*` - Case configuration
  - `/viewer-url` - OHIF viewer URLs
  - `/cases*` - Case listing and metadata

### Case Structure
- **Case ID format**: `case001`, `case002`, etc.
- **Required files per case**:
  - Case metadata (JSON)
  - DICOM images
  - Grading rubric
  - Question set
  - Clinical reports

### Grading Flow
1. Student views DICOM images in OHIF viewer
2. Answers 7 diagnostic questions (ABR categories)
3. AI grades against rubric using GPT-4o
4. System generates follow-up questions for weak areas (<70%)
5. Student answers follow-ups for bonus points
6. Final assessment with improvement tracking

### ABR Grading Categories
1. **Image Interpretation** (35%)
2. **Differential Diagnosis** (25%)
3. **Clinical Correlation** (15%)
4. **Management Recommendations** (10%)
5. **Communication & Organization** (10%)
6. **Professional Judgment** (5%)
7. **Safety Considerations** (5% bonus)

## Current Limitations
- Single case (TCGA-09-0364) hardcoded in many places
- No user authentication system
- No database (filesystem only)
- Manual case creation process
- No automated tests
- Basic error handling

## Testing Approach
- **Current**: Manual testing via frontend
- **API Testing**: curl commands or Postman
- **Planned**: pytest for backend, Jest for frontend
- **No CI/CD**: Manual deployment only

## Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-...        # For AI grading

# Frontend
VITE_API_URL=https://api.casewisemd.org
VITE_VIEWER_URL=https://viewer.casewisemd.org

# Planned for devnet
ENVIRONMENT=dev               # or "production"
```

## Troubleshooting

### OHIF Viewer Issues
```bash
# Check viewer config
cat /var/www/viewer/app-config.js

# Should point to local Orthanc, not CloudFront
# dataSources should use: api.casewisemd.org/orthanc/dicom-web
```

### AI Grading Failures
- Check OpenAI API key: `echo $OPENAI_API_KEY`
- Check API logs: `docker logs mcp`
- Fallback grading activates automatically if AI fails
- Fallback uses word count and keyword matching

### Docker Issues
```bash
# View logs
docker logs mcp --tail 50

# Restart services
docker-compose restart

# Full reset
docker-compose down
docker-compose up -d

# Check port usage
sudo lsof -i :8000  # MCP API
sudo lsof -i :8042  # Orthanc
```

### CORS Issues
- Check nginx configuration includes CORS headers
- Frontend must use configured VITE_API_URL
- API allows origins: localhost:5173, casewisemd.org domains

## Next Architectural Decisions
1. **Database**: PostgreSQL likely (user accounts, case metadata)
2. **Authentication**: JWT tokens with FastAPI security
3. **Case Storage**: S3 for DICOM files vs local filesystem
4. **Test Framework**: pytest + Jest
5. **CI/CD**: GitHub Actions for automated deployment
6. **Monitoring**: Add application metrics and logging

## Memory Bank Reference
Check these files for detailed context:
- `memory-bank/activeContext.md` - Current development state
- `memory-bank/systemPatterns.md` - Architecture decisions  
- `memory-bank/techContext.md` - Technology stack details
- `memory-bank/progress.md` - Feature completion tracking
- `memory-bank/productContext.md` - Educational goals
- `memory-bank/projectbrief.md` - High-level overview

## Important Notes
- **Production is LIVE** - Be careful with changes
- **Real users** - Radiology residents using the platform
- **AI costs** - Each GPT-4o call costs money
- **Medical accuracy** - Critical for educational value
- **Performance** - DICOM files are large, optimize carefully

## Working with Cursor AI Editor
- User codes with Cursor, which needs clear, specific tasks
- Break down complex work into discrete, manageable steps
- Provide clear guidance on what to change and where
- Don't be overly prescriptive - Cursor can handle implementation details

### Good Task Example:
"In mcp/main.py, replace the hardcoded CORS origins list with environment variables. The current hardcoded list includes casewisemd.org domains."

### Bad Task Example:
"Fix CORS" or "Update all hardcoded values in the entire codebase"

## Contact & Resources
- **Main domain**: casewisemd.org
- **VPS IP**: 143.244.154.89
- **SSH**: Standard port 22
- **Memory bank**: Always check for latest project context
- **GitHub**: Code repository (private)

## Quick Command Reference
```bash
# SSH to VPS
ssh user@143.244.154.89

# Navigate to project
cd /path/to/casewise-vps

# Check all services
docker ps
systemctl status nginx

# View API logs
docker logs mcp --follow

# Test endpoints
curl https://api.casewisemd.org/health
curl https://api.casewisemd.org/api/v1/config/available-cases
```

---
*Last updated: Check memory-bank/activeContext.md for latest status*