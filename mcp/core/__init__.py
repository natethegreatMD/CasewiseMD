"""
Core module for MCP backend - defines interfaces and shared models
"""

from .interfaces import (
    Agent,
    OrchestratorInterface,
    AgentResponse,
    AgentRequest
)

from .models import (
    SessionState,
    Question,
    Answer,
    GradingResult,
    TeachingPoint,
    Reference
)

from .exceptions import (
    MCPException,
    SessionNotFoundError,
    AgentExecutionError,
    InvalidStateTransition
)

__all__ = [
    # Interfaces
    'Agent',
    'OrchestratorInterface',
    'AgentResponse',
    'AgentRequest',
    
    # Models
    'SessionState',
    'Question',
    'Answer',
    'GradingResult',
    'TeachingPoint',
    'Reference',
    
    # Exceptions
    'MCPException',
    'SessionNotFoundError',
    'AgentExecutionError',
    'InvalidStateTransition'
]