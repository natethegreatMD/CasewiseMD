# Tech Context: Casewise

## Technology Stack Overview

### Frontend Technologies
- **React 18.3**: Modern React with hooks and functional components
- **TypeScript**: Type safety and enhanced development experience
- **Vite**: Fast build tool and development server
- **ESLint**: Code quality and consistency enforcement
- **CSS3**: Custom styling with responsive design patterns

### Backend Technologies
- **Python 3.11**: Core backend language
- **FastAPI**: High-performance API framework
- **Uvicorn**: ASGI server for FastAPI applications
- **Pydantic**: Data validation and serialization

### Medical Imaging Technologies
- **OHIF Viewer v3**: Open-source medical imaging platform
- **Cornerstone.js**: JavaScript library for medical imaging
- **DICOM**: Medical imaging standard for data handling
- **TCIA API**: The Cancer Imaging Archive data access

### Infrastructure Technologies
- **Docker**: Containerization for consistent deployment
- **Docker Compose**: Multi-container orchestration
- **Orthanc**: DICOM server for medical image management
- **Nginx**: Reverse proxy and static file serving (planned)

### Development Tools
- **Node.js 18+**: Frontend development environment
- **npm**: Package management for frontend dependencies
- **pip**: Python package management
- **Git**: Version control system

## Detailed Technology Analysis

### Frontend Architecture

#### React Ecosystem
```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "typescript": "^5.5.3"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.4.1",
    "eslint": "^9.9.0"
  }
}
```

**Integration Strategy**: 
- Modern React with functional components and hooks
- TypeScript for type safety and better development experience
- Vite for fast development and optimized builds
- ESLint configuration for consistent code quality

**Technical Decisions**:
- **No State Management Library**: Using React's built-in state management (useState, useContext)
- **Component Architecture**: Functional components with hooks over class components
- **Build Tool**: Vite chosen over Create React App for better performance
- **Styling Strategy**: CSS modules and inline styles over CSS-in-JS libraries

#### OHIF Viewer Integration
```typescript
// Multiple integration strategies being evaluated
interface ViewerIntegration {
  iframe: {
    implementation: "OhifIframeViewer.tsx";
    status: "working";
    limitations: ["postMessage communication", "sandbox restrictions"];
  };
  embedded: {
    implementation: "OhifViewer.tsx";
    status: "in-development";
    benefits: ["direct control", "React lifecycle integration"];
  };
  hosted: {
    implementation: "External deployment";
    status: "working";
    usage: "development and testing";
  };
}
```

**Technical Challenges**:
- **Build Complexity**: OHIF has complex webpack configuration requirements
- **Bundle Size**: Large bundle size impacts load performance
- **Customization**: Limited customization options with iframe approach
- **Communication**: Cross-frame communication complexity

### Backend Architecture

#### Python FastAPI Stack
```python
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.4.2
```

**Architecture Decisions**:
- **FastAPI over Flask**: Chosen for automatic API documentation and type hints
- **Uvicorn ASGI**: High-performance async server
- **Modular Routes**: Separated route logic into domain-specific modules
- **Pydantic Models**: Strong typing for request/response validation

#### Route Organization
```python
# mcp/routes/ structure
├── __init__.py          # Route registration
├── diagnostic.py        # Case presentation and interaction
├── grade.py            # Evaluation and rubric processing
├── config.py           # System configuration endpoints
└── __pycache__/        # Compiled Python bytecode
```

**API Design Patterns**:
- **RESTful Endpoints**: Standard HTTP methods and status codes
- **JSON API**: Consistent JSON request/response format
- **Error Handling**: Structured error responses with proper HTTP status codes
- **Validation**: Input validation using Pydantic models

### Medical Data Technologies

#### DICOM Handling
```python
# DICOM data structure
demo_cases/case001/slices/
├── 1.3.6.1.4.1.14519.5.2.1.7695.4007.115512319570807352125051359179/
├── 1.3.6.1.4.1.14519.5.2.1.7695.4007.290560597213035590678005726868/
└── 1.3.6.1.4.1.14519.5.2.1.7695.4007.335478662210512911160907262491/
```

**Technical Implementation**:
- **File System Storage**: DICOM files stored with UID-based directory structure
- **Metadata Extraction**: JSON metadata for quick access without DICOM parsing
- **Series Organization**: Multi-series studies properly organized
- **Lazy Loading**: DICOM data loaded on demand to optimize memory usage

#### TCIA Data Integration
**Data Source**: The Cancer Imaging Archive (TCIA)
**Case Selection**: TCGA-09-0364 ovarian cancer case
**Data Format**: Original DICOM files with accompanying radiology reports
**Access Method**: Direct download and local storage (no real-time API integration yet)

### Evaluation Technologies

#### Rubric System
```json
// Example rubric structure
{
  "case_id": "TCGA-09-0364",
  "rubric_version": "1.0",
  "evaluation_criteria": [
    {
      "category": "Image Quality Assessment",
      "weight": 0.2,
      "subcriteria": [...]
    }
  ]
}
```

**Technical Approach**:
- **JSON Schema**: Structured evaluation criteria
- **Validation**: Schema validation for rubric consistency
- **Scoring Engine**: Python-based scoring logic
- **Versioning**: Rubric version tracking for audit trail

### Infrastructure Technologies

#### Docker Configuration
```yaml
# docker-compose.yml structure
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    volumes: ["./frontend:/app"]
    
  backend:
    build: ./mcp
    ports: ["8000:8000"]
    volumes: ["./demo_cases:/app/data"]
    
  orthanc:
    image: orthanc/orthanc:latest
    ports: ["4242:4242", "8042:8042"]
    volumes: ["./docker/orthanc-config.json:/etc/orthanc/orthanc.json"]
```

**Containerization Strategy**:
- **Multi-Service Architecture**: Separate containers for frontend, backend, and DICOM server
- **Development Volumes**: Source code mounted for hot reload during development
- **Configuration Management**: External configuration files mounted into containers
- **Port Management**: Non-conflicting port assignments for all services

#### Orthanc DICOM Server
```json
// orthanc-config.json
{
  "RemoteAccessAllowed": true,
  "HttpServerEnabled": true,
  "DicomServerEnabled": true,
  "DicomAet": "ORTHANC",
  "DicomPort": 4242,
  "HttpPort": 8042
}
```

**DICOM Server Integration**:
- **Standard DICOM**: Full DICOM protocol support
- **Web Interface**: Built-in web interface for DICOM management
- **API Access**: RESTful API for DICOM data access
- **Storage**: Configurable storage backend for DICOM files

## Development Environment

### Local Development Setup
```bash
# Frontend development
cd frontend
npm install
npm run dev    # Vite dev server on port 5173

# Backend development
cd mcp
pip install -r requirements.txt
uvicorn main:app --reload    # FastAPI on port 8000

# Full stack with Docker
docker-compose up    # All services orchestrated
```

### Build and Deployment
```bash
# Frontend production build
npm run build    # Generates dist/ directory

# Backend containerization
docker build -t casewise-backend ./mcp

# Full deployment
docker-compose -f docker-compose.prod.yml up
```

### Environment Configuration
```bash
# Environment Variables (.env)
REACT_APP_API_URL=http://localhost:8000
PYTHON_ENV=development
OHIF_VIEWER_URL=http://localhost:3000
ORTHANC_URL=http://localhost:8042
```

## Technology Integration Challenges

### Current Technical Challenges

#### 1. OHIF Integration Complexity
- **Build System**: Complex webpack configuration for OHIF platform
- **Bundle Size**: Large JavaScript bundle impacts loading performance
- **Customization**: Limited theming and customization options
- **Version Compatibility**: Keeping up with OHIF platform updates

#### 2. DICOM Performance
- **File Size**: Large DICOM files (100MB+) impact loading performance
- **Memory Usage**: Multiple series consume significant browser memory
- **Network Transfer**: Slow loading over network connections
- **Browser Limitations**: DICOM rendering performance varies by browser

#### 3. Cross-Platform Compatibility
- **Docker Environment**: Differences between host OS and container environment
- **Browser Support**: Medical imaging requires modern browser features
- **Mobile Compatibility**: Touch interfaces for medical image interaction
- **Screen Resolution**: High-resolution displays for diagnostic quality

### Performance Optimization Strategies

#### Frontend Optimization
- **Code Splitting**: Dynamic imports for OHIF components
- **Image Optimization**: DICOM thumbnail generation
- **Caching**: Browser caching for static DICOM data
- **Progressive Loading**: Load images as needed during interaction

#### Backend Optimization
- **Async Processing**: FastAPI async endpoints for concurrent requests
- **Memory Management**: Efficient DICOM data handling
- **Caching Layer**: Redis integration planned for frequently accessed data
- **Database Integration**: PostgreSQL planned for metadata and user data

## Future Technology Roadmap

### Short-term Technology Additions
- **Database**: PostgreSQL for persistent data storage
- **Caching**: Redis for performance optimization
- **Authentication**: JWT-based user authentication
- **Logging**: Structured logging with ELK stack

### Medium-term Enhancements
- **GPT Integration**: OpenAI API for natural language evaluation
- **Real-time Features**: WebSocket connections for collaborative features
- **Mobile Support**: Progressive Web App (PWA) capabilities
- **Analytics**: User interaction tracking and analytics

### Long-term Technology Evolution
- **Microservices**: Service decomposition for scalability
- **Kubernetes**: Container orchestration for cloud deployment
- **AI/ML Pipeline**: Custom machine learning models for evaluation
- **Multi-tenant Architecture**: Support for multiple institutions

## Security and Compliance Considerations

### Data Security
- **HIPAA Compliance**: Medical data handling requirements
- **Encryption**: Data encryption in transit and at rest
- **Access Control**: Role-based access control system
- **Audit Logging**: Comprehensive audit trail for data access

### Technical Security Measures
- **HTTPS**: TLS encryption for all communications
- **CORS Configuration**: Secure cross-origin resource sharing
- **Input Validation**: Comprehensive input sanitization
- **Container Security**: Secure Docker configurations and regular updates 