"""
AI-powered grading service using OpenAI GPT-4o
Provides real grading analysis with follow-up questions for weak areas
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
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
                
                # Check if question was skipped
                is_skipped = answer.strip() == "[SKIPPED]"
                
                formatted_answers.append({
                    "question_number": step,
                    "rubric_category": category,
                    "answer": answer.strip(),
                    "word_count": len(answer.split()) if not is_skipped else 0,
                    "is_skipped": is_skipped
                })
            except (ValueError, IndexError):
                # Handle invalid question numbers
                is_skipped = answer.strip() == "[SKIPPED]"
                formatted_answers.append({
                    "question_number": question_num,
                    "rubric_category": "Unknown",
                    "answer": answer.strip(),
                    "word_count": len(answer.split()) if not is_skipped else 0,
                    "is_skipped": is_skipped
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
            if answer.get('is_skipped', False):
                answers_text += f"Student Answer: [QUESTION SKIPPED BY STUDENT]\n"
                answers_text += f"Word Count: 0\n"
            else:
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
1. **SKIPPED QUESTIONS**: Any question marked as "[QUESTION SKIPPED BY STUDENT]" must receive a score of 0 for that category. Provide feedback explaining that the question was skipped.
2. **Do not award high scores for vague, generic, or padded answers**
3. **Score ranges**: 
   - 85-95%: Excellent ABR oral board level performance
   - 70-84%: Good medical knowledge with minor gaps
   - 50-69%: Basic understanding but significant deficiencies
   - Below 50%: Poor performance with major knowledge gaps

4. **Look for specific medical knowledge**:
   - Accurate imaging interpretation
   - Appropriate differential diagnoses
   - Clinical correlation and staging knowledge
   - Professional communication skills
   - Safety awareness

5. **Penalize**:
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
        """Fallback grading when AI is not available"""
        logger.warning("Using fallback grading system")
        
        # Default categories
        default_categories = [
            "Image Interpretation",
            "Differential Diagnosis", 
            "Clinical Correlation",
            "Management Recommendations",
            "Communication & Organization",
            "Professional Judgment",
            "Safety Considerations"
        ]
        
        category_scores = {}
        total_score = 0
        strengths = []
        areas_for_improvement = []
        
        for question_num, answer in answers.items():
            try:
                step = int(question_num)
                category = default_categories[step - 1] if step <= len(default_categories) else f"Question {step}"
                
                # Check if question was skipped
                if answer.strip() == "[SKIPPED]":
                    # Score skipped questions as 0
                    score = 0
                    percentage = 0
                    feedback = "Question was skipped by student. No assessment possible."
                    areas_for_improvement.append(f"Complete all questions for {category}")
                else:
                    # Calculate score based on content
                    score = self._calculate_content_score(answer)
                    percentage = score
                    feedback = self._generate_fallback_feedback(answer, category, score)
                    
                    if score >= 70:
                        strengths.append(f"Good performance in {category}")
                    else:
                        areas_for_improvement.append(f"Improvement needed in {category}")
                
                category_scores[category] = {
                    "score": score,
                    "percentage": percentage,
                    "feedback": feedback
                }
                total_score += score
                
            except (ValueError, IndexError):
                # Handle invalid question numbers
                if answer.strip() == "[SKIPPED]":
                    score = 0
                    feedback = "Question was skipped by student. No assessment possible."
                else:
                    score = self._calculate_content_score(answer)
                    feedback = self._generate_fallback_feedback(answer, f"Question {question_num}", score)
                
                category_scores[f"Question {question_num}"] = {
                    "score": score,
                    "percentage": score,
                    "feedback": feedback
                }
                total_score += score
        
        # Calculate average
        num_questions = len(answers)
        overall_percentage = total_score / num_questions if num_questions > 0 else 0
        
        # Generate overall feedback
        overall_feedback = self._generate_overall_fallback_feedback(overall_percentage)
        
        # Generate fallback follow-up questions
        follow_up_questions = []
        for category, result in category_scores.items():
            if result["percentage"] < 70:
                follow_up_q = self._generate_fallback_follow_up(category, case_id)
                follow_up_questions.append({
                    "category": category,
                    "question": follow_up_q,
                    "purpose": f"Strengthen understanding in {category}",
                    "score": result["percentage"]
                })
        
        return {
            "category_scores": category_scores,
            "total_score": total_score,
            "overall_percentage": overall_percentage,
            "overall_feedback": overall_feedback,
            "strengths": strengths,
            "areas_for_improvement": areas_for_improvement,
            "abr_readiness": "Limited assessment available due to system constraints",
            "follow_up_questions": follow_up_questions,
            "grading_method": "fallback_content_analysis"
        }
    
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
        """Generate fallback follow-up questions"""
        
        # Map categories to relevant follow-up questions
        category_questions = {
            "Image Interpretation": "What specific imaging findings would you look for in this type of case?",
            "Differential Diagnosis": "What are the most common differential diagnoses for these imaging findings?",
            "Clinical Correlation": "How would you correlate these imaging findings with clinical presentation?",
            "Management Recommendations": "What would be your recommended next steps for patient management?",
            "Communication & Organization": "How would you present these findings to the referring physician?",
            "Professional Judgment": "What factors would influence your clinical decision-making in this case?",
            "Safety Considerations": "What safety considerations should be addressed in this case?"
        }
        
        # Return category-specific question or generic question
        return category_questions.get(category, f"Please provide additional thoughts on {category} for this case.")
    
    def _generate_overall_fallback_feedback(self, score: float) -> str:
        """Generate overall feedback for fallback grading"""
        
        if score < 50:
            return "Significant improvement needed. Focus on developing systematic approach to image interpretation and expanding medical knowledge base."
        elif score < 70:
            return "Good foundation but needs development. Work on incorporating more specific medical terminology and comprehensive analysis."
        else:
            return "Strong performance overall. Continue refining systematic approach and consider advanced radiology concepts."

    async def evaluate_followup_answers(
        self, 
        followup_answers: Dict[str, str],
        original_followup_questions: List[Dict[str, Any]],
        case_id: str,
        original_grading: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate student's follow-up answers and provide personalized feedback
        
        Args:
            followup_answers: Dict mapping question index to student answer
            original_followup_questions: The original follow-up questions that were asked
            case_id: Case identifier
            original_grading: Original grading results before follow-up
            
        Returns:
            Dictionary containing follow-up evaluation and updated assessment
        """
        try:
            if not await self._check_ai_availability():
                return self._fallback_followup_evaluation(followup_answers, original_followup_questions)
            
            # Build evaluation prompt
            evaluation_prompt = self._create_followup_evaluation_prompt(
                followup_answers, original_followup_questions, case_id, original_grading
            )
            
            # Get AI evaluation
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert medical educator providing personalized feedback on student reflections during an ABR oral board examination follow-up session."
                    },
                    {
                        "role": "user", 
                        "content": evaluation_prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.3,
                timeout=30
            )
            
            # Parse the evaluation response
            evaluation_results = self._parse_followup_evaluation(response.choices[0].message.content)
            
            # Calculate learning improvement score
            improvement_score = self._calculate_learning_improvement(
                evaluation_results, original_grading, len(followup_answers)
            )
            
            return {
                "followup_evaluations": evaluation_results,
                "learning_improvement": improvement_score,
                "overall_followup_feedback": self._generate_overall_followup_feedback(evaluation_results),
                "updated_assessment": self._update_assessment_with_followup(original_grading, improvement_score),
                "evaluation_method": "ai_gpt4o"
            }
            
        except Exception as e:
            logger.error(f"Error evaluating follow-up answers: {str(e)}")
            return self._fallback_followup_evaluation(followup_answers, original_followup_questions)

    def _create_followup_evaluation_prompt(
        self, 
        followup_answers: Dict[str, str],
        original_questions: List[Dict[str, Any]], 
        case_id: str,
        original_grading: Dict[str, Any]
    ) -> str:
        """Create prompt for evaluating follow-up answers"""
        
        # Build the evaluation context
        answers_text = ""
        for i, (idx, answer) in enumerate(followup_answers.items()):
            question_idx = int(idx)
            if question_idx < len(original_questions):
                question_info = original_questions[question_idx]
                answers_text += f"""
**Follow-up Question {i+1}**: {question_info.get('question', 'Unknown question')}
**Category**: {question_info.get('category', 'Unknown')}
**Original Score**: {question_info.get('score', 'N/A')}%
**Student's Reflection**: {answer}

---
"""
        
        original_score = original_grading.get('overall_percentage', 0)
        
        prompt = f"""You are evaluating a student's follow-up reflections during an ABR oral board examination for **{case_id.upper()}**.

**ORIGINAL PERFORMANCE**: {original_score}% overall
**WEAK AREAS**: Follow-up questions were generated for categories scoring <70%

**STUDENT'S FOLLOW-UP REFLECTIONS**:
{answers_text}

**EVALUATION TASK**: 
For each follow-up answer, provide specific feedback on:
1. **Knowledge Demonstration**: Did they show improved understanding?
2. **Clinical Reasoning**: How well did they address the knowledge gap?
3. **Learning Progress**: Evidence of reflection and growth
4. **Areas Still Needing Work**: What should they focus on next?

**RESPONSE FORMAT** (JSON):
```json
{{
  "evaluations": [
    {{
      "question_index": 0,
      "category": "category_name",
      "knowledge_demonstration": "assessment of knowledge shown",
      "clinical_reasoning": "evaluation of their reasoning process", 
      "learning_progress": "evidence of improvement/reflection",
      "areas_for_continued_focus": "specific guidance for further study",
      "improvement_score": 0-100,
      "feedback_summary": "encouraging but honest overall assessment"
    }}
  ]
}}
```

**GRADING PHILOSOPHY**:
- Reward genuine reflection and effort (even if incomplete)
- Recognize improved understanding from original weak performance
- Provide constructive guidance for continued learning
- Be encouraging but honest about remaining gaps
- Score 60-80 for good reflection, 80-95 for excellent improvement"""

        return prompt

    def _parse_followup_evaluation(self, ai_response: str) -> List[Dict[str, Any]]:
        """Parse AI evaluation response into structured format"""
        try:
            # Try to extract JSON from response
            import json
            import re
            
            # Look for JSON block
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                parsed = json.loads(json_str)
                return parsed.get("evaluations", [])
            
            # Fallback: try to parse the whole response as JSON
            try:
                parsed = json.loads(ai_response)
                return parsed.get("evaluations", [])
            except:
                pass
            
            # If JSON parsing fails, return empty list
            logger.warning("Could not parse follow-up evaluation response as JSON")
            return []
            
        except Exception as e:
            logger.error(f"Error parsing follow-up evaluation: {str(e)}")
            return []

    def _calculate_learning_improvement(
        self, 
        evaluations: List[Dict[str, Any]], 
        original_grading: Dict[str, Any],
        num_followup_answers: int
    ) -> Dict[str, Any]:
        """Calculate learning improvement score based on follow-up performance"""
        
        if not evaluations:
            return {
                "improvement_points": 0,
                "engagement_score": 0,
                "learning_trajectory": "needs_more_engagement"
            }
        
        # Calculate average improvement score from evaluations
        improvement_scores = [eval.get("improvement_score", 0) for eval in evaluations]
        avg_improvement = sum(improvement_scores) / len(improvement_scores) if improvement_scores else 0
        
        # Engagement score based on completion
        engagement_score = min(100, (len(evaluations) / num_followup_answers) * 100)
        
        # Determine learning trajectory
        if avg_improvement >= 80:
            trajectory = "excellent_improvement"
        elif avg_improvement >= 65:
            trajectory = "good_progress"
        elif avg_improvement >= 50:
            trajectory = "showing_effort"
        else:
            trajectory = "needs_more_focus"
        
        # Calculate bonus points for original score
        original_score = original_grading.get('overall_percentage', 0)
        improvement_points = min(10, (avg_improvement / 100) * 10)  # Up to 10 bonus points
        
        return {
            "improvement_points": improvement_points,
            "engagement_score": engagement_score,
            "learning_trajectory": trajectory,
            "average_reflection_score": avg_improvement,
            "followup_completion_rate": engagement_score
        }

    def _generate_overall_followup_feedback(self, evaluations: List[Dict[str, Any]]) -> str:
        """Generate overall feedback on follow-up performance"""
        
        if not evaluations:
            return "No follow-up evaluations completed. Consider engaging with follow-up questions to enhance learning."
        
        avg_score = sum(eval.get("improvement_score", 0) for eval in evaluations) / len(evaluations)
        
        if avg_score >= 80:
            return "Excellent reflection and learning demonstrated in follow-up responses. You've shown significant improvement in understanding the weak areas identified. Continue this level of analytical thinking."
        elif avg_score >= 65:
            return "Good progress shown in follow-up reflections. You're addressing the knowledge gaps effectively and demonstrating improved clinical reasoning. Focus on the areas highlighted for continued growth."
        elif avg_score >= 50:
            return "Your follow-up responses show effort and some improvement in understanding. Continue to work on the specific areas identified and seek additional resources to strengthen your knowledge base."
        else:
            return "Follow-up responses indicate continued challenges in the weak areas. Consider additional study, mentorship, or review materials to strengthen your understanding before attempting similar cases."

    def _update_assessment_with_followup(
        self, 
        original_grading: Dict[str, Any], 
        improvement_score: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update the overall assessment incorporating follow-up performance"""
        
        original_percentage = original_grading.get('overall_percentage', 0)
        improvement_points = improvement_score.get('improvement_points', 0)
        engagement_score = improvement_score.get('engagement_score', 0)
        
        # Calculate updated score (small bonus for good follow-up work)
        updated_percentage = min(100, original_percentage + improvement_points)
        
        # Update pass/fail status if applicable
        original_passed = original_grading.get('passed', False)
        updated_passed = updated_percentage >= 70
        
        learning_trajectory = improvement_score.get('learning_trajectory', 'needs_more_focus')
        
        return {
            "original_score": original_percentage,
            "improvement_bonus": improvement_points,
            "updated_score": updated_percentage,
            "originally_passed": original_passed,
            "updated_passed": updated_passed,
            "engagement_level": "high" if engagement_score >= 80 else "moderate" if engagement_score >= 50 else "low",
            "learning_trajectory": learning_trajectory,
            "recommendation": self._get_followup_recommendation(learning_trajectory, updated_percentage)
        }

    def _get_followup_recommendation(self, trajectory: str, updated_score: float) -> str:
        """Get recommendation based on follow-up performance"""
        
        if trajectory == "excellent_improvement" and updated_score >= 75:
            return "Outstanding learning progression. Ready for more challenging cases."
        elif trajectory == "good_progress" and updated_score >= 70:
            return "Solid improvement demonstrated. Continue practicing similar cases."
        elif trajectory == "showing_effort":
            return "Effort noted. Focus on the specific areas highlighted for improvement."
        else:
            return "Additional study and practice recommended before attempting ABR-level cases."

    def _fallback_followup_evaluation(
        self, 
        followup_answers: Dict[str, str],
        original_questions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback evaluation when AI is unavailable"""
        
        evaluations = []
        for idx, answer in followup_answers.items():
            question_idx = int(idx)
            if question_idx < len(original_questions):
                question = original_questions[question_idx]
                
                # Simple content analysis
                answer_length = len(answer.split())
                effort_score = min(80, max(40, answer_length * 2))  # 40-80 based on length
                
                evaluations.append({
                    "question_index": question_idx,
                    "category": question.get("category", "Unknown"),
                    "improvement_score": effort_score,
                    "feedback_summary": f"Response shows effort. Consider expanding on {question.get('category', 'this topic')} for deeper understanding."
                })
        
        avg_score = sum(eval["improvement_score"] for eval in evaluations) / len(evaluations) if evaluations else 0
        
        return {
            "followup_evaluations": evaluations,
            "learning_improvement": {
                "improvement_points": min(5, avg_score / 20),
                "engagement_score": len(evaluations) * 50,  # Basic engagement
                "learning_trajectory": "basic_effort"
            },
            "overall_followup_feedback": "Follow-up responses received. AI evaluation unavailable - manual review recommended.",
            "evaluation_method": "fallback_analysis"
        }

# Create singleton instance
ai_grading_service = AIGradingService() 