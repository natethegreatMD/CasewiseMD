"""
Case loader for loading case metadata, reports, and DICOM information
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from ...core.models import CaseInfo


class CaseLoader:
    """Loads case data from demo_cases directory"""
    
    def __init__(self, demo_cases_path: str = "demo_cases"):
        self.demo_cases_path = Path(demo_cases_path)
        self.loaded_cases: Dict[str, CaseInfo] = {}
    
    def load_case_info(self, case_id: str) -> Optional[CaseInfo]:
        """Load case metadata and information"""
        if case_id in self.loaded_cases:
            return self.loaded_cases[case_id]
        
        case_path = self.demo_cases_path / case_id
        if not case_path.exists():
            # Return default case info if case directory doesn't exist
            return self._create_default_case_info(case_id)
        
        metadata_file = case_path / "metadata.json"
        
        if metadata_file.exists():
            case_info = self._load_from_metadata_file(case_id, metadata_file)
        else:
            case_info = self._create_default_case_info(case_id)
        
        # Cache the loaded case
        self.loaded_cases[case_id] = case_info
        return case_info
    
    def _load_from_metadata_file(self, case_id: str, metadata_file: Path) -> CaseInfo:
        """Load case info from metadata.json file"""
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            return CaseInfo(
                case_id=case_id,
                title=metadata.get("title", f"Case {case_id}"),
                specialty=metadata.get("specialty", "Radiology"),
                difficulty=metadata.get("difficulty", "Intermediate"),
                description=metadata.get("description", "Diagnostic case"),
                dicom_study_uid=metadata.get("dicom_study_uid"),
                metadata={
                    "clinical_history": metadata.get("clinical_history", ""),
                    "patient_demographics": metadata.get("patient_demographics", {}),
                    "imaging_modality": metadata.get("imaging_modality", ""),
                    "technique": metadata.get("technique", ""),
                    "findings": metadata.get("findings", ""),
                    "diagnosis": metadata.get("diagnosis", ""),
                    "learning_objectives": metadata.get("learning_objectives", []),
                    "key_images": metadata.get("key_images", []),
                    "references": metadata.get("references", [])
                }
            )
        except Exception as e:
            print(f"Error loading metadata from {metadata_file}: {e}")
            return self._create_default_case_info(case_id)
    
    def _create_default_case_info(self, case_id: str) -> CaseInfo:
        """Create default case info when no metadata is available"""
        return CaseInfo(
            case_id=case_id,
            title=f"Case {case_id}",
            specialty="Radiology",
            difficulty="Intermediate",
            description="Diagnostic radiology case",
            dicom_study_uid=None,
            metadata={
                "clinical_history": "Clinical history not available",
                "patient_demographics": {},
                "imaging_modality": "Unknown",
                "technique": "Standard imaging protocol",
                "findings": "Findings to be determined by student",
                "diagnosis": "To be diagnosed",
                "learning_objectives": [
                    "Systematic image interpretation",
                    "Differential diagnosis development",
                    "Clinical correlation skills"
                ],
                "key_images": [],
                "references": []
            }
        )
    
    def get_case_report(self, case_id: str) -> Optional[str]:
        """Load the case report text if available"""
        case_path = self.demo_cases_path / case_id
        report_file = case_path / "report.txt"
        
        if report_file.exists():
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Error loading report from {report_file}: {e}")
        
        return None
    
    def get_dicom_files(self, case_id: str) -> List[Dict[str, Any]]:
        """Get information about DICOM files for the case"""
        case_path = self.demo_cases_path / case_id
        slices_path = case_path / "slices"
        
        dicom_files = []
        
        if slices_path.exists():
            for file_path in slices_path.glob("*.dcm"):
                dicom_files.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size if file_path.exists() else 0,
                    "series_description": self._extract_series_description(file_path)
                })
        
        return dicom_files
    
    def _extract_series_description(self, file_path: Path) -> str:
        """Extract series description from DICOM file (placeholder)"""
        # In a real implementation, this would use pydicom to read the DICOM header
        # For now, return a placeholder based on filename
        filename = file_path.name
        
        if "axial" in filename.lower():
            return "Axial Series"
        elif "coronal" in filename.lower():
            return "Coronal Series"
        elif "sagittal" in filename.lower():
            return "Sagittal Series"
        else:
            return "Unknown Series"
    
    def get_viewer_config(self, case_id: str) -> Dict[str, Any]:
        """Generate viewer configuration for the case"""
        case_info = self.load_case_info(case_id)
        dicom_files = self.get_dicom_files(case_id)
        
        # This is a simplified viewer config
        # In reality, this would integrate with the viewer_tools.py functionality
        return {
            "case_id": case_id,
            "title": case_info.title if case_info else f"Case {case_id}",
            "study_uid": case_info.dicom_study_uid if case_info else None,
            "dicom_files": dicom_files,
            "viewer_url": f"/viewer?case={case_id}",  # Placeholder
            "total_images": len(dicom_files)
        }
    
    def list_available_cases(self) -> List[str]:
        """Get a list of all available case IDs"""
        if not self.demo_cases_path.exists():
            return []
        
        cases = []
        for item in self.demo_cases_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                cases.append(item.name)
        
        return sorted(cases)
    
    def validate_case(self, case_id: str) -> Dict[str, Any]:
        """Validate that a case has all necessary components"""
        case_path = self.demo_cases_path / case_id
        
        validation_result = {
            "case_id": case_id,
            "exists": case_path.exists(),
            "components": {
                "metadata": (case_path / "metadata.json").exists(),
                "questions": (case_path / "questions.json").exists(),
                "report": (case_path / "report.txt").exists(),
                "dicom_files": len(self.get_dicom_files(case_id)) > 0
            },
            "issues": []
        }
        
        if not validation_result["exists"]:
            validation_result["issues"].append("Case directory does not exist")
        
        if not validation_result["components"]["dicom_files"]:
            validation_result["issues"].append("No DICOM files found")
        
        validation_result["is_valid"] = (
            validation_result["exists"] and 
            validation_result["components"]["dicom_files"]
        )
        
        return validation_result