"""
Diagnostic agent routes
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional

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

def generate_case_questions(case_id: str, metadata: Dict[str, Any], report: Optional[str] = None) -> list:
    """Generate diagnostic questions based on case metadata"""
    modality = metadata.get("modality", "unknown").upper()
    patient_id = metadata.get("patient_id", "unknown")
    
    questions = [
        {
            "step": 1,
            "question": f"Based on the {modality} imaging provided, what are your key imaging findings?",
            "type": "free_text",
            "context": f"Patient ID: {patient_id}. Review the {modality} images and describe the significant findings.",
            "options": None
        },
        {
            "step": 2,
            "question": "What is your differential diagnosis based on the imaging findings?",
            "type": "free_text",
            "context": "Provide a ranked differential diagnosis with your most likely diagnosis first.",
            "options": None
        },
        {
            "step": 3,
            "question": "What is your most likely diagnosis?",
            "type": "free_text",
            "context": "Based on your imaging interpretation, what is the most likely diagnosis?",
            "options": None
        },
        {
            "step": 4,
            "question": "What additional workup or follow-up would you recommend?",
            "type": "free_text",
            "context": "Consider any additional imaging, laboratory tests, or clinical follow-up that would be appropriate.",
            "options": None
        },
        {
            "step": 5,
            "question": "What is the clinical significance of your findings?",
            "type": "free_text",
            "context": "Discuss the clinical implications and urgency of your findings.",
            "options": None
        }
    ]
    
    return questions

@router.get("/diagnostic-session")
async def get_diagnostic_session(case_id: str = Query(default="case001", description="Case ID for diagnostic session")):
    """
    Start a new diagnostic session for a specific case
    Reads from real case data in demo_cases directory
    """
    try:
        # Read case metadata
        metadata = read_case_metadata(case_id)
        
        # Read case report if available
        report = read_case_report(case_id)
        
        # Generate questions for this case
        questions = generate_case_questions(case_id, metadata, report)
        
        # Get first question
        first_question = questions[0] if questions else {
            "step": 1,
            "question": "What is your assessment of this case?",
            "type": "free_text",
            "context": "Please provide your clinical assessment.",
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
            "progress": {
                "completed_steps": 0,
                "current_step": 1,
                "total_steps": len(questions),
                "percentage": 0
            },
            "metadata": {
                "agent_version": "1.0.0",
                "case_source": "filesystem",
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
        
        # Read case metadata to get question count
        metadata = read_case_metadata(case_id)
        questions = generate_case_questions(case_id, metadata)
        
        next_step = current_step + 1
        is_completed = next_step > len(questions)
        
        # Get next question if not completed
        next_question = None
        if not is_completed and next_step <= len(questions):
            next_question = questions[next_step - 1]  # Convert to 0-based index
        
        response = {
            "session_id": session_id,
            "case_id": case_id,
            "agent": "diagnostic",
            "status": "completed" if is_completed else "processed",
            "answer_received": answer,
            "current_step": current_step,
            "next_step": next_step if not is_completed else None,
            "completed": is_completed,
            "feedback": {
                "message": f"Answer for step {current_step} received and processed",
                "acknowledgment": "Thank you for your response. Your answer has been recorded."
            }
        }
        
        # Add next question if not completed
        if next_question:
            response["next_question"] = next_question
        
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