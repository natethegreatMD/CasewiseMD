"""
Main Session Orchestrator that coordinates all agents and manages session flow
"""

import asyncio
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..core.interfaces import (
    OrchestratorInterface, 
    AgentRequest,
    AgentResponse
)
from ..core.models import SessionState, Question, Answer, GradingResult, QuestionType
from ..core.exceptions import (
    SessionNotFoundError, 
    InvalidStateTransition,
    AgentExecutionError
)
from ..session.models import SessionData
from ..session.state_manager import SessionStateManager
from .flow_states import FlowStateMachine, FlowState

# Import agents
from ..agents.grading.grading_agent_v2 import GradingAgentV2
from ..agents.questions import QuestionAgent
from ..agents.case import CaseAgent
# from ..agents.teaching import TeachingAgent
# from ..agents.reference import ReferenceAgent


class SessionOrchestrator(OrchestratorInterface):
    """
    Main orchestrator that manages the flow of diagnostic sessions.
    Coordinates between different agents and maintains session state.
    """
    
    def __init__(self, persistence_type: str = "memory", demo_cases_path: str = "demo_cases"):
        self.session_manager = SessionStateManager(persistence_type=persistence_type)
        self.state_machines: Dict[str, FlowStateMachine] = {}
        
        # Initialize agents
        self.grading_agent = GradingAgentV2()
        self.question_agent = QuestionAgent(demo_cases_path)
        self.case_agent = CaseAgent(demo_cases_path)
        # self.teaching_agent = TeachingAgent()
        # self.reference_agent = ReferenceAgent()
        
        # Configuration
        self.follow_up_threshold = 0.7  # Score below this triggers follow-up
    
    async def start_session(self, case_id: str, user_id: Optional[str] = None) -> str:
        """Start a new diagnostic session"""
        session_id = str(uuid.uuid4())
        
        # Create session using session manager
        session_data = self.session_manager.create_session(
            session_id=session_id, 
            case_id=case_id, 
            user_id=user_id
        )
        
        # Create state machine for this session
        state_machine = FlowStateMachine()
        
        # Store state machine
        self.state_machines[session_id] = state_machine
        
        # Transition to case loaded state
        state_machine.transition(FlowState.CASE_LOADED, "load_case")
        session_data.state = SessionState.CASE_LOADED
        
        # Load case information using CaseAgent
        case_request = AgentRequest(
            session_id=session_id,
            action="load_case_info",
            data={"case_id": case_id}
        )
        
        case_response = await self.case_agent.execute(case_request, session_data)
        if not case_response.success:
            raise Exception(f"Failed to load case info: {case_response.error}")
        
        # Load questions for the case using QuestionAgent
        questions_request = AgentRequest(
            session_id=session_id,
            action="load_case_questions",
            data={"case_id": case_id}
        )
        
        questions_response = await self.question_agent.execute(questions_request, session_data)
        if not questions_response.success:
            raise Exception(f"Failed to load questions: {questions_response.error}")
        
        self.session_manager.update_session(session_id, session_data)
        
        return session_id
    
    async def process_action(self, session_id: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an action within a session"""
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            raise SessionNotFoundError(session_id)
        
        state_machine = self.state_machines.get(session_id)
        if not state_machine:
            raise SessionNotFoundError(f"State machine not found for session {session_id}")
        
        # Validate action is allowed in current state
        if action not in state_machine.get_valid_actions():
            raise InvalidStateTransition(
                state_machine.current_state.value,
                f"action: {action}"
            )
        
        # Route action to appropriate handler
        if action == "start_questions":
            return await self._handle_start_questions(session_id, session_data, state_machine)
        elif action == "get_question":
            return await self._handle_get_question(session_id, session_data, state_machine)
        elif action == "submit_answer":
            return await self._handle_submit_answer(session_id, data, session_data, state_machine)
        elif action == "get_feedback":
            return await self._handle_get_feedback(session_id, session_data, state_machine)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get the current state of a session"""
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            raise SessionNotFoundError(session_id)
        
        state_machine = self.state_machines.get(session_id)
        if not state_machine:
            raise SessionNotFoundError(f"State machine not found for session {session_id}")
        
        return {
            "session_id": session_id,
            "case_id": session_data.case_id,
            "state": state_machine.get_state_info(),
            "progress": {
                "questions_answered": len(session_data.answers),
                "current_question_index": session_data.current_question_index,
                "grades_received": len(session_data.grades),
                "follow_ups_completed": len(session_data.follow_up_questions),
                "teaching_points": len(session_data.teaching_points),
                "current_state": session_data.state.value
            },
            "metadata": session_data.metadata
        }
    
    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a session and return final results"""
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            raise SessionNotFoundError(session_id)
        
        # Calculate final scores using session data methods
        overall_score = session_data.get_average_score()
        category_scores = session_data.get_category_scores()
        
        # Create session summary
        summary = {
            "session_id": session_id,
            "case_id": session_data.case_id,
            "overall_score": overall_score,
            "category_scores": category_scores,
            "questions_answered": len(session_data.answers),
            "follow_ups_completed": len(session_data.follow_up_questions),
            "teaching_points_viewed": len(session_data.teaching_points),
            "duration_minutes": (datetime.utcnow() - session_data.created_at).total_seconds() / 60
        }
        
        # Update session state to completed
        session_data.state = SessionState.COMPLETED
        self.session_manager.update_session(session_id, session_data)
        
        # Clean up state machine
        if session_id in self.state_machines:
            del self.state_machines[session_id]
        
        return summary
    
    # Private handler methods
    
    async def _handle_start_questions(self, session_id: str, session_data: SessionData, 
                                     state_machine: FlowStateMachine) -> Dict[str, Any]:
        """Handle starting the question flow"""
        state_machine.transition(FlowState.ASKING_DIAGNOSTIC, "start_questions")
        session_data.state = SessionState.QUESTIONING
        self.session_manager.update_session(session_id, session_data)
        
        return {
            "status": "ready",
            "message": "Ready to begin diagnostic questions",
            "total_questions": session_data.total_questions
        }
    
    async def _handle_get_question(self, session_id: str, session_data: SessionData,
                                  state_machine: FlowStateMachine) -> Dict[str, Any]:
        """Get the next question for the user"""
        # Use QuestionAgent to get the next question
        question_request = AgentRequest(
            session_id=session_id,
            action="get_next_question",
            data={}
        )
        
        question_response = await self.question_agent.execute(question_request, session_data)
        
        if not question_response.success:
            return {
                "status": "error",
                "message": f"Failed to get question: {question_response.error}"
            }
        
        # Check if all questions are complete
        if question_response.metadata and question_response.metadata.get("complete"):
            state_machine.transition(FlowState.SESSION_COMPLETE, "all_complete")
            session_data.state = SessionState.COMPLETED
            self.session_manager.update_session(session_id, session_data)
            return question_response.data
        
        # Question was successfully retrieved
        state_machine.transition(FlowState.AWAITING_ANSWER, "ask_question")
        session_data.state = SessionState.QUESTIONING
        self.session_manager.update_session(session_id, session_data)
        
        return question_response.data
    
    async def _handle_submit_answer(self, session_id: str, data: Dict[str, Any],
                                   session_data: SessionData, state_machine: FlowStateMachine) -> Dict[str, Any]:
        """Handle answer submission and trigger grading"""
        answer_text = data.get("answer", "")
        question_id = data.get("question_id", "")
        
        # Create proper Answer object
        answer = Answer(
            question_id=question_id,
            session_id=session_id,
            text=answer_text
        )
        
        # Record answer
        session_data.add_answer(answer)
        
        # Transition to grading
        state_machine.transition(FlowState.GRADING_ANSWER, "submit_answer")
        session_data.state = SessionState.GRADING
        
        # Use GradingAgent to grade the answer
        grading_request = AgentRequest(
            session_id=session_id,
            action="grade_single_answer",
            data={
                "question_id": question_id,
                "answer": answer_text
            }
        )
        
        grading_response = await self.grading_agent.execute(grading_request, session_data)
        
        if not grading_response.success:
            return {
                "status": "error",
                "message": f"Failed to grade answer: {grading_response.error}"
            }
        
        # Extract grading result
        grading_data = grading_response.data["grading_result"]
        score = grading_data["score"]
        feedback = grading_data["feedback"]
        
        # Create proper GradingResult object
        grading_result = GradingResult(
            question_id=question_id,
            answer_id=answer.question_id,  # Using question_id as answer identifier for now
            score=score,
            feedback=feedback,
            strengths=grading_data.get("strengths", []),
            weaknesses=grading_data.get("weaknesses", []),
            suggestions=grading_data.get("suggestions", []),
            needs_follow_up=grading_data.get("needs_follow_up", score < self.follow_up_threshold)
        )
        
        session_data.add_grade(grading_result)
        
        # Decide next action
        state_machine.transition(FlowState.DECIDING_FOLLOW_UP, "grade_complete")
        
        # Check if follow-up is needed
        needs_follow_up = score < self.follow_up_threshold
        
        if needs_follow_up:
            state_machine.transition(FlowState.ASKING_FOLLOW_UP, "needs_follow_up")
            session_data.state = SessionState.FOLLOW_UP
            self.session_manager.update_session(session_id, session_data)
            return {
                "status": "follow_up_needed",
                "score": score,
                "feedback": feedback,
                "message": "Follow-up questions available to improve understanding"
            }
        else:
            session_data.current_question_index += 1
            if session_data.current_question_index < session_data.total_questions:
                state_machine.transition(FlowState.ASKING_DIAGNOSTIC, "next_question")
                session_data.state = SessionState.QUESTIONING
                self.session_manager.update_session(session_id, session_data)
                return {
                    "status": "next_question",
                    "score": score,
                    "feedback": feedback
                }
            else:
                state_machine.transition(FlowState.SESSION_COMPLETE, "all_complete")
                session_data.state = SessionState.COMPLETED
                self.session_manager.update_session(session_id, session_data)
                return {
                    "status": "complete",
                    "score": score,
                    "feedback": feedback
                }
    
    async def _handle_get_feedback(self, session_id: str, session_data: SessionData,
                                  state_machine: FlowStateMachine) -> Dict[str, Any]:
        """Get teaching feedback for a question"""
        # For now, return placeholder teaching content
        # In real implementation, this would call the TeachingAgent
        
        from ..core.models import TeachingPoint
        
        teaching_point = TeachingPoint(
            id=f"teaching_{len(session_data.teaching_points)}",
            topic="Diagnostic Reasoning",
            content="Here's a teaching point about the diagnostic approach...",
            references=["Reference 1", "Reference 2"]
        )
        
        session_data.teaching_points.append(teaching_point)
        session_data.state = SessionState.TEACHING
        self.session_manager.update_session(session_id, session_data)
        
        return {
            "teaching": {
                "topic": teaching_point.topic,
                "content": teaching_point.content,
                "references": teaching_point.references
            },
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
    
    def _calculate_overall_score(self, session_data: SessionData) -> float:
        """Calculate overall score for the session - now using SessionData method"""
        return session_data.get_average_score()
    
    def _calculate_category_scores(self, session_data: SessionData) -> Dict[str, float]:
        """Calculate scores by category - now using SessionData method"""
        return session_data.get_category_scores()