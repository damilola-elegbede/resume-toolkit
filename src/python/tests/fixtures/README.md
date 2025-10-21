# Test Fixtures

This directory contains test data files for the Resume Toolkit test suite.

## Resume PDFs

Place sample resume PDF files here for integration testing:

- `sample_resume.pdf` - Basic single-page resume
- `multipage_resume.pdf` - Multi-page resume example
- `scanned_resume.pdf` - Scanned/image-based resume

## Creating Test PDFs

You can create test PDFs using:

1. Online resume builders (e.g., Canva, Resume.io)
2. Convert markdown to PDF using pandoc:

   ```bash
   pandoc sample_resume.md -o sample_resume.pdf
   ```

3. Export from Google Docs/Microsoft Word

## Privacy Note

Do not commit real resumes with personal information.
Use anonymized or fictional resume data for testing.
