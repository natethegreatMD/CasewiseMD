"""
MCP Tools for Case Management
Handles case data, metadata, and organization
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class CaseTools:
    """MCP tools for case management and organization"""
    
    def __init__(self):
        # For now, hardcoded case data (will be database-driven later)
        self.cases_database = {
            "case001": {
                "id": "case001",
                "title": "Ovarian Cancer Case - TCGA-09-0364",
                "description": "Complex ovarian cancer case with multiple series",
                "modality": "CT",
                "body_region": "Pelvis",
                "difficulty": "Advanced",
                "tags": ["oncology", "gynecology", "contrast", "axial"],
                "study_instance_uid": "1.3.6.1.4.1.14519.5.2.1.7695.4007.250730721548000739633557298354",
                "series_count": 3,
                "created_date": "2024-01-01",
                "last_modified": "2024-01-01",
                "status": "active"
            }
        }
    
    async def get_case_info(self, case_id: str) -> Dict[str, Any]:
        """
        MCP Tool: Get comprehensive case information
        
        Args:
            case_id: Case identifier
            
        Returns:
            Dictionary with complete case information
        """
        try:
            case_info = self.cases_database.get(case_id)
            
            if not case_info:
                return {
                    "success": False,
                    "error": f"Case {case_id} not found"
                }
            
            return {
                "success": True,
                "case": case_info
            }
            
        except Exception as e:
            logger.error(f"Error getting case info for {case_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_cases(self, query: Optional[str] = None, 
                          modality: Optional[str] = None,
                          body_region: Optional[str] = None,
                          difficulty: Optional[str] = None,
                          tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        MCP Tool: Search and filter cases
        
        Args:
            query: Text search query
            modality: Filter by modality (CT, MR, etc.)
            body_region: Filter by body region
            difficulty: Filter by difficulty level
            tags: Filter by tags
            
        Returns:
            Dictionary with matching cases
        """
        try:
            matching_cases = []
            
            for case_id, case_data in self.cases_database.items():
                # Apply filters
                if modality and case_data["modality"].lower() != modality.lower():
                    continue
                
                if body_region and case_data["body_region"].lower() != body_region.lower():
                    continue
                
                if difficulty and case_data["difficulty"].lower() != difficulty.lower():
                    continue
                
                if tags:
                    case_tags = [tag.lower() for tag in case_data["tags"]]
                    if not any(tag.lower() in case_tags for tag in tags):
                        continue
                
                if query:
                    # Simple text search in title and description
                    search_text = f"{case_data['title']} {case_data['description']}".lower()
                    if query.lower() not in search_text:
                        continue
                
                matching_cases.append(case_data)
            
            return {
                "success": True,
                "cases": matching_cases,
                "count": len(matching_cases),
                "filters_applied": {
                    "query": query,
                    "modality": modality,
                    "body_region": body_region,
                    "difficulty": difficulty,
                    "tags": tags
                }
            }
            
        except Exception as e:
            logger.error(f"Error searching cases: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "cases": []
            }
    
    async def get_case_statistics(self) -> Dict[str, Any]:
        """
        MCP Tool: Get case statistics and summary
        
        Returns:
            Dictionary with case statistics
        """
        try:
            total_cases = len(self.cases_database)
            
            if total_cases == 0:
                return {
                    "success": True,
                    "statistics": {
                        "total_cases": 0,
                        "by_modality": {},
                        "by_body_region": {},
                        "by_difficulty": {},
                        "by_status": {}
                    }
                }
            
            # Analyze case distribution
            by_modality = {}
            by_body_region = {}
            by_difficulty = {}
            by_status = {}
            
            for case_data in self.cases_database.values():
                # Count by modality
                modality = case_data["modality"]
                by_modality[modality] = by_modality.get(modality, 0) + 1
                
                # Count by body region
                body_region = case_data["body_region"]
                by_body_region[body_region] = by_body_region.get(body_region, 0) + 1
                
                # Count by difficulty
                difficulty = case_data["difficulty"]
                by_difficulty[difficulty] = by_difficulty.get(difficulty, 0) + 1
                
                # Count by status
                status = case_data["status"]
                by_status[status] = by_status.get(status, 0) + 1
            
            return {
                "success": True,
                "statistics": {
                    "total_cases": total_cases,
                    "by_modality": by_modality,
                    "by_body_region": by_body_region,
                    "by_difficulty": by_difficulty,
                    "by_status": by_status
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting case statistics: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            } 