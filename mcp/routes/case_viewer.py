"""
Case Viewer API Routes
Handles case-specific viewer URL generation and management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from ..tools.viewer_tools import ViewerTools
from ..tools.case_tools import CaseTools

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize MCP tools
viewer_tools = ViewerTools()
case_tools = CaseTools()

class ViewerURLRequest(BaseModel):
    case_id: str

class ViewerURLResponse(BaseModel):
    success: bool
    viewer_url: str
    case_id: str
    study_instance_uid: Optional[str] = None
    error: Optional[str] = None

@router.post("/viewer-url", response_model=ViewerURLResponse)
async def get_case_viewer_url(request: ViewerURLRequest) -> ViewerURLResponse:
    """
    Get OHIF viewer URL for a specific case
    
    Args:
        request: Request containing case_id
        
    Returns:
        Response with viewer URL and case information
    """
    try:
        # Call MCP tool to get viewer URL
        result = await viewer_tools.get_case_viewer_url(request.case_id)
        
        if result["success"]:
            return ViewerURLResponse(
                success=True,
                viewer_url=result["viewer_url"],
                case_id=result["case_id"],
                study_instance_uid=result.get("study_instance_uid")
            )
        else:
            return ViewerURLResponse(
                success=False,
                viewer_url=result["viewer_url"],  # Fallback URL
                case_id=request.case_id,
                error=result["error"]
            )
            
    except Exception as e:
        logger.error(f"Error getting viewer URL for case {request.case_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting viewer URL: {str(e)}"
        )

@router.get("/cases")
async def list_available_cases():
    """
    List all available cases
    
    Returns:
        List of available cases with metadata
    """
    try:
        result = await viewer_tools.list_available_cases()
        return result
    
    except Exception as e:
        logger.error(f"Error listing available cases: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing cases: {str(e)}"
        )

@router.get("/cases/{case_id}")
async def get_case_info(case_id: str):
    """
    Get comprehensive case information
    
    Args:
        case_id: Case identifier
        
    Returns:
        Case information and metadata
    """
    try:
        result = await case_tools.get_case_info(case_id)
        return result
    
    except Exception as e:
        logger.error(f"Error getting case info for {case_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting case info: {str(e)}"
        )

@router.get("/cases/{case_id}/metadata")
async def get_case_metadata(case_id: str):
    """
    Get case metadata for viewer configuration
    
    Args:
        case_id: Case identifier
        
    Returns:
        Case metadata
    """
    try:
        result = await viewer_tools.get_case_metadata(case_id)
        return result
    
    except Exception as e:
        logger.error(f"Error getting metadata for case {case_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting case metadata: {str(e)}"
        ) 