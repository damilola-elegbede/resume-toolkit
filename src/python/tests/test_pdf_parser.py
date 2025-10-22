"""
Test suite for PDF resume parser.

Tests cover:
- PDF text extraction
- Section identification
- YAML frontmatter generation
- Personal information extraction
- Error handling
"""

from pathlib import Path

import pytest
from pdf_parser.parser import (
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


@pytest.fixture
def sample_resume_text() -> str:
    """Sample resume text for testing."""
    return """
John Doe
Senior Software Engineer
john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe | github.com/johndoe

PROFESSIONAL SUMMARY
Experienced software engineer with 8+ years building scalable systems.
Expertise in Python, TypeScript, and cloud infrastructure.

EXPERIENCE

Senior Software Engineer | Tech Corp | Jan 2020 - Present
• Led development of microservices architecture serving 10M+ users
• Improved system performance by 40% through optimization
• Mentored team of 5 junior engineers

Software Engineer | StartupXYZ | Jun 2017 - Dec 2019
• Built REST APIs using Python/Django and PostgreSQL
• Implemented CI/CD pipeline reducing deployment time by 60%
• Collaborated with cross-functional teams on product features

EDUCATION

Bachelor of Science in Computer Science | University of Technology | 2013 - 2017
GPA: 3.8/4.0

TECHNICAL SKILLS
Languages: Python, TypeScript, JavaScript, Go, SQL
Frameworks: Django, FastAPI, React, Node.js
Tools: Docker, Kubernetes, AWS, PostgreSQL, Redis
"""


@pytest.fixture
def sample_resume_with_projects() -> str:
    """Sample resume with projects section."""
    return """
Jane Smith
Data Scientist
jane.smith@email.com | +1-555-987-6543

SUMMARY
Data scientist specializing in ML and analytics.

PROJECTS

ML Pipeline Framework | 2023
• Built automated ML pipeline reducing model training time by 70%
• Technologies: Python, TensorFlow, Kubernetes

EXPERIENCE

Data Scientist | AI Company | 2021 - Present
• Developed recommendation system improving user engagement by 25%

EDUCATION

Master of Science in Data Science | MIT | 2019 - 2021

SKILLS
Python, TensorFlow, PyTorch, Pandas, SQL
"""


@pytest.mark.unit
class TestContactInfoExtraction:
    """Test extraction of contact information from resume text."""

    def test_extract_email(self, sample_resume_text: str) -> None:
        """Test email extraction."""
        contact_info = extract_contact_info(sample_resume_text)
        assert contact_info["email"] == "john.doe@email.com"

    def test_extract_phone(self, sample_resume_text: str) -> None:
        """Test phone number extraction."""
        contact_info = extract_contact_info(sample_resume_text)
        assert contact_info["phone"] == "(555) 123-4567"

    def test_extract_linkedin(self, sample_resume_text: str) -> None:
        """Test LinkedIn URL extraction."""
        contact_info = extract_contact_info(sample_resume_text)
        assert contact_info["linkedin"] == "linkedin.com/in/johndoe"

    def test_extract_github(self, sample_resume_text: str) -> None:
        """Test GitHub URL extraction."""
        contact_info = extract_contact_info(sample_resume_text)
        assert contact_info["github"] == "github.com/johndoe"

    def test_extract_name_and_title(self, sample_resume_text: str) -> None:
        """Test name and title extraction from header."""
        contact_info = extract_contact_info(sample_resume_text)
        assert contact_info["name"] == "John Doe"
        assert contact_info["title"] == "Senior Software Engineer"

    def test_missing_contact_info(self) -> None:
        """Test handling of missing contact information."""
        minimal_text = "John Doe\nSoftware Engineer"
        contact_info = extract_contact_info(minimal_text)
        assert contact_info["name"] == "John Doe"
        assert contact_info.get("email") is None
        assert contact_info.get("phone") is None


@pytest.mark.unit
class TestSectionExtraction:
    """Test identification and extraction of resume sections."""

    def test_identify_experience_section(self, sample_resume_text: str) -> None:
        """Test identification of experience section."""
        sections = extract_sections(sample_resume_text)
        assert ResumeSection.EXPERIENCE in sections
        assert "Tech Corp" in sections[ResumeSection.EXPERIENCE]
        assert "StartupXYZ" in sections[ResumeSection.EXPERIENCE]

    def test_identify_education_section(self, sample_resume_text: str) -> None:
        """Test identification of education section."""
        sections = extract_sections(sample_resume_text)
        assert ResumeSection.EDUCATION in sections
        assert "University of Technology" in sections[ResumeSection.EDUCATION]

    def test_identify_skills_section(self, sample_resume_text: str) -> None:
        """Test identification of skills section."""
        sections = extract_sections(sample_resume_text)
        assert ResumeSection.SKILLS in sections
        assert "Python" in sections[ResumeSection.SKILLS]

    def test_identify_summary_section(self, sample_resume_text: str) -> None:
        """Test identification of summary section."""
        sections = extract_sections(sample_resume_text)
        assert ResumeSection.SUMMARY in sections
        assert "8+ years" in sections[ResumeSection.SUMMARY]

    def test_identify_projects_section(self, sample_resume_with_projects: str) -> None:
        """Test identification of projects section."""
        sections = extract_sections(sample_resume_with_projects)
        assert ResumeSection.PROJECTS in sections
        assert "ML Pipeline Framework" in sections[ResumeSection.PROJECTS]

    def test_case_insensitive_section_headers(self) -> None:
        """Test that section headers are matched case-insensitively."""
        text_lower = "experience\nSoftware Engineer | Company | 2020-2021"
        sections = extract_sections(text_lower)
        assert ResumeSection.EXPERIENCE in sections


@pytest.mark.unit
class TestExperienceParsing:
    """Test parsing of experience section into structured data."""

    def test_parse_experience_entries(self, sample_resume_text: str) -> None:
        """Test parsing multiple experience entries."""
        sections = extract_sections(sample_resume_text)
        experience_data = parse_experience_section(sections[ResumeSection.EXPERIENCE])

        assert len(experience_data) == 2
        assert experience_data[0]["title"] == "Senior Software Engineer"
        assert experience_data[0]["company"] == "Tech Corp"
        assert experience_data[1]["company"] == "StartupXYZ"

    def test_parse_experience_dates(self, sample_resume_text: str) -> None:
        """Test extraction of employment dates."""
        sections = extract_sections(sample_resume_text)
        experience_data = parse_experience_section(sections[ResumeSection.EXPERIENCE])

        assert experience_data[0]["start_date"] == "Jan 2020"
        assert experience_data[0]["end_date"] == "Present"
        assert experience_data[1]["start_date"] == "Jun 2017"
        assert experience_data[1]["end_date"] == "Dec 2019"

    def test_parse_experience_responsibilities(self, sample_resume_text: str) -> None:
        """Test extraction of bullet points/responsibilities."""
        sections = extract_sections(sample_resume_text)
        experience_data = parse_experience_section(sections[ResumeSection.EXPERIENCE])

        assert len(experience_data[0]["responsibilities"]) == 3
        assert "microservices" in experience_data[0]["responsibilities"][0].lower()


@pytest.mark.unit
class TestEducationParsing:
    """Test parsing of education section."""

    def test_parse_education_degree(self, sample_resume_text: str) -> None:
        """Test extraction of degree information."""
        sections = extract_sections(sample_resume_text)
        education_data = parse_education_section(sections[ResumeSection.EDUCATION])

        assert len(education_data) == 1
        assert education_data[0]["degree"] == "Bachelor of Science in Computer Science"
        assert education_data[0]["institution"] == "University of Technology"

    def test_parse_education_dates(self, sample_resume_text: str) -> None:
        """Test extraction of education dates."""
        sections = extract_sections(sample_resume_text)
        education_data = parse_education_section(sections[ResumeSection.EDUCATION])

        assert education_data[0]["start_year"] == "2013"
        assert education_data[0]["end_year"] == "2017"

    def test_parse_education_gpa(self, sample_resume_text: str) -> None:
        """Test extraction of GPA."""
        sections = extract_sections(sample_resume_text)
        education_data = parse_education_section(sections[ResumeSection.EDUCATION])

        assert education_data[0]["gpa"] == "3.8/4.0"


@pytest.mark.unit
class TestSkillsParsing:
    """Test parsing of skills section."""

    def test_parse_categorized_skills(self, sample_resume_text: str) -> None:
        """Test parsing of categorized skills."""
        sections = extract_sections(sample_resume_text)
        skills_data = parse_skills_section(sections[ResumeSection.SKILLS])

        assert "Languages" in skills_data
        assert "Python" in skills_data["Languages"]
        assert "TypeScript" in skills_data["Languages"]

        assert "Frameworks" in skills_data
        assert "Django" in skills_data["Frameworks"]

    def test_parse_uncategorized_skills(self) -> None:
        """Test parsing of flat skill lists."""
        skills_text = "Python, JavaScript, Docker, AWS, PostgreSQL"
        skills_data = parse_skills_section(skills_text)

        assert "general" in skills_data
        assert "Python" in skills_data["general"]
        assert len(skills_data["general"]) == 5


@pytest.mark.unit
class TestYAMLFrontmatter:
    """Test YAML frontmatter generation."""

    def test_generate_frontmatter_basic(self) -> None:
        """Test basic frontmatter generation."""
        contact_info = {
            "name": "John Doe",
            "title": "Software Engineer",
            "email": "john@email.com",
            "phone": "(555) 123-4567",
        }
        yaml = generate_yaml_frontmatter(contact_info)

        assert "---" in yaml
        assert "name: John Doe" in yaml
        assert "title: Software Engineer" in yaml
        assert "email: john@email.com" in yaml

    def test_generate_frontmatter_with_links(self) -> None:
        """Test frontmatter with social links."""
        contact_info = {
            "name": "Jane Smith",
            "linkedin": "linkedin.com/in/janesmith",
            "github": "github.com/janesmith",
        }
        yaml = generate_yaml_frontmatter(contact_info)

        assert "linkedin: linkedin.com/in/janesmith" in yaml
        assert "github: github.com/janesmith" in yaml

    def test_generate_frontmatter_handles_none_values(self) -> None:
        """Test that None values are omitted from frontmatter."""
        contact_info = {
            "name": "John Doe",
            "email": None,
            "phone": None,
        }
        yaml = generate_yaml_frontmatter(contact_info)

        assert "name: John Doe" in yaml
        assert "email:" not in yaml
        assert "phone:" not in yaml


@pytest.mark.unit
class TestResumeParser:
    """Test the main ResumeParser class."""

    def test_parser_initialization(self) -> None:
        """Test parser can be initialized."""
        parser = ResumeParser()
        assert parser is not None

    def test_parse_from_text(self, sample_resume_text: str) -> None:
        """Test parsing from plain text."""
        parser = ResumeParser()
        result = parser.parse_text(sample_resume_text)

        assert "frontmatter" in result
        assert "content" in result
        assert "John Doe" in result["frontmatter"]

    def test_parse_generates_markdown(self, sample_resume_text: str) -> None:
        """Test that parser generates valid markdown output."""
        parser = ResumeParser()
        markdown = parser.to_markdown(sample_resume_text)

        assert markdown.startswith("---")
        assert "## Experience" in markdown or "## EXPERIENCE" in markdown
        assert "## Education" in markdown or "## EDUCATION" in markdown

    def test_parse_pdf_file_not_found(self) -> None:
        """Test error handling for missing PDF file."""
        parser = ResumeParser()

        with pytest.raises(PDFParseError, match="not found"):
            parser.parse_pdf(Path("/nonexistent/file.pdf"))

    def test_parse_invalid_pdf(self, tmp_path: Path) -> None:
        """Test error handling for invalid PDF."""
        parser = ResumeParser()
        invalid_pdf = tmp_path / "invalid.pdf"
        invalid_pdf.write_text("This is not a PDF")

        with pytest.raises(PDFParseError, match="Failed to parse PDF"):
            parser.parse_pdf(invalid_pdf)


@pytest.mark.integration
class TestPDFExtraction:
    """Integration tests for PDF extraction (requires pdfplumber)."""

    def test_extract_text_from_valid_pdf(self, sample_resume_pdf: Path) -> None:
        """Test text extraction from a valid PDF."""
        from pdf_parser.parser import ResumeParser

        parser = ResumeParser()
        result = parser.parse_pdf(sample_resume_pdf)

        # Verify expected content is present
        content = result.get("content", "")
        assert "John Doe" in content
        assert "john.doe@email.com" in content
        assert "Senior Software Engineer" in content
        assert "TechCorp Inc" in content or "TechCorp" in content

    def test_parse_multipage_resume(self, multipage_resume_pdf: Path) -> None:
        """Test parsing of multi-page resume PDF."""
        from pdf_parser.parser import ResumeParser
        import pdfplumber

        # Verify it's actually multi-page
        with pdfplumber.open(multipage_resume_pdf) as pdf:
            assert len(pdf.pages) == 2

        # Parse the resume
        parser = ResumeParser()
        result = parser.parse_pdf(multipage_resume_pdf)
        content = result.get("content", "")

        # Verify content from both pages
        assert "Jane Smith" in content
        assert "Position 1" in content  # From page 1
        assert "Ph.D" in content or "PhD" in content  # From page 2

    def test_handle_scanned_pdf_warning(self, scanned_resume_pdf: Path) -> None:
        """Test that scanned PDFs (images) are detected and handled."""
        from pdf_parser.parser import ResumeParser, PDFParseError

        parser = ResumeParser()

        # Scanned PDFs should either raise an error or return minimal text
        try:
            result = parser.parse_pdf(scanned_resume_pdf)
            content = result.get("content", "")
            # If it doesn't raise an error, it should have very little text
            assert len(content.strip()) < 100  # Should be mostly empty
        except PDFParseError as e:
            # Or it should raise an error about no text content
            assert "No text content" in str(e)


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_text(self) -> None:
        """Test handling of empty text."""
        parser = ResumeParser()
        result = parser.parse_text("")

        assert result is not None
        assert "frontmatter" in result

    def test_text_with_special_characters(self) -> None:
        """Test handling of special characters in resume."""
        text = "Jöhn Döe\nSoftware Engineer™\nC++ & C# Expert"
        contact_info = extract_contact_info(text)

        assert contact_info["name"] == "Jöhn Döe"

    def test_malformed_dates(self) -> None:
        """Test handling of various date formats."""
        text = """
        EXPERIENCE
        Engineer | Company A | 2020-Present
        Developer | Company B | Jan 2018 - Dec 2019
        Intern | Company C | Summer 2017
        """
        sections = extract_sections(text)
        experience = parse_experience_section(sections[ResumeSection.EXPERIENCE])

        # Should handle different date formats gracefully
        assert len(experience) >= 1

    def test_no_sections_found(self) -> None:
        """Test handling when no standard sections are found."""
        text = "Just some random text with no structure"
        sections = extract_sections(text)

        # Should return empty dict or handle gracefully
        assert isinstance(sections, dict)

    def test_very_long_resume(self) -> None:
        """Test handling of very long resumes."""
        # Generate a very long resume text
        long_text = "John Doe\nEngineer\n" + "\n".join(
            [f"Experience item {i}" for i in range(1000)]
        )
        parser = ResumeParser()
        result = parser.parse_text(long_text)

        assert result is not None
