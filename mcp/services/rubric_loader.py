"""
Rubric Loader Service
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

class RubricLoaderService:
    """Service for loading and managing grading rubrics"""
    
    def __init__(self, demo_cases_path: Optional[Path] = None):
        self.demo_cases_path = demo_cases_path or (
            Path("/app/demo_cases") if Path("/app/demo_cases").exists() else Path("./demo_cases")
        )
        self._rubric_cache = {}
    
    def load_rubric(self, case_id: str) -> Dict[str, Any]:
        """
        Load rubric for a specific case
        
        Args:
            case_id: Case identifier
            
        Returns:
            Dict containing rubric data
        """
        # Check cache first
        if case_id in self._rubric_cache:
            return self._rubric_cache[case_id]
        
        # Try to load from file
        rubric_path = self.demo_cases_path / case_id / "rubric.json"
        
        if rubric_path.exists():
            try:
                with open(rubric_path, 'r') as f:
                    rubric = json.load(f)
                    
                # Cache the rubric
                self._rubric_cache[case_id] = rubric
                logger.info(f"Loaded rubric for case {case_id}")
                return rubric
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in rubric for case {case_id}: {str(e)}")
                return self._get_default_rubric(case_id)
            except Exception as e:
                logger.error(f"Error loading rubric for case {case_id}: {str(e)}")
                return self._get_default_rubric(case_id)
        else:
            logger.warning(f"Rubric not found for case {case_id}, using default")
            return self._get_default_rubric(case_id)
    
    def _get_default_rubric(self, case_id: str) -> Dict[str, Any]:
        """Get default rubric when case-specific rubric is not available"""
        
        default_rubric = {
            "rubric_id": f"default-{case_id}",
            "version": "1.0",
            "case_type": "radiology_case",
            "total_points": 100,
            "passing_threshold": 70,
            "categories": [
                {
                    "name": "Image Interpretation",
                    "weight": 0.40,
                    "description": "Ability to accurately interpret imaging findings",
                    "criteria": [
                        {
                            "name": "Anatomical Identification",
                            "description": "Correct identification of anatomical structures",
                            "max_score": 25,
                            "weight": 0.25
                        },
                        {
                            "name": "Pathology Detection",
                            "description": "Accurate detection of pathological findings",
                            "max_score": 25,
                            "weight": 0.25
                        },
                        {
                            "name": "Image Quality Assessment",
                            "description": "Assessment of image quality and technical factors",
                            "max_score": 25,
                            "weight": 0.25
                        },
                        {
                            "name": "Systematic Approach",
                            "description": "Use of systematic approach to image interpretation",
                            "max_score": 25,
                            "weight": 0.25
                        }
                    ]
                },
                {
                    "name": "Differential Diagnosis",
                    "weight": 0.30,
                    "description": "Development of appropriate differential diagnosis",
                    "criteria": [
                        {
                            "name": "Diagnostic Accuracy",
                            "description": "Accuracy of primary diagnosis",
                            "max_score": 40,
                            "weight": 0.4
                        },
                        {
                            "name": "Differential Considerations",
                            "description": "Appropriate alternative diagnoses considered",
                            "max_score": 35,
                            "weight": 0.35
                        },
                        {
                            "name": "Clinical Reasoning",
                            "description": "Quality of clinical reasoning and logic",
                            "max_score": 25,
                            "weight": 0.25
                        }
                    ]
                },
                {
                    "name": "Clinical Correlation",
                    "weight": 0.20,
                    "description": "Integration of imaging findings with clinical presentation",
                    "criteria": [
                        {
                            "name": "History Integration",
                            "description": "Integration of clinical history with imaging findings",
                            "max_score": 50,
                            "weight": 0.5
                        },
                        {
                            "name": "Symptom Correlation",
                            "description": "Correlation of symptoms with imaging findings",
                            "max_score": 50,
                            "weight": 0.5
                        }
                    ]
                },
                {
                    "name": "Management Recommendations",
                    "weight": 0.10,
                    "description": "Appropriate recommendations for patient management",
                    "criteria": [
                        {
                            "name": "Follow-up Planning",
                            "description": "Appropriate follow-up recommendations",
                            "max_score": 50,
                            "weight": 0.5
                        },
                        {
                            "name": "Treatment Suggestions",
                            "description": "Relevant treatment and management suggestions",
                            "max_score": 50,
                            "weight": 0.5
                        }
                    ]
                }
            ]
        }
        
        # Cache the default rubric
        self._rubric_cache[case_id] = default_rubric
        return default_rubric
    
    def validate_rubric(self, rubric: Dict[str, Any]) -> bool:
        """
        Validate rubric structure
        
        Args:
            rubric: Rubric dictionary to validate
            
        Returns:
            Boolean indicating if rubric is valid
        """
        required_fields = ["rubric_id", "version", "categories"]
        
        for field in required_fields:
            if field not in rubric:
                logger.error(f"Missing required field in rubric: {field}")
                return False
        
        if not isinstance(rubric["categories"], list):
            logger.error("Categories must be a list")
            return False
        
        for category in rubric["categories"]:
            if not isinstance(category, dict):
                logger.error("Each category must be a dictionary")
                return False
            
            category_required = ["name", "weight", "criteria"]
            for field in category_required:
                if field not in category:
                    logger.error(f"Missing required field in category: {field}")
                    return False
        
        return True
    
    def clear_cache(self):
        """Clear the rubric cache"""
        self._rubric_cache.clear()
        logger.info("Rubric cache cleared")

# Global instance
rubric_loader = RubricLoaderService()

def load_rubric(case_id: str) -> Dict[str, Any]:
    """Module-level function to load rubric for a specific case"""
    return rubric_loader.load_rubric(case_id) 