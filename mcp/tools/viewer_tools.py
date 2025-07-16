"""
MCP Tools for OHIF Medical Image Viewer Configuration
Handles case-specific viewer URLs and DICOM data orchestration
"""

import logging
from typing import Dict, Any, Optional
from ..config import settings

logger = logging.getLogger(__name__)

class ViewerTools:
    """MCP tools for medical image viewer configuration"""
    
    def __init__(self):
        # Case-specific Study Instance UIDs (hardcoded for now, will be database-driven later)
        self.case_study_mapping = {
            "case001": "1.3.6.1.4.1.14519.5.2.1.7695.4007.250730721548000739633557298354"
        }
        
        # OHIF viewer base URL from settings
        self.ohif_base_url = settings.OHIF_BASE_URL
        
        # DICOMweb server endpoint from settings
        self.dicomweb_endpoint = settings.DICOMWEB_ENDPOINT
    
    async def get_case_viewer_url(self, case_id: str) -> Dict[str, Any]:
        """
        MCP Tool: Get OHIF viewer URL for specific case
        
        Args:
            case_id: Case identifier (e.g., "case001")
            
        Returns:
            Dictionary with viewer URL and metadata
        """
        try:
            # Get Study Instance UID for the case
            study_instance_uid = self.case_study_mapping.get(case_id)
            
            if not study_instance_uid:
                return {
                    "success": False,
                    "error": f"Case {case_id} not found",
                    "viewer_url": self.ohif_base_url  # Fallback to default viewer
                }
            
            # Generate case-specific OHIF URL with DICOMweb server configuration
            # Use the correct OHIF parameter names: datasource instead of url
            viewer_url = f"{self.ohif_base_url}?StudyInstanceUIDs={study_instance_uid}&datasource={self.dicomweb_endpoint}"
            
            return {
                "success": True,
                "case_id": case_id,
                "study_instance_uid": study_instance_uid,
                "viewer_url": viewer_url,
                "message": f"OHIF viewer configured for {case_id}"
            }
            
        except Exception as e:
            logger.error(f"Error generating viewer URL for {case_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "viewer_url": self.ohif_base_url
            }
    
    async def get_case_metadata(self, case_id: str) -> Dict[str, Any]:
        """
        MCP Tool: Get case metadata for viewer configuration
        
        Args:
            case_id: Case identifier
            
        Returns:
            Dictionary with case metadata
        """
        try:
            # For now, hardcoded metadata (will be database-driven later)
            case_metadata = {
                "case001": {
                    "title": "Ovarian Cancer Case - TCGA-09-0364",
                    "modality": "CT",
                    "body_region": "Pelvis",
                    "series_count": 3,
                    "series_descriptions": ["AXIAL", "SCOUT", "DELAYED"],
                    "study_date": "19890331",
                    "patient_age": "Adult",
                    "contrast": "Yes - HYPAQUE & OMNI 350"
                }
            }
            
            metadata = case_metadata.get(case_id)
            
            if not metadata:
                return {
                    "success": False,
                    "error": f"Metadata for case {case_id} not found"
                }
            
            return {
                "success": True,
                "case_id": case_id,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error getting metadata for {case_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_available_cases(self) -> Dict[str, Any]:
        """
        MCP Tool: List all available cases
        
        Returns:
            Dictionary with available cases
        """
        try:
            available_cases = []
            
            for case_id, study_uid in self.case_study_mapping.items():
                case_metadata = await self.get_case_metadata(case_id)
                
                if case_metadata["success"]:
                    available_cases.append({
                        "case_id": case_id,
                        "study_instance_uid": study_uid,
                        "title": case_metadata["metadata"]["title"],
                        "modality": case_metadata["metadata"]["modality"],
                        "body_region": case_metadata["metadata"]["body_region"]
                    })
            
            return {
                "success": True,
                "cases": available_cases,
                "count": len(available_cases)
            }
            
        except Exception as e:
            logger.error(f"Error listing available cases: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "cases": []
            } 