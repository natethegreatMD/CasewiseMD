# System Patterns: Casewise

## Architecture Overview

### High-Level System Architecture
Casewise follows a multi-tier architecture with clear separation between presentation, business logic, and data layers:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │   Python MCP    │    │   OHIF Viewer   │
│   (Port 5173)   │◄──►│   (Port 8000)   │◄──►│   (External)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Static Assets │    │   JSON Rubrics  │    │   DICOM Data    │
│   (CSS/JS)      │    │   (Evaluation)  │    │   (demo_cases)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Interaction Patterns
- **Frontend-Backend Communication**: RESTful API over HTTP with JSON payloads
- **DICOM Viewer Integration**: Iframe embedding with postMessage communication
- **State Management**: React component state with prop drilling (no global state management yet)
- **Data Flow**: Unidirectional data flow from backend to frontend with user interaction triggers

## Frontend Architecture Patterns

### React Component Hierarchy
```
App.tsx
├── DiagnosticWorkflow.tsx (Main orchestrator)
│   ├── DicomViewer.tsx (Primary viewer component)
│   ├── OhifViewer.tsx (Direct OHIF integration)
│   └── OhifIframeViewer.tsx (Iframe-based integration)
└── Static components (assets, styles)
```

### Component Design Patterns

#### 1. Container-Presentation Pattern
- **DiagnosticWorkflow.tsx**: Container component managing state and business logic
- **Viewer Components**: Presentation components focused on DICOM display
- **Separation of Concerns**: Business logic separated from UI rendering

#### 2. Multiple Integration Strategies
- **Parallel Implementation**: Multiple OHIF integration approaches maintained simultaneously
- **Strategy Pattern**: Different viewer implementations with common interface
- **Progressive Enhancement**: Iframe fallback while developing embedded solution

### State Management Patterns
- **Local Component State**: useState hooks for component-specific data
- **Prop Drilling**: Parent-to-child data passing (acceptable for current scale)
- **Effect Management**: useEffect for API calls and lifecycle management
- **Future Pattern**: Context API or Redux for global state when scaling

### Styling Architecture
- **CSS Modules**: Component-scoped styling in DicomViewer.css
- **Global Styles**: App.css for application-wide styling
- **Responsive Design**: Media queries for different screen sizes
- **Medical UI Standards**: High contrast, accessibility-focused design

## Backend Architecture Patterns

### Python MCP Server Structure
```
mcp/
├── main.py (FastAPI application entry point)
├── requirements.txt (Dependency management)
├── Dockerfile (Containerization)
└── routes/ (Modular route organization)
    ├── __init__.py
    ├── diagnostic.py (Case presentation logic)
    ├── grade.py (Evaluation and scoring)
    ├── config.py (System configuration)
    └── __pycache__/ (Python bytecode)
```

### Route Organization Pattern
- **Domain Separation**: Routes organized by functional domain
- **Single Responsibility**: Each route file handles specific business logic
- **Dependency Injection**: Shared utilities and configurations injected as needed
- **API Versioning**: Routes structured for future versioning support

### Data Processing Patterns

#### 1. DICOM Data Handling
- **File System Storage**: DICOM files stored in structured directory hierarchy
- **Lazy Loading**: DICOM data loaded on demand to optimize memory usage
- **Metadata Extraction**: Separate metadata.json files for quick access
- **Series Organization**: DICOM series grouped by study/series identifiers

#### 2. Rubric Processing
- **JSON Schema**: Structured evaluation criteria in JSON format
- **Validation**: Input validation against rubric schema
- **Scoring Logic**: Configurable scoring algorithms based on rubric structure
- **Versioning**: Rubric versioning for audit trail and evolution

### Error Handling Patterns
- **Graceful Degradation**: System continues functioning when non-critical components fail
- **Structured Logging**: Consistent log format for debugging and monitoring
- **Exception Hierarchy**: Custom exception classes for different error types
- **User-Friendly Messages**: Technical errors translated to user-appropriate feedback

## Data Architecture Patterns

### DICOM Data Organization
```
demo_cases/
└── case001/ (TCGA-09-0364)
    ├── metadata.json (Case metadata and report)
    ├── report.txt (Original radiology report)
    └── slices/ (DICOM series data)
        ├── series-1/ (UID-based directory naming)
        ├── series-2/
        └── series-3/
```

### Rubric Data Structure
```
rubrics/
├── chest_xray_basic.json
├── ct_abdomen_basic.json
├── mri_brain_basic.json
└── tcga_ovarian_cancer.json (Case-specific rubric)
```

### Data Validation Patterns
- **Schema Validation**: JSON schemas for all structured data
- **DICOM Validation**: Header validation for medical imaging standards
- **Referential Integrity**: Cross-references between cases, rubrics, and reports
- **Data Quality Checks**: Automated validation of data completeness and accuracy

## Integration Patterns

### OHIF Viewer Integration Strategies

#### Current Implementation: Iframe Strategy
```typescript
// OhifIframeViewer.tsx pattern
const OhifIframeViewer = ({ studyInstanceUID }) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  
  // PostMessage communication for viewer control
  const sendMessage = (message) => {
    iframeRef.current?.contentWindow?.postMessage(message, '*');
  };
  
  return <iframe ref={iframeRef} src={ohifUrl} />;
};
```

#### Future Implementation: Direct Embedding
```typescript
// OhifViewer.tsx pattern (in development)
const OhifViewer = ({ studyInstanceUID }) => {
  // Direct OHIF platform integration
  // Custom build and configuration
  // React component lifecycle integration
};
```

### API Communication Patterns
- **RESTful Design**: Standard HTTP methods and status codes
- **JSON API**: Consistent JSON request/response format
- **Error Standardization**: Uniform error response structure
- **Authentication**: Placeholder for future authentication integration

### Docker Integration Patterns
```yaml
# docker-compose.yml pattern
services:
  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    depends_on: [backend]
  
  backend:
    build: ./mcp
    ports: ["8000:8000"]
    volumes: [data persistence]
  
  orthanc:
    image: orthanc/orthanc
    configuration: [DICOM server setup]
```

## Design Patterns and Best Practices

### Code Organization Principles
- **Domain-Driven Design**: Code organized around medical education domains
- **Separation of Concerns**: Clear boundaries between UI, business logic, and data
- **Dependency Inversion**: High-level modules independent of low-level implementation details
- **Single Responsibility**: Each component/module has one primary purpose

### Medical Data Handling Principles
- **HIPAA Awareness**: Privacy and security considerations for medical data
- **DICOM Standards**: Adherence to medical imaging standards
- **Clinical Accuracy**: Data validation ensures medical accuracy
- **Audit Trail**: All data access and modifications logged

### Performance Optimization Patterns
- **Lazy Loading**: DICOM data loaded on demand
- **Caching Strategy**: Frequently accessed data cached appropriately
- **Memory Management**: Large DICOM files handled efficiently
- **Progressive Loading**: Large datasets loaded incrementally

### Security Patterns
- **Input Validation**: All user inputs validated and sanitized
- **CORS Configuration**: Cross-origin requests properly configured
- **Data Encryption**: Sensitive data encrypted in transit and at rest
- **Access Control**: Authorization patterns prepared for multi-user scenarios

## Development Workflow Patterns

### Build and Deployment
- **Multi-Stage Docker**: Optimized container builds for production
- **Environment Configuration**: Separate configs for development/production
- **Health Checks**: System health monitoring and alerting
- **Graceful Shutdown**: Proper cleanup on application termination

### Testing Patterns
- **Unit Testing**: Component-level testing for critical business logic
- **Integration Testing**: API endpoint testing with real data
- **End-to-End Testing**: Complete workflow validation
- **Medical Data Testing**: Validation with real DICOM datasets

### Configuration Management
- **Environment Variables**: External configuration via environment
- **Configuration Files**: JSON/YAML configuration for complex settings
- **Feature Flags**: Conditional feature activation for development
- **Secrets Management**: Secure handling of API keys and credentials

## Scalability Patterns

### Horizontal Scaling Preparation
- **Stateless Design**: Services designed for horizontal scaling
- **Database Abstraction**: Data layer prepared for database integration
- **Session Management**: User session handling for multi-instance deployment
- **Load Balancing**: Architecture compatible with load balancing

### Data Scaling Patterns
- **Case Library Expansion**: Architecture supports multiple cases
- **Rubric Management**: Dynamic rubric loading and management
- **User Management**: Multi-user support architecture
- **Performance Monitoring**: Metrics collection for scaling decisions

### Technology Evolution Patterns
- **API Versioning**: Backward compatibility for API evolution
- **Component Abstraction**: UI components designed for framework changes
- **Data Migration**: Patterns for data schema evolution
- **Feature Toggle**: New feature deployment without breaking changes 