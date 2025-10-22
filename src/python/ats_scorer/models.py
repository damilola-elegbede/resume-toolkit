"""Pydantic models for ATS scoring system."""

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    """Breakdown of individual scoring components.

    Attributes:
        keyword_match: Keyword matching score (0-100)
        formatting: Resume formatting score (0-100)
        skills_alignment: Skills alignment score (0-100)
        section_structure: Section structure score (0-100)
    """

    keyword_match: float = Field(
        ..., ge=0.0, le=100.0, description="Keyword matching score (0-100)"
    )
    formatting: float = Field(..., ge=0.0, le=100.0, description="Formatting score (0-100)")
    skills_alignment: float = Field(
        ..., ge=0.0, le=100.0, description="Skills alignment score (0-100)"
    )
    section_structure: float = Field(
        ..., ge=0.0, le=100.0, description="Section structure score (0-100)"
    )


class Recommendation(BaseModel):
    """A single actionable recommendation for improvement.

    Attributes:
        description: Human-readable recommendation description
        impact: Expected impact on score (0-100)
        category: Category of recommendation (keyword, formatting, skills, structure)
    """

    description: str = Field(..., min_length=1, description="Recommendation description")
    impact: float = Field(..., ge=0.0, le=100.0, description="Expected impact (0-100)")
    category: str = Field(
        ...,
        description="Recommendation category",
        pattern="^(keyword|formatting|skills|structure)$",
    )


class KeywordMatchDetail(BaseModel):
    """Detailed keyword matching information.

    Attributes:
        score: Overall keyword match score (0-100)
        matched_required: Percentage of required keywords matched
        matched_nice_to_have: Percentage of nice-to-have keywords matched
        matched_keywords: List of keywords found in resume
        missing_keywords: List of important keywords missing from resume
    """

    score: float = Field(..., ge=0.0, le=100.0, description="Keyword match score")
    matched_required: float = Field(..., ge=0.0, le=100.0, description="Required match %")
    matched_nice_to_have: float = Field(..., ge=0.0, le=100.0, description="Nice-to-have match %")
    matched_keywords: list[str] = Field(default_factory=list, description="Matched keywords")
    missing_keywords: list[str] = Field(default_factory=list, description="Missing keywords")


class FormattingDetail(BaseModel):
    """Detailed formatting information.

    Attributes:
        score: Overall formatting score (0-100)
        has_sections: Whether standard sections are present
        has_bullet_points: Whether bullet points are used
        date_format_consistent: Whether date formats are consistent
        has_tables: Whether tables are present (ATS-unfriendly)
        found_sections: List of sections found
    """

    score: float = Field(..., ge=0.0, le=100.0, description="Formatting score")
    has_sections: bool = Field(..., description="Has standard sections")
    has_bullet_points: bool = Field(..., description="Uses bullet points")
    date_format_consistent: bool = Field(..., description="Consistent date formats")
    has_tables: bool = Field(default=False, description="Contains tables")
    found_sections: list[str] = Field(default_factory=list, description="Found sections")


class SkillsAlignmentDetail(BaseModel):
    """Detailed skills alignment information.

    Attributes:
        score: Overall skills alignment score (0-100)
        technical_match: Technical skills match percentage
        leadership_match: Leadership skills match percentage
        domain_match: Domain expertise match percentage
    """

    score: float = Field(..., ge=0.0, le=100.0, description="Skills alignment score")
    technical_match: float = Field(..., ge=0.0, le=100.0, description="Technical skills %")
    leadership_match: float = Field(..., ge=0.0, le=100.0, description="Leadership skills %")
    domain_match: float = Field(..., ge=0.0, le=100.0, description="Domain expertise %")


class SectionStructureDetail(BaseModel):
    """Detailed section structure information.

    Attributes:
        score: Overall section structure score (0-100)
        has_contact_info: Whether contact information is present
        has_experience: Whether experience section is present
        has_education: Whether education section is present
        has_skills: Whether skills section is present
        logical_order: Whether sections are in logical order
    """

    score: float = Field(..., ge=0.0, le=100.0, description="Section structure score")
    has_contact_info: bool = Field(..., description="Has contact information")
    has_experience: bool = Field(..., description="Has experience section")
    has_education: bool = Field(..., description="Has education section")
    has_skills: bool = Field(..., description="Has skills section")
    logical_order: bool = Field(..., description="Sections in logical order")


class ATSScore(BaseModel):
    """Complete ATS compatibility score with breakdown and recommendations.

    Attributes:
        overall_score: Weighted overall ATS compatibility score (0-100)
        breakdown: Breakdown of individual scoring components
        recommendations: List of actionable recommendations to improve score
        keyword_details: Detailed keyword matching information (optional)
        formatting_details: Detailed formatting information (optional)
        skills_details: Detailed skills alignment information (optional)
        structure_details: Detailed section structure information (optional)
    """

    overall_score: float = Field(
        ..., ge=0.0, le=100.0, description="Overall ATS compatibility score"
    )
    breakdown: ScoreBreakdown = Field(..., description="Score breakdown by component")
    recommendations: list[Recommendation] = Field(
        default_factory=list, description="Improvement recommendations"
    )

    # Optional detailed information
    keyword_details: KeywordMatchDetail | None = Field(
        None, description="Detailed keyword match info"
    )
    formatting_details: FormattingDetail | None = Field(
        None, description="Detailed formatting info"
    )
    skills_details: SkillsAlignmentDetail | None = Field(
        None, description="Detailed skills alignment info"
    )
    structure_details: SectionStructureDetail | None = Field(
        None, description="Detailed section structure info"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "overall_score": 87.5,
                "breakdown": {
                    "keyword_match": 92.0,
                    "formatting": 85.0,
                    "skills_alignment": 84.0,
                    "section_structure": 90.0,
                },
                "recommendations": [
                    {
                        "description": "Add 'regulatory compliance' keyword (appears 5x in JD, 0x in resume)",
                        "impact": 5.0,
                        "category": "keyword",
                    },
                    {
                        "description": "Standardize date format to 'YYYY-MM - YYYY-MM'",
                        "impact": 3.0,
                        "category": "formatting",
                    },
                ],
            }
        }
    }
