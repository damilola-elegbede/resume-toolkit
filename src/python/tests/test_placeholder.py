"""Placeholder test to ensure pytest is working."""

import pytest


def test_placeholder() -> None:
    """Placeholder test."""
    assert True


@pytest.mark.unit
def test_unit_marker() -> None:
    """Test with unit marker."""
    assert 1 + 1 == 2


@pytest.mark.integration
def test_integration_marker() -> None:
    """Test with integration marker."""
    assert "test" == "test"
