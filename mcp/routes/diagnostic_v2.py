"""
Refactored diagnostic routes using the MCP orchestrator pattern
This is an example of how to migrate from the old monolithic approach
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
import logging

from ..orchestrator import SessionOrchestrator
from ..session import SessionStateManager
from ..core.exceptions import SessionNotFoundError, InvalidStateTransition

# Initialize components
router = APIRouter(prefix="/api/v2/diagnostic", tags=["diagnostic_v2"])
orchestrator = SessionOrchestrator()
session_manager = SessionStateManager(persistence_type="memory")

logger = logging.getLogger(__name__)


@router.post("/start_session")
async def start_session(
    case_id: str = Body(..., description="Case ID to start session with"),
    user_id: Optional[str] = Body(None, description="Optional user ID")
) -> Dict[str, Any]:
    """
    Start a new diagnostic session using the orchestrator
    """
    try:
        # Start session through orchestrator
        session_id = await orchestrator.start_session(case_id, user_id)
        
        # Get initial state
        state = await orchestrator.get_session_state(session_id)
        
        return {
            "session_id": session_id,
            "case_id": case_id,
            "state": state["state"],
            "message": "Session started successfully"
        }
        
    except Exception as e:
        logger.error(f"Error starting session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/action")
async def perform_action(
    session_id: str,
    action: str = Body(..., description="Action to perform"),
    data: Dict[str, Any] = Body(default={}, description="Action data")
) -> Dict[str, Any]:
    """
    Perform an action within a session (delegated to orchestrator)
    """
    try:
        # Process action through orchestrator
        result = await orchestrator.process_action(session_id, action, data)
        
        # Get updated state
        state = await orchestrator.get_session_state(session_id)
        
        return {
            "result": result,
            "state": state["state"],
            "progress": state["progress"]
        }
        
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    except InvalidStateTransition as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing action: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/state")
async def get_session_state(session_id: str) -> Dict[str, Any]:
    """
    Get current session state
    """
    try:
        state = await orchestrator.get_session_state(session_id)
        return state
        
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error getting session state: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/get_question")
async def get_next_question(session_id: str) -> Dict[str, Any]:
    """
    Get the next question in the diagnostic flow
    """
    try:
        # This is now handled by the orchestrator
        result = await orchestrator.process_action(
            session_id, 
            "get_question",
            {}
        )
        
        return result
        
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error getting question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/submit_answer")
async def submit_answer(
    session_id: str,
    question_id: str = Body(..., description="Question ID"),
    answer: str = Body(..., description="Student's answer")
) -> Dict[str, Any]:
    """
    Submit an answer and get grading/feedback
    """
    try:
        # Submit through orchestrator
        result = await orchestrator.process_action(
            session_id,
            "submit_answer",
            {
                "question_id": question_id,
                "answer": answer
            }
        )
        
        return result
        
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error submitting answer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/end")
async def end_session(session_id: str) -> Dict[str, Any]:
    """
    End a session and get final results
    """
    try:
        # End session through orchestrator
        summary = await orchestrator.end_session(session_id)
        
        return {
            "summary": summary,
            "message": "Session completed successfully"
        }
        
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/progress")
async def get_progress(session_id: str) -> Dict[str, Any]:
    """
    Get detailed progress for a session
    """
    try:
        # Get session from manager
        session_data = session_manager.get_session(session_id)
        
        # Calculate progress metrics
        progress = {
            "session_id": session_id,
            "case_id": session_data.case_id,
            "questions_answered": len(session_data.answers),
            "total_questions": session_data.total_questions,
            "current_score": session_data.get_average_score(),
            "category_scores": session_data.get_category_scores(),
            "time_elapsed_minutes": (
                session_data.updated_at - session_data.created_at
            ).total_seconds() / 60
        }
        
        return progress
        
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error getting progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Example of migrating specific functionality
@router.post("/session/{session_id}/request_teaching")
async def request_teaching_moment(
    session_id: str,
    question_id: str = Body(..., description="Question to get teaching for")
) -> Dict[str, Any]:
    """
    Request teaching feedback for a specific question
    """
    try:
        # This would call the teaching agent through orchestrator
        result = await orchestrator.process_action(
            session_id,
            "get_feedback",
            {
                "question_id": question_id,
                "type": "teaching"
            }
        )
        
        return result
        
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error getting teaching feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))