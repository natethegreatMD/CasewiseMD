"""
DICOM Processing Module for Case Management System.
Handles DICOM file validation, metadata extraction, and Orthanc upload.
"""

import os
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import requests
from datetime import datetime
import hashlib
import json

try:
    import pydicom
    from pydicom.errors import InvalidDicomError
    HAS_PYDICOM = True
except ImportError:
    HAS_PYDICOM = False
    logging.warning("pydicom not installed. DICOM processing will be limited.")

# Handle both relative and absolute imports
try:
    from .models import Case, Series, ProcessingLog
except ImportError:
    from models import Case, Series, ProcessingLog

logger = logging.getLogger(__name__)

class DicomProcessor:
    """Main DICOM processing class."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.orthanc_url = config.get('orthanc', {}).get('url', 'http://localhost:8042')
        self.orthanc_user = config.get('orthanc', {}).get('username', 'admin')
        self.orthanc_password = self._get_orthanc_password()
        self.session = requests.Session()
        
        # Only set authentication if password is provided
        if self.orthanc_password:
            self.session.auth = (self.orthanc_user, self.orthanc_password)
            logger.info("Orthanc authentication configured")
        else:
            logger.info("Orthanc running without authentication")
        
        # Processing settings
        self.max_file_size = config.get('processing', {}).get('dicom', {}).get('max_file_size_mb', 500) * 1024 * 1024
        self.supported_modalities = config.get('processing', {}).get('dicom', {}).get('supported_modalities', [])
        self.validation_enabled = config.get('processing', {}).get('dicom', {}).get('validation_enabled', True)
        
    def _get_orthanc_password(self) -> str:
        """Get Orthanc password from environment or config."""
        password_env = self.config.get('orthanc', {}).get('password_env', '')
        
        # If no password environment variable is configured, assume no auth required
        if not password_env:
            logger.info("No password environment variable configured - using no authentication")
            return ""
        
        password = os.getenv(password_env)
        if not password:
            logger.warning(f"Orthanc password environment variable '{password_env}' not set")
            return ""
        return password
    
    def validate_dicom_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate a DICOM file.
        
        Args:
            file_path: Path to the DICOM file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                return False, f"File size ({file_size}) exceeds maximum ({self.max_file_size})"
            
            if not HAS_PYDICOM:
                logger.warning("pydicom not available, skipping DICOM validation")
                return True, ""
            
            # Read DICOM file
            ds = pydicom.dcmread(file_path, stop_before_pixels=True)
            
            # Check required tags
            required_tags = ['PatientID', 'StudyInstanceUID', 'SeriesInstanceUID', 'SOPInstanceUID']
            missing_tags = []
            
            for tag in required_tags:
                if not hasattr(ds, tag) or not getattr(ds, tag):
                    missing_tags.append(tag)
            
            if missing_tags:
                return False, f"Missing required tags: {', '.join(missing_tags)}"
            
            # Check modality if specified
            if self.supported_modalities and hasattr(ds, 'Modality'):
                if ds.Modality not in self.supported_modalities:
                    return False, f"Unsupported modality: {ds.Modality}"
            
            return True, ""
            
        except InvalidDicomError as e:
            return False, f"Invalid DICOM file: {str(e)}"
        except Exception as e:
            return False, f"Error reading DICOM file: {str(e)}"
    
    def extract_dicom_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a DICOM file.
        
        Args:
            file_path: Path to the DICOM file
            
        Returns:
            Dictionary of extracted metadata
        """
        metadata = {
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'file_modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        }
        
        if not HAS_PYDICOM:
            logger.warning("pydicom not available, limited metadata extraction")
            return metadata
        
        try:
            ds = pydicom.dcmread(file_path, stop_before_pixels=True)
            
            # Patient information
            metadata.update({
                'patient_id': getattr(ds, 'PatientID', ''),
                'patient_name': str(getattr(ds, 'PatientName', '')),
                'patient_birth_date': getattr(ds, 'PatientBirthDate', ''),
                'patient_sex': getattr(ds, 'PatientSex', ''),
            })
            
            # Study information
            metadata.update({
                'study_instance_uid': getattr(ds, 'StudyInstanceUID', ''),
                'study_date': getattr(ds, 'StudyDate', ''),
                'study_time': getattr(ds, 'StudyTime', ''),
                'study_description': getattr(ds, 'StudyDescription', ''),
                'accession_number': getattr(ds, 'AccessionNumber', ''),
            })
            
            # Series information
            metadata.update({
                'series_instance_uid': getattr(ds, 'SeriesInstanceUID', ''),
                'series_number': getattr(ds, 'SeriesNumber', ''),
                'series_description': getattr(ds, 'SeriesDescription', ''),
                'modality': getattr(ds, 'Modality', ''),
                'body_part_examined': getattr(ds, 'BodyPartExamined', ''),
            })
            
            # Image information
            metadata.update({
                'sop_instance_uid': getattr(ds, 'SOPInstanceUID', ''),
                'instance_number': getattr(ds, 'InstanceNumber', ''),
                'rows': getattr(ds, 'Rows', 0),
                'columns': getattr(ds, 'Columns', 0),
                'pixel_spacing': getattr(ds, 'PixelSpacing', []),
                'slice_thickness': getattr(ds, 'SliceThickness', 0),
            })
            
            # Additional technical parameters
            if hasattr(ds, 'ImagePositionPatient'):
                metadata['image_position'] = list(ds.ImagePositionPatient)
            if hasattr(ds, 'ImageOrientationPatient'):
                metadata['image_orientation'] = list(ds.ImageOrientationPatient)
            if hasattr(ds, 'WindowCenter'):
                metadata['window_center'] = ds.WindowCenter
            if hasattr(ds, 'WindowWidth'):
                metadata['window_width'] = ds.WindowWidth
                
        except Exception as e:
            logger.error(f"Error extracting DICOM metadata from {file_path}: {str(e)}")
            metadata['error'] = str(e)
        
        return metadata
    
    def scan_directory_for_dicom(self, directory: str) -> List[str]:
        """
        Scan a directory for DICOM files.
        
        Args:
            directory: Directory to scan
            
        Returns:
            List of DICOM file paths
        """
        dicom_files = []
        directory_path = Path(directory)
        
        if not directory_path.exists():
            logger.error(f"Directory does not exist: {directory}")
            return dicom_files
        
        # Common DICOM file extensions
        dicom_extensions = ['.dcm', '.dicom', '.ima', '.img']
        
        for file_path in directory_path.rglob('*'):
            if file_path.is_file():
                # Check by extension first
                if file_path.suffix.lower() in dicom_extensions:
                    dicom_files.append(str(file_path))
                # Check files without extension (common in TCIA)
                elif not file_path.suffix:
                    if self.is_dicom_file(str(file_path)):
                        dicom_files.append(str(file_path))
        
        logger.info(f"Found {len(dicom_files)} DICOM files in {directory}")
        return dicom_files
    
    def is_dicom_file(self, file_path: str) -> bool:
        """
        Check if a file is a DICOM file by examining its header.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file is a DICOM file
        """
        try:
            with open(file_path, 'rb') as f:
                # Read the first 132 bytes to check for DICM signature
                header = f.read(132)
                return header[128:132] == b'DICM'
        except Exception:
            return False
    
    def organize_dicom_files(self, dicom_files: List[str]) -> Dict[str, Dict[str, List[str]]]:
        """
        Organize DICOM files by study and series.
        
        Args:
            dicom_files: List of DICOM file paths
            
        Returns:
            Dictionary organized as {study_uid: {series_uid: [file_paths]}}
        """
        organized = {}
        
        for file_path in dicom_files:
            if not self.validation_enabled:
                # Skip validation if disabled
                metadata = self.extract_dicom_metadata(file_path)
            else:
                # Validate first
                is_valid, error_msg = self.validate_dicom_file(file_path)
                if not is_valid:
                    logger.warning(f"Skipping invalid DICOM file {file_path}: {error_msg}")
                    continue
                metadata = self.extract_dicom_metadata(file_path)
            
            study_uid = metadata.get('study_instance_uid', 'unknown')
            series_uid = metadata.get('series_instance_uid', 'unknown')
            
            if study_uid not in organized:
                organized[study_uid] = {}
            
            if series_uid not in organized[study_uid]:
                organized[study_uid][series_uid] = []
            
            organized[study_uid][series_uid].append(file_path)
        
        return organized
    
    def upload_dicom_to_orthanc(self, file_path: str) -> Tuple[bool, str]:
        """
        Upload a DICOM file to Orthanc.
        
        Args:
            file_path: Path to the DICOM file
            
        Returns:
            Tuple of (success, orthanc_instance_id or error_message)
        """
        try:
            with open(file_path, 'rb') as f:
                dicom_data = f.read()
            
            # Upload to Orthanc
            response = self.session.post(
                f"{self.orthanc_url}/instances",
                data=dicom_data,
                headers={'Content-Type': 'application/dicom'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                instance_id = result.get('ID')
                logger.info(f"Successfully uploaded {file_path} to Orthanc (ID: {instance_id})")
                return True, instance_id
            else:
                error_msg = f"Failed to upload {file_path}: HTTP {response.status_code}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error uploading {file_path}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def upload_series_to_orthanc(self, series_files: List[str], study_uid: str, series_uid: str) -> Dict[str, Any]:
        """
        Upload a complete series to Orthanc.
        
        Args:
            series_files: List of DICOM files in the series
            study_uid: Study Instance UID
            series_uid: Series Instance UID
            
        Returns:
            Dictionary with upload results
        """
        results = {
            'study_uid': study_uid,
            'series_uid': series_uid,
            'total_files': len(series_files),
            'successful_uploads': 0,
            'failed_uploads': 0,
            'orthanc_instance_ids': [],
            'errors': []
        }
        
        logger.info(f"Uploading series {series_uid} with {len(series_files)} files")
        
        for file_path in series_files:
            success, result = self.upload_dicom_to_orthanc(file_path)
            
            if success:
                results['successful_uploads'] += 1
                results['orthanc_instance_ids'].append(result)
            else:
                results['failed_uploads'] += 1
                results['errors'].append(f"{file_path}: {result}")
        
        logger.info(f"Series upload completed: {results['successful_uploads']}/{results['total_files']} successful")
        return results
    
    def get_orthanc_study_info(self, study_uid: str) -> Optional[Dict[str, Any]]:
        """
        Get study information from Orthanc.
        
        Args:
            study_uid: Study Instance UID
            
        Returns:
            Study information dictionary or None if not found
        """
        try:
            # Search for study in Orthanc
            response = self.session.post(
                f"{self.orthanc_url}/tools/find",
                json={
                    "Level": "Study",
                    "Query": {
                        "StudyInstanceUID": study_uid
                    }
                }
            )
            
            if response.status_code == 200:
                study_ids = response.json()
                if study_ids:
                    # Get detailed study information
                    study_response = self.session.get(f"{self.orthanc_url}/studies/{study_ids[0]}")
                    if study_response.status_code == 200:
                        return study_response.json()
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting Orthanc study info for {study_uid}: {str(e)}")
            return None
    
    def verify_orthanc_upload(self, study_uid: str, expected_series: List[str]) -> Dict[str, Any]:
        """
        Verify that a study was uploaded correctly to Orthanc.
        
        Args:
            study_uid: Study Instance UID
            expected_series: List of expected series UIDs
            
        Returns:
            Verification results
        """
        results = {
            'study_uid': study_uid,
            'study_found': False,
            'expected_series': len(expected_series),
            'found_series': 0,
            'missing_series': [],
            'series_details': {}
        }
        
        study_info = self.get_orthanc_study_info(study_uid)
        
        if study_info:
            results['study_found'] = True
            results['found_series'] = len(study_info.get('Series', []))
            
            # Check each expected series
            for series_uid in expected_series:
                series_found = False
                for series_id in study_info.get('Series', []):
                    series_response = self.session.get(f"{self.orthanc_url}/series/{series_id}")
                    if series_response.status_code == 200:
                        series_data = series_response.json()
                        if series_data.get('MainDicomTags', {}).get('SeriesInstanceUID') == series_uid:
                            series_found = True
                            results['series_details'][series_uid] = {
                                'orthanc_id': series_id,
                                'instance_count': len(series_data.get('Instances', [])),
                                'description': series_data.get('MainDicomTags', {}).get('SeriesDescription', '')
                            }
                            break
                
                if not series_found:
                    results['missing_series'].append(series_uid)
        
        return results
    
    def process_patient_directory(self, patient_dir: str, patient_id: str) -> Dict[str, Any]:
        """
        Process a complete patient directory (TCIA format).
        
        Args:
            patient_dir: Path to patient directory
            patient_id: Patient ID
            
        Returns:
            Processing results
        """
        results = {
            'patient_id': patient_id,
            'directory': patient_dir,
            'studies_found': 0,
            'studies_processed': 0,
            'total_files': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'studies': {}
        }
        
        logger.info(f"Processing patient directory: {patient_dir}")
        
        # Find all DICOM files
        dicom_files = self.scan_directory_for_dicom(patient_dir)
        results['total_files'] = len(dicom_files)
        
        if not dicom_files:
            logger.warning(f"No DICOM files found in {patient_dir}")
            return results
        
        # Organize files by study and series
        organized = self.organize_dicom_files(dicom_files)
        results['studies_found'] = len(organized)
        
        # Process each study
        for study_uid, series_dict in organized.items():
            logger.info(f"Processing study: {study_uid}")
            
            study_result = {
                'study_uid': study_uid,
                'series_count': len(series_dict),
                'series_results': {}
            }
            
            # Upload each series
            for series_uid, series_files in series_dict.items():
                series_result = self.upload_series_to_orthanc(series_files, study_uid, series_uid)
                study_result['series_results'][series_uid] = series_result
                
                results['successful_uploads'] += series_result['successful_uploads']
                results['failed_uploads'] += series_result['failed_uploads']
            
            results['studies'][study_uid] = study_result
            results['studies_processed'] += 1
        
        logger.info(f"Patient processing completed: {results['studies_processed']}/{results['studies_found']} studies processed")
        return results

def create_dicom_processor(config: Dict[str, Any]) -> DicomProcessor:
    """Factory function to create a DICOM processor."""
    return DicomProcessor(config) 