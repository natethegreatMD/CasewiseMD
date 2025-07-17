"""
Core data models shared across the MCP system
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class SessionState(str, Enum):
    """Possible states for a diagnostic session"""
    INITIALIZED = "initialized"
    CASE_LOADED = "case_loaded"
    QUESTIONING = "questioning"
    GRADING = "grading"
    FOLLOW_UP = "follow_up"
    TEACHING = "teaching"
    COMPLETED = "completed"
    ERROR = "error"


class QuestionType(str, Enum):
    """Types of questions in the system"""
    DIAGNOSTIC = "diagnostic"
    FOLLOW_UP = "follow_up"
    CLARIFICATION = "clarification"


class Question(BaseModel):
    """Represents a question asked to the user"""
    id: str
    type: QuestionType
    category: str
    text: str
    rubric_category: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Answer(BaseModel):
    """Represents a user's answer to a question"""
    question_id: str
    session_id: str
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GradingResult(BaseModel):
    """Result from grading an answer"""
    question_id: str
    answer_id: str
    score: float  # 0.0 to 1.0
    max_score: float = 1.0
    feedback: str
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    rubric_scores: Dict[str, float] = Field(default_factory=dict)
    needs_follow_up: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TeachingPoint(BaseModel):
    """Educational content delivered to the user"""
    id: str
    related_question_id: Optional[str] = None
    topic: str
    content: str
    references: List[str] = Field(default_factory=list)
    difficulty_level: str = "intermediate"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Reference(BaseModel):
    """Reference material that can be looked up"""
    id: str
    source: str  # textbook, guideline, article, etc.
    title: str
    content: str
    url: Optional[str] = None
    page_number: Optional[int] = None
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CaseInfo(BaseModel):
    """Information about a diagnostic case"""
    case_id: str
    title: str
    specialty: str
    difficulty: str
    description: str
    dicom_study_uid: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionSummary(BaseModel):
    """Summary of a completed session"""
    session_id: str
    case_id: str
    start_time: datetime
    end_time: datetime
    total_questions: int
    questions_answered: int
    overall_score: float
    category_scores: Dict[str, float]
    follow_ups_completed: int
    teaching_points_viewed: int
    time_spent_minutes: float
    metadata: Dict[str, Any] = Field(default_factory=dict)