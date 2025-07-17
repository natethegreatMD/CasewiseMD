"""
Core interfaces for the MCP architecture
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pydantic import BaseModel
from datetime import datetime


class AgentRequest(BaseModel):
    """Standard request format for all agents"""
    session_id: str
    action: str
    data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    """Standard response format from all agents"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SessionContext:
    """Context object passed to agents containing session state and history"""
    def __init__(self, session_id: str, case_id: str):
        self.session_id = session_id
        self.case_id = case_id
        self.current_question_index: int = 0
        self.answers: List[Dict[str, Any]] = []
        self.grades: List[Dict[str, Any]] = []
        self.follow_ups_completed: List[str] = []
        self.teaching_points_delivered: List[str] = []
        self.state: str = "initialized"
        self.metadata: Dict[str, Any] = {}
        self.created_at: datetime = datetime.utcnow()
        self.updated_at: datetime = datetime.utcnow()
    
    def add_answer(self, question_id: str, answer: str, metadata: Optional[Dict] = None):
        """Record an answer in the session context"""
        self.answers.append({
            "question_id": question_id,
            "answer": answer,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        })
        self.updated_at = datetime.utcnow()
    
    def add_grade(self, question_id: str, score: float, feedback: str, metadata: Optional[Dict] = None):
        """Record a grade in the session context"""
        self.grades.append({
            "question_id": question_id,
            "score": score,
            "feedback": feedback,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        })
        self.updated_at = datetime.utcnow()
    
    def get_current_progress(self) -> Dict[str, Any]:
        """Get current progress summary"""
        return {
            "questions_answered": len(self.answers),
            "current_question_index": self.current_question_index,
            "grades_received": len(self.grades),
            "follow_ups_completed": len(self.follow_ups_completed),
            "teaching_points": len(self.teaching_points_delivered),
            "state": self.state
        }


class Agent(ABC):
    """Base interface for all MCP agents"""
    
    @abstractmethod
    async def execute(self, request: AgentRequest, context: SessionContext) -> AgentResponse:
        """Execute the agent's primary function"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the agent's capabilities and supported actions"""
        pass
    
    def validate_request(self, request: AgentRequest) -> bool:
        """Validate that the request is properly formatted for this agent"""
        return True


class OrchestratorInterface(ABC):
    """Interface for the session orchestrator"""
    
    @abstractmethod
    async def start_session(self, case_id: str, user_id: Optional[str] = None) -> str:
        """Start a new diagnostic session"""
        pass
    
    @abstractmethod
    async def process_action(self, session_id: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an action within a session"""
        pass
    
    @abstractmethod
    async def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get the current state of a session"""
        pass
    
    @abstractmethod
    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a session and return final results"""
        pass