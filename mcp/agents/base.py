"""
Base agent class that all agents inherit from
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

from ..core.interfaces import Agent, AgentRequest, AgentResponse, SessionContext
from ..core.exceptions import AgentExecutionError


class AgentCapability(Enum):
    """Capabilities that agents can have"""
    GRADING = "grading"
    QUESTION_GENERATION = "question_generation"
    TEACHING = "teaching"
    REFERENCE_LOOKUP = "reference_lookup"
    FEEDBACK_GENERATION = "feedback_generation"
    FOLLOWUP_GENERATION = "followup_generation"


class BaseAgent(Agent):
    """
    Base implementation of the Agent interface with common functionality
    """
    
    def __init__(self, name: str, capabilities: List[AgentCapability]):
        self.name = name
        self.capabilities = capabilities
        self.logger = logging.getLogger(f"agent.{name}")
    
    async def execute(self, request: AgentRequest, context: SessionContext) -> AgentResponse:
        """Execute the agent's primary function with error handling"""
        try:
            # Validate request
            if not self.validate_request(request):
                return AgentResponse(
                    success=False,
                    error=f"Invalid request format for {self.name} agent"
                )
            
            # Log execution
            self.logger.info(f"Executing {request.action} for session {request.session_id}")
            
            # Delegate to specific implementation
            result = await self._execute_action(request, context)
            
            # Log success
            self.logger.info(f"Successfully executed {request.action}")
            
            return result
            
        except Exception as e:
            # Log error
            self.logger.error(f"Error executing {request.action}: {str(e)}")
            
            # Return error response
            return AgentResponse(
                success=False,
                error=str(e),
                metadata={"agent": self.name, "action": request.action}
            )
    
    @abstractmethod
    async def _execute_action(self, request: AgentRequest, context: SessionContext) -> AgentResponse:
        """
        Implement the actual agent logic here.
        This method should be overridden by subclasses.
        """
        pass
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the agent's capabilities and supported actions"""
        return {
            "name": self.name,
            "capabilities": [cap.value for cap in self.capabilities],
            "supported_actions": self.get_supported_actions(),
            "description": self.get_description()
        }
    
    @abstractmethod
    def get_supported_actions(self) -> List[str]:
        """Return list of actions this agent supports"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return a description of what this agent does"""
        pass
    
    def validate_request(self, request: AgentRequest) -> bool:
        """Validate that the request is properly formatted for this agent"""
        # Basic validation
        if not request.session_id or not request.action:
            return False
        
        # Check if action is supported
        if request.action not in self.get_supported_actions():
            return False
        
        # Subclasses can add more specific validation
        return self._validate_specific_request(request)
    
    def _validate_specific_request(self, request: AgentRequest) -> bool:
        """
        Override this method in subclasses to add specific validation logic
        """
        return True
    
    def log_debug(self, message: str, **kwargs):
        """Log debug message with context"""
        self.logger.debug(message, extra=kwargs)
    
    def log_info(self, message: str, **kwargs):
        """Log info message with context"""
        self.logger.info(message, extra=kwargs)
    
    def log_error(self, message: str, **kwargs):
        """Log error message with context"""
        self.logger.error(message, extra=kwargs)
    
    async def call_external_service(self, service_name: str, **kwargs) -> Any:
        """
        Helper method for calling external services (e.g., OpenAI).
        Subclasses can override this for specific service handling.
        """
        self.log_info(f"Calling external service: {service_name}")
        # Implementation would go here
        pass