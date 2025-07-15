# System Patterns: Casewise VPS Medical Education Platform

## Architecture Overview - MVP COMPLETE, 2.0 DEVELOPMENT ACTIVE

### High-Level System Architecture (MVP OPERATIONAL + 2.0 PLANNING)
Casewise follows a production-ready multi-tier architecture with complete AI integration (MVP) and is expanding to include intelligent case management and navigation systems (2.0):

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CASEWISE 2.0 ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                MVP COMPLETE ✅                                  │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   React Frontend │    │   Python MCP    │    │   OpenAI GPT-4o │            │
│  │  (Production)   │◄──►│  (Production)   │◄──►│  (Real AI)      │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│           │                       │                       │                     │
│           ▼                       ▼                       ▼                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   OHIF Viewer   │    │   AI Grading    │    │   TCIA Data     │            │
│  │  (Embedded)     │    │  (923 lines)    │    │  (Authentic)    │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                               VERSION 2.0 🎯                                   │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │  Case Manager   │    │  Navigation     │    │  AI Case Gen    │            │
│  │  (Planning)     │◄──►│  (Planning)     │◄──►│  (Planning)     │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│           │                       │                       │                     │
│           ▼                       ▼                       ▼                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   DICOM Server  │    │   Case Library  │    │   Multi-Case    │            │
│  │  (Integration)  │    │  (Interface)    │    │  (Support)      │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Production Deployment Architecture (CURRENT + PLANNED)
```
┌─────────────────────────────────────────────────────────────────┐
│                    VPS Production System                         │
├─────────────────────────────────────────────────────────────────┤
│  MVP OPERATIONAL ✅                                             │
│  Frontend: https://app.casewisemd.org                          │
│  Backend API: https://api.casewisemd.org                       │
│  Docker Container Architecture                                  │
│  Health Monitoring & Logging                                   │
│  SSL/HTTPS Configuration                                        │
├─────────────────────────────────────────────────────────────────┤
│  VERSION 2.0 DEVELOPMENT 🎯                                     │
│  Case Manager API: /api/v2/cases                              │
│  Navigation System: Enhanced Frontend                          │
│  AI Case Generation: OpenAI GPT-4o Integration                │
│  DICOM Integration: Automated Image Importing                  │
│  Multi-Case Support: Comprehensive Case Library               │
└─────────────────────────────────────────────────────────────────┘
```

### Component Interaction Patterns (MVP + 2.0)
- **Frontend-Backend Communication**: RESTful API over HTTPS with JSON payloads
- **AI Integration**: OpenAI GPT-4o with structured prompt engineering
- **DICOM Viewer Integration**: Embedded OHIF viewer with React lifecycle
- **State Management**: React hooks with comprehensive workflow state
- **Data Flow**: Bidirectional with AI assessment and interactive follow-up
- **2.0 Enhancements**: Case management, navigation, and AI-powered case generation

## Frontend Architecture Patterns

### MVP Architecture - PRODUCTION COMPLETE ✅
```
App.tsx (Production)
├── DiagnosticWorkflow.tsx (1072 lines) - FULLY FUNCTIONAL
│   ├── Complete diagnostic session management
│   ├── Interactive follow-up questions interface
│   ├── Skip functionality with confirmation dialogs
│   ├── AI evaluation results display
│   ├── Progress tracking and navigation
│   └── Medical image viewer integration
└── Professional medical education interface
```

### Version 2.0 Architecture - PLANNING PHASE 🎯
```
App.tsx (2.0 Enhanced)
├── NavigationSystem.tsx (NEW) - Case browsing and selection
│   ├── CaseLibrary.tsx - Professional case library interface
│   ├── CategoryFilter.tsx - Subspecialty filtering system
│   ├── CaseCard.tsx - Individual case preview component
│   ├── SearchInterface.tsx - Advanced case search capabilities
│   └── ProgressTracker.tsx - Multi-case progress monitoring
├── CaseManager.tsx (NEW) - Administrative case management
│   ├── CaseGenerator.tsx - AI-powered case creation interface
│   ├── ReportUploader.tsx - Radiology report processing
│   ├── RubricEditor.tsx - AI-generated rubric management
│   ├── QuestionBuilder.tsx - Dynamic question generation
│   └── DicomImporter.tsx - DICOM image integration
└── DiagnosticWorkflow.tsx (ENHANCED) - Extended for multi-case support
    ├── Existing MVP functionality maintained
    ├── Multi-case session management
    ├── Case metadata integration
    ├── Enhanced progress tracking
    └── Navigation integration
```

### 2.0 Component Design Patterns

#### 1. Case Management Pattern 🎯
- **AI Case Generator**: OpenAI GPT-4o powered case creation from radiology reports
- **Rubric Generator**: AI-powered evaluation criteria generation
- **Question Generator**: Dynamic diagnostic question creation
- **Case ID System**: Systematic case identification and organization
- **DICOM Integration**: Automated image importing to DICOM server

#### 2. Navigation System Pattern 🎯
- **Category Management**: Radiology subspecialty organization system
- **Case Library Interface**: Professional case browsing experience
- **Filtering System**: Advanced search and filter capabilities
- **Selection Workflow**: Seamless navigation-to-diagnosis transition
- **Progress Tracking**: Multi-case user progress monitoring

#### 3. AI Integration Pattern (ENHANCED) 🎯
- **Case Generation**: AI analysis of radiology reports for case creation
- **Content Creation**: AI-generated questions, rubrics, and learning objectives
- **Medical Validation**: Rigorous accuracy verification for generated content
- **Structured Output**: JSON-formatted case metadata and educational content

### MVP UI/UX Patterns (IMPLEMENTED) ✅
- **Medical Professional Interface**: High contrast, accessibility-focused design
- **Responsive Design**: Cross-device compatibility with mobile optimization
- **Professional Styling**: Medical-grade appearance appropriate for education
- **User Experience Flow**: Intuitive progression from DICOM viewing to AI assessment

### 2.0 UI/UX Patterns (PLANNED) 🎯
- **Case Discovery Interface**: Intuitive browsing and selection system
- **Administrative Interface**: Case management and generation tools
- **Multi-Case Navigation**: Seamless transition between different cases
- **Progress Visualization**: Comprehensive learning analytics and tracking

## Backend Architecture Patterns

### MVP Backend Structure (PRODUCTION OPERATIONAL) ✅
```
mcp/ (Production System)
├── main.py (FastAPI application - operational)
├── requirements.txt (All dependencies resolved)
├── Dockerfile (Production container configuration)
├── routes/ (Complete API implementation)
│   ├── diagnostic.py (Case management - functional)
│   ├── grade.py (AI evaluation - operational)
│   └── config.py (System configuration)
└── services/ (AI Integration Services)
    ├── ai_grading.py (923 lines) - FULLY OPERATIONAL
    ├── rubric_loader.py (Rubric processing)
    └── Production logging and monitoring
```

### Version 2.0 Backend Structure (DEVELOPMENT PLANNING) 🎯
```
mcp/ (Enhanced 2.0 System)
├── main.py (Enhanced FastAPI application)
├── requirements.txt (Extended dependencies)
├── Dockerfile (Enhanced container configuration)
├── routes/ (Extended API implementation)
│   ├── diagnostic.py (Enhanced for multi-case support)
│   ├── grade.py (Maintained MVP functionality)
│   ├── case_management.py (NEW) - Case CRUD operations
│   ├── case_generation.py (NEW) - AI-powered case creation
│   ├── navigation.py (NEW) - Case browsing and filtering
│   └── dicom_integration.py (NEW) - DICOM server integration
├── services/ (Enhanced AI Integration Services)
│   ├── ai_grading.py (Maintained MVP functionality)
│   ├── ai_case_generator.py (NEW) - Report-to-case generation
│   ├── rubric_generator.py (NEW) - AI rubric creation
│   ├── question_generator.py (NEW) - Dynamic question generation
│   ├── case_id_manager.py (NEW) - Case identification system
│   └── dicom_processor.py (NEW) - DICOM image processing
└── models/ (NEW) - Enhanced data models
    ├── case.py - Case metadata and content models
    ├── rubric.py - Rubric structure and validation
    ├── question.py - Question formats and categories
    └── navigation.py - Case browsing and filtering models
```

### AI Integration Patterns

#### MVP AI Integration (FULLY IMPLEMENTED) ✅
```python
# ai_grading.py - OPERATIONAL
class AIGradingService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o"  # Production model
    
    async def grade_answers(self, answers, rubric):
        # Real AI assessment with structured prompts
        # Medical accuracy validation
        # Detailed feedback generation
        # ABR-level evaluation standards
    
    async def generate_followup_questions(self, category_scores):
        # AI-generated adaptive questions
        # Personalized based on weak areas
        # Socratic-style questioning
    
    async def evaluate_followup_answers(self, followup_answers):
        # AI assessment of student reflections
        # Learning progression evaluation
        # Quantified improvement scoring
```

#### 2.0 AI Integration (PLANNING) 🎯
```python
# ai_case_generator.py - PLANNED
class AICaseGeneratorService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o"
    
    async def generate_case_from_report(self, report_text):
        # AI analysis of radiology reports
        # Case metadata extraction
        # Educational content generation
        # Medical accuracy validation
    
    async def generate_rubric(self, case_metadata):
        # AI-powered rubric generation
        # ABR-standard evaluation criteria
        # Subspecialty-specific requirements
        # Weighted scoring system
    
    async def generate_questions(self, case_metadata, rubric):
        # Dynamic question generation
        # Diagnostic workflow questions
        # Difficulty appropriate to case
        # Educational objective alignment
    
    async def validate_medical_content(self, generated_content):
        # Medical accuracy verification
        # Content quality assurance
        # Educational appropriateness
        # Clinical validity checking
```

## Data Architecture Patterns

### MVP Data Organization (IMPLEMENTED) ✅
```
demo_cases/ (Production Data)
└── case001/ (TCGA-09-0364 - Operational)
    ├── metadata.json (Case metadata - functional)
    ├── report.txt (Original radiology report)
    ├── questions.json (7 diagnostic questions)
    ├── rubric.json (AI evaluation criteria)
    └── slices/ (DICOM series - properly loaded)
        ├── series-1/ (Medical imaging data)
        ├── series-2/ (Multi-series support)
        └── series-3/ (Complete case data)
```

### 2.0 Data Organization (PLANNED) 🎯
```
cases/ (Enhanced Multi-Case Data)
├── case001/ (Existing MVP case - maintained)
│   ├── [Existing structure preserved]
├── case002/ (AI-generated case)
│   ├── metadata.json (AI-generated case metadata)
│   ├── report.txt (Source radiology report)
│   ├── questions.json (AI-generated questions)
│   ├── rubric.json (AI-generated rubric)
│   ├── case_id.json (System-generated ID)
│   └── slices/ (Imported DICOM series)
├── case003/ (AI-generated case)
│   └── [Similar structure]
├── categories/ (Subspecialty organization)
│   ├── ovarian_cancer.json
│   ├── chest_xray.json
│   ├── brain_mri.json
│   └── [Additional subspecialties]
└── navigation/ (Case browsing data)
    ├── case_index.json (Searchable case index)
    ├── category_mapping.json (Subspecialty organization)
    └── progress_tracking.json (User progress data)
```

### AI Response Data Structure (ENHANCED) 🎯
```json
{
  "case_generation": {
    "case_id": "AI-generated case identifier",
    "source_report": "Original radiology report text",
    "generated_metadata": {
      "title": "AI-extracted case title",
      "modality": "Imaging modality",
      "subspecialty": "Radiology subspecialty",
      "difficulty": "Educational difficulty level"
    },
    "generated_questions": [
      {
        "id": "Question identifier",
        "category": "Diagnostic category",
        "text": "AI-generated question text",
        "learning_objective": "Educational objective"
      }
    ],
    "generated_rubric": {
      "categories": "AI-generated evaluation criteria",
      "weights": "Scoring weights",
      "standards": "ABR-level standards"
    }
  },
  "navigation": {
    "case_library": "Available cases",
    "categories": "Subspecialty organization",
    "filtering": "Search and filter capabilities",
    "progress": "User progress tracking"
  }
}
```

## Integration Patterns

### MVP Integration (PRODUCTION OPERATIONAL) ✅
```typescript
// DiagnosticWorkflow.tsx - IMPLEMENTED
const MVPIntegration = () => {
  // Complete diagnostic workflow
  // AI assessment integration
  // OHIF viewer embedding
  // Follow-up question system
  // Progress tracking
}
```

### 2.0 Integration (DEVELOPMENT PLANNING) 🎯
```typescript
// NavigationSystem.tsx - PLANNED
const NavigationIntegration = () => {
  // Case library browsing
  // Category filtering
  // Case selection workflow
  // Progress tracking across cases
  // Seamless transition to diagnostic workflow
}

// CaseManager.tsx - PLANNED
const CaseManagerIntegration = () => {
  // AI case generation interface
  // Report upload and processing
  // Generated content review
  // DICOM integration
  // Case publication workflow
}
```

## Development Patterns for 2.0

### Case Generation Workflow Pattern 🎯
```
1. Report Upload → 2. AI Analysis → 3. Case Generation → 4. Content Review → 5. DICOM Integration → 6. Case Publication
```

### Navigation Workflow Pattern 🎯
```
1. Case Discovery → 2. Category Filtering → 3. Case Selection → 4. Preview → 5. Start Diagnostic → 6. Progress Tracking
```

### AI Integration Workflow Pattern 🎯
```
1. Prompt Engineering → 2. Content Generation → 3. Medical Validation → 4. Quality Assurance → 5. System Integration
```

## Version 2.0 Success Metrics

### Technical Architecture Metrics
- **System Integration**: All components working seamlessly together
- **AI Performance**: Consistent and accurate case generation
- **Scalability**: Architecture supporting large case libraries
- **Production Readiness**: 2.0 system ready for live deployment

### User Experience Metrics
- **Case Discovery**: Intuitive browsing and selection workflow
- **Content Quality**: AI-generated cases meeting medical education standards
- **Navigation Efficiency**: Fast case discovery and selection
- **Learning Progression**: Effective multi-case learning tracking

## Current Development Status

### MVP Architecture: PRODUCTION COMPLETE ✅
All MVP architectural patterns implemented and operational

### Version 2.0 Architecture: PLANNING PHASE 🎯
- **Case Manager**: Architecture planning for AI-powered case generation
- **Navigation System**: UI/UX design for professional case browsing
- **AI Integration**: Enhanced OpenAI GPT-4o usage planning
- **Data Architecture**: Multi-case support and organization planning

**Current Focus**: **Case Manager System Architecture Design**
**Next Phase**: **AI Case Generation Implementation**
**Branch**: **2.0 - Active Development** 