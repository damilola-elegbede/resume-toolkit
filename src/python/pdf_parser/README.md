# PDF Resume Parser

Convert PDF resumes into structured markdown format with YAML frontmatter.

## Features

- **Text Extraction**: Extract text from PDF resumes using pdfplumber
- **Section Detection**: Automatically identify standard resume sections:
  - Professional Summary
  - Work Experience
  - Education
  - Technical Skills
  - Projects
  - Certifications
  - Publications
- **Contact Info Extraction**: Parse name, email, phone, LinkedIn, GitHub
- **Structured Parsing**: Convert experience and education into structured data
- **YAML Frontmatter**: Generate metadata for easy querying
- **Markdown Output**: Clean, readable markdown format

## Installation

```bash
pip install -r requirements.txt
```

Required packages:

- pdfplumber
- pydantic

## Usage

### Python Module

```python
from pdf_parser import ResumeParser

parser = ResumeParser()

# Parse PDF file
result = parser.parse_pdf("resume.pdf")

# Generate markdown
markdown = parser.to_markdown(result["content"])

# Save to file
parser.parse_and_save("resume.pdf", "resume.md")
```

### Command Line

```bash
# Using Python module
PYTHONPATH=src/python python -m pdf_parser.cli resume.pdf output.md

# Using TypeScript CLI (recommended)
npm run dev parse-resume resume.pdf
```

### CLI Integration

```bash
resume-toolkit parse-resume <pdf-file> [--output <path>] [--verbose]
```

## Output Format

The parser generates markdown with YAML frontmatter:

```markdown
---
name: John Doe
title: Senior Software Engineer
email: john@example.com
phone: (555) 123-4567
linkedin: linkedin.com/in/johndoe
github: github.com/johndoe
---

## Summary

Experienced software engineer with 8+ years...

## Experience

### Senior Software Engineer | Tech Corp

*Jan 2020 - Present*

- Led development of microservices architecture
- Improved system performance by 40%

## Education

### Bachelor of Science in Computer Science | University of Technology

*2013 - 2017*
GPA: 3.8/4.0

## Skills

**Languages:** Python, TypeScript, JavaScript
**Frameworks:** Django, FastAPI, React
```

## Architecture

### Core Components

1. **Text Extraction** (`extract_text`)

   - Uses pdfplumber to extract text from PDF pages
   - Handles multi-page documents
   - Detects and warns about scanned PDFs

2. **Section Identification** (`extract_sections`)

   - Pattern matching for standard resume sections
   - Case-insensitive header detection
   - Flexible section boundary detection

3. **Contact Info Parser** (`extract_contact_info`)

   - Regex patterns for email, phone, URLs
   - Name and title extraction from header
   - Social profile link detection

4. **Experience Parser** (`parse_experience_section`)

   - Extracts job title, company, dates
   - Parses responsibility bullet points
   - Handles various date formats

5. **Education Parser** (`parse_education_section`)

   - Degree and institution extraction
   - Date parsing
   - GPA detection

6. **Skills Parser** (`parse_skills_section`)

   - Categorized skill groups
   - Comma/semicolon separated lists
   - Flat and nested formats

7. **YAML Generator** (`generate_yaml_frontmatter`)
   - Structured metadata output
   - Field ordering
   - None value filtering

### Data Flow

```
PDF File
  ↓
pdfplumber (text extraction)
  ↓
Raw Text
  ↓
extract_contact_info() → Contact Data
extract_sections() → Section Map
  ↓
parse_experience_section() → Structured Experience
parse_education_section() → Structured Education
parse_skills_section() → Categorized Skills
  ↓
generate_yaml_frontmatter() → YAML Header
to_markdown() → Formatted Sections
  ↓
Final Markdown Document
```

## Testing

### Run Tests

```bash
# All tests
pytest src/python/tests/test_pdf_parser.py -v

# Unit tests only
pytest src/python/tests/test_pdf_parser.py -v -m unit

# With coverage
pytest src/python/tests/test_pdf_parser.py --cov=src/python/pdf_parser --cov-report=term-missing
```

### Test Coverage

Current coverage: **91.74%**

- Contact info extraction: ✓
- Section identification: ✓
- Experience parsing: ✓
- Education parsing: ✓
- Skills parsing: ✓
- YAML frontmatter: ✓
- Error handling: ✓

### Test Fixtures

Place sample PDFs in `src/python/tests/fixtures/`:

- `sample_resume.pdf` - Basic single-page resume
- `multipage_resume.pdf` - Multi-page example
- `scanned_resume.pdf` - Image-based PDF

## Limitations

- **Scanned PDFs**: Image-based PDFs require OCR (not included)
- **Format Variations**: Works best with standard resume formats
- **Complex Layouts**: Multi-column layouts may have extraction issues
- **Tables**: Complex tables might not parse perfectly

## Error Handling

The parser includes robust error handling:

```python
try:
    parser = ResumeParser()
    result = parser.parse_pdf("resume.pdf")
except PDFParseError as e:
    print(f"Failed to parse PDF: {e}")
```

Common errors:

- **File not found**: PDF path is invalid
- **Invalid PDF**: File is corrupted or not a valid PDF
- **No text found**: PDF is image-based (needs OCR)

## Future Enhancements

- [ ] OCR support for scanned PDFs
- [ ] Multi-column layout detection
- [ ] Table extraction
- [ ] Multi-language support
- [ ] Custom section detection
- [ ] PDF quality validation
- [ ] Confidence scoring for extracted data

## Contributing

When adding features:

1. Write tests first (TDD)
2. Ensure test coverage > 90%
3. Update type hints
4. Run linters: `ruff check`, `mypy`
5. Update documentation

## License

MIT
