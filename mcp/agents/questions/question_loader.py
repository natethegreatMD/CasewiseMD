"""
Question loader for loading and managing diagnostic questions
"""

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from ...core.models import Question, QuestionType


class QuestionLoader:
    """Loads questions from files and generates fallback questions"""
    
    def __init__(self, demo_cases_path: str = "demo_cases"):
        self.demo_cases_path = Path(demo_cases_path)
        self.fallback_questions = self._generate_fallback_questions()
    
    def load_questions_for_case(self, case_id: str) -> List[Question]:
        """Load questions for a specific case"""
        case_path = self.demo_cases_path / case_id
        questions_file = case_path / "questions.json"
        
        if questions_file.exists():
            return self._load_from_json(questions_file)
        else:
            # Use fallback questions if no case-specific questions exist
            return self.fallback_questions
    
    def _load_from_json(self, questions_file: Path) -> List[Question]:
        """Load questions from a JSON file"""
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
            
            questions = []
            for i, q_data in enumerate(questions_data.get("questions", [])):
                question = Question(
                    id=f"q_{i+1}",
                    type=QuestionType.DIAGNOSTIC,
                    category=q_data.get("rubric_category", "General"),
                    text=q_data.get("question", ""),
                    rubric_category=q_data.get("rubric_category"),
                    metadata={
                        "step": q_data.get("step", i+1),
                        "context": q_data.get("context", ""),
                        "hint": q_data.get("hint", ""),
                        "focus_areas": q_data.get("focus_areas", []),
                        "difficulty": q_data.get("difficulty", "intermediate"),
                        "expected_elements": q_data.get("expected_elements", []),
                        "type": q_data.get("type", "free_text")
                    }
                )
                questions.append(question)
            
            return questions
        except Exception as e:
            print(f"Error loading questions from {questions_file}: {e}")
            return self.fallback_questions
    
    def _generate_fallback_questions(self) -> List[Question]:
        """Generate fallback questions when no case-specific questions exist"""
        fallback_data = [
            {
                "rubric_category": "Image Interpretation",
                "question": "Describe the key imaging findings in this case. What anatomical structures are involved?",
                "context": "Focus on systematic image interpretation",
                "hint": "Consider location, size, signal characteristics, and enhancement patterns"
            },
            {
                "rubric_category": "Differential Diagnosis", 
                "question": "Based on the imaging findings, what is your differential diagnosis? List the most likely diagnoses in order of probability.",
                "context": "Provide a focused differential diagnosis",
                "hint": "Consider patient demographics, clinical presentation, and imaging patterns"
            },
            {
                "rubric_category": "Clinical Correlation",
                "question": "How do the imaging findings correlate with the patient's clinical presentation and history?",
                "context": "Integrate imaging with clinical information",
                "hint": "Consider symptoms, physical exam findings, and laboratory results"
            },
            {
                "rubric_category": "Management Recommendations",
                "question": "What are your recommendations for further imaging or clinical management?",
                "context": "Provide actionable next steps",
                "hint": "Consider need for additional imaging, biopsy, or follow-up"
            },
            {
                "rubric_category": "Communication & Organization",
                "question": "How would you communicate these findings to the referring physician? What is the most critical information to convey?",
                "context": "Focus on clear, concise communication",
                "hint": "Prioritize urgent findings and actionable recommendations"
            },
            {
                "rubric_category": "Professional Judgment",
                "question": "What is your level of confidence in the diagnosis? What factors contribute to diagnostic uncertainty?",
                "context": "Demonstrate clinical reasoning",
                "hint": "Consider alternative diagnoses and limiting factors"
            },
            {
                "rubric_category": "Safety Considerations",
                "question": "Are there any safety considerations or urgent findings that require immediate attention?",
                "context": "Identify time-sensitive findings",
                "hint": "Consider life-threatening conditions or complications"
            }
        ]
        
        questions = []
        for i, q_data in enumerate(fallback_data):
            question = Question(
                id=f"fallback_q_{i+1}",
                type=QuestionType.DIAGNOSTIC,
                category=q_data["rubric_category"],
                text=q_data["question"],
                rubric_category=q_data["rubric_category"],
                metadata={
                    "step": i+1,
                    "context": q_data["context"],
                    "hint": q_data["hint"],
                    "focus_areas": [],
                    "difficulty": "intermediate",
                    "expected_elements": [],
                    "type": "free_text",
                    "is_fallback": True
                }
            )
            questions.append(question)
        
        return questions
    
    def generate_follow_up_question(self, category: str, weak_areas: List[str]) -> Question:
        """Generate a follow-up question for a specific category"""
        follow_up_templates = {
            "Image Interpretation": "You mentioned {weak_areas}. Can you elaborate on the specific imaging characteristics that led to this assessment?",
            "Differential Diagnosis": "Regarding {weak_areas}, what additional findings would help differentiate between the diagnoses you mentioned?",
            "Clinical Correlation": "You noted {weak_areas}. How would you explain the relationship between these findings and the patient's symptoms?",
            "Management Recommendations": "Considering {weak_areas}, what specific follow-up timeline would you recommend and why?",
            "Communication & Organization": "In discussing {weak_areas}, how would you prioritize this information when speaking with the referring physician?",
            "Professional Judgment": "Given your concerns about {weak_areas}, what additional information would increase your diagnostic confidence?",
            "Safety Considerations": "Regarding {weak_areas}, what immediate steps would you take to ensure patient safety?"
        }
        
        weak_areas_str = ", ".join(weak_areas) if weak_areas else "your response"
        question_text = follow_up_templates.get(category, 
            f"Can you provide more detail about {weak_areas_str}?").format(weak_areas=weak_areas_str)
        
        return Question(
            id=f"followup_{category.lower().replace(' ', '_')}",
            type=QuestionType.FOLLOW_UP,
            category=category,
            text=question_text,
            rubric_category=category,
            metadata={
                "type": "follow_up",
                "original_category": category,
                "weak_areas": weak_areas,
                "difficulty": "advanced"
            }
        )
    
    def get_case_metadata(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Load case metadata if available"""
        case_path = self.demo_cases_path / case_id
        metadata_file = case_path / "metadata.json"
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading metadata from {metadata_file}: {e}")
        
        return None