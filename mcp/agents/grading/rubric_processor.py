"""
Rubric processor for loading and interpreting grading rubrics
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path


class RubricProcessor:
    """
    Processes rubric files and provides criteria for grading
    """
    
    def __init__(self, rubric_path: str = "/app/rubrics"):
        self.rubric_path = Path(rubric_path)
        self.loaded_rubrics: Dict[str, Dict[str, Any]] = {}
        
        # Default ABR category weights
        self.default_weights = {
            "Image Interpretation": 0.35,
            "Differential Diagnosis": 0.25,
            "Clinical Correlation": 0.15,
            "Management Recommendations": 0.10,
            "Communication & Organization": 0.10,
            "Professional Judgment": 0.05,
            "Safety Considerations": 0.05  # Bonus category
        }
    
    async def load_rubric(self, case_id: str) -> Dict[str, Any]:
        """Load rubric for a specific case"""
        if case_id in self.loaded_rubrics:
            return self.loaded_rubrics[case_id]
        
        # Try to find rubric file
        rubric_file = self.rubric_path / f"{case_id}_rubric.json"
        
        if not rubric_file.exists():
            # Try alternate naming
            rubric_file = self.rubric_path / f"rubric_{case_id}.json"
        
        if not rubric_file.exists():
            # Return default rubric structure
            return self._get_default_rubric(case_id)
        
        try:
            with open(rubric_file, 'r') as f:
                rubric = json.load(f)
                self.loaded_rubrics[case_id] = rubric
                return rubric
        except Exception as e:
            # Log error and return default
            return self._get_default_rubric(case_id)
    
    async def get_category_criteria(self, case_id: str, category: str) -> Dict[str, Any]:
        """Get grading criteria for a specific category"""
        rubric = await self.load_rubric(case_id)
        
        # Look for category in rubric
        categories = rubric.get("categories", {})
        
        if category in categories:
            return categories[category]
        
        # Return default criteria for category
        return self._get_default_category_criteria(category)
    
    async def get_category_weights(self, case_id: str) -> Dict[str, float]:
        """Get category weights for final score calculation"""
        rubric = await self.load_rubric(case_id)
        
        # Check if rubric has custom weights
        if "weights" in rubric:
            return rubric["weights"]
        
        return self.default_weights
    
    def _get_default_rubric(self, case_id: str) -> Dict[str, Any]:
        """Generate default rubric structure"""
        return {
            "case_id": case_id,
            "title": f"Grading Rubric for {case_id}",
            "categories": {
                "Image Interpretation": self._get_default_category_criteria("Image Interpretation"),
                "Differential Diagnosis": self._get_default_category_criteria("Differential Diagnosis"),
                "Clinical Correlation": self._get_default_category_criteria("Clinical Correlation"),
                "Management Recommendations": self._get_default_category_criteria("Management Recommendations"),
                "Communication & Organization": self._get_default_category_criteria("Communication & Organization"),
                "Professional Judgment": self._get_default_category_criteria("Professional Judgment"),
                "Safety Considerations": self._get_default_category_criteria("Safety Considerations")
            },
            "weights": self.default_weights
        }
    
    def _get_default_category_criteria(self, category: str) -> Dict[str, Any]:
        """Get default criteria for a category"""
        criteria_map = {
            "Image Interpretation": {
                "description": "Accurate identification and description of imaging findings",
                "criteria": [
                    "Correctly identifies primary abnormality",
                    "Describes location, size, and characteristics",
                    "Notes secondary findings",
                    "Uses appropriate medical terminology"
                ],
                "scoring": {
                    "excellent": "All major findings identified with detailed description",
                    "good": "Most findings identified with adequate description",
                    "satisfactory": "Primary findings identified with basic description",
                    "needs_improvement": "Some findings missed or incorrectly described"
                }
            },
            "Differential Diagnosis": {
                "description": "Appropriate differential diagnosis based on imaging findings",
                "criteria": [
                    "Lists relevant differential diagnoses",
                    "Prioritizes based on likelihood",
                    "Considers patient demographics",
                    "Includes both common and important diagnoses"
                ],
                "scoring": {
                    "excellent": "Comprehensive differential with appropriate prioritization",
                    "good": "Good differential with minor omissions",
                    "satisfactory": "Basic differential with key diagnoses",
                    "needs_improvement": "Limited or inappropriate differential"
                }
            },
            "Clinical Correlation": {
                "description": "Integration of imaging findings with clinical information",
                "criteria": [
                    "Relates findings to clinical presentation",
                    "Considers relevant history",
                    "Suggests clinical significance",
                    "Identifies urgent findings"
                ],
                "scoring": {
                    "excellent": "Strong clinical correlation with insightful connections",
                    "good": "Good correlation with clinical context",
                    "satisfactory": "Basic clinical correlation",
                    "needs_improvement": "Limited clinical integration"
                }
            },
            "Management Recommendations": {
                "description": "Appropriate next steps and management suggestions",
                "criteria": [
                    "Suggests appropriate follow-up imaging",
                    "Recommends clinical actions",
                    "Considers urgency appropriately",
                    "Provides alternative options"
                ],
                "scoring": {
                    "excellent": "Clear, prioritized recommendations with alternatives",
                    "good": "Appropriate recommendations with good reasoning",
                    "satisfactory": "Basic appropriate recommendations",
                    "needs_improvement": "Vague or inappropriate recommendations"
                }
            },
            "Communication & Organization": {
                "description": "Clear, organized communication of findings",
                "criteria": [
                    "Structured reporting format",
                    "Clear, concise language",
                    "Logical flow of information",
                    "Appropriate level of detail"
                ],
                "scoring": {
                    "excellent": "Exceptionally clear and well-organized",
                    "good": "Clear communication with good organization",
                    "satisfactory": "Adequate communication",
                    "needs_improvement": "Unclear or disorganized"
                }
            },
            "Professional Judgment": {
                "description": "Appropriate professional decision-making",
                "criteria": [
                    "Recognizes limitations",
                    "Suggests appropriate consultations",
                    "Maintains professional tone",
                    "Shows clinical maturity"
                ],
                "scoring": {
                    "excellent": "Excellent judgment and professionalism",
                    "good": "Good professional approach",
                    "satisfactory": "Adequate professionalism",
                    "needs_improvement": "Needs development in judgment"
                }
            },
            "Safety Considerations": {
                "description": "Identification of safety-critical findings",
                "criteria": [
                    "Identifies emergent findings",
                    "Recognizes incidental findings requiring follow-up",
                    "Considers patient safety in recommendations",
                    "Appropriate urgency communication"
                ],
                "scoring": {
                    "excellent": "All safety issues identified and communicated",
                    "good": "Most safety considerations addressed",
                    "satisfactory": "Basic safety awareness",
                    "needs_improvement": "Missed important safety considerations"
                }
            }
        }
        
        return criteria_map.get(category, {
            "description": f"Criteria for {category}",
            "criteria": ["General assessment criteria"],
            "scoring": {
                "excellent": "Excellent performance",
                "good": "Good performance",
                "satisfactory": "Satisfactory performance",
                "needs_improvement": "Needs improvement"
            }
        })
    
    def score_to_grade(self, score: float) -> str:
        """Convert numeric score to grade level"""
        if score >= 0.9:
            return "excellent"
        elif score >= 0.75:
            return "good"
        elif score >= 0.6:
            return "satisfactory"
        else:
            return "needs_improvement"
    
    def get_score_thresholds(self) -> Dict[str, float]:
        """Get score thresholds for different grade levels"""
        return {
            "excellent": 0.9,
            "good": 0.75,
            "satisfactory": 0.6,
            "needs_improvement": 0.0
        }