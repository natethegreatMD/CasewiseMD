# Source Documents Directory

This directory contains source documents that can be used to generate rubrics for the Casewise v2 system.

## Directory Structure

```
source-documents/
├── excel-reports/          # Excel files containing case reports
├── other-documents/        # Other document types (PDF, Word, etc.)
└── README.md              # This file
```

## Usage

### Excel Reports
Place Excel files containing case reports in the `excel-reports/` directory. These files should contain:
- Case metadata (patient ID, diagnosis, etc.)
- Detailed case descriptions
- Grading criteria or evaluation points
- Expected findings and keywords

### Other Documents
Place other document types (PDFs, Word documents, etc.) in the `other-documents/` directory.

## Rubric Generation Process

1. **Add Source Document**: Place your Excel file or other document in the appropriate subdirectory
2. **Reference in AI Prompt**: When creating rubrics, reference the source document path
3. **AI Processing**: The AI will analyze the source document to extract:
   - Case-specific criteria
   - Expected keywords
   - Scoring guidelines
   - Clinical rationale
4. **Rubric Creation**: Generate a structured rubric following the established format

## Example Workflow

1. Add `TCGA-case-reports.xlsx` to `excel-reports/`
2. Reference the file when asking the AI to create a rubric
3. AI extracts relevant information and creates a structured rubric
4. Save the generated rubric in the `rubrics/` directory

## File Naming Convention

- Use descriptive names: `TCGA-case-reports.xlsx`, `chest-xray-cases.xlsx`
- Include date if needed: `2024-radiology-cases.xlsx`
- Use underscores for spaces: `pediatric_cases.xlsx`

## Supported Formats

- **Excel**: `.xlsx`, `.xls`
- **PDF**: `.pdf`
- **Word**: `.docx`, `.doc`
- **Text**: `.txt`
- **CSV**: `.csv`

## Notes

- Keep source documents organized by type and date
- Include metadata about the source when possible
- Reference specific rows/sections when creating rubrics
