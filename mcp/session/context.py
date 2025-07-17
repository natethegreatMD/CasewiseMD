"""
Session context manager for providing context to agents
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from ..core.interfaces import SessionContext
from ..core.models import Question, Answer, GradingResult, TeachingPoint
from .models import SessionData


class SessionContextManager:
    """
    Manages the conversion between SessionData (storage) and SessionContext (runtime).
    Provides context objects for agents to use during execution.
    """
    
    @staticmethod
    def create_context_from_session(session_data: SessionData) -> SessionContext:
        """Create a SessionContext from SessionData"""
        context = SessionContext(
            session_id=session_data.session_id,
            case_id=session_data.case_id
        )
        
        # Copy state
        context.state = session_data.state.value
        context.current_question_index = session_data.current_question_index
        
        # Copy answers
        for answer in session_data.answers:
            context.answers.append({
                "question_id": answer.question_id,
                "answer": answer.text,
                "timestamp": answer.timestamp,
                "metadata": answer.metadata
            })
        
        # Copy grades
        for grade in session_data.grades:
            context.grades.append({
                "question_id": grade.question_id,
                "score": grade.score,
                "feedback": grade.feedback,
                "timestamp": datetime.utcnow(),  # Add timestamp
                "metadata": grade.metadata
            })
        
        # Copy follow-ups completed
        context.follow_ups_completed = [
            q.id for q in session_data.follow_up_questions 
            if any(a.question_id == q.id for a in session_data.answers)
        ]
        
        # Copy teaching points delivered
        context.teaching_points_delivered = [tp.id for tp in session_data.teaching_points]
        
        # Copy metadata
        context.metadata = session_data.metadata.copy()
        if session_data.user_id:
            context.metadata["user_id"] = session_data.user_id
        
        # Copy timestamps
        context.created_at = session_data.created_at
        context.updated_at = session_data.updated_at
        
        return context
    
    @staticmethod
    def update_session_from_context(session_data: SessionData, context: SessionContext) -> SessionData:
        """Update SessionData from a SessionContext after agent execution"""
        
        # Update state
        session_data.state = context.state
        session_data.current_question_index = context.current_question_index
        
        # Update metadata
        session_data.metadata.update(context.metadata)
        
        # Note: Individual answers, grades, etc. should be added through
        # specific methods rather than bulk update to maintain data integrity
        
        session_data.update_timestamp()
        
        return session_data
    
    @staticmethod
    def create_agent_context(session_data: SessionData, 
                           include_history: bool = True,
                           include_grades: bool = True) -> Dict[str, Any]:
        """
        Create a context dictionary for agents with relevant session information.
        This is a simplified view that agents can easily work with.
        """
        context = {
            "session_id": session_data.session_id,
            "case_id": session_data.case_id,
            "current_state": session_data.state.value,
            "progress": {
                "current_question": session_data.current_question_index + 1,
                "total_questions": session_data.total_questions,
                "questions_answered": len(session_data.answers),
                "average_score": session_data.get_average_score()
            }
        }
        
        if include_history:
            # Include recent Q&A history
            context["recent_qa"] = []
            for i in range(min(3, len(session_data.questions_asked))):
                idx = -(i + 1)  # Get from end
                if abs(idx) <= len(session_data.questions_asked):
                    q = session_data.questions_asked[idx]
                    a = next((a for a in session_data.answers if a.question_id == q.id), None)
                    context["recent_qa"].append({
                        "question": q.text,
                        "answer": a.text if a else None,
                        "category": q.category
                    })
        
        if include_grades and session_data.grades:
            # Include grading summary
            context["grading_summary"] = {
                "average_score": session_data.get_average_score(),
                "category_scores": session_data.get_category_scores(),
                "weak_areas": [
                    cat for cat, score in session_data.get_category_scores().items()
                    if score < 0.7
                ]
            }
        
        return context
    
    @staticmethod
    def get_question_context(session_data: SessionData, question_id: str) -> Dict[str, Any]:
        """Get context specific to a question"""
        question = next((q for q in session_data.questions_asked if q.id == question_id), None)
        answer = next((a for a in session_data.answers if a.question_id == question_id), None)
        grade = next((g for g in session_data.grades if g.question_id == question_id), None)
        
        return {
            "question": question.dict() if question else None,
            "answer": answer.dict() if answer else None,
            "grade": grade.dict() if grade else None,
            "has_follow_up": any(q.metadata.get("parent_question_id") == question_id 
                                for q in session_data.follow_up_questions)
        }