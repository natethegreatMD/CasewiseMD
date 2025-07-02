"""
Configuration agent routes
"""

import os
import json
from pathlib import Path
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any, List

router = APIRouter()

# Base path for demo cases
DEMO_CASES_PATH = Path("/app/demo_cases")

def scan_available_cases() -> List[str]:
    """Scan demo_cases directory for valid case folders"""
    if not DEMO_CASES_PATH.exists():
        return []
    
    cases = []
    for item in DEMO_CASES_PATH.iterdir():
        if item.is_dir() and (item / "metadata.json").exists():
            cases.append(item.name)
    
    return sorted(cases)

def read_case_metadata(case_id: str) -> Dict[str, Any]:
    """Read metadata.json for a specific case"""
    metadata_path = DEMO_CASES_PATH / case_id / "metadata.json"
    
    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail=f"Metadata not found for case {case_id}")
    
    try:
        with open(metadata_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in metadata for case {case_id}")

def count_dicom_files(case_id: str, series_uid: str) -> int:
    """Count DICOM files in a series directory"""
    series_path = DEMO_CASES_PATH / case_id / "slices" / series_uid
    
    if not series_path.exists():
        return 0
    
    dicom_count = 0
    for file in series_path.iterdir():
        if file.is_file() and file.suffix.lower() in ['.dcm', '.dicom']:
            dicom_count += 1
    
    return dicom_count

def read_case_report(case_id: str) -> Optional[str]:
    """Read report.txt if it exists"""
    report_path = DEMO_CASES_PATH / case_id / "report.txt"
    
    if report_path.exists():
        try:
            with open(report_path, 'r') as f:
                return f.read().strip()
        except Exception:
            return None
    
    return None

@router.get("/config")
async def get_case_config(case_id: str = Query(..., description="Case ID to retrieve configuration for")):
    """
    Get case configuration by case ID
    Reads from real case data in demo_cases directory
    """
    try:
        # Read case metadata
        metadata = read_case_metadata(case_id)
        
        # Read case report if available
        report = read_case_report(case_id)
        
        # Build series information
        series_info = []
        for orientation, series_uid in metadata.get("series", {}).items():
            num_images = count_dicom_files(case_id, series_uid)
            
            series_info.append({
                "series_id": orientation,
                "series_uid": series_uid,
                "orientation": orientation.upper(),
                "base_url": f"/demo_cases/{case_id}/slices/{series_uid}/",
                "num_images": num_images
            })
        
        return {
            "case_id": case_id,
            "agent": "config",
            "status": "active",
            "configuration": {
                "case_type": "radiology_case",
                "difficulty_level": "intermediate",
                "estimated_time_minutes": 20,
                "total_questions": 5,
                "scoring_method": "weighted",
                "passing_threshold": 70.0
            },
            "case_metadata": {
                "title": f"Case {case_id}: {metadata.get('modality', 'Unknown')} Imaging",
                "description": f"Radiology case involving {metadata.get('modality', 'unknown')} imaging",
                "patient_id": metadata.get("patient_id", "unknown"),
                "modality": metadata.get("modality", "unknown"),
                "orientations": metadata.get("orientation", []),
                "series_information": series_info,
                "clinical_report": report
            },
            "grading_rubric": {
                "rubric_id": metadata.get("rubric_id", f"rubric-{case_id}"),
                "version": metadata.get("prompt_version", "v1"),
                "categories": [
                    {
                        "name": "Image Interpretation",
                        "weight": 0.40,
                        "max_points": 40
                    },
                    {
                        "name": "Differential Diagnosis",
                        "weight": 0.30,
                        "max_points": 30
                    },
                    {
                        "name": "Clinical Correlation",
                        "weight": 0.20,
                        "max_points": 20
                    },
                    {
                        "name": "Recommendation",
                        "weight": 0.10,
                        "max_points": 10
                    }
                ]
            },
            "ui_configuration": {
                "show_hints": True,
                "allow_retries": False,
                "time_limit_enabled": False,
                "progress_tracking": True,
                "immediate_feedback": False
            },
            "resources": {
                "dicom_series": series_info,
                "clinical_report": report if report else None
            },
            "metadata": {
                "created_by": "config-agent-filesystem-v1.0",
                "case_source": "filesystem",
                "version": "1.0.0"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading case configuration: {str(e)}")

@router.get("/config/available-cases")
async def get_available_cases():
    """
    Get list of available cases
    Scans demo_cases directory for valid cases
    """
    try:
        case_ids = scan_available_cases()
        
        # Build detailed case list
        available_cases = []
        for case_id in case_ids:
            try:
                metadata = read_case_metadata(case_id)
                available_cases.append({
                    "case_id": case_id,
                    "title": f"Case {case_id}: {metadata.get('modality', 'Unknown')} Imaging",
                    "modality": metadata.get("modality", "unknown"),
                    "patient_id": metadata.get("patient_id", "unknown"),
                    "orientations": metadata.get("orientation", []),
                    "series_count": len(metadata.get("series", {}))
                })
            except Exception:
                # Skip cases with invalid metadata
                continue
        
        return {
            "agent": "config",
            "status": "active",
            "available_cases": available_cases,
            "total_cases": len(available_cases),
            "modalities": list(set(case["modality"] for case in available_cases)),
            "case_source": "filesystem"
        }
        
    except Exception as e:
"""
Configuration agent routes
"""

import os
import json
from pathlib import Path
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any, List

router = APIRouter()

# Base path for demo cases
DEMO_CASES_PATH = Path("/app/demo_cases")

def scan_available_cases() -> List[str]:
    """Scan demo_cases directory for valid case folders"""
    if not DEMO_CASES_PATH.exists():
        return []
    
    cases = []
    for item in DEMO_CASES_PATH.iterdir():
        if item.is_dir() and (item / "metadata.json").exists():
            cases.append(item.name)
    
    return sorted(cases)

def read_case_metadata(case_id: str) -> Dict[str, Any]:
    """Read metadata.json for a specific case"""
    metadata_path = DEMO_CASES_PATH / case_id / "metadata.json"
    
    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail=f"Metadata not found for case {case_id}")
    
    try:
        with open(metadata_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in metadata for case {case_id}")

def count_dicom_files(case_id: str, series_uid: str) -> int:
    """Count DICOM files in a series directory"""
    series_path = DEMO_CASES_PATH / case_id / "slices" / series_uid
    
    if not series_path.exists():
        return 0
    
    dicom_count = 0
    for file in series_path.iterdir():
        if file.is_file() and file.suffix.lower() in ['.dcm', '.dicom']:
            dicom_count += 1
    
    return dicom_count

def read_case_report(case_id: str) -> Optional[str]:
    """Read report.txt if it exists"""
    report_path = DEMO_CASES_PATH / case_id / "report.txt"
    
    if report_path.exists():
        try:
            with open(report_path, 'r') as f:
                return f.read().strip()
        except Exception:
            return None
    
    return None

@router.get("/config")
async def get_case_config(case_id: str = Query(..., description="Case ID to retrieve configuration for")):
    """
    Get case configuration by case ID
    Reads from real case data in demo_cases directory
    """
    try:
        # Read case metadata
        metadata = read_case_metadata(case_id)
        
        # Read case report if available
        report = read_case_report(case_id)
        
        # Build series information
        series_info = []
        for orientation, series_uid in metadata.get("series", {}).items():
            num_images = count_dicom_files(case_id, series_uid)
            
            series_info.append({
                "series_id": orientation,
                "series_uid": series_uid,
                "orientation": orientation.upper(),
                "base_url": f"/demo_cases/{case_id}/slices/{series_uid}/",
                "num_images": num_images
            })
        
        return {
            "case_id": case_id,
            "agent": "config",
            "status": "active",
            "configuration": {
                "case_type": "radiology_case",
                "difficulty_level": "intermediate",
                "estimated_time_minutes": 20,
                "total_questions": 5,
                "scoring_method": "weighted",
                "passing_threshold": 70.0
            },
            "case_metadata": {
                "title": f"Case {case_id}: {metadata.get('modality', 'Unknown')} Imaging",
                "description": f"Radiology case involving {metadata.get('modality', 'unknown')} imaging",
                "patient_id": metadata.get("patient_id", "unknown"),
                "modality": metadata.get("modality", "unknown"),
                "orientations": metadata.get("orientation", []),
                "series_information": series_info,
                "clinical_report": report
            },
            "grading_rubric": {
                "rubric_id": metadata.get("rubric_id", f"rubric-{case_id}"),
                "version": metadata.get("prompt_version", "v1"),
                "categories": [
                    {
                        "name": "Image Interpretation",
                        "weight": 0.40,
                        "max_points": 40
                    },
                    {
                        "name": "Differential Diagnosis",
                        "weight": 0.30,
                        "max_points": 30
                    },
                    {
                        "name": "Clinical Correlation",
                        "weight": 0.20,
                        "max_points": 20
                    },
                    {
                        "name": "Recommendation",
                        "weight": 0.10,
                        "max_points": 10
                    }
                ]
            },
            "ui_configuration": {
                "show_hints": True,
                "allow_retries": False,
                "time_limit_enabled": False,
                "progress_tracking": True,
                "immediate_feedback": False
            },
            "resources": {
                "dicom_series": series_info,
                "clinical_report": report if report else None
            },
            "metadata": {
                "created_by": "config-agent-filesystem-v1.0",
                "case_source": "filesystem",
                "version": "1.0.0"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading case configuration: {str(e)}")

@router.get("/config/available-cases")
async def get_available_cases():
    """
    Get list of available cases
    Scans demo_cases directory for valid cases
    """
    try:
        case_ids = scan_available_cases()
        
        # Build detailed case list
        available_cases = []
        for case_id in case_ids:
            try:
                metadata = read_case_metadata(case_id)
                available_cases.append({
                    "case_id": case_id,
                    "title": f"Case {case_id}: {metadata.get('modality', 'Unknown')} Imaging",
                    "modality": metadata.get("modality", "unknown"),
                    "patient_id": metadata.get("patient_id", "unknown"),
                    "orientations": metadata.get("orientation", []),
                    "series_count": len(metadata.get("series", {}))
                })
            except Exception:
                # Skip cases with invalid metadata
                continue
        
        return {
            "agent": "config",
            "status": "active",
            "available_cases": available_cases,
            "total_cases": len(available_cases),
            "modalities": list(set(case["modality"] for case in available_cases)),
            "case_source": "filesystem"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scanning available cases: {str(e)}") 