# Case Generator Templates

This directory contains flexible templates for creating educational medical cases with AI-powered grading and adaptive follow-up questions.

## Overview

The case generator uses two main components:
- **Rubric Templates**: Define grading criteria and weights for different case types
- **Question Templates**: Define the examination questions aligned with rubric categories

## File Structure

```
case generator/
├── rubric-template.json      # Flexible rubric template
├── questions-template.json   # Flexible questions template
├── examples/                 # Sample implementations
│   ├── abr-radiology-rubric.json
│   └── abr-radiology-questions.json
└── README.md                # This file
```

## Quick Start

### Manual Case Creation

1. **Copy Templates**: Copy `rubric-template.json` and `questions-template.json` to your case directory
2. **Fill Placeholders**: Replace all `{{PLACEHOLDER}}` values with case-specific content
3. **Customize Structure**: Add/remove categories and questions as needed
4. **Place Files**: Save as `rubric.json` and `questions.json` in your case directory

### AI-Assisted Case Creation (Future)

The templates are designed to work with AI generation:

```bash
# Future AI workflow
ai-case-generator --case-report "path/to/report.txt" \
                  --images "path/to/dicom/" \
                  --specialty "radiology" \
                  --difficulty "intermediate" \
                  --output "demo_cases/case123/"
```

## Template System

### Rubric Template (`rubric-template.json`)

**Core Placeholders:**
- `{{CASE_ID}}`: Unique case identifier
- `{{CASE_TYPE}}`: Type of case (e.g., "radiology_oral_board")
- `{{SPECIALTY}}`: Medical specialty (e.g., "diagnostic_radiology")
- `{{DIFFICULTY}}`: Difficulty level (beginner/intermediate/advanced)
- `{{DESCRIPTION}}`: Brief description of the case

**Category Structure:**
```json
"{{CATEGORY_NAME}}": {
  "weight": {{WEIGHT}},
  "description": "{{DESCRIPTION}}",
  "criteria": [
    "{{CRITERION_1}}",
    "{{CRITERION_2}}"
  ],
  "key_findings": [
    "{{KEY_FINDING_1}}",
    "{{KEY_FINDING_2}}"
  ],
  "scoring_guide": {
    "excellent": "{{CRITERIA}}",
    "good": "{{CRITERIA}}",
    "needs_improvement": "{{CRITERIA}}"
  }
}
```

### Questions Template (`questions-template.json`)

**Core Placeholders:**
- `{{CASE_ID}}`: Must match rubric case ID
- `{{RUBRIC_ID}}`: References the rubric file
- `{{QUESTION_STYLE}}`: Style of questions (e.g., "abr_oral_board")
- `{{TOTAL_QUESTIONS}}`: Number of questions
- `{{ESTIMATED_TIME}}`: Expected completion time

**Question Structure:**
```json
{
  "step": {{STEP_NUMBER}},
  "rubric_category": "{{CATEGORY}}",
  "question": "{{QUESTION_TEXT}}",
  "type": "{{QUESTION_TYPE}}",
  "context": "{{CONTEXT}}",
  "hint": "{{HINT}}",
  "focus_areas": ["{{FOCUS_1}}", "{{FOCUS_2}}"],
  "difficulty": "{{DIFFICULTY}}",
  "expected_elements": ["{{ELEMENT_1}}", "{{ELEMENT_2}}"]
}
```

## Question Types

- **`free_text`**: Open-ended response (most common)
- **`multiple_choice`**: Select from options
- **`ranking`**: Rank options in order
- **`short_answer`**: Brief specific response
- **`case_presentation`**: Structured case presentation

## Rubric Categories

### Standard ABR Radiology Categories:
1. **Image Interpretation** (35%) - Systematic evaluation of imaging
2. **Differential Diagnosis** (25%) - Appropriate differential formulation
3. **Clinical Correlation** (15%) - Integration with clinical presentation
4. **Management Recommendations** (10%) - Next steps and follow-up
5. **Communication & Organization** (10%) - Professional presentation
6. **Professional Judgment** (5%) - Critical findings and ethics

### Customizable Categories:
- Adjust weights based on case focus
- Add specialty-specific categories
- Include procedure-specific criteria
- Modify for different examination styles

## AI Generation Compatibility

The template system is designed for AI-assisted case creation:

### Input Requirements:
- **Case Report**: Clinical history, findings, diagnosis
- **DICOM Metadata**: Patient demographics, imaging parameters
- **Specialty Focus**: Target medical specialty
- **Difficulty Level**: Appropriate for learner level

### AI Processing Steps:
1. **Analysis**: Parse case report and extract key information
2. **Category Mapping**: Determine relevant rubric categories
3. **Question Generation**: Create case-specific questions
4. **Rubric Customization**: Adjust weights and criteria
5. **Follow-up Seeds**: Generate targeted follow-up questions

### Template Advantages for AI:
- **Structured Format**: Clear JSON structure for AI parsing
- **Flexible Placeholders**: Easy text replacement
- **Comprehensive Metadata**: Rich context for AI decisions
- **Consistent Schema**: Standardized format across cases

## Best Practices

### Case Creation Guidelines:

1. **Start with Examples**: Review provided examples for your specialty
2. **Align Questions with Rubric**: Ensure 1:1 mapping between questions and categories
3. **Progressive Difficulty**: Order questions from basic to advanced
4. **Clear Instructions**: Provide specific context and hints
5. **Realistic Expectations**: Set appropriate expected elements

### Quality Assurance:

- **Content Review**: Have subject matter experts review generated content
- **Pilot Testing**: Test with small groups before full deployment
- **Iterative Improvement**: Refine based on student feedback
- **Performance Tracking**: Monitor grading accuracy and student outcomes

## Advanced Features

### Follow-up Question Seeds:
Pre-defined prompts for weak areas help AI generate targeted follow-up questions:

```json
"follow_up_question_seeds": {
  "weak_image_interpretation": [
    "Can you describe the specific imaging characteristics?",
    "What systematic approach did you use?"
  ],
  "weak_differential": [
    "What imaging features helped prioritize your differential?",
    "Are there other conditions to consider?"
  ]
}
```

### Adaptive Difficulty:
Questions can be tagged with difficulty levels for adaptive learning:

```json
"difficulty": "intermediate",
"expected_elements": [
  "Basic understanding required",
  "Intermediate analysis expected"
]
```

## Integration with Casewise VPS

### File Placement:
```
demo_cases/
├── case001/
│   ├── rubric.json          # Generated from template
│   ├── questions.json       # Generated from template
│   ├── metadata.json        # DICOM metadata
│   └── images/              # DICOM files
```

### System Integration:
- **Diagnostic Agent**: Loads questions.json for case presentation
- **Grading Agent**: Uses rubric.json for AI-powered assessment
- **Follow-up Generator**: Creates targeted questions for weak areas

## Future Enhancements

### Planned Features:
- **Multi-language Support**: Templates for different languages
- **Specialty Packs**: Pre-configured templates for common specialties
- **Difficulty Adaptation**: Dynamic difficulty adjustment
- **Learning Analytics**: Performance tracking and improvement suggestions

### AI Improvements:
- **Case Similarity Analysis**: Avoid duplicate cases
- **Difficulty Calibration**: Automatic difficulty assessment
- **Learning Outcome Prediction**: Predict student performance
- **Personalized Question Generation**: Adapt to individual learning styles

## Template Validation

### Required Fields:
- All `{{PLACEHOLDER}}` values must be replaced
- Weights must sum to 100 in rubric
- Questions must map to rubric categories
- JSON must be valid and well-formed

### Testing:
```bash
# Validate JSON structure
python -m json.tool rubric.json
python -m json.tool questions.json

# Test with system
curl -X GET "http://localhost:8000/diagnostic-session?case_id=your_case"
```

## Support and Documentation

For questions or issues:
- Review examples in `examples/` directory
- Check system logs for validation errors
- Consult main project documentation
- Test with simple cases first

---

**Template Version:** 2.0  
**Compatible with:** Casewise VPS v2.0+  
**Last Updated:** 2024-12-25 