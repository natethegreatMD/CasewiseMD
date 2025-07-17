"""
State machine for managing session flow
"""

from enum import Enum
from typing import Dict, List, Optional, Set
from dataclasses import dataclass


class FlowState(str, Enum):
    """States in the diagnostic session flow"""
    INITIALIZED = "initialized"
    CASE_LOADED = "case_loaded"
    ASKING_DIAGNOSTIC = "asking_diagnostic"
    AWAITING_ANSWER = "awaiting_answer"
    GRADING_ANSWER = "grading_answer"
    DECIDING_FOLLOW_UP = "deciding_follow_up"
    ASKING_FOLLOW_UP = "asking_follow_up"
    PROVIDING_TEACHING = "providing_teaching"
    SESSION_COMPLETE = "session_complete"
    ERROR = "error"


@dataclass
class StateTransition:
    """Defines a valid state transition"""
    from_state: FlowState
    to_state: FlowState
    action: str
    condition: Optional[str] = None


class FlowStateMachine:
    """Manages the state transitions for a diagnostic session"""
    
    def __init__(self):
        self.current_state = FlowState.INITIALIZED
        self.state_history: List[FlowState] = [FlowState.INITIALIZED]
        self.transitions = self._define_transitions()
    
    def _define_transitions(self) -> List[StateTransition]:
        """Define all valid state transitions"""
        return [
            # Initial flow
            StateTransition(FlowState.INITIALIZED, FlowState.CASE_LOADED, "load_case"),
            StateTransition(FlowState.CASE_LOADED, FlowState.ASKING_DIAGNOSTIC, "start_questions"),
            
            # Main question loop
            StateTransition(FlowState.ASKING_DIAGNOSTIC, FlowState.AWAITING_ANSWER, "ask_question"),
            StateTransition(FlowState.AWAITING_ANSWER, FlowState.GRADING_ANSWER, "submit_answer"),
            StateTransition(FlowState.GRADING_ANSWER, FlowState.DECIDING_FOLLOW_UP, "grade_complete"),
            
            # Follow-up decision branch
            StateTransition(FlowState.DECIDING_FOLLOW_UP, FlowState.ASKING_FOLLOW_UP, "needs_follow_up", "score < 0.7"),
            StateTransition(FlowState.DECIDING_FOLLOW_UP, FlowState.ASKING_DIAGNOSTIC, "next_question", "has_more_questions"),
            StateTransition(FlowState.DECIDING_FOLLOW_UP, FlowState.SESSION_COMPLETE, "all_complete", "no_more_questions"),
            
            # Follow-up flow
            StateTransition(FlowState.ASKING_FOLLOW_UP, FlowState.AWAITING_ANSWER, "ask_follow_up"),
            
            # Teaching moments
            StateTransition(FlowState.DECIDING_FOLLOW_UP, FlowState.PROVIDING_TEACHING, "provide_teaching", "needs_teaching"),
            StateTransition(FlowState.PROVIDING_TEACHING, FlowState.ASKING_DIAGNOSTIC, "continue_questions", "has_more_questions"),
            StateTransition(FlowState.PROVIDING_TEACHING, FlowState.SESSION_COMPLETE, "complete", "no_more_questions"),
            
            # Error handling
            StateTransition(FlowState.ASKING_DIAGNOSTIC, FlowState.ERROR, "error"),
            StateTransition(FlowState.GRADING_ANSWER, FlowState.ERROR, "error"),
            StateTransition(FlowState.ERROR, FlowState.INITIALIZED, "reset"),
        ]
    
    def can_transition(self, to_state: FlowState, action: str) -> bool:
        """Check if a transition is valid from current state"""
        for transition in self.transitions:
            if (transition.from_state == self.current_state and 
                transition.to_state == to_state and 
                transition.action == action):
                return True
        return False
    
    def transition(self, to_state: FlowState, action: str) -> bool:
        """Attempt to transition to a new state"""
        if self.can_transition(to_state, action):
            self.current_state = to_state
            self.state_history.append(to_state)
            return True
        return False
    
    def get_valid_actions(self) -> Set[str]:
        """Get all valid actions from current state"""
        actions = set()
        for transition in self.transitions:
            if transition.from_state == self.current_state:
                actions.add(transition.action)
        return actions
    
    def get_state_info(self) -> Dict[str, any]:
        """Get current state information"""
        return {
            "current_state": self.current_state.value,
            "valid_actions": list(self.get_valid_actions()),
            "state_history": [state.value for state in self.state_history[-10:]],  # Last 10 states
        }
    
    def reset(self):
        """Reset the state machine"""
        self.current_state = FlowState.INITIALIZED
        self.state_history = [FlowState.INITIALIZED]