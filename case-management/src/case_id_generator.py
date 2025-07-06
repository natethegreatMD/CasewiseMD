"""
Case ID Generator Module
Generates meaningful, scalable case IDs for the case management system.
"""

import re
from typing import Dict, Any, Optional
from datetime import datetime


class CaseIdGenerator:
    """Generates meaningful case IDs based on data source and patient information."""
    
    def __init__(self):
        # Source prefixes
        self.source_prefixes = {
            'TCIA': 'TCIA',
            'PACS': 'PACS',
            'LOCAL': 'LOCAL',
            'CUSTOM': 'CUSTOM'
        }
        
        # Cancer type mappings for TCGA
        self.tcga_types = {
            'TCGA-09': 'OV',  # Ovarian
            'TCGA-23': 'BR',  # Breast
            'TCGA-24': 'OV',  # Ovarian
            'TCGA-25': 'OV',  # Ovarian
            'TCGA-13': 'OV',  # Ovarian
            'TCGA-10': 'OV',  # Ovarian
            'TCGA-30': 'OV',  # Ovarian
            'TCGA-61': 'OV',  # Ovarian
            'TCGA-OY': 'OV',  # Ovarian
            # Add more as needed
        }
    
    def generate_tcia_case_id(self, patient_id: str, study_description: str = "") -> str:
        """
        Generate case ID for TCIA data.
        
        Args:
            patient_id: TCGA patient ID (e.g., "TCGA-09-0364")
            study_description: Study description for additional context
            
        Returns:
            Generated case ID (e.g., "TCIA-OV-TCGA09-0364")
        """
        # Extract cancer type from patient ID
        cancer_type = self._extract_cancer_type(patient_id)
        
        # Clean up patient ID (remove hyphens, make uppercase)
        clean_patient_id = self._clean_patient_id(patient_id)
        
        # Format: TCIA-{CANCER_TYPE}-{CLEAN_PATIENT_ID}
        case_id = f"TCIA-{cancer_type}-{clean_patient_id}"
        
        return case_id
    
    def generate_pacs_case_id(self, modality: str, date: datetime, sequence: int = 1) -> str:
        """
        Generate case ID for PACS data.
        
        Args:
            modality: Imaging modality (CT, MR, US, etc.)
            date: Study date
            sequence: Sequential number for that day
            
        Returns:
            Generated case ID (e.g., "PACS-CT-20250115-001")
        """
        date_str = date.strftime("%Y%m%d")
        case_id = f"PACS-{modality.upper()}-{date_str}-{sequence:03d}"
        return case_id
    
    def generate_local_case_id(self, category: str, sequence: int) -> str:
        """
        Generate case ID for local data.
        
        Args:
            category: Case category (BRAIN, CARDIAC, etc.)
            sequence: Sequential number
            
        Returns:
            Generated case ID (e.g., "LOCAL-BRAIN-001")
        """
        case_id = f"LOCAL-{category.upper()}-{sequence:03d}"
        return case_id
    
    def generate_custom_case_id(self, prefix: str, identifier: str) -> str:
        """
        Generate case ID for custom data sources.
        
        Args:
            prefix: Custom prefix
            identifier: Unique identifier
            
        Returns:
            Generated case ID
        """
        clean_prefix = re.sub(r'[^A-Z0-9]', '', prefix.upper())
        clean_id = re.sub(r'[^A-Z0-9]', '', identifier.upper())
        case_id = f"CUSTOM-{clean_prefix}-{clean_id}"
        return case_id
    
    def _extract_cancer_type(self, patient_id: str) -> str:
        """Extract cancer type from TCGA patient ID."""
        # Extract first part (e.g., "TCGA-09" from "TCGA-09-0364")
        parts = patient_id.split('-')
        if len(parts) >= 2:
            tcga_prefix = f"{parts[0]}-{parts[1]}"
            return self.tcga_types.get(tcga_prefix, 'UNK')  # UNK = Unknown
        return 'UNK'
    
    def _clean_patient_id(self, patient_id: str) -> str:
        """Clean patient ID for use in case ID."""
        # Convert TCGA-09-0364 to TCGA09-0364
        cleaned = patient_id.replace('-', '', 1)  # Remove first hyphen only
        return cleaned.upper()
    
    def validate_case_id(self, case_id: str) -> bool:
        """
        Validate case ID format.
        
        Args:
            case_id: Case ID to validate
            
        Returns:
            True if valid format
        """
        # Basic validation patterns
        patterns = [
            r'^TCIA-[A-Z]{2,3}-TCGA\d{2}-\d{4}$',  # TCIA format
            r'^PACS-[A-Z]{2,3}-\d{8}-\d{3}$',      # PACS format
            r'^LOCAL-[A-Z]+-\d{3}$',               # LOCAL format
            r'^CUSTOM-[A-Z0-9]+-[A-Z0-9]+$',       # CUSTOM format
            r'^case\d{3}$'                         # Legacy format
        ]
        
        return any(re.match(pattern, case_id) for pattern in patterns)
    
    def parse_case_id(self, case_id: str) -> Dict[str, str]:
        """
        Parse case ID to extract components.
        
        Args:
            case_id: Case ID to parse
            
        Returns:
            Dictionary with parsed components
        """
        parts = case_id.split('-')
        
        if len(parts) >= 3:
            return {
                'source': parts[0],
                'type_or_modality': parts[1],
                'identifier': '-'.join(parts[2:]),
                'format': 'structured'
            }
        elif case_id.startswith('case'):
            return {
                'source': 'legacy',
                'type_or_modality': 'unknown',
                'identifier': case_id,
                'format': 'legacy'
            }
        else:
            return {
                'source': 'unknown',
                'type_or_modality': 'unknown',
                'identifier': case_id,
                'format': 'unknown'
            }


def create_case_id_generator() -> CaseIdGenerator:
    """Factory function to create a case ID generator."""
    return CaseIdGenerator()


# Example usage and testing
if __name__ == '__main__':
    generator = CaseIdGenerator()
    
    # Test TCIA case IDs
    tcia_cases = [
        "TCGA-09-0364",
        "TCGA-25-1316",
        "TCGA-61-1725",
        "TCGA-OY-A56P"
    ]
    
    print("TCIA Case ID Examples:")
    for patient_id in tcia_cases:
        case_id = generator.generate_tcia_case_id(patient_id)
        print(f"  {patient_id} → {case_id}")
    
    # Test PACS case IDs
    print("\nPACS Case ID Examples:")
    pacs_examples = [
        ("CT", datetime(2025, 1, 15), 1),
        ("MR", datetime(2025, 1, 15), 2),
        ("US", datetime(2025, 2, 1), 1)
    ]
    
    for modality, date, seq in pacs_examples:
        case_id = generator.generate_pacs_case_id(modality, date, seq)
        print(f"  {modality} {date.strftime('%Y-%m-%d')} #{seq} → {case_id}")
    
    # Test validation
    print("\nValidation Examples:")
    test_ids = [
        "TCIA-OV-TCGA09-0364",
        "PACS-CT-20250115-001",
        "LOCAL-BRAIN-001",
        "case001",
        "invalid-format"
    ]
    
    for test_id in test_ids:
        valid = generator.validate_case_id(test_id)
        parsed = generator.parse_case_id(test_id)
        print(f"  {test_id}: Valid={valid}, Source={parsed['source']}") 