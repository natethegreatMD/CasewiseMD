# Project Brief: Casewise

## Core Concept

Casewise is an AI-powered medical education platform designed specifically for radiology residents preparing for oral board examinations. The platform simulates realistic oral board scenarios using authentic medical imaging data and leverages AI to provide intelligent evaluation and personalized learning feedback.

## Primary Use Case

**Target User**: Radiology residents preparing for oral board exams
**Primary Need**: Practice realistic case presentations with immediate, intelligent feedback
**Key Differentiator**: Uses real DICOM imaging data from TCIA (The Cancer Imaging Archive) with authentic radiology reports

## MVP Scope

### Core MVP Features
- **Single Test Case**: TCGA-09-0364 from TCIA as proof of concept
- **Real Medical Data**: Authentic DICOM slices and radiology reports
- **AI Evaluation**: Rubric-based assessment system with structured feedback
- **Medical Image Viewing**: OHIF viewer integration for DICOM display
- **Interactive Workflow**: Guided diagnostic process with question prompting

### MVP Boundaries
- **No Subspecialty Filtering**: Generic radiology focus for initial version
- **Single Case Study**: TCGA-09-0364 only
- **Rubric-Based Grading**: JSON-structured evaluation (GPT grading deferred)
- **Hosted Viewer**: OHIF runs separately (embedding planned for later)

## Success Criteria

### MVP Success Metrics
1. **Functional Case Presentation**: User can view DICOM images and submit diagnostic responses
2. **Accurate AI Evaluation**: Rubric-based scoring matches expert assessment
3. **Complete Workflow**: End-to-end case interaction from image viewing to feedback
4. **Data Integrity**: Real medical data handled appropriately and securely

### Long-term Vision
- Multi-case library with subspecialty filtering
- Advanced GPT-based evaluation with natural language assessment
- Embedded OHIF viewer with annotation capabilities
- Performance analytics and learning progression tracking
- Collaborative features for group study sessions

## Project Constraints

### Technical Constraints
- Must handle real DICOM medical imaging data
- AI evaluation must be explainable and auditable
- System must maintain medical data privacy standards
- Image viewing must meet diagnostic quality requirements

### Business Constraints
- MVP focused on single case validation
- No subspecialty complexity in initial version
- Prioritize accuracy over feature breadth
- Ship-first mentality with iterative improvement

## Key Stakeholders

**Primary User**: Mike (Radiology Resident)
- Deep focus on AI accuracy and zero hallucination
- Pragmatic, MVP-first development approach
- Strong architectural consistency requirements
- Preference for CLI workflows and systematic prompt tracking

## Project Timeline

**Current Phase**: MVP Development and Validation
**Next Phase**: Multi-case expansion and advanced AI integration
**Future Phases**: Platform scaling and collaborative features 