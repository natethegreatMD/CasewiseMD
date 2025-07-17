"""
Core interfaces for the MCP architecture
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TYPE_CHECKING
from pydantic import BaseModel

# Import proper session models
if TYPE_CHECKING:
    from ..session.models import SessionData


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


class Agent(ABC):
    """Base interface for all MCP agents"""
    
    @abstractmethod
    async def execute(self, request: AgentRequest, session_data: "SessionData") -> AgentResponse:
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