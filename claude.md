# Casewise VPS - AI Assistant Guide

## Quick Start
- **Project**: AI-powered medical education platform for radiology residents
- **Status**: Production system with 1 case, planning major refactors
- **Key Achievement**: Real AI grading with GPT-4o (replaced fake scoring)
- **URLs**: 
  - Frontend: https://app.casewisemd.org
  - API: https://api.casewisemd.org
  - Viewer: https://viewer.casewisemd.org
  - DICOM: https://dicom.casewisemd.org

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

## Active Development Goals (Priority Order)

### 1. Devnet Setup
- **Goal**: Isolated development environment
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