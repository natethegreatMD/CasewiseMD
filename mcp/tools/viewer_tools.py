"""
MCP Tools for OHIF Medical Image Viewer Configuration
Handles case-specific viewer URLs and DICOM data orchestration
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add case management src to path
case_management_path = Path(__file__).parent.parent.parent / "case-management" / "src"
sys.path.insert(0, str(case_management_path))

try:
    from models import Case, Series
    CASE_MANAGEMENT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import case management models: {e}")
    CASE_MANAGEMENT_AVAILABLE = False

logger = logging.getLogger(__name__)

class ViewerTools:
    """MCP tools for medical image viewer configuration"""
    
    def __init__(self):
        # Legacy case-specific Study Instance UIDs (for backward compatibility)
        self.legacy_case_study_mapping = {
            "case001": "1.3.6.1.4.1.14519.5.2.1.7695.4007.250730721548000739633557298354"
        }
        
        # OHIF viewer base URL
        self.ohif_base_url = "https://viewer.casewisemd.org/viewer"
        
        # DICOMweb server endpoint (through nginx proxy)
        self.dicomweb_endpoint = "https://api.casewisemd.org/orthanc/dicom-web"
        
        # Database connection
        self.database_url = os.getenv("CASE_DB_URL", "sqlite:///case-management/database/cases.db")
        self.engine = None
        self.Session = None
        
        # Initialize database connection if case management is available
        if CASE_MANAGEMENT_AVAILABLE:
            self._init_database()
    
    def _init_database(self):
        """Initialize database connection"""
        try:
            self.engine = create_engine(self.database_url)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Database connection initialized for viewer tools")
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            self.engine = None
            self.Session = None
    
    def _get_case_from_database(self, case_id: str) -> Optional[Case]:
        """Get case from database by case ID"""
        if not self.Session or not CASE_MANAGEMENT_AVAILABLE:
            return None
        
        try:
            session = self.Session()
            case = session.query(Case).filter(Case.id == case_id).first()
            session.close()
            return case
        except Exception as e:
            logger.error(f"Error querying database for case {case_id}: {e}")
            return None
    
    async def get_case_viewer_url(self, case_id: str) -> Dict[str, Any]:
        """
        MCP Tool: Get OHIF viewer URL for specific case
        
        Args:
            case_id: Case identifier (e.g., "case001" or "TCIA-OV-TCGA09-0364")
            
        Returns:
            Dictionary with viewer URL and metadata
        """
        try:
            study_instance_uid = None
            
            # First try to get from database
            case = self._get_case_from_database(case_id)
            
            if case and case.study_instance_uid:
                study_instance_uid = case.study_instance_uid
                logger.info(f"Found case {case_id} in database with Study UID: {study_instance_uid}")
            else:
                # Fallback to legacy mapping
                study_instance_uid = self.legacy_case_study_mapping.get(case_id)
                if study_instance_uid:
                    logger.info(f"Using legacy mapping for case {case_id}")
            
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
            # First try to get from database
            case = self._get_case_from_database(case_id)
            
            if case:
                # Get series information
                series_info = []
                if self.Session and CASE_MANAGEMENT_AVAILABLE:
                    session = self.Session()
                    series_list = session.query(Series).filter(Series.case_id == case_id).all()
                    for series in series_list:
                        series_info.append({
                            "series_uid": series.series_instance_uid,
                            "modality": series.modality,
                            "description": series.series_description,
                            "number": series.series_number,
                            "image_count": series.image_count
                        })
                    session.close()
                
                metadata = {
                    "title": case.title,
                    "modality": case.modality,
                    "body_region": case.anatomy,
                    "series_count": len(series_info),
                    "series_descriptions": [s["description"] for s in series_info],
                    "study_instance_uid": case.study_instance_uid,
                    "patient_id": case.patient_id,
                    "difficulty": case.difficulty,
                    "specialty": case.specialty,
                    "source": case.source,
                    "learning_objectives": case.learning_objectives or [],
                    "case_complexity": case.case_complexity,
                    "series_info": series_info
                }
                
                return {
                    "success": True,
                    "case_id": case_id,
                    "metadata": metadata
                }
            
            # Fallback to legacy hardcoded metadata
            legacy_metadata = {
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
            
            metadata = legacy_metadata.get(case_id)
            
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
            
            # First try to get from database
            if self.Session and CASE_MANAGEMENT_AVAILABLE:
                session = self.Session()
                cases = session.query(Case).filter(Case.study_instance_uid.isnot(None)).all()
                
                for case in cases:
                    available_cases.append({
                        "case_id": case.id,
                        "study_instance_uid": case.study_instance_uid,
                        "title": case.title,
                        "modality": case.modality,
                        "body_region": case.anatomy,
                        "difficulty": case.difficulty,
                        "specialty": case.specialty,
                        "source": case.source,
                        "patient_id": case.patient_id
                    })
                
                session.close()
            
            # Add legacy cases if database is empty
            if not available_cases:
                for case_id, study_uid in self.legacy_case_study_mapping.items():
                    case_metadata = await self.get_case_metadata(case_id)
                    
                    if case_metadata["success"]:
                        available_cases.append({
                            "case_id": case_id,
                            "study_instance_uid": study_uid,
                            "title": case_metadata["metadata"]["title"],
                            "modality": case_metadata["metadata"]["modality"],
                            "body_region": case_metadata["metadata"]["body_region"],
                            "difficulty": "intermediate",
                            "specialty": "oncology",
                            "source": "legacy"
                        })
            
            return {
                "success": True,
                "cases": available_cases,
                "count": len(available_cases),
                "database_connected": self.Session is not None
            }
            
        except Exception as e:
            logger.error(f"Error listing available cases: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "cases": []
            } 