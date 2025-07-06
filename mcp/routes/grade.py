"""
Grading agent routes with AI-powered assessment and follow-up questions
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime

from mcp.services.ai_grading import ai_grading_service
from mcp.services.rubric_loader import load_rubric
from mcp.routes.diagnostic import read_case_questions, read_case_metadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Base path for demo cases
DEMO_CASES_PATH = Path("/app/demo_cases") if Path("/app/demo_cases").exists() else Path("./demo_cases")

class GradeRequest(BaseModel):
    """Request model for grading submission"""
    case_id: str
    session_id: str
    answers: Dict[str, str]
    metadata: Optional[Dict[str, Any]] = None

@router.post("/grade")
async def grade_diagnostic_session(grade_data: Dict[str, Any]):
    """
    Grade a completed diagnostic session
    Returns scores, feedback, and follow-up questions for weak areas
    """
    try:
        case_id = grade_data.get("case_id", "case001")
        session_id = grade_data.get("session_id", "unknown")
        answers = grade_data.get("answers", {})
        
        if not answers:
            raise HTTPException(status_code=400, detail="No answers provided for grading")
        
        # Load rubric for this case
        rubric = load_rubric(case_id)
        if not rubric:
            raise HTTPException(status_code=404, detail=f"Rubric not found for case {case_id}")
        
        # Load questions for context
        questions = read_case_questions(case_id)
        
        # Grade the answers using AI service
        grading_results = await ai_grading_service.grade_answers(answers, case_id, rubric)
        
        # Format response for frontend
        formatted_response = _format_grading_response(
            grading_results, case_id, session_id, questions, rubric
        )
        
        return formatted_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error grading diagnostic session: {str(e)}")

@router.post("/evaluate-followup")
async def evaluate_followup_answers(evaluation_data: Dict[str, Any]):
    """
    Evaluate student's follow-up answers and provide personalized feedback
    """
    try:
        case_id = evaluation_data.get("case_id", "case001")
        session_id = evaluation_data.get("session_id", "unknown")
        followup_answers = evaluation_data.get("followup_answers", {})
        original_followup_questions = evaluation_data.get("original_followup_questions", [])
        original_grading = evaluation_data.get("original_grading", {})
        
        if not followup_answers:
            raise HTTPException(status_code=400, detail="No follow-up answers provided for evaluation")
        
        if not original_followup_questions:
            raise HTTPException(status_code=400, detail="Original follow-up questions required for evaluation")
        
        # Evaluate follow-up answers using AI service
        evaluation_results = await ai_grading_service.evaluate_followup_answers(
            followup_answers, 
            original_followup_questions, 
            case_id, 
            original_grading
        )
        
        # Format response with comprehensive feedback
        response = {
            "evaluation_id": f"followup-eval-{case_id}-{session_id}",
            "case_id": case_id,
            "session_id": session_id,
            "status": "completed",
            "evaluation_method": evaluation_results.get("evaluation_method", "ai_gpt4o"),
            
            # Individual follow-up evaluations
            "followup_evaluations": evaluation_results.get("followup_evaluations", []),
            
            # Learning improvement analysis
            "learning_improvement": evaluation_results.get("learning_improvement", {}),
            
            # Overall feedback on follow-up performance
            "overall_followup_feedback": evaluation_results.get("overall_followup_feedback", ""),
            
            # Updated assessment incorporating follow-up
            "updated_assessment": evaluation_results.get("updated_assessment", {}),
            
            # Metadata
            "metadata": {
                "followup_questions_answered": len(followup_answers),
                "total_followup_questions": len(original_followup_questions),
                "completion_rate": len(followup_answers) / max(1, len(original_followup_questions)) * 100,
                "evaluation_timestamp": datetime.now().isoformat(),
                "case_type": "ovarian_cancer"
            }
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating follow-up answers: {str(e)}")

def _load_case_questions(case_id: str) -> List[Dict[str, Any]]:
    """Load questions for case context"""
    try:
        questions_path = DEMO_CASES_PATH / case_id / "questions.json"
        if questions_path.exists():
            with open(questions_path, 'r') as f:
                questions_data = json.load(f)
                return questions_data.get("core_questions", [])
    except Exception as e:
        logger.warning(f"Could not load questions for {case_id}: {str(e)}")
    
    return []

def _get_default_rubric() -> Dict[str, Any]:
    """Default rubric if none found"""
    return {
        "rubric_id": "default_abr_rubric",
        "version": "2.0",
        "case_type": "radiology_oral_board",
        "description": "ABR-style oral board examination rubric",
        "categories": {
            "Image Interpretation": {
                "weight": 35,
                "description": "Systematic evaluation of imaging findings",
                "criteria": [
                    "Accurate identification of key imaging findings",
                    "Systematic approach to image interpretation",
                    "Appropriate use of imaging terminology",
                    "Recognition of normal vs abnormal findings"
                ]
            },
            "Differential Diagnosis": {
                "weight": 25,
                "description": "Appropriate differential diagnosis formulation",
                "criteria": [
                    "Comprehensive differential diagnosis list",
                    "Logical prioritization of diagnoses",
                    "Consideration of clinical context",
                    "Appropriate reasoning for differential"
                ]
            },
            "Clinical Correlation": {
                "weight": 15,
                "description": "Integration of imaging with clinical presentation",
                "criteria": [
                    "Understanding of clinical presentation",
                    "Correlation of imaging with symptoms",
                    "Appropriate urgency assessment",
                    "Clinical staging knowledge"
                ]
            },
            "Management Recommendations": {
                "weight": 10,
                "description": "Appropriate next steps and follow-up",
                "criteria": [
                    "Appropriate additional workup",
                    "Relevant laboratory tests",
                    "Specialist referral recommendations",
                    "Treatment planning consideration"
                ]
            },
            "Communication & Organization": {
                "weight": 10,
                "description": "Clear and professional presentation",
                "criteria": [
                    "Organized presentation of findings",
                    "Professional communication style",
                    "Appropriate medical terminology",
                    "Clear and concise reporting"
                ]
            },
            "Professional Judgment": {
                "weight": 5,
                "description": "Critical finding recognition and ethics",
                "criteria": [
                    "Recognition of critical findings",
                    "Understanding of communication urgency",
                    "Ethical considerations",
                    "Professional responsibility awareness"
                ]
            },
            "Safety Considerations": {
                "weight": 5,
                "description": "Radiation safety and imaging appropriateness",
                "criteria": [
                    "Radiation dose awareness",
                    "Contrast considerations",
                    "Alternative imaging modalities",
                    "ALARA principles"
                ]
            }
        }
    }

def _format_grading_response(
    grading_results: Dict[str, Any], 
    case_id: str, 
    session_id: str,
    questions: List[Dict[str, Any]],
    rubric: Dict[str, Any]
) -> Dict[str, Any]:
    """Format grading response with all required information"""
    
    # Extract core data
    category_scores = grading_results.get("category_scores", {})
    total_score = grading_results.get("total_score", 0)
    overall_percentage = grading_results.get("overall_percentage", 0)
    follow_up_questions = grading_results.get("follow_up_questions", [])
    
    # Build category results for detailed breakdown
    category_results = []
    
    # Handle different rubric formats
    rubric_categories = rubric.get("categories", [])
    if isinstance(rubric_categories, list):
        # New format: categories is an array
        category_weights = {cat.get("name"): cat.get("weight", 0) * 100 for cat in rubric_categories}
    else:
        # Old format: categories is an object 
        category_weights = {name: data.get("weight", 0) for name, data in rubric_categories.items()}
    
    for category, score_data in category_scores.items():
        weight = category_weights.get(category, 10)
        category_results.append({
            "category_name": category,
            "name": category,  # Frontend expects both fields
            "score": score_data.get("score", 0),
            "max_score": 100,
            "percentage": score_data.get("percentage", 0),
            "feedback": score_data.get("feedback", ""),
            "weight": weight,
            "criteria_results": [
                {
                    "criterion_name": "Overall Assessment",
                    "score": score_data.get("score", 0),
                    "max_score": 100,
                    "feedback": score_data.get("feedback", "")
                }
            ]
        })
    
    # Determine if student passed (70% threshold)
    passed = overall_percentage >= 70
    
    # Build comprehensive response
    response = {
        "grading_id": f"grade-{case_id}-{session_id}",
        "case_id": case_id,
        "session_id": session_id,
        "agent": "grade",
        "status": "completed",
        "total_score": total_score,
        "total_possible": 100,
        "max_score": 100,
        "overall_percentage": overall_percentage,
        "percentage": overall_percentage,  # Frontend expects this field
        "passed": passed,
        "confidence": 0.9 if grading_results.get("grading_method") == "ai_gpt4o" else 0.6,
        
        # Detailed category breakdown
        "category_results": category_results,
        
        # Feedback and guidance
        "overall_feedback": grading_results.get("overall_feedback", "Grading completed successfully"),
        "strengths": grading_results.get("strengths", []),
        "areas_for_improvement": grading_results.get("areas_for_improvement", []),
        "abr_readiness": grading_results.get("abr_readiness", "Assessment completed"),
        
        # Follow-up questions for learning
        "follow_up_questions": follow_up_questions,
        
        # Case-specific context
        "case_specific_feedback": {
            "ai_grading": grading_results.get("grading_method") == "ai_gpt4o",
            "rubric_version": rubric.get("version", "1.0"),
            "case_difficulty": "intermediate",
            "total_questions": len(questions),
            "rubric_categories": len(category_scores),
            "follow_up_count": len(follow_up_questions)
        },
        
        # Questions for context
        "questions_asked": [
            {
                "step": q.get("step", i+1),
                "category": q.get("rubric_category", "Unknown"),
                "question": q.get("question", ""),
                "type": q.get("type", "free_text")
            }
            for i, q in enumerate(questions)
        ],
        
        # Metadata
        "metadata": {
            "graded_by": "ai-grading-gpt4o" if grading_results.get("grading_method") == "ai_gpt4o" else "content-analysis-fallback",
            "graded_at": "2024-12-25T00:00:00Z",
            "ai_grading": grading_results.get("grading_method") == "ai_gpt4o",
            "fallback_used": grading_results.get("grading_method") == "fallback_content_analysis",
            "grading_method": grading_results.get("grading_method", "unknown"),
            "rubric_id": rubric.get("rubric_id", f"rubric-{case_id}"),
            "processing_time_ms": 0,
            "agent_version": "2.0.0"
        }
    }
    
    return response

@router.get("/grade-status/{case_id}")
async def get_grade_status(case_id: str):
    """
    Get grading status and capability for a case
    """
    try:
        # Check if rubric exists
        rubric = load_rubric(case_id)
        has_rubric = rubric is not None
        
        # Check if AI grading is available
        api_key = ai_grading_service.client.api_key if hasattr(ai_grading_service, 'client') else None
        ai_available = bool(api_key)
        
        return {
            "case_id": case_id,
            "grading_available": True,
            "ai_grading_available": ai_available,
            "rubric_available": has_rubric,
            "follow_up_questions_available": True,
            "grading_method": "ai_with_fallback" if ai_available else "content_analysis",
            "rubric_version": rubric.get("version", "1.0") if rubric else "default",
            "categories": list(rubric.get("categories", {}).keys()) if rubric else [],
            "estimated_time_seconds": 10 if ai_available else 2,
            "features": {
                "category_scoring": True,
                "detailed_feedback": True,
                "follow_up_questions": True,
                "abr_alignment": True,
                "adaptive_learning": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting grade status for {case_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get grade status: {str(e)}")

@router.get("/rubric/{case_id}")
async def get_case_rubric(case_id: str):
    """
    Get the grading rubric for a specific case
    """
    try:
        rubric = load_rubric(case_id)
        if not rubric:
            rubric = _get_default_rubric()
        
        return {
            "case_id": case_id,
            "rubric": rubric,
            "total_categories": len(rubric.get("categories", {})),
            "total_weight": sum(cat.get("weight", 0) for cat in rubric.get("categories", {}).values()),
            "description": rubric.get("description", ""),
            "version": rubric.get("version", "1.0")
        }
        
    except Exception as e:
        logger.error(f"Error getting rubric for {case_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get rubric: {str(e)}") 