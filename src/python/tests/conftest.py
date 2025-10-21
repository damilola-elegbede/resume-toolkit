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
