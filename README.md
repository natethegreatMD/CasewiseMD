# Casewise: AI-Powered Radiology Education Platform

**Casewise** is an advanced AI-powered oral board simulator designed specifically for radiology training and assessment. It combines professional DICOM image viewing with intelligent AI agents to create realistic, interactive diagnostic scenarios that mirror real-world radiology practice and oral board examinations.

## 🎯 Vision

Transform radiology education by providing an immersive, interactive platform where residents and practicing radiologists can:
- Engage with real medical imaging through a professional DICOM viewer
- Receive AI-powered feedback on diagnostic reasoning
- Practice case presentation skills in a structured oral board format
- Track progress with detailed performance analytics

## 🏗️ Project Structure

### **📁 Core Directories**

#### **`frontend/`** - React User Interface
Modern, responsive React application built with Vite for fast development and optimized production builds.

**Contents**:
- `src/` - React components and application logic
- `public/` - Static assets and HTML template
- `dist/` - Production build output (generated)
- `package.json` - Frontend dependencies and build scripts
- `vite.config.ts` - Vite build configuration

**Status**: ✅ **Built** - Production-ready build available, ready for deployment

#### **`mcp/`** - Multi-Agent Backend
FastAPI backend implementing Multi-Agent Communication Protocol for AI-powered assessment.

**Contents**:
- `main.py` - FastAPI application with CORS and routing
- `routes/` - API endpoints for different AI agents
  - `diagnostic.py` - Interactive case session management
  - `grade.py` - Assessment and feedback generation
  - `config.py` - Case configuration and metadata
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration for deployment

**Status**: 🚧 **In Development** - Scaffolded with dummy data, ready for production deployment

#### **`viewer-deploy/`** - OHIF Viewer Deployment
Production deployment configuration for the OHIF medical imaging viewer.

**Contents**:
- OHIF viewer build files
- NGINX configuration for static serving
- SSL certificate management

**Status**: ✅ **Live** - Operational at https://viewer.casewisemd.org

#### **`memory-bank/`** - Development Context Documentation
**🔥 CRITICAL for Development** - Essential documentation that maintains project context across development sessions.

**Contents**:
- `activeContext.md` - Current development status and live services
- `productContext.md` - Product vision and user requirements
- `projectbrief.md` - 4-phase development plan overview
- `progress.md` - Chronological development timeline
- `systemPatterns.md` - Architecture patterns and design decisions
- `techContext.md` - Technology stack and implementation details

**Purpose**: Enables context-aware development by preserving architectural decisions, progress tracking, and system understanding across development sessions.

#### **`demo_cases/`** - Medical Case Data
Sample medical imaging cases and associated metadata for development and testing.

**Contents**:
- DICOM imaging files (`.dcm`)
- Case metadata and clinical context
- Sample rubrics and assessment criteria

**Status**: Available for development; will be replaced by dynamic case management in Phase 4

#### **`source-documents/`** - Project Documentation
Original project specifications, requirements documents, and reference materials.

**Contents**:
- Project requirements and specifications
- Medical education standards and guidelines
- Technical reference documentation

### **📄 Configuration Files**

- `docker-compose.yml` - Production deployment orchestration for MCP backend
- `.env` - Environment variables and configuration
- `requirements.txt` - Python dependencies for legacy components
- `pyproject.toml` - Python project configuration

## 🚀 Development Phases

### **Phase 1: OHIF Viewer Foundation** ✅ **COMPLETED**
*Establish professional medical imaging capability*

**Goal**: Deploy industry-standard DICOM viewer as foundation
- ✅ OHIF viewer configured and deployed
- ✅ NGINX reverse proxy with SSL termination
- ✅ Live at https://viewer.casewisemd.org
- ✅ DNS and certificate automation via Certbot

**Achievement**: Professional medical imaging viewing capability operational

---

### **Phase 2: React Frontend** ✅ **COMPLETED**
*Build modern user interface for case interaction*

**Goal**: Create responsive, component-based frontend
- ✅ React 19 + Vite 6 + TypeScript application
- ✅ Component architecture for scalability
- ✅ OHIF viewer integration points prepared
- ✅ Production build system (505ms build time)
- ✅ Clean dist/ output ready for deployment

**Achievement**: Production-ready frontend awaiting deployment to casewisemd.org

---

### **Phase 3: MCP Backend** 🚧 **IN PROGRESS**
*Implement Multi-Agent AI assessment system*

**Goal**: Create modular AI backend with specialized agents
- ✅ FastAPI application with MCP architecture
- ✅ Three specialized AI agents:
  - **Diagnostic Agent**: Session management and case flow
  - **Grading Agent**: Assessment scoring and feedback
  - **Config Agent**: Case metadata and rubric management
- ✅ Docker containerization with health monitoring
- ✅ All endpoints operational with structured dummy data
- 🎯 **Next**: Production deployment to api.casewisemd.org

**Current API Endpoints**:
```
GET  /api/v1/diagnostic-session      → Start interactive case session
POST /api/v1/diagnostic-answer       → Submit case responses
POST /api/v1/grade                   → Grade case submissions
GET  /api/v1/grade/{id}             → Retrieve grading results
GET  /api/v1/config?case_id=X       → Get case configuration
GET  /api/v1/config/available-cases → List available cases
```

---

### **Phase 4: DICOM Server + AI Integration** 📋 **PLANNED**
*Complete ecosystem with medical imaging and intelligent assessment*

**Goal**: Full AI-powered educational platform
- **DICOM Server**: Medical imaging infrastructure at dicom.casewisemd.org
- **AI Integration**: OpenAI GPT-4 powered assessment replacing dummy data
- **Case Management**: Dynamic case loading and DICOM association
- **User System**: Authentication, progress tracking, and analytics
- **Database**: Persistent storage for sessions and user data

**Target Architecture**:
```
Frontend (React)     → https://casewisemd.org
MCP Backend (FastAPI) → https://api.casewisemd.org  
OHIF Viewer         → https://viewer.casewisemd.org
DICOM Server        → https://dicom.casewisemd.org
```

## 🛠️ Development Setup

### **Prerequisites**
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- Docker (for containerized deployment)

### **Frontend Development**
```bash
cd frontend/
npm install
npm run dev          # Development server with hot reload
npm run build        # Production build
```

### **MCP Backend Development**
```bash
cd mcp/
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### **Docker Development**
```bash
# Build and run MCP backend
docker-compose up --build

# View logs
docker-compose logs -f mcp
```

## 🚀 Deployment Guide

### **Frontend Deployment**
1. **Build Production Assets**:
   ```bash
   cd frontend/
   npm run build
   ```

2. **Deploy to Web Server**:
   ```bash
   # Copy dist/ contents to web server
   rsync -av dist/ user@server:/var/www/casewise/frontend/
   ```

3. **Configure NGINX**:
   ```nginx
   server {
       server_name casewisemd.org;
       root /var/www/casewise/frontend/dist;
       try_files $uri $uri/ /index.html;
   }
   ```

### **MCP Backend Deployment**
1. **Deploy via Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Configure NGINX Reverse Proxy**:
   ```nginx
   server {
       server_name api.casewisemd.org;
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Set up SSL Certificate**:
   ```bash
   certbot --nginx -d api.casewisemd.org
   ```

### **Health Monitoring**
```bash
# Check backend health
curl https://api.casewisemd.org/health

# Monitor container status
docker-compose ps
```

## 🧠 Memory Bank System

### **Critical for Development Context**

The `memory-bank/` folder is **essential** for maintaining development context across sessions. It contains comprehensive documentation that enables:

- **Context Continuity**: Understand current project state and decisions
- **Architecture Awareness**: Grasp system design patterns and rationale
- **Progress Tracking**: View chronological development timeline
- **Technology Context**: Understand stack decisions and configurations

### **Development Workflow**
1. **Start each session** by reading relevant memory bank files
2. **Update documentation** when making architectural changes
3. **Record progress** in chronological development log
4. **Maintain context** for future development sessions

**For Cursor AI**: The memory bank enables context-aware development by providing complete system understanding across conversation boundaries.

## 📊 Current Status

### **✅ Operational Services**
- **OHIF Viewer**: Live at https://viewer.casewisemd.org
- **Frontend Build**: Production-ready dist/ folder
- **MCP Backend**: Local development server functional

### **🚧 In Progress**
- **MCP Backend**: Production deployment to api.casewisemd.org
- **Frontend Integration**: API connection and testing

### **📋 Planned**
- **DICOM Server**: Medical imaging infrastructure
- **AI Integration**: GPT-4 powered assessment
- **User System**: Authentication and progress tracking

## 🔗 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   MCP Backend   │    │   OHIF Viewer   │
│  (React/Vite)   │    │   (FastAPI)     │    │   (Medical)     │
│                 │◄──►│                 │    │                 │
│ casewisemd.org  │    │ api.casewise    │    │ viewer.casewise │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  DICOM Server   │
                    │   (DICOMweb)    │
                    │                 │
                    │ dicom.casewise  │
                    └─────────────────┘
```

## 🤝 Contributing

### **Development Process**
1. Review memory bank documentation for context
2. Follow phase-based development approach
3. Update documentation with architectural changes
4. Test thoroughly before production deployment

### **Code Quality**
- TypeScript for type safety
- ESLint for code quality
- Docker for consistent environments
- Comprehensive testing before deployment

## 📞 Support

For development questions or deployment issues:
1. Check memory bank documentation for context
2. Review phase-specific requirements
3. Test in development environment first
4. Document any architectural changes

---

# Casewise: AI-Powered Radiology Education Platform

**Casewise** is an advanced AI-powered oral board simulator designed specifically for radiology training and assessment. It combines professional DICOM image viewing with intelligent AI agents to create realistic, interactive diagnostic scenarios that mirror real-world radiology practice and oral board examinations.

## 🎯 Vision

Transform radiology education by providing an immersive, interactive platform where residents and practicing radiologists can:
- Engage with real medical imaging through a professional DICOM viewer
- Receive AI-powered feedback on diagnostic reasoning
- Practice case presentation skills in a structured oral board format
- Track progress with detailed performance analytics

## 🏗️ Project Structure

### **📁 Core Directories**

#### **`frontend/`** - React User Interface
Modern, responsive React application built with Vite for fast development and optimized production builds.

**Contents**:
- `src/` - React components and application logic
- `public/` - Static assets and HTML template
- `dist/` - Production build output (generated)
- `package.json` - Frontend dependencies and build scripts
- `vite.config.ts` - Vite build configuration

**Status**: ✅ **Built** - Production-ready build available, ready for deployment

#### **`mcp/`** - Multi-Agent Backend
FastAPI backend implementing Multi-Agent Communication Protocol for AI-powered assessment.

**Contents**:
- `main.py` - FastAPI application with CORS and routing
- `routes/` - API endpoints for different AI agents
  - `diagnostic.py` - Interactive case session management
  - `grade.py` - Assessment and feedback generation
  - `config.py` - Case configuration and metadata
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration for deployment

**Status**: 🚧 **In Development** - Scaffolded with dummy data, ready for production deployment

#### **`viewer-deploy/`** - OHIF Viewer Deployment
Production deployment configuration for the OHIF medical imaging viewer.

**Contents**:
- OHIF viewer build files
- NGINX configuration for static serving
- SSL certificate management

**Status**: ✅ **Live** - Operational at https://viewer.casewisemd.org

#### **`memory-bank/`** - Development Context Documentation
**🔥 CRITICAL for Development** - Essential documentation that maintains project context across development sessions.

**Contents**:
- `activeContext.md` - Current development status and live services
- `productContext.md` - Product vision and user requirements
- `projectbrief.md` - 4-phase development plan overview
- `progress.md` - Chronological development timeline
- `systemPatterns.md` - Architecture patterns and design decisions
- `techContext.md` - Technology stack and implementation details

**Purpose**: Enables context-aware development by preserving architectural decisions, progress tracking, and system understanding across development sessions.

#### **`demo_cases/`** - Medical Case Data
Sample medical imaging cases and associated metadata for development and testing.

**Contents**:
- DICOM imaging files (`.dcm`)
- Case metadata and clinical context
- Sample rubrics and assessment criteria

**Status**: Available for development; will be replaced by dynamic case management in Phase 4

#### **`source-documents/`** - Project Documentation
Original project specifications, requirements documents, and reference materials.

**Contents**:
- Project requirements and specifications
- Medical education standards and guidelines
- Technical reference documentation

### **📄 Configuration Files**

- `docker-compose.yml` - Production deployment orchestration for MCP backend
- `.env` - Environment variables and configuration
- `requirements.txt` - Python dependencies for legacy components
- `pyproject.toml` - Python project configuration

## 🚀 Development Phases

### **Phase 1: OHIF Viewer Foundation** ✅ **COMPLETED**
*Establish professional medical imaging capability*

**Goal**: Deploy industry-standard DICOM viewer as foundation
- ✅ OHIF viewer configured and deployed
- ✅ NGINX reverse proxy with SSL termination
- ✅ Live at https://viewer.casewisemd.org
- ✅ DNS and certificate automation via Certbot

**Achievement**: Professional medical imaging viewing capability operational

---

### **Phase 2: React Frontend** ✅ **COMPLETED**
*Build modern user interface for case interaction*

**Goal**: Create responsive, component-based frontend
- ✅ React 19 + Vite 6 + TypeScript application
- ✅ Component architecture for scalability
- ✅ OHIF viewer integration points prepared
- ✅ Production build system (505ms build time)
- ✅ Clean dist/ output ready for deployment

**Achievement**: Production-ready frontend awaiting deployment to casewisemd.org

---

### **Phase 3: MCP Backend** 🚧 **IN PROGRESS**
*Implement Multi-Agent AI assessment system*

**Goal**: Create modular AI backend with specialized agents
- ✅ FastAPI application with MCP architecture
- ✅ Three specialized AI agents:
  - **Diagnostic Agent**: Session management and case flow
  - **Grading Agent**: Assessment scoring and feedback
  - **Config Agent**: Case metadata and rubric management
- ✅ Docker containerization with health monitoring
- ✅ All endpoints operational with structured dummy data
- 🎯 **Next**: Production deployment to api.casewisemd.org

**Current API Endpoints**:
```
GET  /api/v1/diagnostic-session      → Start interactive case session
POST /api/v1/diagnostic-answer       → Submit case responses
POST /api/v1/grade                   → Grade case submissions
GET  /api/v1/grade/{id}             → Retrieve grading results
GET  /api/v1/config?case_id=X       → Get case configuration
GET  /api/v1/config/available-cases → List available cases
```

---

### **Phase 4: DICOM Server + AI Integration** 📋 **PLANNED**
*Complete ecosystem with medical imaging and intelligent assessment*

**Goal**: Full AI-powered educational platform
- **DICOM Server**: Medical imaging infrastructure at dicom.casewisemd.org
- **AI Integration**: OpenAI GPT-4 powered assessment replacing dummy data
- **Case Management**: Dynamic case loading and DICOM association
- **User System**: Authentication, progress tracking, and analytics
- **Database**: Persistent storage for sessions and user data

**Target Architecture**:
```
Frontend (React)     → https://casewisemd.org
MCP Backend (FastAPI) → https://api.casewisemd.org  
OHIF Viewer         → https://viewer.casewisemd.org
DICOM Server        → https://dicom.casewisemd.org
```

## 🛠️ Development Setup

### **Prerequisites**
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- Docker (for containerized deployment)

### **Frontend Development**
```bash
cd frontend/
npm install
npm run dev          # Development server with hot reload
npm run build        # Production build
```

### **MCP Backend Development**
```bash
cd mcp/
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### **Docker Development**
```bash
# Build and run MCP backend
docker-compose up --build

# View logs
docker-compose logs -f mcp
```

## 🚀 Deployment Guide

### **Frontend Deployment**
1. **Build Production Assets**:
   ```bash
   cd frontend/
   npm run build
   ```

2. **Deploy to Web Server**:
   ```bash
   # Copy dist/ contents to web server
   rsync -av dist/ user@server:/var/www/casewise/frontend/
   ```

3. **Configure NGINX**:
   ```nginx
   server {
       server_name casewisemd.org;
       root /var/www/casewise/frontend/dist;
       try_files $uri $uri/ /index.html;
   }
   ```

### **MCP Backend Deployment**
1. **Deploy via Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Configure NGINX Reverse Proxy**:
   ```nginx
   server {
       server_name api.casewisemd.org;
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Set up SSL Certificate**:
   ```bash
   certbot --nginx -d api.casewisemd.org
   ```

### **Health Monitoring**
```bash
# Check backend health
curl https://api.casewisemd.org/health

# Monitor container status
docker-compose ps
```

## 🧠 Memory Bank System

### **Critical for Development Context**

The `memory-bank/` folder is **essential** for maintaining development context across sessions. It contains comprehensive documentation that enables:

- **Context Continuity**: Understand current project state and decisions
- **Architecture Awareness**: Grasp system design patterns and rationale
- **Progress Tracking**: View chronological development timeline
- **Technology Context**: Understand stack decisions and configurations

### **Development Workflow**
1. **Start each session** by reading relevant memory bank files
2. **Update documentation** when making architectural changes
3. **Record progress** in chronological development log
4. **Maintain context** for future development sessions

**For Cursor AI**: The memory bank enables context-aware development by providing complete system understanding across conversation boundaries.

## 📊 Current Status

### **✅ Operational Services**
- **OHIF Viewer**: Live at https://viewer.casewisemd.org
- **Frontend Build**: Production-ready dist/ folder
- **MCP Backend**: Local development server functional

### **🚧 In Progress**
- **MCP Backend**: Production deployment to api.casewisemd.org
- **Frontend Integration**: API connection and testing

### **📋 Planned**
- **DICOM Server**: Medical imaging infrastructure
- **AI Integration**: GPT-4 powered assessment
- **User System**: Authentication and progress tracking

## 🔗 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   MCP Backend   │    │   OHIF Viewer   │
│  (React/Vite)   │    │   (FastAPI)     │    │   (Medical)     │
│                 │◄──►│                 │    │                 │
│ casewisemd.org  │    │ api.casewise    │    │ viewer.casewise │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  DICOM Server   │
                    │   (DICOMweb)    │
                    │                 │
                    │ dicom.casewise  │
                    └─────────────────┘
```

## 🤝 Contributing

### **Development Process**
1. Review memory bank documentation for context
2. Follow phase-based development approach
3. Update documentation with architectural changes
4. Test thoroughly before production deployment

### **Code Quality**
- TypeScript for type safety
- ESLint for code quality
- Docker for consistent environments
- Comprehensive testing before deployment

## 📞 Support

For development questions or deployment issues:
1. Check memory bank documentation for context
2. Review phase-specific requirements
3. Test in development environment first
4. Document any architectural changes

---

**Casewise** represents the future of medical education, combining cutting-edge AI technology with clinical-grade medical imaging to create an immersive, effective learning platform for radiology professionals worldwide. 