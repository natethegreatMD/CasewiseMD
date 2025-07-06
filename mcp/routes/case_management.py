"""
Case Management API routes
Connects the new case management database to the MCP backend
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add the case management src directory to the path
case_management_path = Path(__file__).parent.parent.parent / "case-management" / "src"
sys.path.insert(0, str(case_management_path))

try:
    from models import Case, Annotation, Reviewer, Series
    from case_id_generator import create_case_id_generator
except ImportError as e:
    print(f"Warning: Could not import case management models: {e}")
    # Define minimal models for fallback
    class Case:
        pass
    class Annotation:
        pass
    class Reviewer:
        pass
    class Series:
        pass

router = APIRouter()

# Database configuration
DATABASE_URL = os.getenv("CASE_DB_URL", "sqlite:///case-management/database/cases.db")

def get_database_session():
    """Get database session for case management"""
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@router.get("/cases")
async def list_cases(
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    modality: Optional[str] = Query(None, description="Filter by modality"),
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: Optional[int] = Query(None, description="Limit number of results")
):
    """
    List all available cases with optional filtering
    """
    session = get_database_session()
    if not session:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        query = session.query(Case)
        
        # Apply filters
        if specialty:
            query = query.filter(Case.specialty == specialty)
        if difficulty:
            query = query.filter(Case.difficulty == difficulty)
        if modality:
            query = query.filter(Case.modality == modality)
        if source:
            query = query.filter(Case.source == source)
        
        # Apply limit
        if limit:
            query = query.limit(limit)
        
        cases = query.order_by(Case.created_date.desc()).all()
        
        # Format response
        case_list = []
        for case in cases:
            # Get annotation count
            annotation_count = session.query(Annotation).filter(Annotation.case_id == case.id).count()
            
            # Get series count
            series_count = session.query(Series).filter(Series.case_id == case.id).count()
            
            case_data = {
                "case_id": case.id,
                "title": case.title,
                "description": case.description,
                "specialty": case.specialty,
                "difficulty": case.difficulty,
                "modality": case.modality,
                "anatomy": case.anatomy,
                "source": case.source,
                "patient_id": case.patient_id,
                "study_instance_uid": case.study_instance_uid,
                "keywords": case.keywords.split(",") if case.keywords else [],
                "learning_objectives": case.learning_objectives or [],
                "difficulty_score": case.difficulty_score,
                "case_complexity": case.case_complexity,
                "annotation_count": annotation_count,
                "series_count": series_count,
                "created_date": case.created_date.isoformat() if case.created_date else None
            }
            case_list.append(case_data)
        
        return {
            "success": True,
            "cases": case_list,
            "total_count": len(case_list),
            "filters_applied": {
                "specialty": specialty,
                "difficulty": difficulty,
                "modality": modality,
                "source": source
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing cases: {str(e)}")
    finally:
        session.close()

@router.get("/cases/by-category")
async def list_cases_by_category(
    category: str = Query(..., description="Category to filter by (e.g., 'ovarian-cancer', 'chest-xray')")
):
    """
    List cases by category for the frontend case selection
    """
    session = get_database_session()
    if not session:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        # Map frontend categories to database filters
        category_filters = {
            "ovarian-cancer": {"specialty": "Oncology", "anatomy": "Abdomen/Pelvis"},
            "chest-xray": {"modality": "X-Ray", "anatomy": "Chest"},
            "brain-mri": {"modality": "MRI", "anatomy": "Brain"},
            "abdomen-ct": {"modality": "CT", "anatomy": "Abdomen"},
            "obstetric-ultrasound": {"modality": "Ultrasound", "anatomy": "Pelvis"},
            "cardiac-ct": {"modality": "CT", "anatomy": "Chest"}
        }
        
        filters = category_filters.get(category, {})
        
        if not filters:
            # Return empty result for unknown categories
            return {
                "success": True,
                "category": category,
                "cases": [],
                "total_count": 0,
                "message": f"No cases found for category: {category}"
            }
        
        # Build query with category filters
        query = session.query(Case)
        
        for field, value in filters.items():
            if hasattr(Case, field):
                query = query.filter(getattr(Case, field) == value)
        
        cases = query.order_by(Case.difficulty_score.asc()).all()
        
        # Format response
        case_list = []
        for case in cases:
            # Get annotation count for reviewer info
            annotation_count = session.query(Annotation).filter(Annotation.case_id == case.id).count()
            reviewer_count = session.query(Annotation.reviewer_id).filter(Annotation.case_id == case.id).distinct().count()
            
            case_data = {
                "case_id": case.id,
                "title": case.title,
                "description": case.description,
                "difficulty": case.difficulty,
                "difficulty_score": case.difficulty_score,
                "patient_id": case.patient_id,
                "modality": case.modality,
                "anatomy": case.anatomy,
                "learning_objectives": case.learning_objectives or [],
                "annotation_count": annotation_count,
                "reviewer_count": reviewer_count,
                "case_complexity": case.case_complexity,
                "created_date": case.created_date.isoformat() if case.created_date else None,
                "preview_info": {
                    "specialty": case.specialty,
                    "source": case.source,
                    "keywords": case.keywords.split(",") if case.keywords else []
                }
            }
            case_list.append(case_data)
        
        return {
            "success": True,
            "category": category,
            "cases": case_list,
            "total_count": len(case_list),
            "category_info": {
                "filters_applied": filters,
                "difficulty_distribution": _get_difficulty_distribution(cases),
                "complexity_distribution": _get_complexity_distribution(cases)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing cases by category: {str(e)}")
    finally:
        session.close()

@router.get("/cases/{case_id}")
async def get_case_details(case_id: str):
    """
    Get detailed information about a specific case
    """
    session = get_database_session()
    if not session:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        case = session.query(Case).filter(Case.id == case_id).first()
        
        if not case:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
        
        # Get annotations with reviewer info
        annotations = session.query(Annotation).filter(Annotation.case_id == case_id).all()
        
        # Get series information
        series = session.query(Series).filter(Series.case_id == case_id).all()
        
        # Format annotations
        annotation_data = []
        for annotation in annotations:
            annotation_data.append({
                "id": annotation.id,
                "reviewer_id": annotation.reviewer_id,
                "category": annotation.category,
                "finding_type": annotation.finding_type,
                "measurement_value": annotation.measurement_value,
                "measurement_unit": annotation.measurement_unit,
                "confidence": annotation.confidence,
                "comments": annotation.comments,
                "created_date": annotation.created_date.isoformat() if annotation.created_date else None
            })
        
        # Format series
        series_data = []
        for s in series:
            series_data.append({
                "series_instance_uid": s.series_instance_uid,
                "modality": s.modality,
                "series_description": s.series_description,
                "series_number": s.series_number,
                "image_count": s.image_count,
                "slice_thickness": s.slice_thickness
            })
        
        return {
            "success": True,
            "case": {
                "id": case.id,
                "title": case.title,
                "description": case.description,
                "specialty": case.specialty,
                "difficulty": case.difficulty,
                "modality": case.modality,
                "anatomy": case.anatomy,
                "source": case.source,
                "patient_id": case.patient_id,
                "study_instance_uid": case.study_instance_uid,
                "keywords": case.keywords.split(",") if case.keywords else [],
                "learning_objectives": case.learning_objectives or [],
                "difficulty_score": case.difficulty_score,
                "case_complexity": case.case_complexity,
                "data_source_path": case.data_source_path,
                "created_date": case.created_date.isoformat() if case.created_date else None
            },
            "annotations": annotation_data,
            "series": series_data,
            "statistics": {
                "annotation_count": len(annotation_data),
                "reviewer_count": len(set(ann["reviewer_id"] for ann in annotation_data)),
                "series_count": len(series_data)
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting case details: {str(e)}")
    finally:
        session.close()

@router.get("/categories")
async def get_case_categories():
    """
    Get case categories with counts from the database
    """
    session = get_database_session()
    if not session:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        # Get case counts by specialty and anatomy
        case_counts = session.query(
            Case.specialty,
            Case.anatomy,
            Case.modality,
            func.count(Case.id).label('count')
        ).group_by(Case.specialty, Case.anatomy, Case.modality).all()
        
        # Map to frontend categories
        categories = {
            "ovarian-cancer": {
                "id": "ovarian-cancer",
                "title": "Ovarian Cancer",
                "description": "Complex cases involving ovarian malignancies and differential diagnoses",
                "difficulty": "intermediate",
                "modality": "CT",
                "count": 0
            },
            "chest-xray": {
                "id": "chest-xray",
                "title": "Chest X-Ray",
                "description": "Basic to advanced chest radiography interpretation",
                "difficulty": "beginner",
                "modality": "X-Ray",
                "count": 0
            },
            "brain-mri": {
                "id": "brain-mri",
                "title": "Brain MRI",
                "description": "Neurological imaging cases including tumors and vascular conditions",
                "difficulty": "advanced",
                "modality": "MRI",
                "count": 0
            },
            "abdomen-ct": {
                "id": "abdomen-ct",
                "title": "Abdomen CT",
                "description": "Abdominal pathology and trauma cases",
                "difficulty": "intermediate",
                "modality": "CT",
                "count": 0
            },
            "obstetric-ultrasound": {
                "id": "obstetric-ultrasound",
                "title": "Obstetric Ultrasound",
                "description": "Prenatal imaging and fetal development assessment",
                "difficulty": "beginner",
                "modality": "Ultrasound",
                "count": 0
            },
            "cardiac-ct": {
                "id": "cardiac-ct",
                "title": "Cardiac CT",
                "description": "Cardiovascular imaging and coronary artery assessment",
                "difficulty": "advanced",
                "modality": "CT",
                "count": 0
            }
        }
        
        # Update counts from database
        for specialty, anatomy, modality, count in case_counts:
            # Map database values to category IDs
            if specialty == "Oncology" and anatomy == "Abdomen/Pelvis":
                categories["ovarian-cancer"]["count"] += count
            elif modality == "X-Ray" and anatomy == "Chest":
                categories["chest-xray"]["count"] += count
            elif modality == "MRI" and anatomy == "Brain":
                categories["brain-mri"]["count"] += count
            elif modality == "CT" and anatomy == "Abdomen":
                categories["abdomen-ct"]["count"] += count
            elif modality == "Ultrasound" and anatomy == "Pelvis":
                categories["obstetric-ultrasound"]["count"] += count
            elif modality == "CT" and anatomy == "Chest":
                categories["cardiac-ct"]["count"] += count
        
        return {
            "success": True,
            "categories": list(categories.values()),
            "total_categories": len(categories),
            "total_cases": sum(cat["count"] for cat in categories.values())
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting case categories: {str(e)}")
    finally:
        session.close()

def _get_difficulty_distribution(cases: List[Case]) -> Dict[str, int]:
    """Get difficulty distribution for cases"""
    distribution = {}
    for case in cases:
        difficulty = case.difficulty or "Unknown"
        distribution[difficulty] = distribution.get(difficulty, 0) + 1
    return distribution

def _get_complexity_distribution(cases: List[Case]) -> Dict[str, int]:
    """Get complexity distribution for cases"""
    distribution = {}
    for case in cases:
        complexity = case.case_complexity or "Unknown"
        distribution[complexity] = distribution.get(complexity, 0) + 1
    return distribution 