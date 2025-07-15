# Casewise VPS Medical Education Platform - Detailed System Flow

## Overview
This document provides an extremely detailed explanation of how the Casewise VPS Medical Education Platform operates, from initial user access through complete diagnostic assessment and AI-powered feedback delivery.

---

## **PHASE 1: Initial System Access & Homepage**

### **1.1 User Navigation to Platform**
1. **User accesses**: `https://casewisemd.org` (homepage)
2. **DNS Resolution**: Domain resolves to VPS IP `143.244.154.89`
3. **nginx Reverse Proxy**: Routes request to appropriate service
4. **Static File Serving**: Homepage served from `/var/www/frontend/`

### **1.2 Homepage Component Loading**
1. **React Application Bootstrap**: `App.tsx` component initializes
2. **State Management Setup**:
   ```typescript
   const [currentPage, setCurrentPage] = useState('home');
   const [currentRoute, setCurrentRoute] = useState('home');
   ```
3. **Navigation Items Loaded**: Static configuration of available features
4. **Case Categories Rendered**: Display of available diagnostic categories

### **1.3 Homepage User Interface**
1. **Hero Section Display**: Platform introduction and statistics
2. **Quick Actions Section**: Primary call-to-action buttons
3. **Case Categories Grid**: Available diagnostic categories (6 total)
   - Ovarian Cancer (Available)
   - Chest X-Ray (Coming Soon)
   - Brain MRI (Coming Soon)
   - Abdomen CT (Coming Soon)
   - Obstetric Ultrasound (Coming Soon)
   - Cardiac CT (Coming Soon)
4. **Features Section**: Platform capabilities overview

---

## **PHASE 2: Case Selection & Navigation**

### **2.1 User Case Selection**
1. **User clicks "Start Case"** on Ovarian Cancer category
2. **JavaScript Event Handler**: `handleCaseClick('ovarian-cancer')` triggered
3. **Category Validation**: System checks `category.available = true`
4. **Route Transition**: 
   ```typescript
   window.history.pushState({}, '', '/diagnostic');
   setCurrentRoute('diagnostic');
   ```

### **2.2 Cross-Domain Navigation**
1. **Homepage Domain**: User on `casewisemd.org`
2. **Redirect Trigger**: Click redirects to `app.casewisemd.org`
3. **DNS Resolution**: New subdomain resolves to same VPS IP
4. **nginx Configuration**: Routes `app.` subdomain to React application
5. **Component Switch**: App renders `<DiagnosticWorkflow />` component

---

## **PHASE 3: Diagnostic Workflow Initialization**

### **3.1 DiagnosticWorkflow Component Bootstrap**
1. **Component Mount**: `DiagnosticWorkflow.tsx` (1510 lines) initializes
2. **State Management Setup**:
   ```typescript
   const [session, setSession] = useState<DiagnosticSession | null>(null);
   const [currentAnswer, setCurrentAnswer] = useState('');
   const [loading, setLoading] = useState(false);
   const [caseMetadata, setCaseMetadata] = useState<CaseMetadata | null>(null);
   const [viewerUrl, setViewerUrl] = useState<string | null>(null);
   ```

### **3.2 Case Data Loading Process**
1. **useEffect Trigger**: Component mount triggers `loadCaseData()`
2. **API Request 1 - Case Metadata**:
   ```typescript
   fetch(`${API_URL}/cases/case001/metadata`)
   ```
   - **Endpoint**: `https://api.casewisemd.org/api/v1/cases/case001/metadata`
   - **Method**: GET
   - **Purpose**: Load case information and DICOM metadata

3. **Backend Processing** (`case_viewer.py`):
   ```python
   # MCP tools retrieve case information
   case_metadata = case_tools.get_case_info("case001")
   # Returns structured metadata from demo_cases/case001/metadata.json
   ```

4. **API Response Processing**:
   ```json
   {
     "success": true,
     "case_id": "case001",
     "metadata": {
       "title": "Ovarian Cancer Case",
       "modality": "CT",
       "body_region": "Abdomen/Pelvis",
       "study_instance_uid": "1.3.6.1.4.1.14519.5.2.1.7695.4007.250730721548000739633557298354",
       "series_count": 3,
       "study_date": "2005-06-08",
       "patient_age": "58Y",
       "contrast": "IV Contrast"
     }
   }
   ```

### **3.3 OHIF Viewer URL Generation**
1. **API Request 2 - Viewer URL**:
   ```typescript
   fetch(`${API_URL}/viewer-url`, {
     method: 'POST',
     body: JSON.stringify({ case_id: 'case001' })
   })
   ```

2. **Backend Processing** (`viewer_tools.py`):
   ```python
   # Generate OHIF viewer URL with study UID
   study_uid = "1.3.6.1.4.1.14519.5.2.1.7695.4007.250730721548000739633557298354"
   dicomweb_endpoint = "https://api.casewisemd.org/orthanc/dicom-web"
   viewer_url = f"https://viewer.casewisemd.org/viewer?StudyInstanceUIDs={study_uid}&url={dicomweb_endpoint}"
   ```

3. **API Response**:
   ```json
   {
     "success": true,
     "viewer_url": "https://viewer.casewisemd.org/viewer?StudyInstanceUIDs=1.3.6.1.4.1.14519.5.2.1.7695.4007.250730721548000739633557298354&url=https://api.casewisemd.org/orthanc/dicom-web",
     "case_id": "case001"
   }
   ```

---

## **PHASE 4: Medical Imaging Display**

### **4.1 OHIF Viewer Integration**
1. **iframe Rendering**: React component renders OHIF viewer
   ```typescript
   <iframe
     src={viewerUrl}
     style={{ width: '100%', height: 'calc(90vh - 3rem)' }}
     title="Medical Image Viewer"
   />
   ```

2. **DICOM Data Loading**: OHIF viewer requests DICOM data
   - **Request Path**: `https://api.casewisemd.org/orthanc/dicom-web/studies/{study_uid}/series`
   - **nginx Proxy**: Routes to Orthanc DICOM server on port 8042
   - **Orthanc Response**: Returns DICOM series metadata and image data

3. **Image Rendering**: OHIF displays medical imaging with professional tools
   - **Viewport**: 90vh height for maximum diagnostic space
   - **Tools**: Window/level, zoom, pan, measurement tools
   - **Series Navigation**: Multiple CT series available for review

### **4.2 Case Information Display**
1. **Metadata Rendering**: Professional case information display
   ```typescript
   <div className="case-metadata">
     <h2>Ovarian Cancer Diagnostic Case</h2>
     <div className="clinical-history-panel">
       <h3>Clinical History</h3>
       <div>Chief Complaint: 6-month progressive pelvic discomfort</div>
       <div>History: Early satiety, increasing abdominal girth</div>
       <div>Clinical Concern: Suspected ovarian mass</div>
     </div>
   </div>
   ```

---

## **PHASE 5: Diagnostic Session Initiation**

### **5.1 Session Creation**
1. **User clicks "Start Diagnostic Session"**
2. **API Request - Session Start**:
   ```typescript
   fetch(`${API_URL}/diagnostic-session`, {
     method: 'POST',
     body: JSON.stringify({ case_id: 'case001' })
   })
   ```

3. **Backend Processing** (`diagnostic.py`):
   ```python
   # Generate unique session ID
   session_id = f"session_{int(time.time())}_{case_id}"
   
   # Load case questions from demo_cases/case001/questions.json
   questions = read_case_questions(case_id)
   
   # Return first question
   first_question = questions[0] if questions else None
   ```

4. **Session Response**:
   ```json
   {
     "session_id": "session_1704567890_case001",
     "case_id": "case001",
     "current_step": 1,
     "total_questions": 7,
     "current_question": {
       "id": 1,
       "text": "What is your primary diagnosis based on the imaging findings?",
       "category": "Primary Diagnosis",
       "hint": "Focus on the dominant pelvic mass characteristics"
     },
     "progress_percentage": 14.3
   }
   ```

### **5.2 Question Display System**
1. **React State Update**: Session data stored in component state
2. **UI Rendering**: Question interface displayed
   ```typescript
   <div className="question-section">
     <h3>Question 1 of 7: Primary Diagnosis</h3>
     <p>{session.current_question.text}</p>
     <button onClick={() => setShowHint(true)}>Show Hint</button>
   </div>
   ```

3. **Answer Input Interface**:
   ```typescript
   <textarea
     value={currentAnswer}
     onChange={(e) => setCurrentAnswer(e.target.value)}
     placeholder="Enter your detailed answer here..."
     rows={6}
   />
   ```

---

## **PHASE 6: Question Progression & Answer Collection**

### **6.1 Answer Submission Process**
1. **User types answer** in textarea interface
2. **User clicks "Submit Answer"** button
3. **Validation**: Check answer is not empty
4. **API Request - Answer Submission**:
   ```typescript
   fetch(`${API_URL}/diagnostic-answer`, {
     method: 'POST',
     body: JSON.stringify({
       session_id: session.session_id,
       case_id: 'case001',
       current_step: session.current_step,
       answer: currentAnswer,
       answers: session.answers
     })
   })
   ```

### **6.2 Backend Answer Processing**
1. **Request Handling** (`diagnostic.py`):
   ```python
   # Extract request data
   session_id = answer_data.get("session_id")
   current_step = answer_data.get("current_step")
   answer = answer_data.get("answer")
   previous_answers = answer_data.get("answers", {})
   
   # Update answers dictionary
   updated_answers = previous_answers.copy()
   updated_answers[str(current_step)] = answer
   
   # Calculate next step
   next_step = current_step + 1
   is_completed = next_step > len(questions)
   ```

2. **Response Generation**:
   ```json
   {
     "success": true,
     "session_id": "session_1704567890_case001",
     "current_step": 2,
     "answers": {
       "1": "Primary diagnosis: Ovarian carcinoma with peritoneal carcinomatosis..."
     },
     "completed": false,
     "current_question": {
       "id": 2,
       "text": "Describe the imaging characteristics that support your diagnosis",
       "category": "Image Interpretation"
     },
     "progress_percentage": 28.6
   }
   ```

### **6.3 Progressive Question Flow**
This process repeats for all 7 questions:

1. **Question 1**: Primary Diagnosis (Primary Diagnosis category)
2. **Question 2**: Imaging Characteristics (Image Interpretation category)
3. **Question 3**: Differential Diagnosis (Differential Diagnosis category)
4. **Question 4**: Clinical Correlation (Clinical Correlation category)
5. **Question 5**: Management Recommendations (Management category)
6. **Question 6**: Communication Strategy (Communication category)
7. **Question 7**: Safety Considerations (Safety category)

Each question follows the same submission → processing → next question cycle.

---

## **PHASE 7: AI-Powered Assessment System**

### **7.1 Session Completion Detection**
1. **Final Answer Submitted**: User completes question 7
2. **Backend Detection**: `is_completed = next_step > len(questions)` = True
3. **Response Modification**:
   ```json
   {
     "success": true,
     "completed": true,
     "answers": {
       "1": "Primary diagnosis: Ovarian carcinoma...",
       "2": "Imaging shows large complex pelvic mass...",
       "3": "Differential includes ovarian carcinoma...",
       "4": "Clinical correlation with CA-125...",
       "5": "Recommend surgical staging...",
       "6": "Discuss findings with gynecologic oncology...",
       "7": "Consider VTE prophylaxis..."
     }
   }
   ```

### **7.2 AI Grading Initiation**
1. **Frontend Processing**: Detects `completed: true`
2. **AI Grading API Call**:
   ```typescript
   const gradingRes = await fetch(`${API_URL}/grade`, {
     method: 'POST',
     body: JSON.stringify({
       session_id: session.session_id,
       case_id: 'case001',
       answers: data.answers
     })
   });
   ```

### **7.3 Backend AI Processing** (`ai_grading.py` - 923 lines)

#### **7.3.1 Rubric Loading**
```python
# Load evaluation rubric from demo_cases/case001/rubric.json
rubric = load_rubric(case_id)
# Rubric contains 7 categories with weights totaling 100%
```

#### **7.3.2 OpenAI GPT-4o Integration**
```python
class AIGradingService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o"
    
    async def grade_answers(self, answers, case_id, rubric):
        # Construct comprehensive prompt with medical context
        prompt = self._build_grading_prompt(answers, rubric, case_id)
        
        # Call OpenAI GPT-4o with structured prompt
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": MEDICAL_ASSESSMENT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        # Parse structured JSON response
        return json.loads(response.choices[0].message.content)
```

#### **7.3.3 Medical Assessment Prompt Engineering**
```python
MEDICAL_ASSESSMENT_SYSTEM_PROMPT = """
You are an expert radiologist and medical educator conducting an ABR 
(American Board of Radiology) oral board examination. Your role is to 
provide rigorous, accurate medical assessment of diagnostic reasoning.

CRITICAL REQUIREMENTS:
- Zero tolerance for medical inaccuracies or hallucinations
- Assessment must match oral board examination standards
- Provide detailed, educational feedback for medical learning
- Score based on medical accuracy, clinical reasoning, and communication

EVALUATION CATEGORIES:
1. Primary Diagnosis (20%)
2. Image Interpretation (20%)
3. Differential Diagnosis (15%)
4. Clinical Correlation (15%)
5. Management Recommendations (15%)
6. Communication & Organization (10%)
7. Safety Considerations (5%)

Return structured JSON with scores, feedback, and educational guidance.
"""
```

#### **7.3.4 AI Response Processing**
GPT-4o returns structured evaluation:
```json
{
  "category_scores": {
    "Primary Diagnosis": 85,
    "Image Interpretation": 90,
    "Differential Diagnosis": 75,
    "Clinical Correlation": 80,
    "Management Recommendations": 70,
    "Communication & Organization": 85,
    "Safety Considerations": 95
  },
  "total_score": 82.5,
  "detailed_feedback": {
    "strengths": [
      "Excellent identification of primary ovarian malignancy",
      "Accurate description of peritoneal enhancement pattern",
      "Appropriate safety considerations for contrast contraindications"
    ],
    "areas_for_improvement": [
      "Consider additional differential diagnoses",
      "More specific staging recommendations needed",
      "Enhanced clinical correlation discussion required"
    ]
  },
  "grading_rationale": "Strong diagnostic accuracy with room for improvement in differential considerations..."
}
```

### **7.4 Follow-up Question Generation**
```python
# Identify weak areas (scores < 70%)
weak_categories = [cat for cat, score in category_scores.items() if score < 70]

if weak_categories:
    # Generate AI-powered follow-up questions
    followup_questions = await self.generate_followup_questions(weak_categories, case_id)
```

Example follow-up question generation:
```json
{
  "follow_up_questions": [
    {
      "category": "Management Recommendations",
      "question": "Given the imaging findings of probable ovarian carcinoma with ascites, what specific imaging-guided procedures would you recommend next?",
      "purpose": "Assess understanding of interventional radiology role in oncologic care",
      "educational_focus": "Management pathway knowledge"
    }
  ]
}
```

---

## **PHASE 8: Results Display & Follow-up Learning**

### **8.1 Initial Results Processing**
1. **AI Response Received**: Frontend receives comprehensive grading data
2. **Follow-up Detection**: System checks for `follow_up_questions` array
3. **Conditional Flow**:
   ```typescript
   if (gradingData.follow_up_questions && gradingData.follow_up_questions.length > 0) {
     setFollowUpQuestions(gradingData.follow_up_questions);
     setShowingFollowUps(true);
     setGradingResult(gradingData); // Store for later display
   } else {
     setGradingResult(gradingData); // Show results immediately
   }
   ```

### **8.2 Follow-up Question Interface**
1. **Follow-up UI Rendering**:
   ```typescript
   <div className="follow-up-questions">
     <h2>Follow-up Questions</h2>
     <p>Based on your responses, let's explore areas for improvement...</p>
     <div className="follow-up-question">
       <span className="follow-up-category">Management Recommendations</span>
       <p className="follow-up-question-text">{currentQuestion.question}</p>
       <p className="follow-up-purpose">{currentQuestion.purpose}</p>
     </div>
   </div>
   ```

### **8.3 Follow-up Answer Processing**
1. **Answer Submission**: Similar flow to main questions
2. **API Call - Follow-up Evaluation**:
   ```typescript
   fetch(`${API_URL}/evaluate-followup`, {
     method: 'POST',
     body: JSON.stringify({
       case_id: 'case001',
       followup_answers: followupAnswers,
       original_followup_questions: followUpQuestions,
       original_grading: gradingResult
     })
   })
   ```

3. **AI Re-evaluation**: GPT-4o assesses follow-up responses and learning progression

### **8.4 Comprehensive Results Display**
```typescript
<div className="results-section">
  <h2>Diagnostic Assessment Results</h2>
  
  {/* Score Summary */}
  <div className="score-summary">
    <div className="score-card">
      <div className="score-number">{Math.round(gradingResult.scores.total_score)}</div>
      <div className="score-percentage">/ 100</div>
      <div className="score-status">
        {gradingResult.scores.total_score >= 70 ? 'PASSED' : 'NEEDS IMPROVEMENT'}
      </div>
    </div>
  </div>
  
  {/* Category Breakdown */}
  <div className="category-results">
    {Object.entries(gradingResult.scores.category_scores).map(([category, score]) => (
      <div className="category-card">
        <h4>{category}</h4>
        <div className="category-score">{score}%</div>
      </div>
    ))}
  </div>
  
  {/* Detailed Feedback */}
  <div className="feedback-section">
    <div className="strengths">
      <h4>Strengths</h4>
      <ul>
        {gradingResult.feedback.strengths.map(strength => (
          <li>{strength}</li>
        ))}
      </ul>
    </div>
    <div className="improvements">
      <h4>Areas for Improvement</h4>
      <ul>
        {gradingResult.feedback.areas_for_improvement.map(improvement => (
          <li>{improvement}</li>
        ))}
      </ul>
    </div>
  </div>
</div>
```

---

## **PHASE 9: System Architecture & Data Flow**

### **9.1 Complete Request Flow**
```
User Browser (app.casewisemd.org)
    ↓ HTTP Request
nginx Reverse Proxy (143.244.154.89:443)
    ↓ Route to Service
Docker Container (Frontend: React App)
    ↓ API Calls
Docker Container (Backend: FastAPI)
    ↓ AI Processing
OpenAI GPT-4o API (External)
    ↓ DICOM Requests
Docker Container (Orthanc DICOM Server)
    ↓ Medical Image Data
File System (/app/demo_cases/)
```

### **9.2 Data Persistence & Storage**
1. **Session Storage**: Browser localStorage for temporary session data
2. **Case Data**: File system storage in `/app/demo_cases/case001/`
   - `metadata.json` - Case information and DICOM metadata
   - `questions.json` - 7 diagnostic questions with categories
   - `rubric.json` - AI evaluation criteria and weightings
   - `report.txt` - Original radiology report for reference
   - `slices/` - DICOM image files organized by series

3. **AI Responses**: Temporary processing, not permanently stored
4. **Logs**: Application and nginx logs for monitoring and debugging

### **9.3 Error Handling & Fallback Systems**
1. **API Failures**: Graceful degradation with user-friendly error messages
2. **AI Unavailability**: Fallback scoring system maintains functionality
3. **DICOM Loading Issues**: Error display with retry mechanisms
4. **Network Issues**: Loading states and timeout handling
5. **Session Recovery**: Local storage backup for session continuity

---

## **PHASE 10: Technical Performance & Optimization**

### **10.1 Frontend Performance**
1. **Component Optimization**: React hooks for efficient rendering
2. **Code Splitting**: Vite builds optimized bundles
3. **Image Loading**: Lazy loading for medical imaging data
4. **State Management**: Efficient useState and useEffect patterns
5. **Memory Management**: Proper cleanup on component unmount

### **10.2 Backend Performance**
1. **Async Processing**: FastAPI async endpoints for concurrent requests
2. **AI Caching**: Intelligent caching of similar assessment patterns
3. **Database Ready**: Architecture supports PostgreSQL for scaling
4. **Container Optimization**: Docker containers with health checks
5. **Load Balancing**: nginx configuration for high availability

### **10.3 Security Implementation**
1. **HTTPS/SSL**: All communication encrypted with professional certificates
2. **CORS Configuration**: Restricted origins for API access
3. **Input Validation**: Pydantic models for request validation
4. **Rate Limiting**: Protection against abuse (100 requests/hour)
5. **Environment Security**: Sensitive data in environment variables

---

## **PHASE 11: Monitoring & Maintenance**

### **11.1 Health Monitoring**
1. **Container Health Checks**: Docker healthcheck commands
2. **API Endpoint Monitoring**: Regular health check endpoints
3. **Log Aggregation**: Comprehensive logging for debugging
4. **Performance Metrics**: Response time and error rate tracking
5. **Uptime Monitoring**: External monitoring of service availability

### **11.2 Deployment & Updates**
1. **Git Workflow**: Version control with production branch
2. **Build Process**: Automated frontend builds with npm/vite
3. **Container Updates**: Docker container rebuilding and redeployment
4. **Zero-Downtime Deployment**: Rolling updates with health checks
5. **Rollback Capability**: Quick rollback to previous working versions

---

## **PHASE 12: Educational Impact & Assessment**

### **12.1 Learning Effectiveness**
1. **ABR Alignment**: Assessment criteria match oral board standards
2. **Medical Accuracy**: Zero tolerance for AI hallucination through prompt engineering
3. **Progressive Learning**: Adaptive follow-up questions for weak areas
4. **Immediate Feedback**: Real-time assessment and educational guidance
5. **Skill Development**: Focus on diagnostic reasoning and clinical correlation

### **12.2 User Experience Design**
1. **Medical Professional Interface**: Styling appropriate for clinical education
2. **Intuitive Navigation**: Clear workflow progression and status indicators
3. **Professional Presentation**: Medical-grade interface design and terminology
4. **Accessibility**: Responsive design for various devices and environments
5. **Educational Context**: Case presentation mimicking real clinical scenarios

---

This comprehensive flow demonstrates how Casewise integrates React frontend technology, Python backend processing, OpenAI GPT-4o artificial intelligence, professional medical imaging, and educational assessment into a complete medical education platform that provides authentic, ABR-level diagnostic training for radiology residents.

The system successfully bridges the gap between traditional medical education and modern AI technology, providing a production-ready platform that delivers immediate, expert-level feedback on diagnostic reasoning while maintaining the highest standards of medical accuracy and educational effectiveness. 