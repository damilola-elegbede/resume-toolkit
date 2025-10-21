"""Company Analyzer Package.

Analyzes company data and generates comprehensive research reports.
"""

from .analyzer import (
    analyze_company_data,
    detect_green_flags,
    detect_red_flags,
    generate_talking_points,
    synthesize_interview_insights,
)

__all__ = [
    "analyze_company_data",
    "detect_green_flags",
    "detect_red_flags",
    "generate_talking_points",
    "synthesize_interview_insights",
]
