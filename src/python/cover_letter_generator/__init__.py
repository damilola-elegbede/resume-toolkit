"""Cover Letter Generator Package.

Generates personalized, compelling cover letters based on JD analysis,
company research, and resume anecdotes.
"""

from .generator import (
    generate_body,
    generate_closing,
    generate_cover_letter,
    generate_opening,
    select_relevant_anecdotes,
)

__all__ = [
    "generate_body",
    "generate_closing",
    "generate_cover_letter",
    "generate_opening",
    "select_relevant_anecdotes",
]
