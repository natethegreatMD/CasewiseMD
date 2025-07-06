#!/usr/bin/env python3
"""
Case Management System - Main CLI Interface

This script provides command-line tools for managing medical cases:
- Discover and ingest TCIA data
- Process DICOM files and upload to Orthanc
- Manage case database
- Generate reports and statistics
"""

import os
import sys
import argparse
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from models import Base, Case, Series, Annotation, Reviewer, ProcessingLog
from dicom_processor import create_dicom_processor
from tcia_ingestion import create_tcia_ingestion

# Database imports
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CaseManager:
    """Main case management system."""
    
    def __init__(self, config_path: str = None):
        """Initialize case manager with configuration."""
        self.config = self.load_config(config_path)
        self.engine = self.setup_database()
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize processors
        self.dicom_processor = create_dicom_processor(self.config)
        self.tcia_ingestion = create_tcia_ingestion(self.config)
        
    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
        
        config_path = Path(config_path)
        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Loaded configuration from: {config_path}")
        return config
    
    def setup_database(self) -> Any:
        """Setup database connection and create tables."""
        db_config = self.config.get('database', {})
        env = self.config.get('environment', 'development')
        
        if env not in db_config:
            logger.error(f"Database configuration not found for environment: {env}")
            sys.exit(1)
        
        db_settings = db_config[env]
        
        if db_settings['type'] == 'sqlite':
            # Ensure database directory exists
            db_path = Path(db_settings['path'])
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            database_url = f"sqlite:///{db_path}"
        elif db_settings['type'] == 'postgresql':
            password = os.getenv(db_settings.get('password_env', 'DB_PASSWORD'), '')
            database_url = (
                f"postgresql://{db_settings['username']}:{password}@"
                f"{db_settings['host']}:{db_settings['port']}/{db_settings['database']}"
            )
        else:
            logger.error(f"Unsupported database type: {db_settings['type']}")
            sys.exit(1)
        
        # Create engine
        engine = create_engine(database_url)
        
        # Create tables
        Base.metadata.create_all(engine)
        
        logger.info(f"Database setup complete: {database_url}")
        return engine
    
    def discover_cases(self) -> Dict[str, Any]:
        """Discover all available cases from data sources."""
        logger.info("Discovering cases from data sources...")
        
        results = {
            'tcia_patients': [],
            'total_patients': 0,
            'total_studies': 0
        }
        
        # Discover TCIA patients
        if self.config.get('data_sources', {}).get('tcia', {}).get('enabled', False):
            tcia_patients = self.tcia_ingestion.discover_tcia_patients()
            results['tcia_patients'] = tcia_patients
            results['total_patients'] += len(tcia_patients)
            
            # Count studies
            for patient in tcia_patients:
                studies = self.tcia_ingestion.get_tcia_studies(patient)
                results['total_studies'] += len(studies)
        
        logger.info(f"Discovery complete: {results['total_patients']} patients, {results['total_studies']} studies")
        return results
    
    def ingest_tcia_cases(self, limit: int = None) -> Dict[str, Any]:
        """
        Ingest TCIA cases into the system with automatic meaningful case ID generation.
        
        Args:
            limit: Maximum number of cases to process
            
        Returns:
            Processing results
        """
        logger.info(f"Starting TCIA ingestion with automatic case ID generation (limit: {limit})")
        
        results = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'cases': [],
            'errors': []
        }
        
        # Discover patients
        patients = self.tcia_ingestion.discover_tcia_patients()
        
        if limit:
            patients = patients[:limit]
        
        # Process each patient
        with self.Session() as session:
            for patient in patients:
                try:
                    logger.info(f"Processing {patient.patient_id} with automatic case ID generation")
                    
                    # Process patient - case ID will be automatically generated
                    process_result = self.tcia_ingestion.process_tcia_patient(patient)
                    
                    if process_result['success']:
                        # Get the automatically generated case ID
                        case = process_result['case']
                        case_id = case.id
                        
                        # Check if case already exists
                        existing_case = session.query(Case).filter(Case.id == case_id).first()
                        if existing_case:
                            logger.warning(f"Case {case_id} already exists, skipping")
                            continue
                        
                        # Save to database
                        annotations = process_result['annotations']
                        
                        # Add case
                        session.add(case)
                        
                        # Add annotations
                        for annotation in annotations:
                            session.add(annotation)
                        
                        # Add reviewers if they don't exist
                        reviewers = self.tcia_ingestion.get_reviewers()
                        for reviewer_id, reviewer in reviewers.items():
                            existing_reviewer = session.query(Reviewer).filter(Reviewer.id == reviewer_id).first()
                            if not existing_reviewer:
                                session.add(reviewer)
                        
                        # Create processing log
                        dicom_results = process_result['dicom_results']
                        log = ProcessingLog(
                            operation="tcia_ingestion",
                            source=patient.patient_id,
                            target=case_id,
                            status="completed",
                            items_processed=dicom_results['total_files'],
                            items_successful=dicom_results['successful_uploads'],
                            items_failed=dicom_results['failed_uploads']
                        )
                        session.add(log)
                        
                        # Commit transaction
                        session.commit()
                        
                        results['successful'] += 1
                        results['cases'].append(case_id)
                        
                        logger.info(f"Successfully processed {patient.patient_id} as {case_id}")
                        
                    else:
                        results['failed'] += 1
                        error_msg = process_result.get('error', 'Unknown error')
                        results['errors'].append(f"{patient.patient_id}: {error_msg}")
                        logger.error(f"Failed to process {patient.patient_id}: {error_msg}")
                    
                    results['processed'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing patient {patient.patient_id}: {str(e)}")
                    results['failed'] += 1
                    results['errors'].append(f"{patient.patient_id}: {str(e)}")
        
        logger.info(f"TCIA ingestion complete: {results['successful']}/{results['processed']} successful")
        return results
    
    def list_cases(self, specialty: str = None, difficulty: str = None) -> List[Case]:
        """List cases with optional filtering."""
        with self.Session() as session:
            query = session.query(Case)
            
            if specialty:
                query = query.filter(Case.specialty == specialty)
            
            if difficulty:
                query = query.filter(Case.difficulty == difficulty)
            
            cases = query.order_by(Case.id).all()
            
        return cases
    
    def get_case_details(self, case_id: str) -> Dict[str, Any]:
        """Get detailed information about a case."""
        with self.Session() as session:
            case = session.query(Case).filter(Case.id == case_id).first()
            
            if not case:
                return {'error': f'Case {case_id} not found'}
            
            # Get annotations
            annotations = session.query(Annotation).filter(Annotation.case_id == case_id).all()
            
            # Get series
            series = session.query(Series).filter(Series.case_id == case_id).all()
            
            return {
                'case': case,
                'annotations': annotations,
                'series': series,
                'reviewer_count': len(set(ann.reviewer_id for ann in annotations)),
                'annotation_count': len(annotations),
                'series_count': len(series)
            }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate system status report."""
        with self.Session() as session:
            # Basic counts
            case_count = session.query(Case).count()
            annotation_count = session.query(Annotation).count()
            reviewer_count = session.query(Reviewer).count()
            series_count = session.query(Series).count()
            
            # Cases by specialty
            specialty_counts = session.query(
                Case.specialty, func.count(Case.id)
            ).group_by(Case.specialty).all()
            
            # Cases by difficulty
            difficulty_counts = session.query(
                Case.difficulty, func.count(Case.id)
            ).group_by(Case.difficulty).all()
            
            # Cases by source
            source_counts = session.query(
                Case.source, func.count(Case.id)
            ).group_by(Case.source).all()
            
            # Recent processing logs
            recent_logs = session.query(ProcessingLog).order_by(
                ProcessingLog.started_date.desc()
            ).limit(10).all()
            
            return {
                'summary': {
                    'cases': case_count,
                    'annotations': annotation_count,
                    'reviewers': reviewer_count,
                    'series': series_count
                },
                'cases_by_specialty': dict(specialty_counts),
                'cases_by_difficulty': dict(difficulty_counts),
                'cases_by_source': dict(source_counts),
                'recent_processing': [
                    {
                        'operation': log.operation,
                        'status': log.status,
                        'items_processed': log.items_processed,
                        'started': log.started_date.isoformat() if log.started_date else None
                    }
                    for log in recent_logs
                ]
            }
    
    def verify_orthanc_uploads(self) -> Dict[str, Any]:
        """Verify that cases are properly uploaded to Orthanc."""
        logger.info("Verifying Orthanc uploads...")
        
        results = {
            'checked': 0,
            'verified': 0,
            'missing': 0,
            'errors': []
        }
        
        with self.Session() as session:
            cases = session.query(Case).all()
            
            for case in cases:
                try:
                    # Get expected series UIDs
                    series = session.query(Series).filter(Series.case_id == case.id).all()
                    expected_series = [s.series_instance_uid for s in series]
                    
                    if not expected_series:
                        # If no series in database, skip verification
                        continue
                    
                    # Verify in Orthanc
                    verification = self.dicom_processor.verify_orthanc_upload(
                        case.study_instance_uid, expected_series
                    )
                    
                    if verification['study_found'] and len(verification['missing_series']) == 0:
                        results['verified'] += 1
                        logger.info(f"Case {case.id} verified in Orthanc")
                    else:
                        results['missing'] += 1
                        error_msg = f"Case {case.id}: Study found={verification['study_found']}, Missing series={len(verification['missing_series'])}"
                        results['errors'].append(error_msg)
                        logger.warning(error_msg)
                    
                    results['checked'] += 1
                    
                except Exception as e:
                    error_msg = f"Error verifying case {case.id}: {str(e)}"
                    results['errors'].append(error_msg)
                    logger.error(error_msg)
        
        logger.info(f"Verification complete: {results['verified']}/{results['checked']} verified")
        return results

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='Case Management System CLI')
    parser.add_argument('--config', '-c', help='Configuration file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Discover available cases')
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest TCIA cases')
    ingest_parser.add_argument('--limit', '-l', type=int, help='Maximum number of cases to process')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List cases')
    list_parser.add_argument('--specialty', help='Filter by specialty')
    list_parser.add_argument('--difficulty', help='Filter by difficulty')
    
    # Case detail command
    detail_parser = subparsers.add_parser('detail', help='Get case details')
    detail_parser.add_argument('case_id', help='Case ID to examine')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate system report')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify Orthanc uploads')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize case manager
    try:
        case_manager = CaseManager(args.config)
    except Exception as e:
        logger.error(f"Failed to initialize case manager: {str(e)}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'discover':
            results = case_manager.discover_cases()
            print(f"\nDiscovery Results:")
            print(f"  Total Patients: {results['total_patients']}")
            print(f"  Total Studies: {results['total_studies']}")
            print(f"  TCIA Patients: {len(results['tcia_patients'])}")
            
            if results['tcia_patients']:
                print(f"\nTCIA Patients:")
                for patient in results['tcia_patients'][:10]:  # Show first 10
                    print(f"  - {patient.patient_id} ({len(patient.studies)} studies)")
                
                if len(results['tcia_patients']) > 10:
                    print(f"  ... and {len(results['tcia_patients']) - 10} more")
        
        elif args.command == 'ingest':
            results = case_manager.ingest_tcia_cases(limit=args.limit)
            print(f"\nIngestion Results:")
            print(f"  Processed: {results['processed']}")
            print(f"  Successful: {results['successful']}")
            print(f"  Failed: {results['failed']}")
            
            if results['cases']:
                print(f"\nCreated Cases:")
                for case_id in results['cases']:
                    print(f"  - {case_id}")
            
            if results['errors']:
                print(f"\nErrors:")
                for error in results['errors'][:5]:  # Show first 5 errors
                    print(f"  - {error}")
        
        elif args.command == 'list':
            cases = case_manager.list_cases(args.specialty, args.difficulty)
            print(f"\nCases ({len(cases)} total):")
            for case in cases:
                print(f"  {case.id}: {case.title} [{case.specialty}, {case.difficulty}]")
        
        elif args.command == 'detail':
            details = case_manager.get_case_details(args.case_id)
            
            if 'error' in details:
                print(f"Error: {details['error']}")
            else:
                case = details['case']
                print(f"\nCase Details: {case.id}")
                print(f"  Title: {case.title}")
                print(f"  Patient ID: {case.patient_id}")
                print(f"  Specialty: {case.specialty}")
                print(f"  Difficulty: {case.difficulty}")
                print(f"  Modality: {case.modality}")
                print(f"  Source: {case.source}")
                print(f"  Study UID: {case.study_instance_uid}")
                print(f"  Annotations: {details['annotation_count']} from {details['reviewer_count']} reviewers")
                print(f"  Series: {details['series_count']}")
                
                if case.learning_objectives:
                    print(f"\nLearning Objectives:")
                    for obj in case.learning_objectives:
                        print(f"  - {obj}")
        
        elif args.command == 'report':
            report = case_manager.generate_report()
            print(f"\nSystem Report")
            print(f"=============")
            
            summary = report['summary']
            print(f"\nSummary:")
            print(f"  Cases: {summary['cases']}")
            print(f"  Annotations: {summary['annotations']}")
            print(f"  Reviewers: {summary['reviewers']}")
            print(f"  Series: {summary['series']}")
            
            if report['cases_by_specialty']:
                print(f"\nCases by Specialty:")
                for specialty, count in report['cases_by_specialty'].items():
                    print(f"  {specialty}: {count}")
            
            if report['cases_by_difficulty']:
                print(f"\nCases by Difficulty:")
                for difficulty, count in report['cases_by_difficulty'].items():
                    print(f"  {difficulty}: {count}")
            
            if report['recent_processing']:
                print(f"\nRecent Processing:")
                for log in report['recent_processing'][:5]:
                    print(f"  {log['operation']}: {log['status']} ({log['items_processed']} items)")
        
        elif args.command == 'verify':
            results = case_manager.verify_orthanc_uploads()
            print(f"\nOrthanc Verification Results:")
            print(f"  Checked: {results['checked']}")
            print(f"  Verified: {results['verified']}")
            print(f"  Missing: {results['missing']}")
            
            if results['errors']:
                print(f"\nErrors/Warnings:")
                for error in results['errors'][:10]:  # Show first 10
                    print(f"  - {error}")
    
    except Exception as e:
        logger.error(f"Command failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 