"""
Database models for the Case Management System.
Supports SQLite (development) and PostgreSQL (production).
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

# Association table for case-reviewer relationships
case_reviewer_association = Table(
    'case_reviewers',
    Base.metadata,
    Column('case_id', String, ForeignKey('cases.id'), primary_key=True),
    Column('reviewer_id', String, ForeignKey('reviewers.id'), primary_key=True)
)

class Case(Base):
    """Main case model representing a medical case."""
    __tablename__ = 'cases'
    
    # Primary identifiers
    id = Column(String, primary_key=True)  # case001, case002, etc.
    patient_id = Column(String, nullable=False, index=True)  # TCGA-09-0364
    study_instance_uid = Column(String, nullable=False, unique=True, index=True)
    
    # Case metadata
    title = Column(String, nullable=False)
    description = Column(Text)
    keywords = Column(Text)  # Comma-separated keywords
    
    # Classification
    specialty = Column(String, nullable=False)  # "Oncology", "Cardiology", etc.
    difficulty = Column(String, nullable=False)  # "Beginner", "Intermediate", "Advanced"
    modality = Column(String, nullable=False)  # "CT", "MR", "PET", etc.
    anatomy = Column(String)  # "Abdomen", "Chest", "Pelvis", etc.
    
    # Clinical data
    diagnosis = Column(String)
    clinical_history = Column(Text)
    findings = Column(Text)
    
    # Processing metadata
    source = Column(String, nullable=False)  # "TCIA", "Local", etc.
    data_source_path = Column(String)
    processed_date = Column(DateTime, default=datetime.utcnow)
    
    # System fields
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, default="active")  # "active", "review", "archived"
    
    # Educational metadata
    learning_objectives = Column(JSON)
    difficulty_score = Column(Float)
    case_complexity = Column(String)
    
    # Relationships
    series = relationship("Series", back_populates="case", cascade="all, delete-orphan")
    annotations = relationship("Annotation", back_populates="case", cascade="all, delete-orphan")
    reviewers = relationship("Reviewer", secondary=case_reviewer_association, back_populates="cases")
    
    def __repr__(self):
        return f"<Case(id='{self.id}', patient_id='{self.patient_id}', specialty='{self.specialty}')>"

class Series(Base):
    """DICOM series within a case."""
    __tablename__ = 'series'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey('cases.id'), nullable=False)
    series_instance_uid = Column(String, nullable=False, unique=True, index=True)
    
    # Series metadata
    series_number = Column(String)
    series_description = Column(String)
    modality = Column(String)
    body_part = Column(String)
    
    # Technical parameters
    image_count = Column(Integer)
    slice_thickness = Column(Float)
    pixel_spacing = Column(String)
    
    # Processing status
    orthanc_series_id = Column(String, unique=True)
    upload_status = Column(String, default="pending")  # "pending", "uploading", "completed", "failed"
    upload_date = Column(DateTime)
    
    # Relationships
    case = relationship("Case", back_populates="series")
    
    def __repr__(self):
        return f"<Series(id='{self.id}', description='{self.series_description}')>"

class Annotation(Base):
    """Expert annotations and measurements for cases."""
    __tablename__ = 'annotations'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey('cases.id'), nullable=False)
    reviewer_id = Column(String, ForeignKey('reviewers.id'))
    
    # Annotation metadata
    annotation_type = Column(String, nullable=False)  # "measurement", "finding", "assessment"
    category = Column(String)  # "lesion", "organ", "pathology"
    
    # Measurements (from CSV data)
    lesion_length = Column(Float)
    measurements = Column(JSON)  # Store complex measurements
    
    # Clinical findings
    findings = Column(JSON)  # Store boolean findings from CSV
    assessment = Column(Text)
    confidence = Column(Float)
    
    # Coordinates (if available)
    coordinates = Column(JSON)
    roi_data = Column(JSON)
    
    # Timestamps
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    case = relationship("Case", back_populates="annotations")
    reviewer = relationship("Reviewer", back_populates="annotations")
    
    def __repr__(self):
        return f"<Annotation(id='{self.id}', type='{self.annotation_type}')>"

class Reviewer(Base):
    """Expert reviewers who provide annotations."""
    __tablename__ = 'reviewers'
    
    id = Column(String, primary_key=True)  # "ashinagare", "avargas", etc.
    name = Column(String, nullable=False)
    email = Column(String)
    institution = Column(String)
    specialty = Column(String)
    
    # Expertise
    years_experience = Column(Integer)
    certification = Column(String)
    expertise_areas = Column(JSON)
    
    # Statistics
    cases_reviewed = Column(Integer, default=0)
    annotations_count = Column(Integer, default=0)
    
    # Timestamps
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cases = relationship("Case", secondary=case_reviewer_association, back_populates="reviewers")
    annotations = relationship("Annotation", back_populates="reviewer")
    
    def __repr__(self):
        return f"<Reviewer(id='{self.id}', name='{self.name}')>"

class ProcessingLog(Base):
    """Log of processing activities."""
    __tablename__ = 'processing_logs'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Processing details
    operation = Column(String, nullable=False)  # "ingest", "upload", "validate"
    source = Column(String, nullable=False)
    target = Column(String)
    
    # Status
    status = Column(String, nullable=False)  # "started", "completed", "failed"
    progress = Column(Float, default=0.0)
    
    # Results
    items_processed = Column(Integer, default=0)
    items_successful = Column(Integer, default=0)
    items_failed = Column(Integer, default=0)
    
    # Error handling
    error_message = Column(Text)
    error_details = Column(JSON)
    
    # Timestamps
    started_date = Column(DateTime, default=datetime.utcnow)
    completed_date = Column(DateTime)
    
    def __repr__(self):
        return f"<ProcessingLog(id='{self.id}', operation='{self.operation}', status='{self.status}')>"

class Configuration(Base):
    """System configuration stored in database."""
    __tablename__ = 'configurations'
    
    id = Column(String, primary_key=True)
    category = Column(String, nullable=False)
    key = Column(String, nullable=False)
    value = Column(JSON)
    description = Column(String)
    
    # Timestamps
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Configuration(category='{self.category}', key='{self.key}')>"

# Database utility functions
def get_case_by_id(session, case_id: str) -> Optional[Case]:
    """Get a case by its ID."""
    return session.query(Case).filter(Case.id == case_id).first()

def get_case_by_patient_id(session, patient_id: str) -> Optional[Case]:
    """Get a case by patient ID."""
    return session.query(Case).filter(Case.patient_id == patient_id).first()

def get_cases_by_specialty(session, specialty: str) -> List[Case]:
    """Get all cases for a specific specialty."""
    return session.query(Case).filter(Case.specialty == specialty).all()

def get_cases_by_difficulty(session, difficulty: str) -> List[Case]:
    """Get all cases for a specific difficulty level."""
    return session.query(Case).filter(Case.difficulty == difficulty).all()

def search_cases(session, query: str) -> List[Case]:
    """Search cases by keywords in title, description, or keywords."""
    search_term = f"%{query}%"
    return session.query(Case).filter(
        Case.title.ilike(search_term) |
        Case.description.ilike(search_term) |
        Case.keywords.ilike(search_term)
    ).all()

def get_processing_status(session, operation: str) -> List[ProcessingLog]:
    """Get recent processing logs for an operation."""
    return session.query(ProcessingLog).filter(
        ProcessingLog.operation == operation
    ).order_by(ProcessingLog.started_date.desc()).limit(10).all()

def create_case_from_tcia(patient_id: str, study_uid: str, metadata: Dict[str, Any]) -> Case:
    """Create a case from TCIA data."""
    # Generate case ID
    case_count = metadata.get('case_count', 1)
    case_id = f"case{case_count:03d}"
    
    # Extract case information
    case = Case(
        id=case_id,
        patient_id=patient_id,
        study_instance_uid=study_uid,
        title=f"Case {case_count}: {patient_id}",
        description=f"TCIA case from {patient_id}",
        specialty="Oncology",  # Default for TCGA cases
        difficulty="Intermediate",  # Default, can be calculated
        modality="CT",  # Default, should be extracted from DICOM
        source="TCIA",
        keywords=f"oncology,{patient_id.lower()},tcia"
    )
    
    return case 