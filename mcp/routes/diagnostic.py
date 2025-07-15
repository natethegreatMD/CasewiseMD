"""
Diagnostic agent routes
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional, List

router = APIRouter()

# Base path for demo cases (works for both Docker and local)
DEMO_CASES_PATH = Path("/app/demo_cases") if Path("/app/demo_cases").exists() else Path("./demo_cases")

def read_case_metadata(case_id: str) -> Dict[str, Any]:
    """Read metadata.json for a specific case"""
    metadata_path = DEMO_CASES_PATH / case_id / "metadata.json"
    
    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail=f"Metadata not found for case {case_id}")
    
    try:
        with open(metadata_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in metadata for case {case_id}")

def read_case_report(case_id: str) -> Optional[str]:
    """Read report.txt if it exists"""
    report_path = DEMO_CASES_PATH / case_id / "report.txt"
    
    if report_path.exists():
        try:
            with open(report_path, 'r') as f:
                return f.read().strip()
        except Exception:
            return None
    
    return None

def read_case_questions(case_id: str) -> List[Dict[str, Any]]:
    """Read structured questions from questions.json for a specific case"""
    questions_path = DEMO_CASES_PATH / case_id / "questions.json"
    
    if questions_path.exists():
        try:
            with open(questions_path, 'r') as f:
                questions_data = json.load(f)
                return questions_data.get("core_questions", [])
        except json.JSONDecodeError:
            # Fall back to generated questions if JSON is invalid
            pass
        except Exception:
            # Fall back to generated questions if file can't be read
            pass
    
    # Fallback to generated questions if no questions.json file
    return generate_fallback_questions(case_id)

def generate_fallback_questions(case_id: str) -> List[Dict[str, Any]]:
    """Generate fallback questions when questions.json is not available"""
    
    questions = [
        {
            "step": 1,
            "rubric_category": "Image Interpretation",
            "question": "Based on the imaging provided, what are your key imaging findings?",
            "type": "free_text",
            "context": "Review the images and describe the significant findings.",
            "hint": "Look for abnormal densities, masses, fluid collections, or structural changes. Use systematic approach to image interpretation.",
            "options": None
        },
        {
            "step": 2,
            "rubric_category": "Differential Diagnosis",
            "question": "What is your differential diagnosis based on the imaging findings?",
            "type": "free_text",
            "context": "Provide a ranked differential diagnosis with your most likely diagnosis first.",
            "hint": "Consider the patient demographics, location of findings, imaging characteristics, and clinical context. List 3-5 differential diagnoses in order of likelihood.",
            "options": None
        },
        {
            "step": 3,
            "rubric_category": "Clinical Correlation",
            "question": "How do these findings correlate with the likely clinical presentation?",
            "type": "free_text",
            "context": "Consider the clinical significance and correlation of your imaging findings.",
            "hint": "Think about symptoms, clinical presentation, and the urgency of your findings.",
            "options": None
        },
        {
            "step": 4,
            "rubric_category": "Management Recommendations",
            "question": "What additional workup or follow-up would you recommend?",
            "type": "free_text",
            "context": "Consider any additional imaging, laboratory tests, or clinical follow-up that would be appropriate.",
            "hint": "Think about confirmatory tests, staging studies, laboratory values, or specialized imaging that would help confirm your diagnosis or guide treatment planning.",
            "options": None
        },
        {
            "step": 5,
            "rubric_category": "Communication & Organization",
            "question": "Provide a structured summary of your findings for the referring physician.",
            "type": "free_text",
            "context": "Organize your findings clearly and professionally as you would in a radiology report.",
            "hint": "Structure: Brief clinical context, key findings, impression, recommendations. Use clear, professional language.",
            "options": None
        },
        {
            "step": 6,
            "rubric_category": "Professional Judgment",
            "question": "Are there any critical findings that require urgent communication?",
            "type": "free_text",
            "context": "Consider the urgency and professional responsibilities related to your findings.",
            "hint": "Think about what constitutes a critical finding and how you would handle urgent communication.",
            "options": None
        },
        {
            "step": 7,
            "rubric_category": "Safety Considerations",
            "question": "Comment on the imaging technique and any safety considerations.",
            "type": "free_text",
            "context": "Consider radiation safety, contrast use, and appropriateness of imaging approach.",
            "hint": "Think about radiation dose, contrast considerations, alternative imaging modalities, and safety protocols.",
            "options": None
        }
    ]
    
    return questions

@router.get("/diagnostic-session")
async def get_diagnostic_session(case_id: str = Query(default="case001", description="Case ID for diagnostic session")):
    """
    Start a new diagnostic session for a specific case
    Reads from real case data and structured questions in demo_cases directory
    """
    try:
        # Read case metadata
        metadata = read_case_metadata(case_id)
        
        # Read case report if available
        report = read_case_report(case_id)
        
        # Load structured questions for this case
        questions = read_case_questions(case_id)
        
        # Get first question
        first_question = questions[0] if questions else {
            "step": 1,
            "rubric_category": "Image Interpretation",
            "question": "What is your assessment of this case?",
            "type": "free_text",
            "context": "Please provide your clinical assessment.",
            "hint": "Use a systematic approach to evaluate the imaging findings.",
            "options": None
        }
        
        return {
            "session_id": f"diag-{case_id}-001",
            "agent": "diagnostic",
            "status": "active",
            "case_id": case_id,
            "current_step": 1,
            "total_steps": len(questions),
            "completed": False,
            "answers": {},  # Empty answers object for new session
            "case_info": {
                "patient_id": metadata.get("patient_id", "unknown"),
                "modality": metadata.get("modality", "unknown"),
                "orientations": metadata.get("orientation", []),
                "series_count": len(metadata.get("series", {}))
            },
            "current_question": first_question,
            "all_questions": questions,  # Include all questions for frontend reference
            "rubric_aligned": True,  # Indicate this uses structured rubric-aligned questions
            "progress": {
                "completed_steps": 0,
                "current_step": 1,
                "total_steps": len(questions),
                "percentage": 0
            },
            "metadata": {
                "agent_version": "2.0.0",
                "case_source": "filesystem",
                "questions_source": "structured" if len(questions) == 7 else "fallback",
                "rubric_id": metadata.get("rubric_id", f"rubric-{case_id}")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating diagnostic session: {str(e)}")

@router.post("/diagnostic-answer")
async def submit_diagnostic_answer(answer_data: Dict[str, Any]):
    """
    Submit answer to diagnostic session
    Process answer and return next question or completion status
    """
    try:
        session_id = answer_data.get("session_id", "unknown")
        case_id = answer_data.get("case_id", "case001")
        current_step = answer_data.get("current_step", 1)
        answer = answer_data.get("answer", "")
        previous_answers = answer_data.get("answers", {})
        
        # Read case metadata to get question count
        metadata = read_case_metadata(case_id)
        questions = read_case_questions(case_id)
        
        # Update answers with current response
        updated_answers = previous_answers.copy()
        updated_answers[str(current_step)] = answer
        
        next_step = current_step + 1
        is_completed = next_step > len(questions)
        
        # Get next question if not completed (this becomes the current question)
        current_question = None
        if not is_completed and next_step <= len(questions):
            current_question = questions[next_step - 1]  # Convert to 0-based index
        
        response = {
            "session_id": session_id,
            "case_id": case_id,
            "agent": "diagnostic",
            "status": "completed" if is_completed else "processed",
            "answer_received": answer,
            "current_step": current_step,
            "next_step": next_step if not is_completed else None,
            "completed": is_completed,
            "answers": updated_answers,  # Include all answers so far
            "feedback": {
                "message": f"Answer for step {current_step} received and processed",
                "acknowledgment": "Thank you for your response. Your answer has been recorded.",
                "rubric_category": questions[current_step - 1].get("rubric_category", "Unknown") if current_step <= len(questions) else None
            }
        }
        
        # Add current question (was next_question) if not completed
        if current_question:
            response["current_question"] = current_question
        
        # Add completion message if done
        if is_completed:
            response["completion_message"] = "Diagnostic session completed. Ready for grading."
            response["progress"] = {
                "completed_steps": len(questions),
                "current_step": len(questions),
                "total_steps": len(questions),
                "percentage": 100
            }
        else:
            response["progress"] = {
                "completed_steps": current_step,
                "current_step": next_step,
                "total_steps": len(questions),
                "percentage": (current_step / len(questions)) * 100
            }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing diagnostic answer: {str(e)}") 