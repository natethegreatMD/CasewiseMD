# Casewise VPS - Project Overview & Future Directions

## Working Context
- **Ask for location**: Always ask "Are we working locally or on the VPS?" at session start
- **Cursor Integration**: User codes with Cursor (AI editor) - provide specific, detailed tasks
- **Task Style**: Break down work into small, explicit steps like for a junior developer
- **VPS vs Local**: 
  - VPS (143.244.154.89): nginx, docker, production/devnet deployments
  - Local: development, code editing with Cursor

## Project Overview
- **What**: AI-powered medical education platform for radiology residents
- **Status**: Production system with 1 case (TCGA-09-0364), live with real users
- **Key Achievement**: Real AI grading with GPT-4o (replaced fake scoring)
- **Architecture**: FastAPI backend (MCP pattern), React frontend, OHIF viewer, Orthanc DICOM
- **Business Model**: Educational platform for medical residency programs

## Current URLs

### Production (LIVE)
- Frontend: https://app.casewisemd.org
- API: https://api.casewisemd.org
- Viewer: https://viewer.casewisemd.org
- DICOM: https://dicom.casewisemd.org

### Development (LIVE - Deployed 2025-07-15)
- Frontend: https://dev-app.casewisemd.org
- API: https://dev-api.casewisemd.org
- Viewer: https://dev-viewer.casewisemd.org
- DICOM: https://dev-dicom.casewisemd.org

## Devnet Architecture (DEPLOYED!)
- **Same VPS**: Both prod and devnet run on 143.244.154.89 ✅
- **Different Ports**: Prod uses 8000/8042, devnet uses 8001/8043 ✅
- **Same Nginx**: Single nginx config handles both environments ✅
- **Simultaneous**: Both environments run at the same time ✅
- **No Switching**: Access prod at app.casewisemd.org, dev at dev-app.casewisemd.org ✅
- **Containers**: mcp/orthanc (prod), mcp-dev/orthanc-dev (dev) ✅

## System Architecture

### Directory Structure
```
/root/casewise-vps/ (on VPS)
├── frontend/           # React 19 + TypeScript + Vite
├── mcp/               # Backend API with routes, services, tools
├── memory-bank/       # Project documentation and context
├── rubrics/           # Grading criteria JSON files
├── source-documents/  # Medical case data
├── case generator/    # Tools for creating new cases
├── docker/            # Docker configuration files
├── scripts/           # Deployment and utility scripts
└── docs/             # Documentation
```

### Critical Code Locations

#### Legacy V1 Architecture (Preserved for Compatibility)
- **AI Grading**: `/mcp/services/ai_grading.py` (923 lines - legacy)
- **Diagnostic Flow**: `/mcp/routes/diagnostic.py` (V1 routes)
- **Grade Route**: `/mcp/routes/grade.py`
- **Frontend Workflow**: `/frontend/src/DiagnosticWorkflow.tsx`
- **Viewer Tools**: `/mcp/tools/viewer_tools.py`
- **Settings**: `/mcp/config/settings.py` (centralized config)

#### New MCP Architecture (Production Ready - 2025-07-17)
- **Orchestrator**: `/mcp/orchestrator/session_orchestrator.py` (main coordinator)
- **Core Models**: `/mcp/core/models.py` (Pydantic data models)
- **Agent Interfaces**: `/mcp/core/interfaces.py` (standardized contracts)
- **Session Management**: `/mcp/session/models.py` (complete lifecycle)
- **V2 Routes**: `/mcp/routes/diagnostic_v2.py` (orchestrator-based APIs)
- **Grading Agent**: `/mcp/agents/grading/grading_agent_v2.py` (modular AI grading)
- **Question Agent**: `/mcp/agents/questions/question_agent.py` (dynamic questions)
- **Case Agent**: `/mcp/agents/case/case_agent.py` (case management)

## Completed Development Goals

### 1. Devnet Setup ✅ (FULLY DEPLOYED - 2025-07-15)
- **Goal**: Isolated development environment
- **Status**: COMPLETE - Both environments running simultaneously on VPS
- **Deployed**: All dev-* domains live with SSL certificates

### 2. MCP Backend Refactor ✅ (COMPLETED & TESTED - 2025-07-17)
- **Goal**: Transform monolithic backend into agent-based orchestrator architecture
- **Status**: COMPLETE AND PRODUCTION READY
- **Testing**: 6/6 execution tests passed (100% success rate)
- **Benefits**: Modular, testable, extensible, backward compatible
- **Documentation**: Complete technical guides and test reports available

## Planned Development Goals (Priority Order)

#### Implementation Details (What Was Done)

**Environment Variable Refactor (Completed):**
The entire codebase has been refactored to use environment variables instead of hardcoded URLs.

**Devnet Deployment (Completed):**
- Added nginx configurations for all dev-* domains to existing config
- Obtained SSL certificates via certbot for all dev domains
- Built frontend with development environment variables
- Deployed containers: mcp-dev (port 8001), orthanc-dev (port 8043)
- Fixed deployment scripts (Windows line endings → Unix)
- Created /var/www/frontend-dev for development frontend files

**Backend Environment Variables:**
- `ENVIRONMENT`: production/development
- `MCP_PORT`: API port (8000/8001)
- `ORTHANC_PORT`: DICOM port (8042/8043)
- `ALLOWED_ORIGINS`: CORS allowed origins
- `API_BASE_URL`: Backend API endpoint
- `OHIF_BASE_URL`: OHIF viewer base URL
- `DICOMWEB_ENDPOINT`: DICOMweb endpoint URL
- `ORTHANC_URL`: Internal Orthanc URL
- `OPENAI_API_KEY`: Required for AI grading

**Frontend Environment Variables (VITE_ prefix required):**
- `VITE_API_URL`: Backend API endpoint
- `VITE_VIEWER_URL`: OHIF viewer URL
- `VITE_APP_URL`: Frontend application URL
- `VITE_DICOM_URL`: DICOM server URL
- `VITE_ENVIRONMENT`: Environment name

**Docker Environment Variables:**
- `COMPOSE_PROJECT_NAME`: Docker project name
- `DOCKER_MCP_PORT`: External MCP port
- `DOCKER_ORTHANC_PORT`: External Orthanc port
- `DOCKER_MCP_CONTAINER`: MCP container name
- `DOCKER_ORTHANC_CONTAINER`: Orthanc container name

**Created Files:**
- `/mcp/config/settings.py`: Centralized configuration
- `.env` / `.env.dev`: Backend environment files
- `frontend/.env` / `frontend/.env.dev`: Frontend build variables
- `docker-compose.dev.yml`: Development Docker configuration
- `scripts/deploy-prod.sh`: Production deployment
- `scripts/deploy-dev.sh`: Development deployment

### 2. MCP Case Loader Refactor (Next Priority)
- **Current**: Hardcoded case001, basic filesystem scanning
- **Goal**: Dynamic, cached, modular case loading
- **New structure**: `/mcp/case_loader/`
- **Features**:
  - Pluggable loader classes (demo_cases, TCGA, custom)
  - In-memory caching with TTL
  - Dynamic file watching for development
  - Case filtering by subspecialty/difficulty
  - Metadata indexing for fast queries
- **Why Important**: Enables multi-case support, essential for platform growth

### 3. Frontend Migration to V2 APIs
- **Current**: Frontend uses V1 routes (diagnostic.py)
- **Goal**: Migrate to V2 orchestrator-based routes
- **Benefits**: Real-time session state, enhanced progress tracking, better error handling
- **Status**: V2 routes ready, frontend migration needed

### 4. Additional MCP Agents
- **Teaching Agent**: Educational content delivery and teaching moments
- **Reference Agent**: Medical reference lookup and integration
- **Status**: Framework complete, ready for implementation

### 5. MCP Case Loader Enhancement
- **Current**: Basic case loading via CaseAgent
- **Goal**: Multi-source dynamic case loading
- **Features**: Pluggable loaders, advanced caching, case filtering
- **Status**: Ready for implementation

### 6. Database Integration
- **Technology**: PostgreSQL with SQLAlchemy
- **Schema**:
  - Users table (authentication, profiles)
  - Cases table (metadata, not DICOM files)
  - Sessions table (student attempts)
  - Grades table (AI grading results)
  - Analytics table (performance tracking)
- **Migration strategy**: Start with hybrid (DB + filesystem)

### 7. Authentication System
- **Technology**: JWT tokens with FastAPI security
- **Features**:
  - Email/password login
  - Role-based access (student, instructor, admin)
  - Session management
  - API key support for programmatic access

### 8. Multi-Case Support
- **Goal**: Expand beyond single TCGA case
- **Sources**:
  - TCGA collection (public dataset)
  - Radiopaedia cases
  - Custom institutional cases
- **Challenges**:
  - DICOM anonymization
  - Rubric creation for each case
  - Storage management

### 9. Analytics Dashboard
- **For Students**:
  - Performance over time
  - Weak areas identification
  - Progress tracking
- **For Instructors**:
  - Class performance metrics
  - Individual student progress
  - Question difficulty analysis

## Architecture Patterns

### API Design
- **V1 Base URL**: `/api/v1/` (legacy routes - diagnostic.py)
- **V2 Base URL**: `/api/v2/diagnostic/` (orchestrator-based routes)
- **Pattern**: RESTful with JSON responses
- **Authentication**: Bearer tokens (future)
- **Versioning**: URL-based with backward compatibility

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

## Technical Debt & Limitations

### Current Limitations
- Single case (TCGA-09-0364) hardcoded in many places
- No user authentication system
- No database (filesystem only)
- Manual case creation process
- Limited monitoring/logging
- Frontend uses V1 APIs (V2 available but not integrated)

### Technical Debt Items (Reduced after MCP Refactor)
1. **Hardcoded case references** throughout codebase (partially addressed by CaseAgent)
2. **Frontend migration** - need to switch from V1 to V2 APIs
3. **No input validation** framework
4. **Frontend state management** - consider Redux/Zustand
5. **No API documentation** - need OpenAPI/Swagger
6. **No rate limiting** on API endpoints

### Technical Debt Resolved ✅
1. **Monolithic backend** - ✅ Refactored to agent-based architecture
2. **Tightly coupled services** - ✅ Modular agents with clean interfaces
3. **Limited error handling** - ✅ Multi-level error strategy implemented
4. **No automated tests** - ✅ Comprehensive test suite created
5. **Basic dependency management** - ✅ Proper requirements.txt with pydantic

## Infrastructure Decisions

### Next Architectural Decisions
1. **Database**: PostgreSQL (user accounts, case metadata)
2. **Cache**: Redis for session management, API caching
3. **Storage**: S3 for DICOM files vs local filesystem
4. **CDN**: CloudFront for static assets and DICOM
5. **Monitoring**: Datadog or Prometheus + Grafana
6. **CI/CD**: GitHub Actions for automated deployment
7. **Testing**: pytest + Jest + Playwright

### Scaling Considerations
- **Current**: Single VPS handles everything
- **Future**: 
  - Separate DICOM storage (S3 + CloudFront)
  - Database on managed service (RDS)
  - API on container service (ECS/K8s)
  - Frontend on CDN
  - Load balancer for multiple API instances



## Important Business Context
- **Users**: Radiology residents in training programs
- **Value Prop**: AI-powered feedback for diagnostic accuracy
- **Differentiator**: Real medical cases with expert-validated rubrics
- **Revenue Model**: SaaS for residency programs
- **Competition**: Traditional case review sessions
- **Compliance**: HIPAA considerations for future

## Contact & Resources
- **Main domain**: casewisemd.org
- **VPS IP**: 143.244.154.89
- **SSH**: Standard port 22
- **GitHub**: Private repository
- **OpenAI**: GPT-4o for grading

## Recent Accomplishments (2025-07-15)
- ✅ Completed environment variable refactor across entire codebase
- ✅ Successfully deployed devnet environment on VPS
- ✅ Both prod and dev environments running simultaneously
- ✅ All dev-* domains have SSL certificates and are live
- ✅ Fixed deployment script issues (Windows → Unix line endings)

---
*Last updated: 2025-07-15 - Devnet deployment complete! Next priority: MCP Case Loader Refactor*