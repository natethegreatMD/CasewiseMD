"""
Data models for session storage
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from ..core.models import SessionState, Question, Answer, GradingResult, TeachingPoint


class SessionData(BaseModel):
    """Complete session data for storage"""
    session_id: str
    case_id: str
    user_id: Optional[str] = None
    state: SessionState = SessionState.INITIALIZED
    
    # Progress tracking
    current_question_index: int = 0
    total_questions: int = 7
    
    # Session data
    questions_asked: List[Question] = Field(default_factory=list)
    answers: List[Answer] = Field(default_factory=list)
    grades: List[GradingResult] = Field(default_factory=list)
    follow_up_questions: List[Question] = Field(default_factory=list)
    teaching_points: List[TeachingPoint] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Performance metrics
    time_per_question: List[float] = Field(default_factory=list)
    
    def update_timestamp(self):
        """Update the last modified timestamp"""
        self.updated_at = datetime.utcnow()
    
    def add_question(self, question: Question):
        """Add a question to the session"""
        self.questions_asked.append(question)
        self.update_timestamp()
    
    def add_answer(self, answer: Answer):
        """Add an answer to the session"""
        self.answers.append(answer)
        self.update_timestamp()
    
    def add_grade(self, grade: GradingResult):
        """Add a grading result to the session"""
        self.grades.append(grade)
        self.update_timestamp()
    
    def get_last_question(self) -> Optional[Question]:
        """Get the most recently asked question"""
        return self.questions_asked[-1] if self.questions_asked else None
    
    def get_last_answer(self) -> Optional[Answer]:
        """Get the most recent answer"""
        return self.answers[-1] if self.answers else None
    
    def get_average_score(self) -> float:
        """Calculate average score across all graded answers"""
        if not self.grades:
            return 0.0
        return sum(g.score for g in self.grades) / len(self.grades)
    
    def get_category_scores(self) -> Dict[str, float]:
        """Get average scores by category"""
        category_scores = {}
        category_counts = {}
        
        for i, grade in enumerate(self.grades):
            if i < len(self.questions_asked):
                category = self.questions_asked[i].category
                if category not in category_scores:
                    category_scores[category] = 0.0
                    category_counts[category] = 0
                category_scores[category] += grade.score
                category_counts[category] += 1
        
        # Calculate averages
        for category in category_scores:
            category_scores[category] /= category_counts[category]
        
        return category_scores


class SessionStore(BaseModel):
    """In-memory session storage"""
    sessions: Dict[str, SessionData] = Field(default_factory=dict)
    
    def create_session(self, session_id: str, case_id: str, user_id: Optional[str] = None) -> SessionData:
        """Create a new session"""
        session = SessionData(
            session_id=session_id,
            case_id=case_id,
            user_id=user_id
        )
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Retrieve a session by ID"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, session_data: SessionData) -> bool:
        """Update session data"""
        if session_id in self.sessions:
            self.sessions[session_id] = session_data
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_active_sessions(self) -> List[SessionData]:
        """Get all active (non-completed) sessions"""
        return [
            session for session in self.sessions.values()
            if session.state != SessionState.COMPLETED
        ]
    
    def cleanup_old_sessions(self, hours: int = 24):
        """Remove sessions older than specified hours"""
        cutoff = datetime.utcnow()
        to_remove = []
        
        for session_id, session in self.sessions.items():
            age = (cutoff - session.updated_at).total_seconds() / 3600
            if age > hours:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            self.delete_session(session_id)