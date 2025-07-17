"""
Grading Agent - Handles rubric-based grading using GPT-4o
"""

import json
import logging
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
import os

from ..base import BaseAgent, AgentCapability
from ...core.interfaces import AgentRequest, AgentResponse, SessionContext
from ...core.models import GradingResult
from .rubric_processor import RubricProcessor


class GradingAgent(BaseAgent):
    """
    Agent responsible for grading student responses using rubric criteria
    and GPT-4o for intelligent assessment
    """
    
    def __init__(self):
        super().__init__(
            name="grading",
            capabilities=[
                AgentCapability.GRADING,
                AgentCapability.FEEDBACK_GENERATION
            ]
        )
        
        # Initialize OpenAI client
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=60.0,
            max_retries=3
        )
        
        self.model = "gpt-4o"
        self.max_tokens = 2000
        self.temperature = 0.3  # Lower for consistent grading
        
        # Initialize rubric processor
        self.rubric_processor = RubricProcessor()
    
    def get_supported_actions(self) -> List[str]:
        """Return list of actions this agent supports"""
        return [
            "grade_answer",
            "grade_batch",
            "get_category_feedback",
            "calculate_final_score"
        ]
    
    def get_description(self) -> str:
        """Return a description of what this agent does"""
        return "Grades student responses using rubric criteria and GPT-4o analysis"
    
    async def _execute_action(self, request: AgentRequest, context: SessionContext) -> AgentResponse:
        """Execute grading action based on request"""
        
        if request.action == "grade_answer":
            return await self._grade_single_answer(request, context)
        elif request.action == "grade_batch":
            return await self._grade_batch_answers(request, context)
        elif request.action == "get_category_feedback":
            return await self._get_category_feedback(request, context)
        elif request.action == "calculate_final_score":
            return await self._calculate_final_score(request, context)
        else:
            return AgentResponse(
                success=False,
                error=f"Unsupported action: {request.action}"
            )
    
    async def _grade_single_answer(self, request: AgentRequest, context: SessionContext) -> AgentResponse:
        """Grade a single answer"""
        try:
            # Extract data from request
            question_id = request.data.get("question_id")
            answer_text = request.data.get("answer")
            question_text = request.data.get("question_text")
            category = request.data.get("category")
            case_id = context.case_id
            
            # Load rubric for this case and category
            rubric_criteria = await self.rubric_processor.get_category_criteria(case_id, category)
            
            # Create grading prompt
            prompt = self._create_grading_prompt(
                question_text=question_text,
                answer_text=answer_text,
                category=category,
                rubric_criteria=rubric_criteria
            )
            
            # Get AI grading
            grading_result = await self._get_ai_grading(prompt)
            
            # Parse and structure result
            result = self._parse_grading_result(grading_result, question_id)
            
            # Determine if follow-up is needed
            result.needs_follow_up = result.score < 0.7
            
            return AgentResponse(
                success=True,
                data={
                    "grading_result": result.dict(),
                    "needs_follow_up": result.needs_follow_up
                }
            )
            
        except Exception as e:
            self.log_error(f"Error grading answer: {str(e)}")
            return AgentResponse(
                success=False,
                error=str(e)
            )
    
    async def _grade_batch_answers(self, request: AgentRequest, context: SessionContext) -> AgentResponse:
        """Grade multiple answers at once"""
        try:
            answers = request.data.get("answers", [])
            results = []
            
            for answer_data in answers:
                # Create individual request
                single_request = AgentRequest(
                    session_id=request.session_id,
                    action="grade_answer",
                    data=answer_data
                )
                
                # Grade individual answer
                response = await self._grade_single_answer(single_request, context)
                
                if response.success:
                    results.append(response.data["grading_result"])
                else:
                    self.log_error(f"Failed to grade answer: {response.error}")
            
            return AgentResponse(
                success=True,
                data={
                    "grading_results": results,
                    "total_graded": len(results)
                }
            )
            
        except Exception as e:
            self.log_error(f"Error in batch grading: {str(e)}")
            return AgentResponse(
                success=False,
                error=str(e)
            )
    
    async def _get_ai_grading(self, prompt: str) -> Dict[str, Any]:
        """Get grading from GPT-4o"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert medical educator grading radiology resident responses. Provide detailed, constructive feedback based on the rubric criteria."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            self.log_error(f"OpenAI API error: {str(e)}")
            raise
    
    def _create_grading_prompt(self, question_text: str, answer_text: str, 
                              category: str, rubric_criteria: Dict[str, Any]) -> str:
        """Create a detailed grading prompt"""
        return f"""
Grade the following radiology resident response according to the rubric criteria.

QUESTION: {question_text}

STUDENT ANSWER: {answer_text}

RUBRIC CATEGORY: {category}

RUBRIC CRITERIA:
{json.dumps(rubric_criteria, indent=2)}

Provide your grading in JSON format with the following structure:
{{
    "score": 0.0-1.0 (based on rubric),
    "feedback": "Detailed constructive feedback",
    "strengths": ["List of strengths in the answer"],
    "weaknesses": ["List of areas for improvement"],
    "suggestions": ["Specific suggestions for improvement"],
    "rubric_scores": {{
        "criterion_1": 0.0-1.0,
        "criterion_2": 0.0-1.0,
        ...
    }}
}}

Be specific and educational in your feedback. Focus on medical accuracy and clinical reasoning.
"""
    
    def _parse_grading_result(self, ai_result: Dict[str, Any], question_id: str) -> GradingResult:
        """Parse AI grading into structured result"""
        return GradingResult(
            question_id=question_id,
            answer_id=f"ans_{question_id}",  # Generate answer ID
            score=float(ai_result.get("score", 0.0)),
            feedback=ai_result.get("feedback", ""),
            strengths=ai_result.get("strengths", []),
            weaknesses=ai_result.get("weaknesses", []),
            suggestions=ai_result.get("suggestions", []),
            rubric_scores=ai_result.get("rubric_scores", {}),
            metadata={
                "grading_model": self.model,
                "grading_method": "ai_gpt4o"
            }
        )
    
    async def _get_category_feedback(self, request: AgentRequest, context: SessionContext) -> AgentResponse:
        """Get detailed feedback for a specific category"""
        try:
            category = request.data.get("category")
            
            # Get all grades for this category
            category_grades = [
                grade for grade in context.grades
                if grade.get("metadata", {}).get("category") == category
            ]
            
            if not category_grades:
                return AgentResponse(
                    success=True,
                    data={"feedback": "No grades available for this category"}
                )
            
            # Calculate average score
            avg_score = sum(g["score"] for g in category_grades) / len(category_grades)
            
            # Compile feedback
            feedback = {
                "category": category,
                "average_score": avg_score,
                "total_questions": len(category_grades),
                "strengths": [],
                "areas_for_improvement": [],
                "recommendations": []
            }
            
            # Aggregate feedback from individual grades
            for grade in category_grades:
                if "strengths" in grade:
                    feedback["strengths"].extend(grade["strengths"])
                if "weaknesses" in grade:
                    feedback["areas_for_improvement"].extend(grade["weaknesses"])
                if "suggestions" in grade:
                    feedback["recommendations"].extend(grade["suggestions"])
            
            return AgentResponse(
                success=True,
                data={"category_feedback": feedback}
            )
            
        except Exception as e:
            self.log_error(f"Error getting category feedback: {str(e)}")
            return AgentResponse(
                success=False,
                error=str(e)
            )
    
    async def _calculate_final_score(self, request: AgentRequest, context: SessionContext) -> AgentResponse:
        """Calculate final weighted score across all categories"""
        try:
            # Get category weights from rubric
            case_id = context.case_id
            weights = await self.rubric_processor.get_category_weights(case_id)
            
            # Calculate weighted score
            category_scores = {}
            for grade in context.grades:
                category = grade.get("metadata", {}).get("category", "Unknown")
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(grade["score"])
            
            # Average scores by category
            category_averages = {
                cat: sum(scores) / len(scores)
                for cat, scores in category_scores.items()
            }
            
            # Apply weights
            weighted_score = sum(
                category_averages.get(cat, 0.0) * weight
                for cat, weight in weights.items()
            )
            
            return AgentResponse(
                success=True,
                data={
                    "final_score": weighted_score,
                    "category_scores": category_averages,
                    "weights_applied": weights
                }
            )
            
        except Exception as e:
            self.log_error(f"Error calculating final score: {str(e)}")
            return AgentResponse(
                success=False,
                error=str(e)
            )