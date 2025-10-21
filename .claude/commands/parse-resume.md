---
description: Convert PDF resume to structured markdown template
---

# Parse Resume Command

Extract structured resume data from PDF and save as markdown with YAML frontmatter.

## Usage

```bash
/parse-resume <pdf-path>
```

## Example

```bash
/parse-resume ~/Downloads/resume.pdf
```

## What it does

1. Extracts text from PDF resume using pdfplumber
2. Identifies sections (Summary, Experience, Education, Skills, etc.)
3. Extracts contact information (name, email, phone, LinkedIn, GitHub)
4. Parses experience entries with dates, companies, and responsibilities
5. Parses education with degrees, institutions, and dates
6. Categorizes skills
7. Generates YAML frontmatter with metadata
8. Outputs structured markdown to `.resume-toolkit/base-resume.md`

## Output Format

The generated markdown file includes:

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

### Software Engineer | StartupXYZ
*Jun 2017 - Dec 2019*

- Built REST APIs using Python/Django
- Implemented CI/CD pipeline

## Education

### Bachelor of Science in Computer Science | University of Technology
*2013 - 2017*
GPA: 3.8/4.0

## Skills

**Languages:** Python, TypeScript, JavaScript, Go, SQL
**Frameworks:** Django, FastAPI, React, Node.js
**Tools:** Docker, Kubernetes, AWS, PostgreSQL
```

## Requirements

- Python 3.11+ with venv activated
- pdfplumber package installed: `pip install -r requirements.txt`
- Valid PDF resume file

## Notes

- The command creates `.resume-toolkit/` directory if it doesn't exist
- You can customize the output path with `--output` option
- Scanned PDFs (images) may have limited text extraction quality
- Review and edit the generated markdown for accuracy
