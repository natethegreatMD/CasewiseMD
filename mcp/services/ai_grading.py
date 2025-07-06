"""
AI-powered grading service using OpenAI GPT-4o
Provides real grading analysis with follow-up questions for weak areas
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
import aiohttp
import aiofiles
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=60.0,
    max_retries=3
)

class AIGradingService:
    """AI-powered grading service with follow-up question generation"""
    
    def __init__(self):
        self.model = "gpt-4o"
        self.max_tokens = 2000
        self.temperature = 0.3  # Lower temperature for more consistent grading
        
    async def grade_answers(self, answers: Dict[str, str], case_id: str, rubric: Dict[str, Any]) -> Dict[str, Any]:
        """
        Grade student answers and generate follow-up questions for weak areas
        
        Args:
            answers: Dictionary of student answers keyed by question number
            case_id: Case identifier
            rubric: Grading rubric with categories and criteria
            
        Returns:
            Dictionary containing scores, feedback, and follow-up questions
        """
        try:
            # Check if AI grading is available
            if not await self._check_ai_availability():
                logger.warning("AI grading unavailable, using fallback")
                return await self._fallback_grading(answers, case_id, rubric)
            
            # Format answers for grading
            formatted_answers = self._format_answers_for_grading(answers)
            
            # Generate grading prompt
            grading_prompt = self._create_grading_prompt(formatted_answers, case_id, rubric)
            
            # Get AI grading
            grading_response = await self._get_ai_grading(grading_prompt)
            
            # Parse grading response
            grading_results = self._parse_grading_response(grading_response)
            
            # Generate follow-up questions for weak areas
            follow_up_questions = await self._generate_follow_up_questions(
                grading_results, formatted_answers, case_id, rubric
            )
            
            # Add follow-up questions to results
            grading_results["follow_up_questions"] = follow_up_questions
            
            # Add grading method metadata
            grading_results["grading_method"] = "ai_gpt4o"
            
            return grading_results
            
        except Exception as e:
            logger.error(f"Error in AI grading: {str(e)}")
            return await self._fallback_grading(answers, case_id, rubric)
    
    async def _check_ai_availability(self) -> bool:
        """Check if OpenAI API is available"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OpenAI API key not found")
                return False
            
            # Test API connectivity with a minimal request
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5,
                timeout=10
            )
            return bool(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"AI availability check failed: {str(e)}")
            return False
    
    def _format_answers_for_grading(self, answers: Dict[str, str]) -> List[Dict[str, Any]]:
        """Format answers for AI grading"""
        formatted_answers = []
        
        # Default rubric categories for question mapping
        default_categories = [
            "Image Interpretation",
            "Differential Diagnosis", 
            "Clinical Correlation",
            "Management Recommendations",
            "Communication & Organization",
            "Professional Judgment",
            "Safety Considerations"
        ]
        
        for question_num, answer in answers.items():
            try:
                step = int(question_num)
                category = default_categories[step - 1] if step <= len(default_categories) else f"Question {step}"
                
                formatted_answers.append({
                    "question_number": step,
                    "rubric_category": category,
                    "answer": answer.strip(),
                    "word_count": len(answer.split())
                })
            except (ValueError, IndexError):
                # Handle invalid question numbers
                formatted_answers.append({
                    "question_number": question_num,
                    "rubric_category": "Unknown",
                    "answer": answer.strip(),
                    "word_count": len(answer.split())
                })
        
        return formatted_answers
    
    def _create_grading_prompt(self, answers: List[Dict[str, Any]], case_id: str, rubric: Dict[str, Any]) -> str:
        """Create comprehensive grading prompt for AI"""
        
        # Format rubric for display
        rubric_text = ""
        categories = rubric.get("categories", [])
        
        # Handle both array and dict formats for categories
        if isinstance(categories, list):
            # New format: categories is an array
            for category in categories:
                name = category.get("name", "Unknown")
                weight = category.get("weight", 0)
                description = category.get("description", "")
                
                rubric_text += f"\n**{name}** ({weight*100:.0f}% of total grade):\n"
                rubric_text += f"Description: {description}\n"
                
                # Add criteria
                for criterion in category.get("criteria", []):
                    criterion_name = criterion.get("name", "")
                    criterion_desc = criterion.get("description", "")
                    rubric_text += f"- {criterion_name}: {criterion_desc}\n"
                    
                    # Add key findings
                    key_findings = criterion.get("key_findings", [])
                    if key_findings:
                        rubric_text += f"  Key findings: {', '.join(key_findings)}\n"
                rubric_text += "\n"
        else:
            # Legacy format: categories is a dict
            for category, details in categories.items():
                weight = details.get("weight", 0)
                rubric_text += f"\n**{category}** ({weight}% of total grade):\n"
                
                for criterion in details.get("criteria", []):
                    rubric_text += f"- {criterion}\n"
                
                # Add key findings if available
                if "key_findings" in details:
                    rubric_text += f"Key findings to look for: {', '.join(details['key_findings'])}\n"
        
        # Format answers
        answers_text = ""
        for answer in answers:
            answers_text += f"\n**{answer['rubric_category']} (Question {answer['question_number']})**:\n"
            answers_text += f"Student Answer: {answer['answer']}\n"
            answers_text += f"Word Count: {answer['word_count']}\n"
        
        prompt = f"""You are an expert medical educator evaluating radiology resident performance on an ABR-style oral board examination.

**CASE CONTEXT**: {case_id.upper()} - Ovarian Cancer Case
This is a complex gynecological oncology case requiring systematic evaluation of CT imaging findings.

**GRADING RUBRIC**:
{rubric_text}

**STUDENT ANSWERS**:
{answers_text}

**GRADING INSTRUCTIONS**:
1. **Do not award high scores for vague, generic, or padded answers**
2. **Score ranges**: 
   - 85-95%: Excellent ABR oral board level performance
   - 70-84%: Good medical knowledge with minor gaps
   - 50-69%: Basic understanding but significant deficiencies
   - Below 50%: Poor performance with major knowledge gaps

3. **Look for specific medical knowledge**:
   - Accurate imaging interpretation
   - Appropriate differential diagnoses
   - Clinical correlation and staging knowledge
   - Professional communication skills
   - Safety awareness

4. **Penalize**:
   - Generic or vague responses
   - Lack of specific medical terminology
   - Missing key findings or diagnoses
   - Poor organization or communication
   - Inappropriate management recommendations

**REQUIRED OUTPUT FORMAT** (JSON):
{{
  "category_scores": {{
    "Image Interpretation": {{"score": X, "percentage": Y, "feedback": "specific feedback"}},
    "Differential Diagnosis": {{"score": X, "percentage": Y, "feedback": "specific feedback"}},
    "Clinical Correlation": {{"score": X, "percentage": Y, "feedback": "specific feedback"}},
    "Management Recommendations": {{"score": X, "percentage": Y, "feedback": "specific feedback"}},
    "Communication & Organization": {{"score": X, "percentage": Y, "feedback": "specific feedback"}},
    "Professional Judgment": {{"score": X, "percentage": Y, "feedback": "specific feedback"}},
    "Safety Considerations": {{"score": X, "percentage": Y, "feedback": "specific feedback"}}
  }},
  "total_score": X,
  "overall_percentage": Y,
  "overall_feedback": "comprehensive summary of performance",
  "strengths": ["strength1", "strength2"],
  "areas_for_improvement": ["area1", "area2"],
  "abr_readiness": "assessment of ABR oral board readiness"
}}

Provide detailed, constructive feedback that helps the student improve their ABR oral board performance."""

        return prompt
    
    async def _get_ai_grading(self, prompt: str) -> str:
        """Get grading response from OpenAI"""
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert medical educator and radiologist evaluating student performance on ABR oral board examinations. Provide detailed, accurate, and constructive feedback."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=60
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error getting AI grading: {str(e)}")
            raise
    
    def _parse_grading_response(self, response: str) -> Dict[str, Any]:
        """Parse AI grading response"""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            grading_data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["category_scores", "total_score", "overall_percentage", "overall_feedback"]
            for field in required_fields:
                if field not in grading_data:
                    raise ValueError(f"Missing required field: {field}")
            
            return grading_data
            
        except Exception as e:
            logger.error(f"Error parsing grading response: {str(e)}")
            logger.error(f"Response content: {response}")
            raise
    
    async def _generate_follow_up_questions(
        self, 
        grading_results: Dict[str, Any], 
        formatted_answers: List[Dict[str, Any]], 
        case_id: str, 
        rubric: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate follow-up questions for weak rubric categories (< 70%)"""
        
        try:
            # Identify weak categories
            weak_categories = []
            category_scores = grading_results.get("category_scores", {})
            
            for category, score_data in category_scores.items():
                percentage = score_data.get("percentage", 0)
                if percentage < 70:
                    weak_categories.append({
                        "category": category,
                        "score": percentage,
                        "feedback": score_data.get("feedback", "")
                    })
            
            # If no weak categories, return empty list
            if not weak_categories:
                return []
            
            # Limit to 2 weakest categories
            weak_categories = sorted(weak_categories, key=lambda x: x["score"])[:2]
            
            # Generate follow-up questions for weak areas
            follow_up_questions = []
            
            for weak_cat in weak_categories:
                category = weak_cat["category"]
                
                # Find the student's answer for this category
                student_answer = ""
                for answer in formatted_answers:
                    if answer["rubric_category"] == category:
                        student_answer = answer["answer"]
                        break
                
                # Generate follow-up question
                follow_up_question = await self._generate_category_follow_up(
                    category, student_answer, case_id, weak_cat["feedback"]
                )
                
                if follow_up_question:
                    follow_up_questions.append({
                        "category": category,
                        "score": weak_cat["score"],
                        "question": follow_up_question,
                        "purpose": "Encourage deeper thinking and address knowledge gaps",
                        "type": "learning_only"
                    })
            
            return follow_up_questions
            
        except Exception as e:
            logger.error(f"Error generating follow-up questions: {str(e)}")
            return []
    
    async def _generate_category_follow_up(
        self, 
        category: str, 
        student_answer: str, 
        case_id: str, 
        feedback: str
    ) -> Optional[str]:
        """Generate a specific follow-up question for a weak category"""
        
        try:
            prompt = f"""You are an expert medical educator conducting an ABR oral board examination. The student has shown weakness in the "{category}" category.

**CASE**: {case_id.upper()} - Ovarian Cancer Case
**WEAK CATEGORY**: {category}
**STUDENT'S ANSWER**: {student_answer}
**FEEDBACK**: {feedback}

Generate ONE thoughtful, Socratic-style follow-up question that:
1. Encourages deeper thinking about this specific category
2. Addresses the knowledge gap identified in the feedback
3. Sounds like a natural follow-up an oral board examiner would ask
4. Is specific to this ovarian cancer case
5. Helps the student learn, not just test them

**CATEGORY-SPECIFIC GUIDANCE**:
- Image Interpretation: Ask about specific imaging findings they missed or misinterpreted
- Differential Diagnosis: Challenge their reasoning or ask about alternative diagnoses
- Clinical Correlation: Explore symptom correlation or staging implications
- Management Recommendations: Ask about specific next steps or specialist involvement
- Communication & Organization: Focus on how they would explain findings to clinicians
- Professional Judgment: Explore critical finding recognition or ethical considerations
- Safety Considerations: Ask about radiation safety, contrast issues, or alternative imaging

Return only the question, no additional text or explanation."""

            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert medical educator specializing in radiology education and ABR oral board examinations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.4,
                timeout=30
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating category follow-up for {category}: {str(e)}")
            return None
    
    async def _fallback_grading(self, answers: Dict[str, str], case_id: str, rubric: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced fallback grading when AI is unavailable"""
        
        try:
            category_scores = {}
            total_weighted_score = 0
            
            # Default rubric categories with weights
            default_categories = {
                "Image Interpretation": 35,
                "Differential Diagnosis": 25,
                "Clinical Correlation": 15,
                "Management Recommendations": 10,
                "Communication & Organization": 10,
                "Professional Judgment": 5,
                "Safety Considerations": 5
            }
            
            for i, (question_num, answer) in enumerate(answers.items(), 1):
                category = list(default_categories.keys())[i-1] if i <= len(default_categories) else f"Question {i}"
                weight = default_categories.get(category, 10)
                
                # Content-based scoring
                score = self._calculate_content_score(answer)
                weighted_score = (score * weight) / 100
                total_weighted_score += weighted_score
                
                # Generate basic feedback
                feedback = self._generate_fallback_feedback(answer, category, score)
                
                category_scores[category] = {
                    "score": score,
                    "percentage": score,
                    "feedback": feedback,
                    "weight": weight
                }
            
            # Generate fallback follow-up questions for weak areas
            follow_up_questions = []
            for category, score_data in category_scores.items():
                if score_data["percentage"] < 70:
                    follow_up_questions.append({
                        "category": category,
                        "score": score_data["percentage"],
                        "question": self._generate_fallback_follow_up(category, case_id),
                        "purpose": "Encourage deeper thinking and address knowledge gaps",
                        "type": "learning_only"
                    })
            
            # Limit to 2 follow-up questions
            follow_up_questions = follow_up_questions[:2]
            
            return {
                "category_scores": category_scores,
                "total_score": round(total_weighted_score),
                "overall_percentage": round(total_weighted_score),
                "overall_feedback": self._generate_overall_fallback_feedback(total_weighted_score),
                "strengths": ["Completed all questions", "Provided detailed responses"],
                "areas_for_improvement": ["Consider more specific medical terminology", "Focus on key diagnostic findings"],
                "abr_readiness": "Additional study recommended" if total_weighted_score < 70 else "Good foundation for ABR preparation",
                "follow_up_questions": follow_up_questions,
                "grading_method": "fallback_content_analysis"
            }
            
        except Exception as e:
            logger.error(f"Error in fallback grading: {str(e)}")
            return self._emergency_fallback()
    
    def _calculate_content_score(self, answer: str) -> int:
        """Calculate score based on content analysis"""
        if not answer or not answer.strip():
            return 0
        
        answer_lower = answer.lower().strip()
        word_count = len(answer.split())
        
        # Detect gibberish or non-medical content
        gibberish_terms = [
            "lorem", "ipsum", "dolor", "sit", "amet", "test", "testing", "xyz", 
            "asdf", "qwerty", "hello", "world", "yo", "sup", "what", "huh", "umm",
            "asd", "zxc", "qwe", "rty", "fgh", "dfg", "cvb", "bnm"
        ]
        
        gibberish_count = sum(1 for term in gibberish_terms if term in answer_lower)
        if gibberish_count > 2:
            return 0
        
        # Very short or minimal effort
        if word_count < 10:
            return 25
        
        # Basic medical terminology check
        medical_terms = [
            "imaging", "findings", "diagnosis", "differential", "clinical", "patient",
            "medical", "treatment", "management", "follow", "workup", "test", "scan",
            "ct", "mri", "ultrasound", "radiologist", "physician", "doctor", "hospital",
            "disease", "condition", "symptoms", "signs", "abnormal", "normal", "study",
            "examination", "evaluation", "assessment", "recommendation", "consultation",
            "ovarian", "cancer", "malignancy", "tumor", "mass", "peritoneal", "ascites",
            "metastasis", "staging", "oncology", "gynecology", "radiology", "abdominal",
            "pelvic", "contrast", "enhancement", "biopsy", "surgery", "chemotherapy"
        ]
        
        medical_term_count = sum(1 for term in medical_terms if term in answer_lower)
        
        # Content caps for poor content
        if word_count < 50 and medical_term_count < 10:
            return min(40, 20 + medical_term_count * 2)
        
        # Score based on completeness and medical content
        if word_count >= 100 and medical_term_count >= 15:
            return min(85, 60 + medical_term_count)
        elif word_count >= 50 and medical_term_count >= 10:
            return min(75, 45 + medical_term_count * 2)
        elif word_count >= 25 and medical_term_count >= 5:
            return min(65, 35 + medical_term_count * 3)
        else:
            return min(45, 25 + medical_term_count * 4)
    
    def _generate_fallback_feedback(self, answer: str, category: str, score: int) -> str:
        """Generate basic feedback for fallback grading"""
        
        if score < 30:
            return f"Insufficient response for {category}. Please provide more detailed medical analysis."
        elif score < 50:
            return f"Basic response for {category}. Consider including more specific medical terminology and detailed analysis."
        elif score < 70:
            return f"Good effort on {category}. Work on providing more comprehensive and systematic evaluation."
        else:
            return f"Strong response for {category}. Good use of medical terminology and systematic approach."
    
    def _generate_fallback_follow_up(self, category: str, case_id: str) -> str:
        """Generate fallback follow-up questions for weak categories"""
        
        category_questions = {
            "Image Interpretation": "Can you describe the specific imaging characteristics that led to your assessment? What systematic approach did you use to evaluate the images?",
            "Differential Diagnosis": "What specific imaging features helped you prioritize your differential diagnosis? Are there any other conditions you should consider?",
            "Clinical Correlation": "How would you expect this patient to present clinically? What is the staging significance of the findings you described?",
            "Management Recommendations": "What specific tumor markers would you recommend? Which specialists should be involved in this patient's care?",
            "Communication & Organization": "How would you structure your radiology report for this case? What are the key points you would emphasize to the referring clinician?",
            "Professional Judgment": "What findings in this case would require urgent communication? How would you handle the timing of result communication?",
            "Safety Considerations": "What are the radiation safety considerations for this imaging approach? Are there alternative imaging modalities you would consider?"
        }
        
        return category_questions.get(category, f"Can you elaborate on your approach to {category.lower()} in this case?")
    
    def _generate_overall_fallback_feedback(self, score: float) -> str:
        """Generate overall feedback for fallback grading"""
        
        if score < 50:
            return "Significant improvement needed. Focus on developing systematic approach to image interpretation and expanding medical knowledge base."
        elif score < 70:
            return "Good foundation but needs development. Work on incorporating more specific medical terminology and comprehensive analysis."
        else:
            return "Strong performance overall. Continue refining systematic approach and consider advanced radiology concepts."
    
    def _emergency_fallback(self) -> Dict[str, Any]:
        """Emergency fallback when all other methods fail"""
        
        return {
            "category_scores": {
                "Image Interpretation": {"score": 50, "percentage": 50, "feedback": "Unable to grade - system error"},
                "Differential Diagnosis": {"score": 50, "percentage": 50, "feedback": "Unable to grade - system error"},
                "Clinical Correlation": {"score": 50, "percentage": 50, "feedback": "Unable to grade - system error"},
                "Management Recommendations": {"score": 50, "percentage": 50, "feedback": "Unable to grade - system error"},
                "Communication & Organization": {"score": 50, "percentage": 50, "feedback": "Unable to grade - system error"},
                "Professional Judgment": {"score": 50, "percentage": 50, "feedback": "Unable to grade - system error"},
                "Safety Considerations": {"score": 50, "percentage": 50, "feedback": "Unable to grade - system error"}
            },
            "total_score": 50,
            "overall_percentage": 50,
            "overall_feedback": "Grading system temporarily unavailable. Please try again later.",
            "strengths": ["Completed diagnostic session"],
            "areas_for_improvement": ["System unable to provide detailed feedback"],
            "abr_readiness": "Unable to assess",
            "follow_up_questions": [],
            "grading_method": "emergency_fallback",
            "error": "Grading system temporarily unavailable"
        }

# Create singleton instance
ai_grading_service = AIGradingService() 