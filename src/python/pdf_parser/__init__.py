"""PDF parsing module for extracting structured data from resumes and job descriptions."""

from .parser import (
    PDFParseError,
    ResumeParser,
    ResumeSection,
    extract_contact_info,
    extract_sections,
    generate_yaml_frontmatter,
    parse_education_section,
    parse_experience_section,
    parse_skills_section,
)

__version__ = "0.1.0"

__all__ = [
    "PDFParseError",
    "ResumeParser",
    "ResumeSection",
    "extract_contact_info",
    "extract_sections",
    "generate_yaml_frontmatter",
    "parse_education_section",
    "parse_experience_section",
    "parse_skills_section",
]
