"""
Main Session Orchestrator that coordinates all agents and manages session flow
"""

import asyncio
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..core.interfaces import (
    OrchestratorInterface, 
    SessionContext, 
    AgentRequest,
    AgentResponse
)
from ..core.models import SessionState, Question, Answer, GradingResult
from ..core.exceptions import (
    SessionNotFoundError, 
    InvalidStateTransition,
    AgentExecutionError
)
from .flow_states import FlowStateMachine, FlowState

# Import agents (to be created)
# from ..agents.grading import GradingAgent
# from ..agents.questions import QuestionAgent
# from ..agents.teaching import TeachingAgent
# from ..agents.reference import ReferenceAgent


class SessionOrchestrator(OrchestratorInterface):
    """
    Main orchestrator that manages the flow of diagnostic sessions.
    Coordinates between different agents and maintains session state.
    """
    
    def __init__(self):
        self.sessions: Dict[str, SessionContext] = {}
        self.state_machines: Dict[str, FlowStateMachine] = {}
        
        # Initialize agents (placeholder for now)
        # self.grading_agent = GradingAgent()
        # self.question_agent = QuestionAgent()
        # self.teaching_agent = TeachingAgent()
        # self.reference_agent = ReferenceAgent()
        
        # For now, we'll use placeholder values
        self.total_questions = 7  # ABR categories
        self.follow_up_threshold = 0.7  # Score below this triggers follow-up
    
    async def start_session(self, case_id: str, user_id: Optional[str] = None) -> str:
        """Start a new diagnostic session"""
        session_id = str(uuid.uuid4())
        
        # Create session context
        context = SessionContext(session_id=session_id, case_id=case_id)
        if user_id:
            context.metadata["user_id"] = user_id
        
        # Create state machine for this session
        state_machine = FlowStateMachine()
        
        # Store session and state machine
        self.sessions[session_id] = context
        self.state_machines[session_id] = state_machine
        
        # Transition to case loaded state
        state_machine.transition(FlowState.CASE_LOADED, "load_case")
        context.state = FlowState.CASE_LOADED.value
        
        return session_id
    
    async def process_action(self, session_id: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an action within a session"""
        if session_id not in self.sessions:
            raise SessionNotFoundError(session_id)
        
        context = self.sessions[session_id]
        state_machine = self.state_machines[session_id]
        
        # Validate action is allowed in current state
        if action not in state_machine.get_valid_actions():
            raise InvalidStateTransition(
                state_machine.current_state.value,
                f"action: {action}"
            )
        
        # Route action to appropriate handler
        if action == "start_questions":
            return await self._handle_start_questions(session_id, context, state_machine)
        elif action == "get_question":
            return await self._handle_get_question(session_id, context, state_machine)
        elif action == "submit_answer":
            return await self._handle_submit_answer(session_id, data, context, state_machine)
        elif action == "get_feedback":
            return await self._handle_get_feedback(session_id, context, state_machine)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get the current state of a session"""
        if session_id not in self.sessions:
            raise SessionNotFoundError(session_id)
        
        context = self.sessions[session_id]
        state_machine = self.state_machines[session_id]
        
        return {
            "session_id": session_id,
            "case_id": context.case_id,
            "state": state_machine.get_state_info(),
            "progress": context.get_current_progress(),
            "metadata": context.metadata
        }
    
    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a session and return final results"""
        if session_id not in self.sessions:
            raise SessionNotFoundError(session_id)
        
        context = self.sessions[session_id]
        
        # Calculate final scores
        overall_score = self._calculate_overall_score(context)
        category_scores = self._calculate_category_scores(context)
        
        # Create session summary
        summary = {
            "session_id": session_id,
            "case_id": context.case_id,
            "overall_score": overall_score,
            "category_scores": category_scores,
            "questions_answered": len(context.answers),
            "follow_ups_completed": len(context.follow_ups_completed),
            "teaching_points_viewed": len(context.teaching_points_delivered),
            "duration_minutes": (datetime.utcnow() - context.created_at).total_seconds() / 60
        }
        
        # Clean up session
        del self.sessions[session_id]
        del self.state_machines[session_id]
        
        return summary
    
    # Private handler methods
    
    async def _handle_start_questions(self, session_id: str, context: SessionContext, 
                                     state_machine: FlowStateMachine) -> Dict[str, Any]:
        """Handle starting the question flow"""
        state_machine.transition(FlowState.ASKING_DIAGNOSTIC, "start_questions")
        context.state = FlowState.ASKING_DIAGNOSTIC.value
        
        return {
            "status": "ready",
            "message": "Ready to begin diagnostic questions",
            "total_questions": self.total_questions
        }
    
    async def _handle_get_question(self, session_id: str, context: SessionContext,
                                  state_machine: FlowStateMachine) -> Dict[str, Any]:
        """Get the next question for the user"""
        # For now, return a placeholder question
        # In real implementation, this would call the QuestionAgent
        
        question_index = context.current_question_index
        if question_index >= self.total_questions:
            state_machine.transition(FlowState.SESSION_COMPLETE, "all_complete")
            return {"status": "complete", "message": "All questions answered"}
        
        # Placeholder question
        question = {
            "id": f"q_{question_index + 1}",
            "text": f"Diagnostic question {question_index + 1} of {self.total_questions}",
            "category": self._get_abr_category(question_index),
            "type": "diagnostic"
        }
        
        state_machine.transition(FlowState.AWAITING_ANSWER, "ask_question")
        context.state = FlowState.AWAITING_ANSWER.value
        
        return {
            "question": question,
            "question_number": question_index + 1,
            "total_questions": self.total_questions
        }
    
    async def _handle_submit_answer(self, session_id: str, data: Dict[str, Any],
                                   context: SessionContext, state_machine: FlowStateMachine) -> Dict[str, Any]:
        """Handle answer submission and trigger grading"""
        answer_text = data.get("answer", "")
        question_id = data.get("question_id", "")
        
        # Record answer
        context.add_answer(question_id, answer_text)
        
        # Transition to grading
        state_machine.transition(FlowState.GRADING_ANSWER, "submit_answer")
        
        # For now, return a placeholder grade
        # In real implementation, this would call the GradingAgent
        score = 0.8  # Placeholder score
        feedback = "Good answer with strong reasoning."
        
        context.add_grade(question_id, score, feedback)
        
        # Decide next action
        state_machine.transition(FlowState.DECIDING_FOLLOW_UP, "grade_complete")
        
        # Check if follow-up is needed
        needs_follow_up = score < self.follow_up_threshold
        
        if needs_follow_up:
            state_machine.transition(FlowState.ASKING_FOLLOW_UP, "needs_follow_up")
            return {
                "status": "follow_up_needed",
                "score": score,
                "feedback": feedback,
                "message": "Follow-up questions available to improve understanding"
            }
        else:
            context.current_question_index += 1
            if context.current_question_index < self.total_questions:
                state_machine.transition(FlowState.ASKING_DIAGNOSTIC, "next_question")
                return {
                    "status": "next_question",
                    "score": score,
                    "feedback": feedback
                }
            else:
                state_machine.transition(FlowState.SESSION_COMPLETE, "all_complete")
                return {
                    "status": "complete",
                    "score": score,
                    "feedback": feedback
                }
    
    async def _handle_get_feedback(self, session_id: str, context: SessionContext,
                                  state_machine: FlowStateMachine) -> Dict[str, Any]:
        """Get teaching feedback for a question"""
        # For now, return placeholder teaching content
        # In real implementation, this would call the TeachingAgent
        
        teaching_content = {
            "topic": "Diagnostic Reasoning",
            "content": "Here's a teaching point about the diagnostic approach...",
            "references": ["Reference 1", "Reference 2"]
        }
        
        context.teaching_points_delivered.append(f"teaching_{len(context.teaching_points_delivered)}")
        
        return {
            "teaching": teaching_content,
            "status": "teaching_delivered"
        }
    
    # Helper methods
    
    def _get_abr_category(self, index: int) -> str:
        """Get ABR category for question index"""
        categories = [
            "Image Interpretation",
            "Differential Diagnosis", 
            "Clinical Correlation",
            "Management Recommendations",
            "Communication & Organization",
            "Professional Judgment",
            "Safety Considerations"
        ]
        return categories[index] if index < len(categories) else "General"
    
    def _calculate_overall_score(self, context: SessionContext) -> float:
        """Calculate overall score for the session"""
        if not context.grades:
            return 0.0
        
        total_score = sum(grade["score"] for grade in context.grades)
        return total_score / len(context.grades)
    
    def _calculate_category_scores(self, context: SessionContext) -> Dict[str, float]:
        """Calculate scores by category"""
        # Placeholder implementation
        # In real implementation, would aggregate by actual categories
        return {
            "Image Interpretation": 0.85,
            "Differential Diagnosis": 0.75,
            "Clinical Correlation": 0.80,
            "Management Recommendations": 0.70,
            "Communication & Organization": 0.90,
            "Professional Judgment": 0.85,
            "Safety Considerations": 0.95
        }