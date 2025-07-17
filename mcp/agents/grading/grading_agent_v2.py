"""
Grading Agent V2 - Updated to work with SessionData and MCP architecture
Incorporates functionality from the original ai_grading.py service
"""

import json
import os
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI

from ...core.interfaces import Agent, AgentRequest, AgentResponse
from ...core.models import GradingResult, Answer, Question
from ...session.models import SessionData


class GradingAgentV2(Agent):
    """
    Agent responsible for grading student responses using GPT-4o
    Based on the original ai_grading.py functionality
    """
    
    def __init__(self, rubrics_path: str = "rubrics"):
        self.rubrics_path = rubrics_path
        
        # Initialize OpenAI client
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=60.0,
            max_retries=3
        )
        
        self.model = "gpt-4o"
        self.max_tokens = 4000
        self.temperature = 0.3  # Lower for consistent grading
        
        self.capabilities = {
            "grade_single_answer": "Grade a single answer against rubric",
            "grade_complete_session": "Grade all answers in a diagnostic session",
            "generate_follow_up": "Generate follow-up questions for weak areas",
            "evaluate_follow_up": "Evaluate follow-up answer responses"
        }
    
    async def execute(self, request: AgentRequest, session_data: SessionData) -> AgentResponse:
        """Execute the agent's functionality"""
        try:
            action = request.action
            data = request.data
            
            if action == "grade_single_answer":
                return await self._grade_single_answer(data, session_data)
            elif action == "grade_complete_session":
                return await self._grade_complete_session(session_data)
            elif action == "generate_follow_up":
                return await self._generate_follow_up(data, session_data)
            elif action == "evaluate_follow_up":
                return await self._evaluate_follow_up(data, session_data)
            else:
                return AgentResponse(
                    success=False,
                    error=f"Unknown action: {action}"
                )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"GradingAgent error: {str(e)}"
            )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the agent's capabilities"""
        return self.capabilities
    
    async def _grade_single_answer(self, data: Dict[str, Any], session_data: SessionData) -> AgentResponse:
        """Grade a single answer"""
        try:
            question_id = data.get("question_id")
            answer_text = data.get("answer", "")
            
            # Find the question in the session
            question = None
            for q in session_data.questions_asked:
                if q.id == question_id:
                    question = q
                    break
            
            if not question:
                return AgentResponse(
                    success=False,
                    error=f"Question {question_id} not found in session"
                )
            
            # Load rubric for the case
            rubric = await self._load_rubric(session_data.case_id)
            if not rubric:
                return AgentResponse(
                    success=False,
                    error=f"Rubric not found for case {session_data.case_id}"
                )
            
            # Get category criteria
            category_criteria = rubric.get("categories", {}).get(question.category, {})
            
            # Create grading prompt
            prompt = self._create_single_answer_prompt(
                question=question,
                answer=answer_text,
                case_id=session_data.case_id,
                category_criteria=category_criteria
            )
            
            # Get AI grading
            grading_response = await self._call_openai(prompt)
            
            # Parse result
            grading_result = self._parse_grading_response(
                grading_response, 
                question_id, 
                answer_text
            )
            
            return AgentResponse(
                success=True,
                data={
                    "grading_result": {
                        "question_id": grading_result.question_id,
                        "score": grading_result.score,
                        "feedback": grading_result.feedback,
                        "strengths": grading_result.strengths,
                        "weaknesses": grading_result.weaknesses,
                        "suggestions": grading_result.suggestions,
                        "needs_follow_up": grading_result.needs_follow_up
                    }
                },
                metadata={"action": "grade_single_answer"}
            )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Failed to grade single answer: {str(e)}"
            )
    
    async def _grade_complete_session(self, session_data: SessionData) -> AgentResponse:
        """Grade all answers in a diagnostic session (comprehensive grading)"""
        try:
            if not session_data.answers:
                return AgentResponse(
                    success=False,
                    error="No answers found to grade"
                )
            
            # Load rubric
            rubric = await self._load_rubric(session_data.case_id)
            if not rubric:
                return AgentResponse(
                    success=False,
                    error=f"Rubric not found for case {session_data.case_id}"
                )
            
            # Create comprehensive grading prompt
            prompt = self._create_comprehensive_prompt(session_data, rubric)
            
            # Get AI grading
            grading_response = await self._call_openai(prompt)
            
            # Parse comprehensive results
            results = self._parse_comprehensive_grading(grading_response, session_data)
            
            # Calculate overall score and identify weak areas
            overall_score = self._calculate_overall_score(results["category_scores"])
            weak_categories = [
                cat for cat, score in results["category_scores"].items() 
                if score < 0.7
            ]
            
            # Determine if follow-up is needed
            needs_follow_up = len(weak_categories) > 0
            
            return AgentResponse(
                success=True,
                data={
                    "overall_score": overall_score,
                    "category_scores": results["category_scores"],
                    "category_feedback": results["category_feedback"],
                    "strengths": results["strengths"],
                    "areas_for_improvement": results["areas_for_improvement"],
                    "recommendations": results["recommendations"],
                    "weak_categories": weak_categories[:2],  # Limit to 2 weakest
                    "needs_follow_up": needs_follow_up,
                    "abr_readiness": results.get("abr_readiness", ""),
                    "pass_threshold": overall_score >= 0.7
                },
                metadata={"action": "grade_complete_session"}
            )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Failed to grade complete session: {str(e)}"
            )
    
    async def _generate_follow_up(self, data: Dict[str, Any], session_data: SessionData) -> AgentResponse:
        """Generate follow-up questions for weak categories"""
        try:
            weak_categories = data.get("weak_categories", [])
            
            if not weak_categories:
                return AgentResponse(
                    success=True,
                    data={"follow_up_questions": []},
                    metadata={"action": "generate_follow_up"}
                )
            
            follow_up_questions = []
            
            for category in weak_categories[:2]:  # Limit to 2 categories
                prompt = self._create_follow_up_prompt(category, session_data)
                
                response = await self._call_openai(prompt)
                
                if "question" in response:
                    follow_up_questions.append({
                        "category": category,
                        "question": response["question"],
                        "guidance": response.get("guidance", ""),
                        "learning_objectives": response.get("learning_objectives", [])
                    })
            
            return AgentResponse(
                success=True,
                data={"follow_up_questions": follow_up_questions},
                metadata={"action": "generate_follow_up"}
            )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Failed to generate follow-up: {str(e)}"
            )
    
    async def _evaluate_follow_up(self, data: Dict[str, Any], session_data: SessionData) -> AgentResponse:
        """Evaluate follow-up answer responses"""
        try:
            follow_up_answers = data.get("follow_up_answers", [])
            
            if not follow_up_answers:
                return AgentResponse(
                    success=True,
                    data={"evaluation": "No follow-up answers to evaluate"},
                    metadata={"action": "evaluate_follow_up"}
                )
            
            # Create evaluation prompt
            prompt = self._create_follow_up_evaluation_prompt(follow_up_answers, session_data)
            
            # Get AI evaluation
            evaluation_response = await self._call_openai(prompt)
            
            return AgentResponse(
                success=True,
                data={
                    "evaluation": evaluation_response.get("evaluation", ""),
                    "improvement_noted": evaluation_response.get("improvement_noted", False),
                    "learning_progress": evaluation_response.get("learning_progress", ""),
                    "final_recommendations": evaluation_response.get("final_recommendations", [])
                },
                metadata={"action": "evaluate_follow_up"}
            )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Failed to evaluate follow-up: {str(e)}"
            )
    
    async def _load_rubric(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Load rubric for the case"""
        try:
            rubric_file = f"{self.rubrics_path}/{case_id}_rubric_detailed.json"
            
            if os.path.exists(rubric_file):
                with open(rubric_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Return default rubric structure
                return self._get_default_rubric()
        except Exception as e:
            print(f"Error loading rubric: {e}")
            return self._get_default_rubric()
    
    def _get_default_rubric(self) -> Dict[str, Any]:
        """Get default rubric when specific rubric not found"""
        return {
            "categories": {
                "Image Interpretation": {
                    "weight": 0.2,
                    "criteria": "Systematic image interpretation and technical quality assessment"
                },
                "Differential Diagnosis": {
                    "weight": 0.2,
                    "criteria": "Comprehensive differential diagnosis with appropriate prioritization"
                },
                "Clinical Correlation": {
                    "weight": 0.15,
                    "criteria": "Integration of imaging findings with clinical presentation"
                },
                "Management Recommendations": {
                    "weight": 0.15,
                    "criteria": "Appropriate next steps and management recommendations"
                },
                "Communication & Organization": {
                    "weight": 0.15,
                    "criteria": "Clear, organized communication of findings"
                },
                "Professional Judgment": {
                    "weight": 0.1,
                    "criteria": "Appropriate confidence level and clinical reasoning"
                },
                "Safety Considerations": {
                    "weight": 0.05,
                    "criteria": "Recognition of urgent findings and safety considerations"
                }
            }
        }
    
    async def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API with error handling and fallback"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert radiology attending physician grading resident responses. Provide detailed, constructive feedback following ABR standards."
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
            print(f"OpenAI API error: {e}")
            # Return fallback grading
            return self._get_fallback_grading()
    
    def _get_fallback_grading(self) -> Dict[str, Any]:
        """Fallback grading when AI is unavailable"""
        return {
            "score": 0.75,
            "feedback": "AI grading temporarily unavailable. Manual review recommended.",
            "strengths": ["Response provided"],
            "weaknesses": ["Requires manual evaluation"],
            "suggestions": ["Please review with attending physician"],
            "needs_follow_up": False
        }
    
    def _create_single_answer_prompt(self, question: Question, answer: str, 
                                   case_id: str, category_criteria: Dict[str, Any]) -> str:
        """Create prompt for grading a single answer"""
        return f"""
Grade this radiology resident's response according to ABR standards.

CASE ID: {case_id}
CATEGORY: {question.category}
QUESTION: {question.text}
STUDENT ANSWER: {answer}

RUBRIC CRITERIA: {json.dumps(category_criteria, indent=2)}

Provide grading in JSON format:
{{
    "score": 0.0-1.0,
    "feedback": "Detailed constructive feedback",
    "strengths": ["specific strengths"],
    "weaknesses": ["areas for improvement"],
    "suggestions": ["specific improvement suggestions"],
    "needs_follow_up": boolean
}}

Focus on medical accuracy, clinical reasoning, and ABR competency standards.
"""
    
    def _create_comprehensive_prompt(self, session_data: SessionData, rubric: Dict[str, Any]) -> str:
        """Create prompt for comprehensive session grading"""
        answers_text = ""
        for i, answer in enumerate(session_data.answers):
            question = session_data.questions_asked[i] if i < len(session_data.questions_asked) else None
            q_text = question.text if question else f"Question {i+1}"
            answers_text += f"\nQ{i+1} ({question.category if question else 'Unknown'}): {q_text}\nA{i+1}: {answer.text}\n"
        
        return f"""
Grade this complete radiology resident diagnostic session according to ABR standards.

CASE ID: {session_data.case_id}
TOTAL QUESTIONS: {len(session_data.answers)}

QUESTIONS AND ANSWERS:
{answers_text}

RUBRIC CATEGORIES: {json.dumps(rubric.get('categories', {}), indent=2)}

Provide comprehensive grading in JSON format:
{{
    "category_scores": {{
        "Image Interpretation": 0.0-1.0,
        "Differential Diagnosis": 0.0-1.0,
        "Clinical Correlation": 0.0-1.0,
        "Management Recommendations": 0.0-1.0,
        "Communication & Organization": 0.0-1.0,
        "Professional Judgment": 0.0-1.0,
        "Safety Considerations": 0.0-1.0
    }},
    "category_feedback": {{
        "category_name": "specific feedback for each category"
    }},
    "strengths": ["overall strengths"],
    "areas_for_improvement": ["areas needing work"],
    "recommendations": ["specific recommendations"],
    "abr_readiness": "assessment of ABR exam readiness"
}}

Evaluate comprehensively across all ABR competency areas.
"""
    
    def _create_follow_up_prompt(self, category: str, session_data: SessionData) -> str:
        """Create prompt for generating follow-up questions"""
        return f"""
Generate a targeted follow-up question for a radiology resident who showed weakness in: {category}

CASE ID: {session_data.case_id}
WEAK CATEGORY: {category}

Create a Socratic-style follow-up question that helps the resident:
1. Recognize their knowledge gap
2. Think through the correct approach
3. Learn the underlying principles

Provide response in JSON format:
{{
    "question": "targeted follow-up question",
    "guidance": "teaching points to help the resident",
    "learning_objectives": ["specific learning goals"]
}}

Make the question specific to the case and educational.
"""
    
    def _create_follow_up_evaluation_prompt(self, follow_up_answers: List[Dict], session_data: SessionData) -> str:
        """Create prompt for evaluating follow-up responses"""
        answers_text = "\n".join([
            f"Category: {ans.get('category', 'Unknown')}\nQuestion: {ans.get('question', '')}\nAnswer: {ans.get('answer', '')}\n"
            for ans in follow_up_answers
        ])
        
        return f"""
Evaluate this radiology resident's follow-up responses and learning progress.

CASE ID: {session_data.case_id}
FOLLOW-UP RESPONSES:
{answers_text}

Assess the resident's learning and improvement. Provide evaluation in JSON format:
{{
    "evaluation": "overall assessment of follow-up responses",
    "improvement_noted": boolean,
    "learning_progress": "description of learning progression",
    "final_recommendations": ["recommendations for continued learning"]
}}

Focus on educational value and learning trajectory.
"""
    
    def _parse_grading_response(self, response: Dict[str, Any], question_id: str, answer_text: str) -> GradingResult:
        """Parse AI response into GradingResult object"""
        return GradingResult(
            question_id=question_id,
            answer_id=f"ans_{question_id}",
            score=float(response.get("score", 0.0)),
            feedback=response.get("feedback", ""),
            strengths=response.get("strengths", []),
            weaknesses=response.get("weaknesses", []),
            suggestions=response.get("suggestions", []),
            needs_follow_up=response.get("needs_follow_up", False),
            metadata={
                "model": self.model,
                "answer_length": len(answer_text),
                "grading_method": "ai_comprehensive"
            }
        )
    
    def _parse_comprehensive_grading(self, response: Dict[str, Any], session_data: SessionData) -> Dict[str, Any]:
        """Parse comprehensive grading response"""
        return {
            "category_scores": response.get("category_scores", {}),
            "category_feedback": response.get("category_feedback", {}),
            "strengths": response.get("strengths", []),
            "areas_for_improvement": response.get("areas_for_improvement", []),
            "recommendations": response.get("recommendations", []),
            "abr_readiness": response.get("abr_readiness", "")
        }
    
    def _calculate_overall_score(self, category_scores: Dict[str, float]) -> float:
        """Calculate weighted overall score"""
        default_weights = {
            "Image Interpretation": 0.2,
            "Differential Diagnosis": 0.2,
            "Clinical Correlation": 0.15,
            "Management Recommendations": 0.15,
            "Communication & Organization": 0.15,
            "Professional Judgment": 0.1,
            "Safety Considerations": 0.05
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for category, score in category_scores.items():
            weight = default_weights.get(category, 0.1)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def validate_request(self, request: AgentRequest) -> bool:
        """Validate that the request is properly formatted"""
        if not request.action:
            return False
        
        if request.action not in self.capabilities:
            return False
        
        return True