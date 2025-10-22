"""
Pytest configuration and shared fixtures.
"""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_pdf_path(fixtures_dir: Path) -> Path:
    """Return path to sample resume PDF for testing.

    Note: You should place a real resume PDF in the fixtures directory
    for integration testing.
    """
    return fixtures_dir / "sample_resume.pdf"


@pytest.fixture
def sample_resume_pdf(tmp_path: Path) -> Path:
    """Generate a sample single-page resume PDF for testing.

    Args:
        tmp_path: Pytest temporary directory

    Returns:
        Path to generated PDF file
    """
    try:
        from fpdf import FPDF
    except ImportError:
        pytest.skip("fpdf2 not installed - required for PDF generation")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    # Resume header
    pdf.cell(0, 10, "John Doe", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "john.doe@email.com | (555) 123-4567", ln=True, align="C")
    pdf.cell(
        0,
        10,
        "linkedin.com/in/johndoe | github.com/johndoe",
        ln=True,
        align="C",
    )
    pdf.ln(5)

    # Professional Summary
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Professional Summary", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        5,
        "Senior Software Engineer with 8+ years of experience building scalable web applications. "
        "Expertise in Python, JavaScript, and cloud architecture. Proven track record of leading "
        "technical initiatives and mentoring engineers.",
    )
    pdf.ln(3)

    # Skills
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Skills", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        5,
        "Languages: Python, JavaScript, TypeScript, Go\n"
        "Frameworks: React, Node.js, Django, FastAPI\n"
        "Databases: PostgreSQL, MongoDB, Redis\n"
        "Cloud: AWS, Docker, Kubernetes, Terraform",
    )
    pdf.ln(3)

    # Experience
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Work Experience", ln=True)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, "Senior Software Engineer - TechCorp Inc.", ln=True)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 5, "2020 - Present | San Francisco, CA", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        5,
        "- Architected microservices platform handling 2M+ daily active users\n"
        "- Led migration from monolith to microservices, reducing deployment time by 70%\n"
        "- Implemented CI/CD pipeline cutting release cycle from 2 weeks to daily deploys\n"
        "- Mentored team of 5 junior engineers",
    )
    pdf.ln(2)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, "Software Engineer - StartupXYZ", ln=True)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 5, "2018 - 2020 | Remote", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        5,
        "- Built real-time analytics dashboard processing 100K events/second\n"
        "- Optimized API response times by 60% through query optimization\n"
        "- Developed GraphQL API serving mobile and web clients",
    )
    pdf.ln(3)

    # Education
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Education", ln=True)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, "M.S. Computer Science - Stanford University", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 5, "2016 | GPA: 3.9/4.0", ln=True)

    # Save to temporary file
    pdf_path = tmp_path / "sample_resume.pdf"
    pdf.output(str(pdf_path))

    return pdf_path


@pytest.fixture
def multipage_resume_pdf(tmp_path: Path) -> Path:
    """Generate a multi-page resume PDF for testing.

    Args:
        tmp_path: Pytest temporary directory

    Returns:
        Path to generated PDF file
    """
    try:
        from fpdf import FPDF
    except ImportError:
        pytest.skip("fpdf2 not installed - required for PDF generation")

    pdf = FPDF()

    # Page 1
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Jane Smith", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "jane.smith@email.com | (555) 987-6543", ln=True, align="C")
    pdf.ln(5)

    # Add lots of content to fill first page
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Professional Summary", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        5,
        "Experienced technical leader with 10+ years in software engineering. "
        "Specialized in distributed systems, cloud architecture, and team leadership. "
        "Track record of delivering high-impact projects and building high-performing teams.",
    )
    pdf.ln(3)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Work Experience", ln=True)

    # Add multiple positions
    for i in range(5):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 7, f"Position {i+1} - Company {i+1}", ln=True)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 5, f"201{i} - 201{i+2} | Location", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(
            0,
            5,
            f"- Accomplishment 1 for position {i+1}\n"
            f"- Accomplishment 2 for position {i+1}\n"
            f"- Accomplishment 3 for position {i+1}\n"
            f"- Accomplishment 4 for position {i+1}",
        )
        pdf.ln(2)

    # Page 2 - More content
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Skills & Expertise", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        5,
        "Programming Languages: Python, Java, Go, JavaScript, TypeScript, Rust\n"
        "Frameworks: Spring Boot, Django, React, Vue.js, Angular\n"
        "Databases: PostgreSQL, MySQL, MongoDB, Cassandra, Redis\n"
        "Cloud: AWS, GCP, Azure, Kubernetes, Docker, Terraform\n"
        "Tools: Git, Jenkins, CircleCI, Datadog, Grafana",
    )
    pdf.ln(3)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Education", ln=True)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, "Ph.D. Computer Science - MIT", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 5, "2015 | Dissertation: Distributed Systems", ln=True)
    pdf.ln(2)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, "M.S. Computer Science - UC Berkeley", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 5, "2012", ln=True)

    pdf_path = tmp_path / "multipage_resume.pdf"
    pdf.output(str(pdf_path))

    return pdf_path


@pytest.fixture
def scanned_resume_pdf(tmp_path: Path) -> Path:
    """Generate a scanned (image-based) PDF for testing.

    This creates a PDF with embedded images rather than text,
    simulating a scanned document.

    Args:
        tmp_path: Pytest temporary directory

    Returns:
        Path to generated PDF file
    """
    try:
        from fpdf import FPDF
        from PIL import Image, ImageDraw
    except ImportError:
        pytest.skip("fpdf2 or Pillow not installed - required for image PDF generation")

    # Create a simple image that looks like text
    img = Image.new("RGB", (800, 1000), color="white")
    draw = ImageDraw.Draw(img)

    # Draw some "text-like" rectangles (simulating scanned text)
    y_pos = 50
    for line in range(20):
        # Simulate text lines with rectangles
        draw.rectangle([50, y_pos, 750, y_pos + 15], fill="black")
        y_pos += 40

    # Save image temporarily
    img_path = tmp_path / "scanned_page.png"
    img.save(str(img_path))

    # Create PDF with the image
    pdf = FPDF()
    pdf.add_page()
    pdf.image(str(img_path), x=0, y=0, w=210)  # A4 width

    pdf_path = tmp_path / "scanned_resume.pdf"
    pdf.output(str(pdf_path))

    return pdf_path
