"""
Question Agent for handling question generation and management
"""

from typing import Dict, Any, List, Optional

from ...core.interfaces import Agent, AgentRequest, AgentResponse
from ...core.models import Question, QuestionType
from ...session.models import SessionData
from .question_loader import QuestionLoader


class QuestionAgent(Agent):
    """Agent responsible for loading and managing questions in diagnostic sessions"""
    
    def __init__(self, demo_cases_path: str = "demo_cases"):
        self.question_loader = QuestionLoader(demo_cases_path)
        self.capabilities = {
            "load_case_questions": "Load questions for a specific case",
            "get_next_question": "Get the next question in sequence",
            "generate_follow_up": "Generate follow-up questions for weak areas",
            "get_question_metadata": "Get detailed metadata for a question"
        }
    
    async def execute(self, request: AgentRequest, session_data: SessionData) -> AgentResponse:
        """Execute the agent's functionality"""
        try:
            action = request.action
            data = request.data
            
            if action == "load_case_questions":
                return await self._load_case_questions(session_data.case_id, session_data)
            elif action == "get_next_question":
                return await self._get_next_question(session_data)
            elif action == "generate_follow_up":
                return await self._generate_follow_up(data, session_data)
            elif action == "get_question_metadata":
                return await self._get_question_metadata(data.get("question_id"), session_data)
            else:
                return AgentResponse(
                    success=False,
                    error=f"Unknown action: {action}"
                )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"QuestionAgent error: {str(e)}"
            )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the agent's capabilities"""
        return self.capabilities
    
    async def _load_case_questions(self, case_id: str, session_data: SessionData) -> AgentResponse:
        """Load all questions for a case"""
        try:
            questions = self.question_loader.load_questions_for_case(case_id)
            case_metadata = self.question_loader.get_case_metadata(case_id)
            
            # Clear any existing questions and add the loaded ones
            session_data.questions_asked.clear()
            session_data.total_questions = len(questions)
            
            # Store questions in session metadata for later retrieval
            session_data.metadata["available_questions"] = [
                {
                    "id": q.id,
                    "type": q.type.value,
                    "category": q.category,
                    "text": q.text,
                    "rubric_category": q.rubric_category,
                    "metadata": q.metadata
                }
                for q in questions
            ]
            
            if case_metadata:
                session_data.metadata["case_metadata"] = case_metadata
            
            return AgentResponse(
                success=True,
                data={
                    "questions_loaded": len(questions),
                    "case_metadata": case_metadata,
                    "total_questions": len(questions)
                },
                metadata={"action": "load_case_questions"}
            )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Failed to load questions for case {case_id}: {str(e)}"
            )
    
    async def _get_next_question(self, session_data: SessionData) -> AgentResponse:
        """Get the next question in the sequence"""
        try:
            available_questions = session_data.metadata.get("available_questions", [])
            
            if not available_questions:
                return AgentResponse(
                    success=False,
                    error="No questions available. Please load case questions first."
                )
            
            current_index = session_data.current_question_index
            
            if current_index >= len(available_questions):
                return AgentResponse(
                    success=True,
                    data={
                        "status": "complete",
                        "message": "All questions have been answered"
                    },
                    metadata={"action": "get_next_question", "complete": True}
                )
            
            question_data = available_questions[current_index]
            
            # Create Question object from stored data
            question = Question(
                id=question_data["id"],
                type=QuestionType(question_data["type"]),
                category=question_data["category"],
                text=question_data["text"],
                rubric_category=question_data.get("rubric_category"),
                metadata=question_data.get("metadata", {})
            )
            
            # Add question to session
            session_data.add_question(question)
            
            return AgentResponse(
                success=True,
                data={
                    "question": {
                        "id": question.id,
                        "text": question.text,
                        "category": question.category,
                        "type": question.type.value,
                        "rubric_category": question.rubric_category,
                        "metadata": question.metadata
                    },
                    "question_number": current_index + 1,
                    "total_questions": len(available_questions),
                    "progress": (current_index + 1) / len(available_questions)
                },
                metadata={"action": "get_next_question"}
            )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Failed to get next question: {str(e)}"
            )
    
    async def _generate_follow_up(self, data: Dict[str, Any], session_data: SessionData) -> AgentResponse:
        """Generate follow-up questions for weak performance areas"""
        try:
            category = data.get("category")
            weak_areas = data.get("weak_areas", [])
            
            if not category:
                return AgentResponse(
                    success=False,
                    error="Category is required for follow-up question generation"
                )
            
            follow_up_question = self.question_loader.generate_follow_up_question(category, weak_areas)
            
            # Add follow-up question to session
            session_data.follow_up_questions.append(follow_up_question)
            
            return AgentResponse(
                success=True,
                data={
                    "follow_up_question": {
                        "id": follow_up_question.id,
                        "text": follow_up_question.text,
                        "category": follow_up_question.category,
                        "type": follow_up_question.type.value,
                        "metadata": follow_up_question.metadata
                    }
                },
                metadata={"action": "generate_follow_up", "category": category}
            )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Failed to generate follow-up question: {str(e)}"
            )
    
    async def _get_question_metadata(self, question_id: str, session_data: SessionData) -> AgentResponse:
        """Get detailed metadata for a specific question"""
        try:
            # Search in regular questions
            for question in session_data.questions_asked:
                if question.id == question_id:
                    return AgentResponse(
                        success=True,
                        data={
                            "question_id": question.id,
                            "metadata": question.metadata,
                            "category": question.category,
                            "type": question.type.value
                        },
                        metadata={"action": "get_question_metadata"}
                    )
            
            # Search in follow-up questions
            for question in session_data.follow_up_questions:
                if question.id == question_id:
                    return AgentResponse(
                        success=True,
                        data={
                            "question_id": question.id,
                            "metadata": question.metadata,
                            "category": question.category,
                            "type": question.type.value
                        },
                        metadata={"action": "get_question_metadata"}
                    )
            
            return AgentResponse(
                success=False,
                error=f"Question with ID {question_id} not found"
            )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Failed to get question metadata: {str(e)}"
            )
    
    def validate_request(self, request: AgentRequest) -> bool:
        """Validate that the request is properly formatted"""
        if not request.action:
            return False
        
        if request.action not in self.capabilities:
            return False
        
        # Validate specific action requirements
        if request.action == "generate_follow_up":
            return "category" in request.data
        elif request.action == "get_question_metadata":
            return "question_id" in request.data
        
        return True