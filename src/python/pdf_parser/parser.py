"""
PDF Resume Parser - Extract structured data from resume PDFs.

This module provides functionality to:
- Extract text from PDF resumes
- Identify sections (Experience, Education, Skills, etc.)
- Parse contact information
- Generate YAML frontmatter and markdown output
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import pdfplumber


class ResumeSection(str, Enum):
    """Standard resume section identifiers."""

    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    PUBLICATIONS = "publications"


class PDFParseError(Exception):
    """Custom exception for PDF parsing errors."""



@dataclass
class ResumeData:
    """Structured resume data."""

    contact_info: dict[str, Any] = field(default_factory=dict)
    sections: dict[ResumeSection, str] = field(default_factory=dict)
    raw_text: str = ""


def extract_contact_info(text: str) -> dict[str, Any]:
    """
    Extract contact information from resume text.

    Args:
        text: Resume text content

    Returns:
        Dictionary containing name, title, email, phone, linkedin, github, etc.
    """
    contact_info: dict[str, Any] = {}

    # Extract email
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    email_match = re.search(email_pattern, text)
    if email_match:
        contact_info["email"] = email_match.group(0)

    # Extract phone number (various formats)
    phone_patterns = [
        r"\(\d{3}\)\s*\d{3}-\d{4}",  # (555) 123-4567
        r"\+?\d{1}-\d{3}-\d{3}-\d{4}",  # +1-555-123-4567
        r"\d{3}-\d{3}-\d{4}",  # 555-123-4567
        r"\+?\d{1,3}[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}",  # Various
    ]
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            contact_info["phone"] = phone_match.group(0)
            break

    # Extract LinkedIn
    linkedin_pattern = r"linkedin\.com/in/[\w-]+"
    linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
    if linkedin_match:
        contact_info["linkedin"] = linkedin_match.group(0)

    # Extract GitHub
    github_pattern = r"github\.com/[\w-]+"
    github_match = re.search(github_pattern, text, re.IGNORECASE)
    if github_match:
        contact_info["github"] = github_match.group(0)

    # Extract name and title from first few lines
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if lines:
        # First non-empty line is typically the name
        contact_info["name"] = lines[0]

        # Second line might be title (if it doesn't contain contact info)
        if len(lines) > 1:
            second_line = lines[1]
            # Check if it's not a contact line
            if (
                "@" not in second_line
                and not re.search(r"\d{3}", second_line)
                and "linkedin" not in second_line.lower()
                and "github" not in second_line.lower()
            ):
                contact_info["title"] = second_line

    return contact_info


def extract_sections(text: str) -> dict[ResumeSection, str]:
    """
    Identify and extract resume sections from text.

    Args:
        text: Resume text content

    Returns:
        Dictionary mapping section types to their content
    """
    sections: dict[ResumeSection, str] = {}

    # Define section header patterns
    section_patterns = {
        ResumeSection.SUMMARY: r"\b(SUMMARY|PROFESSIONAL SUMMARY|PROFILE|OBJECTIVE)\b",
        ResumeSection.EXPERIENCE: r"\b(EXPERIENCE|WORK EXPERIENCE|EMPLOYMENT|PROFESSIONAL EXPERIENCE)\b",
        ResumeSection.EDUCATION: r"\b(EDUCATION|ACADEMIC BACKGROUND)\b",
        ResumeSection.SKILLS: r"\b(SKILLS|TECHNICAL SKILLS|CORE COMPETENCIES)\b",
        ResumeSection.PROJECTS: r"\b(PROJECTS|PORTFOLIO)\b",
        ResumeSection.CERTIFICATIONS: r"\b(CERTIFICATIONS|CERTIFICATES|LICENSES)\b",
        ResumeSection.PUBLICATIONS: r"\b(PUBLICATIONS|RESEARCH)\b",
    }

    # Find all section headers with their positions
    section_positions: list[tuple[int, ResumeSection, str]] = []

    for section_type, pattern in section_patterns.items():
        for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
            section_positions.append((match.start(), section_type, match.group(0)))

    # Sort by position
    section_positions.sort(key=lambda x: x[0])

    # Extract content between sections
    for i, (pos, section_type, header) in enumerate(section_positions):
        # Find the start of content (after the header line)
        start = pos
        # Find end of this line
        line_end = text.find("\n", start)
        if line_end == -1:
            line_end = len(text)
        content_start = line_end + 1

        # Find the end of this section (start of next section or end of text)
        if i < len(section_positions) - 1:
            content_end = section_positions[i + 1][0]
        else:
            content_end = len(text)

        # Extract and clean content
        content = text[content_start:content_end].strip()
        sections[section_type] = content

    return sections


def parse_experience_section(text: str) -> list[dict[str, Any]]:
    """
    Parse experience section into structured entries.

    Args:
        text: Experience section content

    Returns:
        List of experience entries with title, company, dates, responsibilities
    """
    experiences: list[dict[str, Any]] = []

    # Pattern to match job entries: Title | Company | Dates
    # or: Title, Company (Dates)
    # or: Title at Company (Dates)
    entry_pattern = r"^(.+?)\s*[|]\s*(.+?)\s*[|]\s*(.+?)$"

    lines = text.split("\n")
    current_entry: dict[str, Any] | None = None
    responsibilities: list[str] = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if this is a new job entry
        match = re.match(entry_pattern, line)
        if match:
            # Save previous entry if exists
            if current_entry:
                current_entry["responsibilities"] = responsibilities
                experiences.append(current_entry)
                responsibilities = []

            title, company, dates = match.groups()

            # Parse dates
            date_parts = dates.split("-")
            start_date = date_parts[0].strip() if date_parts else ""
            end_date = date_parts[1].strip() if len(date_parts) > 1 else ""

            current_entry = {
                "title": title.strip(),
                "company": company.strip(),
                "start_date": start_date,
                "end_date": end_date,
                "responsibilities": [],
            }
        elif line.startswith("•") or line.startswith("-") or line.startswith("*"):
            # This is a responsibility bullet point
            bullet_text = re.sub(r"^[•\-*]\s*", "", line)
            responsibilities.append(bullet_text)

    # Don't forget the last entry
    if current_entry:
        current_entry["responsibilities"] = responsibilities
        experiences.append(current_entry)

    return experiences


def parse_education_section(text: str) -> list[dict[str, Any]]:
    """
    Parse education section into structured entries.

    Args:
        text: Education section content

    Returns:
        List of education entries with degree, institution, dates, GPA
    """
    education: list[dict[str, Any]] = []

    # Pattern: Degree | Institution | Dates
    # or: Degree, Institution (Dates)
    entry_pattern = r"^(.+?)\s*[|]\s*(.+?)\s*[|]\s*(.+?)$"

    lines = text.split("\n")
    current_entry: dict[str, Any] | None = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if this is an education entry
        match = re.match(entry_pattern, line)
        if match:
            degree, institution, dates = match.groups()

            # Parse years
            years = re.findall(r"\d{4}", dates)
            start_year = years[0] if years else ""
            end_year = years[1] if len(years) > 1 else ""

            current_entry = {
                "degree": degree.strip(),
                "institution": institution.strip(),
                "start_year": start_year,
                "end_year": end_year,
                "gpa": None,
            }
            education.append(current_entry)
        elif current_entry and "gpa" in line.lower():
            # Extract GPA
            gpa_match = re.search(r"(\d+\.\d+/\d+\.\d+)", line)
            if gpa_match:
                current_entry["gpa"] = gpa_match.group(1)

    return education


def parse_skills_section(text: str) -> dict[str, list[str]]:
    """
    Parse skills section into categorized or flat list.

    Args:
        text: Skills section content

    Returns:
        Dictionary of skill categories to skill lists
    """
    skills: dict[str, list[str]] = {}

    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for categorized format: "Category: skill1, skill2"
        if ":" in line:
            parts = line.split(":", 1)
            category = parts[0].strip()
            skills_text = parts[1].strip()

            # Split by comma or other separators
            skill_list = [s.strip() for s in re.split(r"[,;]", skills_text) if s.strip()]
            skills[category] = skill_list
        else:
            # Uncategorized skills
            if "general" not in skills:
                skills["general"] = []

            # Split by comma
            skill_list = [s.strip() for s in re.split(r"[,;]", line) if s.strip()]
            skills["general"].extend(skill_list)

    return skills


def generate_yaml_frontmatter(contact_info: dict[str, Any]) -> str:
    """
    Generate YAML frontmatter from contact information.

    Args:
        contact_info: Dictionary of contact details

    Returns:
        YAML frontmatter string
    """
    yaml_lines = ["---"]

    # Add fields in a specific order
    field_order = [
        "name",
        "title",
        "email",
        "phone",
        "linkedin",
        "github",
        "website",
        "location",
    ]

    for field in field_order:
        value = contact_info.get(field)
        if value is not None and value != "":
            yaml_lines.append(f"{field}: {value}")

    # Add any additional fields not in the standard order
    for key, value in contact_info.items():
        if key not in field_order and value is not None and value != "":
            yaml_lines.append(f"{key}: {value}")

    yaml_lines.append("---")
    return "\n".join(yaml_lines)


class ResumeParser:
    """Main parser class for converting PDF resumes to structured markdown."""

    def __init__(self) -> None:
        """Initialize the resume parser."""

    def parse_text(self, text: str) -> dict[str, Any]:
        """
        Parse resume text into structured data.

        Args:
            text: Resume text content

        Returns:
            Dictionary with frontmatter and parsed content
        """
        contact_info = extract_contact_info(text)
        sections = extract_sections(text)

        frontmatter = generate_yaml_frontmatter(contact_info)

        return {
            "frontmatter": frontmatter,
            "contact_info": contact_info,
            "sections": sections,
            "content": text,
        }

    def parse_pdf(self, pdf_path: Path) -> dict[str, Any]:
        """
        Parse a PDF resume file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with parsed resume data

        Raises:
            PDFParseError: If PDF cannot be parsed
        """
        if not pdf_path.exists():
            raise PDFParseError(f"PDF file not found: {pdf_path}")

        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract text from all pages
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

                if not text_parts:
                    raise PDFParseError("No text content found in PDF")

                full_text = "\n\n".join(text_parts)
                return self.parse_text(full_text)

        except PDFParseError:
            raise
        except Exception as e:
            raise PDFParseError(f"Failed to parse PDF: {e}") from e

    def to_markdown(self, text: str) -> str:
        """
        Convert resume text to markdown format with YAML frontmatter.

        Args:
            text: Resume text content

        Returns:
            Markdown formatted resume
        """
        result = self.parse_text(text)
        sections = result["sections"]

        markdown_parts = [result["frontmatter"], ""]

        # Add sections in standard order
        section_order = [
            (ResumeSection.SUMMARY, "Summary"),
            (ResumeSection.EXPERIENCE, "Experience"),
            (ResumeSection.PROJECTS, "Projects"),
            (ResumeSection.EDUCATION, "Education"),
            (ResumeSection.SKILLS, "Skills"),
            (ResumeSection.CERTIFICATIONS, "Certifications"),
            (ResumeSection.PUBLICATIONS, "Publications"),
        ]

        for section_type, section_title in section_order:
            if section_type in sections:
                markdown_parts.append(f"## {section_title}")
                markdown_parts.append("")

                content = sections[section_type]

                # Parse and format based on section type
                if section_type == ResumeSection.EXPERIENCE:
                    experiences = parse_experience_section(content)
                    for exp in experiences:
                        markdown_parts.append(
                            f"### {exp['title']} | {exp['company']}"
                        )
                        markdown_parts.append(
                            f"*{exp['start_date']} - {exp['end_date']}*"
                        )
                        markdown_parts.append("")
                        for resp in exp["responsibilities"]:
                            markdown_parts.append(f"- {resp}")
                        markdown_parts.append("")

                elif section_type == ResumeSection.EDUCATION:
                    education_entries = parse_education_section(content)
                    for edu in education_entries:
                        markdown_parts.append(
                            f"### {edu['degree']} | {edu['institution']}"
                        )
                        if edu["start_year"] and edu["end_year"]:
                            markdown_parts.append(
                                f"*{edu['start_year']} - {edu['end_year']}*"
                            )
                        if edu.get("gpa"):
                            markdown_parts.append(f"GPA: {edu['gpa']}")
                        markdown_parts.append("")

                elif section_type == ResumeSection.SKILLS:
                    skills_data = parse_skills_section(content)
                    for category, skills in skills_data.items():
                        if category != "general":
                            markdown_parts.append(f"**{category}:** {', '.join(skills)}")
                        else:
                            markdown_parts.append(f"{', '.join(skills)}")
                    markdown_parts.append("")

                else:
                    # For other sections, just add the raw content
                    markdown_parts.append(content)
                    markdown_parts.append("")

        return "\n".join(markdown_parts)

    def parse_and_save(self, pdf_path: Path, output_path: Path) -> None:
        """
        Parse PDF resume and save as markdown.

        Args:
            pdf_path: Path to input PDF file
            output_path: Path to output markdown file
        """
        result = self.parse_pdf(pdf_path)
        markdown = self.to_markdown(result["content"])

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
