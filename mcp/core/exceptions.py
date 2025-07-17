"""
Custom exceptions for the MCP system
"""


class MCPException(Exception):
    """Base exception for all MCP-related errors"""
    pass


class SessionNotFoundError(MCPException):
    """Raised when a session ID is not found"""
    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(f"Session not found: {session_id}")


class AgentExecutionError(MCPException):
    """Raised when an agent fails to execute properly"""
    def __init__(self, agent_name: str, error_message: str):
        self.agent_name = agent_name
        self.error_message = error_message
        super().__init__(f"Agent '{agent_name}' execution failed: {error_message}")


class InvalidStateTransition(MCPException):
    """Raised when an invalid state transition is attempted"""
    def __init__(self, current_state: str, attempted_state: str):
        self.current_state = current_state
        self.attempted_state = attempted_state
        super().__init__(
            f"Invalid state transition from '{current_state}' to '{attempted_state}'"
        )


class CaseNotFoundError(MCPException):
    """Raised when a case ID is not found"""
    def __init__(self, case_id: str):
        self.case_id = case_id
        super().__init__(f"Case not found: {case_id}")


class GradingError(MCPException):
    """Raised when grading fails"""
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Grading failed: {reason}")


class ReferenceNotFoundError(MCPException):
    """Raised when a reference lookup fails"""
    def __init__(self, reference_id: str):
        self.reference_id = reference_id
        super().__init__(f"Reference not found: {reference_id}")