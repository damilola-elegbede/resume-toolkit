"""ATS scoring module for analyzing resume-job description match quality."""

from .models import (
    ATSScore,
    FormattingDetail,
    KeywordMatchDetail,
    Recommendation,
    ScoreBreakdown,
    SectionStructureDetail,
    SkillsAlignmentDetail,
)
from .scorer import (
    ATSScorerError,
    calculate_formatting_score,
    calculate_keyword_match,
    calculate_overall_score,
    calculate_section_structure_score,
    calculate_skills_alignment,
    check_date_format_consistency,
    extract_keywords_from_resume,
    generate_recommendations,
    score_resume,
)

__all__ = [
    # Models
    "ATSScore",
    "ATSScorerError",
    "FormattingDetail",
    "KeywordMatchDetail",
    "Recommendation",
    "ScoreBreakdown",
    "SectionStructureDetail",
    "SkillsAlignmentDetail",
    # Scorer functions
    "calculate_formatting_score",
    "calculate_keyword_match",
    "calculate_overall_score",
    "calculate_section_structure_score",
    "calculate_skills_alignment",
    "check_date_format_consistency",
    "extract_keywords_from_resume",
    "generate_recommendations",
    "score_resume",
]
