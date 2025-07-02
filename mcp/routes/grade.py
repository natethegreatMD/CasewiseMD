"""
Grading agent routes
"""

import json
import random
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional

router = APIRouter()

# Base path for demo cases (flexible for Docker and local development)
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

def generate_realistic_feedback(case_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Generate realistic feedback based on case metadata"""
    modality = metadata.get("modality", "unknown").upper()
    patient_id = metadata.get("patient_id", "unknown")
    
    # Generate realistic but dummy scores
    base_scores = [82, 85, 88, 90, 78, 85, 92, 80]  # Realistic score distribution
    scores = random.sample(base_scores, 4)
    
    category_scores = [
        {
            "category": "Image Interpretation",
            "score": scores[0],
            "max_score": 100,
            "percentage": scores[0],
            "feedback": f"Good interpretation of {modality} imaging findings. Clear identification of key features."
        },
        {
            "category": "Differential Diagnosis",
            "score": scores[1],
            "max_score": 100,
            "percentage": scores[1],
            "feedback": "Solid differential diagnosis with appropriate considerations. Good clinical reasoning."
        },
        {
            "category": "Clinical Correlation",
            "score": scores[2],
            "max_score": 100,
            "percentage": scores[2],
            "feedback": "Effective correlation of imaging findings with clinical presentation."
        },
        {
            "category": "Recommendation",
            "score": scores[3],
            "max_score": 100,
            "percentage": scores[3],
            "feedback": "Appropriate recommendations for follow-up and management."
        }
    ]
    
    total_score = sum(scores) / len(scores)
    
    return {
        "total_score": round(total_score, 1),
        "category_scores": category_scores,
        "passed": total_score >= 70.0
    }

@router.post("/grade")
async def grade_submission(submission_data: Dict[str, Any]):
    """
    Grade a case submission
    Returns realistic dummy grading data based on case information
    """
    try:
        session_id = submission_data.get("session_id", "unknown")
        case_id = submission_data.get("case_id", "case001")
        answers = submission_data.get("answers", {})
        
        # Read case metadata for realistic feedback
        try:
            metadata = read_case_metadata(case_id)
        except HTTPException:
            # If case not found, use generic metadata
            metadata = {"modality": "CT", "patient_id": "unknown"}
        
        # Generate realistic feedback
        feedback_data = generate_realistic_feedback(case_id, metadata)
        
        grading_id = f"grade-{session_id}-{case_id}"
        
        return {
            "grading_id": grading_id,
            "session_id": session_id,
            "case_id": case_id,
            "agent": "grade",
            "status": "completed",
            "overall_score": {
                "total_points": feedback_data["total_score"],
                "max_points": 100.0,
                "percentage": feedback_data["total_score"],
                "grade": "A" if feedback_data["total_score"] >= 90 else "B+" if feedback_data["total_score"] >= 85 else "B" if feedback_data["total_score"] >= 80 else "C+",
                "passed": feedback_data["passed"]
            },
            "category_scores": feedback_data["category_scores"],
            "detailed_feedback": {
                "strengths": [
                    "Systematic approach to image interpretation",
                    "Good clinical correlation with imaging findings",
                    "Appropriate use of medical terminology"
                ],
                "areas_for_improvement": [
                    "Consider expanding differential diagnosis",
                    "Include more specific imaging descriptors",
                    "Elaborate on clinical significance"
                ],
                "next_steps": [
                    "Review similar cases for pattern recognition",
                    "Practice structured reporting techniques",
                    f"Study {metadata.get('modality', 'imaging')} anatomy and pathology"
                ]
            },
            "case_specific_feedback": {
                "modality": metadata.get("modality", "unknown"),
                "patient_id": metadata.get("patient_id", "unknown"),
                "rubric_used": metadata.get("rubric_id", f"rubric-{case_id}"),
                "case_difficulty": "intermediate"
            },
            "metadata": {
                "graded_by": "grading-agent-filesystem-v1.0",
                "graded_at": "2024-12-25T00:00:00Z",
                "rubric_version": metadata.get("prompt_version", "v1"),
                "processing_time_ms": random.randint(1500, 3500),
                "ai_grading": "dummy_mode"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error grading submission: {str(e)}")

@router.get("/grade/{grading_id}")
async def get_grade_result(grading_id: str):
    """
    Retrieve grading results by ID
    Returns dummy grade summary data
    """
    try:
        # Extract case_id from grading_id if possible
        case_id = "case001"  # Default
        if "-" in grading_id:
            parts = grading_id.split("-")
            if len(parts) >= 3:
                case_id = parts[2]
        
        # Generate consistent dummy score based on grading_id
        random.seed(hash(grading_id) % 1000)  # Consistent random seed
        score = random.randint(75, 95)
        
        return {
            "grading_id": grading_id,
            "agent": "grade",
            "status": "completed",
            "retrieved_at": "2024-12-25T00:00:00Z",
            "case_id": case_id,
            "summary": {
                "total_score": score,
                "grade": "A" if score >= 90 else "B+" if score >= 85 else "B" if score >= 80 else "C+",
                "passed": score >= 70,
                "completion_time": f"{random.randint(10, 25)} minutes"
            },
            "metadata": {
                "ai_grading": "dummy_mode",
                "case_source": "filesystem"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving grade result: {str(e)}") 