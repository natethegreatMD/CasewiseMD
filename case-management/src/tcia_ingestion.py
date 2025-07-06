"""
TCIA Ingestion Module for Case Management System.
Handles parsing TCIA data structures and CSV metadata files.
"""

import os
import csv
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
import pandas as pd
from dataclasses import dataclass

# Handle both relative and absolute imports
try:
    from .models import Case, Annotation, Reviewer, create_case_from_tcia
    from .dicom_processor import DicomProcessor
    from .case_id_generator import create_case_id_generator
except ImportError:
    from models import Case, Annotation, Reviewer, create_case_from_tcia
    from dicom_processor import DicomProcessor
    from case_id_generator import create_case_id_generator

logger = logging.getLogger(__name__)

@dataclass
class TciaPatient:
    """Represents a TCIA patient."""
    patient_id: str
    directory: str
    studies: List[str]
    metadata: Dict[str, Any]

@dataclass
class TciaStudy:
    """Represents a TCIA study."""
    patient_id: str
    study_uid: str
    study_date: str
    study_description: str
    series_count: int
    directory: str

class TciaIngestion:
    """Main TCIA ingestion class."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tcia_config = config.get('data_sources', {}).get('tcia', {})
        self.data_path = self.tcia_config.get('path', '')
        self.metadata_path = self.tcia_config.get('metadata_path', '')
        
        # Initialize DICOM processor
        self.dicom_processor = DicomProcessor(config)
        
        # Initialize Case ID generator
        self.case_id_generator = create_case_id_generator()
        
        # CSV metadata cache
        self._csv_metadata = None
        self._reviewers = {}
        
    def discover_tcia_patients(self) -> List[TciaPatient]:
        """
        Discover all TCIA patients in the data directory.
        
        Returns:
            List of TciaPatient objects
        """
        patients = []
        data_path = Path(self.data_path)
        
        if not data_path.exists():
            logger.error(f"TCIA data path does not exist: {self.data_path}")
            return patients
        
        logger.info(f"Discovering TCIA patients in: {self.data_path}")
        
        # TCIA structure: PatientID directories
        for patient_dir in data_path.iterdir():
            if patient_dir.is_dir() and patient_dir.name.startswith('TCGA-'):
                patient_id = patient_dir.name
                
                # Find study directories
                studies = []
                for study_dir in patient_dir.iterdir():
                    if study_dir.is_dir():
                        studies.append(study_dir.name)
                
                if studies:
                    patient = TciaPatient(
                        patient_id=patient_id,
                        directory=str(patient_dir),
                        studies=studies,
                        metadata={}
                    )
                    patients.append(patient)
                    logger.info(f"Found patient {patient_id} with {len(studies)} studies")
        
        logger.info(f"Discovered {len(patients)} TCIA patients")
        return patients
    
    def parse_study_directory_name(self, study_dir_name: str) -> Dict[str, str]:
        """
        Parse TCIA study directory name to extract metadata.
        
        Args:
            study_dir_name: Study directory name (e.g., "09-09-1994-NA-FOREIGN CT ABPEL-78315")
            
        Returns:
            Dictionary with parsed metadata
        """
        parts = study_dir_name.split('-')
        
        # Try to parse date (MM-DD-YYYY format)
        study_date = ""
        if len(parts) >= 3:
            try:
                month, day, year = parts[0], parts[1], parts[2]
                study_date = f"{year}{month.zfill(2)}{day.zfill(2)}"
            except ValueError:
                logger.warning(f"Could not parse date from study directory: {study_dir_name}")
        
        # Extract description (everything after the year)
        description = ""
        if len(parts) > 3:
            description = "-".join(parts[3:])
        
        return {
            'study_date': study_date,
            'study_description': description,
            'original_name': study_dir_name
        }
    
    def get_tcia_studies(self, patient: TciaPatient) -> List[TciaStudy]:
        """
        Get all studies for a TCIA patient.
        
        Args:
            patient: TciaPatient object
            
        Returns:
            List of TciaStudy objects
        """
        studies = []
        patient_path = Path(patient.directory)
        
        for study_name in patient.studies:
            study_path = patient_path / study_name
            
            if not study_path.exists():
                continue
            
            # Parse study directory name
            study_metadata = self.parse_study_directory_name(study_name)
            
            # Count series (subdirectories)
            series_count = len([d for d in study_path.iterdir() if d.is_dir()])
            
            # Try to extract Study Instance UID from DICOM files
            study_uid = self._extract_study_uid_from_directory(str(study_path))
            
            if study_uid:
                study = TciaStudy(
                    patient_id=patient.patient_id,
                    study_uid=study_uid,
                    study_date=study_metadata['study_date'],
                    study_description=study_metadata['study_description'],
                    series_count=series_count,
                    directory=str(study_path)
                )
                studies.append(study)
                logger.info(f"Found study {study_uid} for patient {patient.patient_id}")
        
        return studies
    
    def _extract_study_uid_from_directory(self, study_dir: str) -> Optional[str]:
        """
        Extract Study Instance UID from the first DICOM file in a study directory.
        
        Args:
            study_dir: Path to study directory
            
        Returns:
            Study Instance UID or None if not found
        """
        try:
            # Find the first DICOM file
            dicom_files = self.dicom_processor.scan_directory_for_dicom(study_dir)
            
            if dicom_files:
                # Extract metadata from first file
                metadata = self.dicom_processor.extract_dicom_metadata(dicom_files[0])
                return metadata.get('study_instance_uid')
            
        except Exception as e:
            logger.error(f"Error extracting Study UID from {study_dir}: {str(e)}")
        
        return None
    
    def load_csv_metadata(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load CSV metadata file and organize by patient ID.
        
        Returns:
            Dictionary mapping patient IDs to list of expert reviews
        """
        if self._csv_metadata is not None:
            return self._csv_metadata
        
        metadata = {}
        
        if not self.metadata_path:
            logger.warning("No metadata path configured")
            return metadata
        
        csv_path = Path(self.metadata_path)
        if not csv_path.exists():
            logger.error(f"CSV metadata file not found: {self.metadata_path}")
            return metadata
        
        logger.info(f"Loading CSV metadata from: {self.metadata_path}")
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_path)
            
            # Group by PatientID
            for patient_id in df['PatientID'].unique():
                patient_data = df[df['PatientID'] == patient_id]
                
                reviews = []
                for _, row in patient_data.iterrows():
                    review = {
                        'patient_id': row['PatientID'],
                        'reviewer': row['Reviewer'],
                        'lesion_length': row['LesionLength'],
                        'findings': self._extract_findings_from_row(row),
                        'measurements': self._extract_measurements_from_row(row),
                        'raw_data': row.to_dict()
                    }
                    reviews.append(review)
                
                metadata[patient_id] = reviews
                logger.info(f"Loaded {len(reviews)} reviews for patient {patient_id}")
            
            # Cache the metadata
            self._csv_metadata = metadata
            
            logger.info(f"Successfully loaded metadata for {len(metadata)} patients")
            
        except Exception as e:
            logger.error(f"Error loading CSV metadata: {str(e)}")
        
        return metadata
    
    def _extract_findings_from_row(self, row: pd.Series) -> Dict[str, Any]:
        """
        Extract clinical findings from a CSV row.
        
        Args:
            row: Pandas Series representing a CSV row
            
        Returns:
            Dictionary of clinical findings
        """
        findings = {}
        
        # PD (Peritoneal Disease) findings
        pd_fields = [
            'PDinMesentericImplant', 'PDinMesentery', 'PDinParacolicGutters',
            'PDinPouchofDouglas', 'PDinSpleenLUQ', 'PDinLesserSac',
            'PDinLiverRUQ', 'PDCalcifications', 'PDOmentalImplant'
        ]
        
        pd_findings = {}
        for field in pd_fields:
            if field in row:
                pd_findings[field] = row[field]
        
        findings['peritoneal_disease'] = pd_findings
        
        # Nodal disease findings
        nodal_fields = [
            'InfrarenalRetroNodalStation', 'PelvicNodalStation', 'InguinalNodalStation',
            'PortaCelGastroNodalStation', 'RetrocruralNodalStation', 'SupradiaphragmNodalStation',
            'SuprarenalRetroNodalStation', 'ThoracicNodalStation'
        ]
        
        nodal_findings = {}
        for field in nodal_fields:
            if field in row:
                nodal_findings[field] = row[field]
        
        findings['nodal_disease'] = nodal_findings
        
        # Metastatic disease
        met_fields = [
            'LiverMets', 'LungMets', 'PleuraMets', 'SpleenMets', 'OtherMets',
            'MetCalcifications'
        ]
        
        met_findings = {}
        for field in met_fields:
            if field in row:
                met_findings[field] = row[field]
        
        findings['metastatic_disease'] = met_findings
        
        # Additional findings
        additional_fields = [
            'PleuralEffusionSize', 'Ascites', 'MassLaterality', 'MassCalcifications',
            'MassSeptations', 'MassIntArchitecture', 'PDShape'
        ]
        
        additional_findings = {}
        for field in additional_fields:
            if field in row:
                additional_findings[field] = row[field]
        
        findings['additional'] = additional_findings
        
        return findings
    
    def _extract_measurements_from_row(self, row: pd.Series) -> Dict[str, Any]:
        """
        Extract measurements from a CSV row.
        
        Args:
            row: Pandas Series representing a CSV row
            
        Returns:
            Dictionary of measurements
        """
        measurements = {}
        
        # Primary lesion measurement
        if 'LesionLength' in row:
            measurements['lesion_length'] = row['LesionLength']
        
        # Add other measurement fields as needed
        measurement_fields = [
            'LesionLength'
        ]
        
        for field in measurement_fields:
            if field in row and pd.notna(row[field]):
                measurements[field] = row[field]
        
        return measurements
    
    def get_reviewers(self) -> Dict[str, Reviewer]:
        """
        Get unique reviewers from the CSV metadata.
        
        Returns:
            Dictionary mapping reviewer IDs to Reviewer objects
        """
        if self._reviewers:
            return self._reviewers
        
        metadata = self.load_csv_metadata()
        reviewer_ids = set()
        
        # Collect all unique reviewer IDs
        for patient_reviews in metadata.values():
            for review in patient_reviews:
                reviewer_ids.add(review['reviewer'])
        
        # Create Reviewer objects
        reviewers = {}
        for reviewer_id in reviewer_ids:
            reviewer = Reviewer(
                id=reviewer_id,
                name=reviewer_id.title(),  # Simple name formatting
                specialty="Radiology",  # Default specialty
                created_date=datetime.utcnow()
            )
            reviewers[reviewer_id] = reviewer
        
        self._reviewers = reviewers
        logger.info(f"Found {len(reviewers)} unique reviewers")
        return reviewers
    
    def create_case_from_tcia_study(self, study: TciaStudy) -> Case:
        """
        Create a Case object from a TCIA study with automatically generated meaningful case ID.
        
        Args:
            study: TciaStudy object
            
        Returns:
            Case object with generated case ID
        """
        # Generate meaningful case ID based on patient ID
        case_id = self.case_id_generator.generate_tcia_case_id(study.patient_id)
        
        # Get metadata for this patient
        metadata = self.load_csv_metadata()
        patient_metadata = metadata.get(study.patient_id, [])
        
        # Calculate average lesion length across reviewers
        lesion_lengths = [review['lesion_length'] for review in patient_metadata 
                         if 'lesion_length' in review and pd.notna(review['lesion_length'])]
        avg_lesion_length = sum(lesion_lengths) / len(lesion_lengths) if lesion_lengths else 0
        
        # Create case
        case = Case(
            id=case_id,
            patient_id=study.patient_id,
            study_instance_uid=study.study_uid,
            title=f"Case {case_id}: {study.patient_id}",
            description=f"TCIA Ovarian Cancer case from {study.patient_id}",
            specialty="Oncology",
            difficulty=self._calculate_difficulty(avg_lesion_length, patient_metadata),
            modality="CT",  # Default for TCGA-OV
            anatomy="Abdomen/Pelvis",
            source="TCIA",
            data_source_path=study.directory,
            keywords=f"oncology,ovarian cancer,{study.patient_id.lower()},tcia,tcga",
            learning_objectives=self._generate_learning_objectives(patient_metadata),
            difficulty_score=avg_lesion_length / 200.0 if avg_lesion_length > 0 else 0.5,  # Normalize to 0-1
            case_complexity=self._assess_complexity(patient_metadata)
        )
        
        return case
    
    def _calculate_difficulty(self, avg_lesion_length: float, patient_metadata: List[Dict[str, Any]]) -> str:
        """
        Calculate case difficulty based on lesion characteristics.
        
        Args:
            avg_lesion_length: Average lesion length across reviewers
            patient_metadata: List of expert reviews
            
        Returns:
            Difficulty level string
        """
        if not patient_metadata:
            return "Intermediate"
        
        # Analyze complexity factors
        complexity_factors = []
        
        # Lesion size factor
        if avg_lesion_length > 150:
            complexity_factors.append("large_lesion")
        elif avg_lesion_length < 50:
            complexity_factors.append("small_lesion")
        
        # Check for metastatic disease
        for review in patient_metadata:
            findings = review.get('findings', {})
            met_disease = findings.get('metastatic_disease', {})
            
            if any(met_disease.values()):
                complexity_factors.append("metastatic_disease")
                break
        
        # Check for nodal involvement
        for review in patient_metadata:
            findings = review.get('findings', {})
            nodal_disease = findings.get('nodal_disease', {})
            
            if any(nodal_disease.values()):
                complexity_factors.append("nodal_involvement")
                break
        
        # Determine difficulty
        if len(complexity_factors) >= 3:
            return "Advanced"
        elif len(complexity_factors) >= 1:
            return "Intermediate"
        else:
            return "Beginner"
    
    def _assess_complexity(self, patient_metadata: List[Dict[str, Any]]) -> str:
        """
        Assess case complexity based on expert reviews.
        
        Args:
            patient_metadata: List of expert reviews
            
        Returns:
            Complexity assessment string
        """
        if not patient_metadata:
            return "Moderate"
        
        # Count various findings across reviewers
        pd_findings = []
        nodal_findings = []
        met_findings = []
        
        for review in patient_metadata:
            findings = review.get('findings', {})
            
            # Count PD findings
            pd_count = sum(1 for v in findings.get('peritoneal_disease', {}).values() if v)
            pd_findings.append(pd_count)
            
            # Count nodal findings
            nodal_count = sum(1 for v in findings.get('nodal_disease', {}).values() if v)
            nodal_findings.append(nodal_count)
            
            # Count metastatic findings
            met_count = sum(1 for v in findings.get('metastatic_disease', {}).values() if v)
            met_findings.append(met_count)
        
        # Calculate average findings
        avg_pd = sum(pd_findings) / len(pd_findings) if pd_findings else 0
        avg_nodal = sum(nodal_findings) / len(nodal_findings) if nodal_findings else 0
        avg_met = sum(met_findings) / len(met_findings) if met_findings else 0
        
        total_findings = avg_pd + avg_nodal + avg_met
        
        if total_findings >= 5:
            return "High"
        elif total_findings >= 2:
            return "Moderate"
        else:
            return "Low"
    
    def _generate_learning_objectives(self, patient_metadata: List[Dict[str, Any]]) -> List[str]:
        """
        Generate learning objectives based on case findings.
        
        Args:
            patient_metadata: List of expert reviews
            
        Returns:
            List of learning objectives
        """
        objectives = [
            "Identify primary ovarian mass characteristics",
            "Assess peritoneal disease spread patterns",
            "Evaluate nodal involvement"
        ]
        
        if not patient_metadata:
            return objectives
        
        # Add specific objectives based on findings
        common_findings = set()
        
        for review in patient_metadata:
            findings = review.get('findings', {})
            
            # Check for specific findings
            if findings.get('metastatic_disease', {}).get('LiverMets'):
                common_findings.add("liver_metastases")
            if findings.get('metastatic_disease', {}).get('LungMets'):
                common_findings.add("lung_metastases")
            if findings.get('additional', {}).get('Ascites') not in ['None', None]:
                common_findings.add("ascites")
            if findings.get('additional', {}).get('PleuralEffusionSize') not in ['None', None]:
                common_findings.add("pleural_effusion")
        
        # Add specific objectives
        if "liver_metastases" in common_findings:
            objectives.append("Recognize hepatic metastases")
        if "lung_metastases" in common_findings:
            objectives.append("Identify pulmonary metastases")
        if "ascites" in common_findings:
            objectives.append("Assess ascites volume and distribution")
        if "pleural_effusion" in common_findings:
            objectives.append("Evaluate pleural effusion")
        
        return objectives
    
    def create_annotations_from_metadata(self, case: Case, patient_metadata: List[Dict[str, Any]]) -> List[Annotation]:
        """
        Create annotation objects from CSV metadata.
        
        Args:
            case: Case object
            patient_metadata: List of expert reviews
            
        Returns:
            List of Annotation objects
        """
        annotations = []
        
        for review in patient_metadata:
            annotation = Annotation(
                case_id=case.id,
                reviewer_id=review['reviewer'],
                annotation_type="assessment",
                category="expert_review",
                lesion_length=review.get('lesion_length'),
                measurements=review.get('measurements', {}),
                findings=review.get('findings', {}),
                assessment=f"Expert review by {review['reviewer']}",
                created_date=datetime.utcnow()
            )
            annotations.append(annotation)
        
        return annotations
    
    def process_tcia_patient(self, patient: TciaPatient) -> Dict[str, Any]:
        """
        Process a single TCIA patient with automatic case ID generation.
        
        Args:
            patient: TciaPatient object
            
        Returns:
            Processing results with case, annotations, and upload results
        """
        logger.info(f"Processing TCIA patient {patient.patient_id}")
        
        try:
            # Get the first study (most have only one)
            if not patient.studies:
                raise ValueError(f"No studies found for patient {patient.patient_id}")
            
            study = patient.studies[0]  # Use first study
            
            # Create case with automatic ID generation
            case = self.create_case_from_tcia_study(study)
            
            # Get metadata and create annotations
            metadata = self.load_csv_metadata()
            patient_metadata = metadata.get(patient.patient_id, [])
            
            annotations = []
            for review in patient_metadata:
                annotation = Annotation(
                    case_id=case.id,
                    reviewer_id=review['reviewer_name'],
                    category='clinical_assessment',
                    finding_type='lesion_measurement',
                    measurement_type='length',
                    measurement_value=review.get('lesion_length', 0),
                    measurement_unit='mm',
                    confidence=review.get('confidence', 0.8),
                    comments=review.get('additional_findings', ''),
                    raw_data=review
                )
                annotations.append(annotation)
            
            # Process DICOM files
            dicom_results = self.dicom_processor.process_study_directory(study.directory)
            
            return {
                'success': True,
                'case': case,
                'annotations': annotations,
                'dicom_results': dicom_results
            }
            
        except Exception as e:
            logger.error(f"Error processing TCIA patient {patient.patient_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

def create_tcia_ingestion(config: Dict[str, Any]) -> TciaIngestion:
    """Factory function to create a TCIA ingestion processor."""
    return TciaIngestion(config) 