# Case Management System - Quick Start Guide

## 🚀 **Overview**
This guide will get you up and running with the automated case management system to process TCIA data and integrate with your Casewise platform.

## 📋 **Prerequisites**
- Python 3.8+
- Access to TCIA data directory
- Orthanc server running (api.casewisemd.org/orthanc/)
- CSV metadata file

## ⚙️ **Installation**

### 1. Install Dependencies
```bash
cd case-management
pip install -r requirements.txt
```

### 2. Configure Environment Variables
```bash
# No environment variables required for basic operation
# Orthanc server runs without authentication

# Optional: Only if using PostgreSQL in production
export DB_PASSWORD="your_db_password"
```

### 3. Update Configuration
Edit `config/config.yaml` to match your environment:

```yaml
data_sources:
  tcia:
    path: "C:/Users/Mike/Documents/TCIA Direct DL Data/TCGA-OV"
    metadata_path: "source-documents/excel-reports/TCGA-case-reports.csv"
    enabled: true

orthanc:
  url: "https://api.casewisemd.org/orthanc/"
  dicom_web_url: "https://api.casewisemd.org/orthanc/dicom-web"
  username: "admin"
  # No password required - server runs without authentication
```

## 🎯 **Basic Usage**

### 1. Discovery Phase
First, discover what cases are available:

```bash
python scripts/case_manager.py discover
```

**Expected Output:**
```
Discovery Results:
  Total Patients: 15
  Total Studies: 15
  TCIA Patients: 15

TCIA Patients:
  - TCGA-09-0364 (1 studies)
  - TCGA-09-0367 (1 studies)
  - TCGA-09-1659 (1 studies)
  ...
```

### 2. Ingestion Phase
Process and ingest cases into the system:

```bash
# Ingest first 3 cases starting from case002
python scripts/case_manager.py ingest --limit 3 --start 2

# Ingest all available cases
python scripts/case_manager.py ingest
```

**Expected Output:**
```
Ingestion Results:
  Processed: 3
  Successful: 3
  Failed: 0

Created Cases:
  - case002
  - case003
  - case004
```

### 3. List and Explore Cases
View all processed cases:

```bash
# List all cases
python scripts/case_manager.py list

# Filter by specialty
python scripts/case_manager.py list --specialty Oncology

# Get detailed case information
python scripts/case_manager.py detail case002
```

### 4. System Reports
Generate system status reports:

```bash
python scripts/case_manager.py report
```

**Expected Output:**
```
System Report
=============

Summary:
  Cases: 3
  Annotations: 24
  Reviewers: 8
  Series: 12

Cases by Specialty:
  Oncology: 3

Cases by Difficulty:
  Intermediate: 2
  Advanced: 1
```

### 5. Verify Orthanc Integration
Ensure cases are properly uploaded to Orthanc:

```bash
python scripts/case_manager.py verify
```

## 🔄 **Automated Workflow**

### Complete Processing Pipeline
```bash
#!/bin/bash
# automated_processing.sh

echo "Starting automated case processing..."

# 1. Discovery
echo "Discovering cases..."
python scripts/case_manager.py discover

# 2. Ingestion (process 5 cases at a time)
echo "Ingesting cases..."
python scripts/case_manager.py ingest --limit 5

# 3. Verification
echo "Verifying uploads..."
python scripts/case_manager.py verify

# 4. Generate report
echo "Generating report..."
python scripts/case_manager.py report

echo "Processing complete!"
```

## 📊 **What Gets Created**

### Database Records
For each processed case:
- **Case**: Basic case information (ID, patient, specialty, difficulty)
- **Annotations**: Expert reviews from CSV (8 reviewers × lesion measurements)
- **Series**: DICOM series metadata
- **Processing Logs**: Audit trail of all operations

### Orthanc Integration
- DICOM files uploaded to Orthanc server
- Study Instance UIDs mapped to case IDs
- Integration with existing OHIF viewer

### Case Metadata
```json
{
  "id": "case002",
  "patient_id": "TCGA-09-0364",
  "title": "Case 002: TCGA-09-0364",
  "specialty": "Oncology",
  "difficulty": "Intermediate",
  "modality": "CT",
  "anatomy": "Abdomen/Pelvis",
  "learning_objectives": [
    "Identify primary ovarian mass characteristics",
    "Assess peritoneal disease spread patterns",
    "Evaluate nodal involvement"
  ],
  "expert_annotations": {
    "lesion_length": 144.8,
    "peritoneal_disease": {...},
    "metastatic_disease": {...}
  }
}
```

## 🔧 **Advanced Usage**

### Custom Configuration
Create environment-specific config files:

```bash
# Development
python scripts/case_manager.py --config config/dev.yaml discover

# Production
python scripts/case_manager.py --config config/prod.yaml ingest
```

### Batch Processing
Process specific patient subsets:

```python
# Custom Python script
from src.tcia_ingestion import create_tcia_ingestion
from src.case_manager import CaseManager

# Initialize
manager = CaseManager()
tcia = create_tcia_ingestion(manager.config)

# Filter patients by criteria
patients = tcia.discover_tcia_patients()
oncology_patients = [p for p in patients if "TCGA-OV" in p.patient_id]

# Process specific patients
for patient in oncology_patients[:5]:
    result = tcia.process_tcia_patient(patient, f"case{len(cases)+1:03d}")
    print(f"Processed {patient.patient_id}: {result['success']}")
```

### Integration with MCP Backend
Update the MCP viewer tools to use the new case database:

```python
# In mcp/tools/viewer_tools.py
from case_management.src.models import Case, get_case_by_id

def get_case_study_uid(case_id: str) -> str:
    """Get Study Instance UID for a case from the database."""
    with SessionLocal() as session:
        case = get_case_by_id(session, case_id)
        return case.study_instance_uid if case else None
```

## 🚨 **Troubleshooting**

### Common Issues

**1. "TCIA data path does not exist"**
```bash
# Check path in config.yaml
# Ensure Windows path uses forward slashes or escaped backslashes
path: "C:/Users/Mike/Documents/TCIA Direct DL Data/TCGA-OV"
```

**2. "pydicom not installed"**
```bash
pip install pydicom
```

**3. "Database permission error"**
```bash
# Ensure database directory is writable
mkdir -p case-management/database
chmod 755 case-management/database
```

**4. "Orthanc connection failed"**
```bash
# Test Orthanc connectivity
curl "https://api.casewisemd.org/orthanc/system"
# Should return JSON with API version and capabilities
```

### Debug Mode
Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 **Next Steps**

### 1. Expand Data Sources
Add support for additional data sources:
- Local PACS exports
- RadiAnt/OsiriX exports
- Custom DICOM directories

### 2. Frontend Integration
Update the Casewise frontend to:
- List cases dynamically from database
- Display expert annotations
- Show case difficulty and learning objectives

### 3. Advanced Features
- Automated difficulty assessment using AI
- Multi-reviewer annotation aggregation
- Quality control workflows
- Educational assessment tools

### 4. Scaling
- Move to PostgreSQL for production
- Implement distributed processing
- Add monitoring and alerting
- Create REST API endpoints

---

**🎉 You're Ready!** Your automated case management system is now configured and ready to process medical cases efficiently. Start with discovery and small batch ingestion to verify everything works correctly.