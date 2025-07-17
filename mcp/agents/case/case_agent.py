"""
Case Agent for handling case loading and management
"""

from typing import Dict, Any, List, Optional

from ...core.interfaces import Agent, AgentRequest, AgentResponse
from ...core.models import CaseInfo
from ...session.models import SessionData
from .case_loader import CaseLoader


class CaseAgent(Agent):
    """Agent responsible for loading and managing case data"""
    
    def __init__(self, demo_cases_path: str = "demo_cases"):
        self.case_loader = CaseLoader(demo_cases_path)
        self.capabilities = {
            "load_case_info": "Load metadata and information for a case",
            "get_case_report": "Get the case report text",
            "get_dicom_info": "Get DICOM file information",
            "get_viewer_config": "Get viewer configuration for case",
            "validate_case": "Validate case has all necessary components",
            "list_cases": "List all available cases"
        }
    
    async def execute(self, request: AgentRequest, session_data: SessionData) -> AgentResponse:
        """Execute the agent's functionality"""
        try:
            action = request.action
            data = request.data
            
            if action == "load_case_info":
                return await self._load_case_info(data.get("case_id", session_data.case_id), session_data)
            elif action == "get_case_report":
                return await self._get_case_report(data.get("case_id", session_data.case_id))
            elif action == "get_dicom_info":
                return await self._get_dicom_info(data.get("case_id", session_data.case_id))
            elif action == "get_viewer_config":
                return await self._get_viewer_config(data.get("case_id", session_data.case_id))
            elif action == "validate_case":
                return await self._validate_case(data.get("case_id", session_data.case_id))
            elif action == "list_cases":
                return await self._list_cases()
            else:
                return AgentResponse(
                    success=False,
                    error=f"Unknown action: {action}"
                )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"CaseAgent error: {str(e)}"
            )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the agent's capabilities"""
        return self.capabilities
    
    async def _load_case_info(self, case_id: str, session_data: SessionData) -> AgentResponse:
        """Load case information and metadata"""
        try:
            case_info = self.case_loader.load_case_info(case_id)
            
            if not case_info:
                return AgentResponse(
                    success=False,
                    error=f"Failed to load case info for {case_id}"
                )
            
            # Store case info in session metadata
            session_data.metadata["case_info"] = {
                "case_id": case_info.case_id,
                "title": case_info.title,
                "specialty": case_info.specialty,
                "difficulty": case_info.difficulty,
                "description": case_info.description,
                "dicom_study_uid": case_info.dicom_study_uid,
                "metadata": case_info.metadata
            }
            
            return AgentResponse(
                success=True,
                data={
                    "case_info": {
                        "case_id": case_info.case_id,
                        "title": case_info.title,
                        "specialty": case_info.specialty,
                        "difficulty": case_info.difficulty,
                        "description": case_info.description,
                        "dicom_study_uid": case_info.dicom_study_uid,
                        "clinical_history": case_info.metadata.get("clinical_history", ""),
                        "patient_demographics": case_info.metadata.get("patient_demographics", {}),
                        "imaging_modality": case_info.metadata.get("imaging_modality", ""),
                        "learning_objectives": case_info.metadata.get("learning_objectives", [])
                    }
                },
                metadata={"action": "load_case_info", "case_id": case_id}
            )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Failed to load case info for {case_id}: {str(e)}"
            )
    
    async def _get_case_report(self, case_id: str) -> AgentResponse:
        """Get the case report text"""
        try:
            report = self.case_loader.get_case_report(case_id)
            
            return AgentResponse(
                success=True,
                data={
                    "case_id": case_id,
                    "report": report,
                    "has_report": report is not None
                },
                metadata={"action": "get_case_report", "case_id": case_id}
            )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Failed to get case report for {case_id}: {str(e)}"
            )
    
    async def _get_dicom_info(self, case_id: str) -> AgentResponse:
        """Get DICOM file information"""
        try:
            dicom_files = self.case_loader.get_dicom_files(case_id)
            
            return AgentResponse(
                success=True,
                data={
                    "case_id": case_id,
                    "dicom_files": dicom_files,
                    "total_files": len(dicom_files),
                    "has_dicom": len(dicom_files) > 0
                },
                metadata={"action": "get_dicom_info", "case_id": case_id}
            )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Failed to get DICOM info for {case_id}: {str(e)}"
            )
    
    async def _get_viewer_config(self, case_id: str) -> AgentResponse:
        """Get viewer configuration for the case"""
        try:
            viewer_config = self.case_loader.get_viewer_config(case_id)
            
            return AgentResponse(
                success=True,
                data={
                    "viewer_config": viewer_config
                },
                metadata={"action": "get_viewer_config", "case_id": case_id}
            )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Failed to get viewer config for {case_id}: {str(e)}"
            )
    
    async def _validate_case(self, case_id: str) -> AgentResponse:
        """Validate that a case has all necessary components"""
        try:
            validation_result = self.case_loader.validate_case(case_id)
            
            return AgentResponse(
                success=True,
                data={
                    "validation": validation_result
                },
                metadata={"action": "validate_case", "case_id": case_id}
            )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Failed to validate case {case_id}: {str(e)}"
            )
    
    async def _list_cases(self) -> AgentResponse:
        """List all available cases"""
        try:
            cases = self.case_loader.list_available_cases()
            
            # Get basic info for each case
            case_summaries = []
            for case_id in cases:
                case_info = self.case_loader.load_case_info(case_id)
                if case_info:
                    case_summaries.append({
                        "case_id": case_info.case_id,
                        "title": case_info.title,
                        "specialty": case_info.specialty,
                        "difficulty": case_info.difficulty,
                        "description": case_info.description
                    })
                else:
                    case_summaries.append({
                        "case_id": case_id,
                        "title": f"Case {case_id}",
                        "specialty": "Unknown",
                        "difficulty": "Unknown",
                        "description": "Case information not available"
                    })
            
            return AgentResponse(
                success=True,
                data={
                    "cases": case_summaries,
                    "total_cases": len(cases)
                },
                metadata={"action": "list_cases"}
            )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Failed to list cases: {str(e)}"
            )
    
    def validate_request(self, request: AgentRequest) -> bool:
        """Validate that the request is properly formatted"""
        if not request.action:
            return False
        
        if request.action not in self.capabilities:
            return False
        
        # Most actions don't require specific data validation
        # case_id can be taken from session if not provided in data
        return True