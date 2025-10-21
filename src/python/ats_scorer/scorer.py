"""ATS scoring engine for resume analysis.

Calculates ATS compatibility scores with detailed feedback based on:
- Keyword matching (50% weight)
- Formatting quality (20% weight)
- Skills alignment (20% weight)
- Section structure (10% weight)
"""

import re
from typing import Any

from jd_analyzer.analyzer import analyze_job_description, extract_keywords

from .models import (
    ATSScore,
    FormattingDetail,
    KeywordMatchDetail,
    Recommendation,
    ScoreBreakdown,
    SectionStructureDetail,
    SkillsAlignmentDetail,
)


class ATSScorerError(Exception):
    """Base exception for ATS scorer errors."""



# Standard resume sections
STANDARD_SECTIONS = {
    "SUMMARY",
    "OBJECTIVE",
    "PROFESSIONAL SUMMARY",
    "EXPERIENCE",
    "WORK EXPERIENCE",
    "EMPLOYMENT",
    "EDUCATION",
    "SKILLS",
    "TECHNICAL SKILLS",
    "CERTIFICATIONS",
    "PROJECTS",
}


def extract_keywords_from_resume(resume_text: str) -> list[str]:
    """Extract keywords from resume text.

    Args:
        resume_text: Resume content as string

    Returns:
        List of extracted keywords (lowercase, deduplicated)
    """
    if not resume_text:
        return []

    # Use JD analyzer's keyword extraction (it works for resumes too)
    keywords = extract_keywords(resume_text)

    # Normalize to lowercase and deduplicate
    normalized = list(set(k.lower() for k in keywords))

    return normalized


def calculate_keyword_match(
    resume_keywords: list[str],
    jd_keywords: list[str],
    jd_importance: dict[str, float],
) -> dict[str, Any]:
    """Calculate keyword matching score between resume and job description.

    Args:
        resume_keywords: Keywords extracted from resume
        jd_keywords: Keywords extracted from job description
        jd_importance: Importance scores for JD keywords (0-1)

    Returns:
        Dictionary with keyword match details
    """
    if not jd_keywords:
        return {
            "score": 0.0,
            "matched_required": 0.0,
            "matched_nice_to_have": 0.0,
            "matched_keywords": [],
            "missing_keywords": [],
        }

    # Normalize all keywords to lowercase
    resume_kw_lower = [k.lower() for k in resume_keywords]
    jd_kw_lower = [k.lower() for k in jd_keywords]

    # Separate required (high importance) from nice-to-have (low importance)
    required_keywords = [k for k in jd_kw_lower if jd_importance.get(k, 0.5) >= 0.7]
    nice_to_have_keywords = [k for k in jd_kw_lower if jd_importance.get(k, 0.5) < 0.7]

    # If no importance scores, treat all as equally important
    if not jd_importance:
        required_keywords = jd_kw_lower
        nice_to_have_keywords = []

    # Calculate matches
    matched_required = [k for k in required_keywords if k in resume_kw_lower]
    matched_nice_to_have = [k for k in nice_to_have_keywords if k in resume_kw_lower]
    all_matched = matched_required + matched_nice_to_have

    # Calculate percentages
    required_pct = (
        (len(matched_required) / len(required_keywords) * 100) if required_keywords else 100.0
    )
    nice_pct = (
        (len(matched_nice_to_have) / len(nice_to_have_keywords) * 100)
        if nice_to_have_keywords
        else 100.0
    )

    # Calculate weighted score
    # Required keywords weighted more heavily
    if required_keywords and nice_to_have_keywords:
        weighted_score = required_pct * 0.7 + nice_pct * 0.3
    elif required_keywords:
        weighted_score = required_pct
    else:
        weighted_score = nice_pct

    # Find missing important keywords
    missing_required = [k for k in required_keywords if k not in resume_kw_lower]
    missing_important_nice = [
        k
        for k in nice_to_have_keywords
        if k not in resume_kw_lower and jd_importance.get(k, 0) >= 0.5
    ]
    missing_keywords = missing_required + missing_important_nice[:5]  # Top 5 missing nice-to-have

    return {
        "score": round(weighted_score, 2),
        "matched_required": round(required_pct, 2),
        "matched_nice_to_have": round(nice_pct, 2),
        "matched_keywords": all_matched,
        "missing_keywords": missing_keywords,
    }


def check_date_format_consistency(resume_text: str) -> bool:
    """Check if date formats are consistent throughout resume.

    Args:
        resume_text: Resume content

    Returns:
        True if dates are consistent or no dates found, False otherwise
    """
    # Extract various date patterns
    patterns = [
        r"\b\d{4}-\d{2}\b",  # YYYY-MM
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b",  # Mon YYYY
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",  # Month YYYY
        r"\b\d{1,2}/\d{4}\b",  # MM/YYYY
    ]

    found_formats = []
    for pattern in patterns:
        matches = re.findall(pattern, resume_text)
        if matches:
            found_formats.append(pattern)

    # If 0 or 1 format found, it's consistent
    # If multiple formats found, it's inconsistent
    return len(found_formats) <= 1


def calculate_formatting_score(resume_text: str) -> dict[str, Any]:
    """Calculate resume formatting score.

    Checks:
    - Presence of standard sections
    - Bullet points usage
    - Date format consistency
    - Absence of tables (ATS-unfriendly)

    Args:
        resume_text: Resume content

    Returns:
        Dictionary with formatting score and details
    """
    score = 100.0
    has_sections = False
    has_bullet_points = False
    has_tables = False
    found_sections = []

    # Check for standard sections
    text_upper = resume_text.upper()
    for section in STANDARD_SECTIONS:
        if section in text_upper:
            found_sections.append(section)

    has_sections = len(found_sections) >= 3  # At least 3 standard sections

    if not has_sections:
        score -= 20

    # Check for bullet points
    bullet_patterns = [r"^\s*[•\-\*]", r"^\s*\d+\."]
    for pattern in bullet_patterns:
        if re.search(pattern, resume_text, re.MULTILINE):
            has_bullet_points = True
            break

    if not has_bullet_points:
        score -= 15

    # Check date format consistency
    date_consistent = check_date_format_consistency(resume_text)
    if not date_consistent:
        score -= 20

    # Check for tables (ATS-unfriendly)
    table_patterns = [r"\|.*\|.*\|", r"─{3,}", r"═{3,}"]
    for pattern in table_patterns:
        if re.search(pattern, resume_text):
            has_tables = True
            score -= 15
            break

    # Ensure score is in valid range
    score = max(0.0, min(100.0, score))

    return {
        "score": round(score, 2),
        "has_sections": has_sections,
        "has_bullet_points": has_bullet_points,
        "date_format_consistent": date_consistent,
        "has_tables": has_tables,
        "found_sections": found_sections,
    }


def calculate_skills_alignment(
    resume_text: str,
    jd_analysis: dict[str, Any],
) -> dict[str, Any]:
    """Calculate skills alignment between resume and JD.

    Args:
        resume_text: Resume content
        jd_analysis: Job description analysis from JD analyzer

    Returns:
        Dictionary with skills alignment score and details
    """
    resume_lower = resume_text.lower()

    # Extract required skills from JD
    jd_technical = jd_analysis.get("technical_skills", [])
    jd_leadership = jd_analysis.get("leadership_skills", [])
    jd_domain = jd_analysis.get("domain_expertise", [])

    # Calculate technical skills match
    technical_match = 0.0
    if jd_technical:
        matched_technical = sum(1 for skill in jd_technical if skill.lower() in resume_lower)
        technical_match = (matched_technical / len(jd_technical)) * 100

    # Calculate leadership skills match
    leadership_match = 0.0
    if jd_leadership:
        # Leadership skills might be in full sentences, so check more loosely
        matched_leadership = sum(1 for skill in jd_leadership if skill.lower() in resume_lower)
        leadership_match = (matched_leadership / len(jd_leadership)) * 100

    # Calculate domain expertise match
    domain_match = 0.0
    if jd_domain:
        matched_domain = sum(1 for exp in jd_domain if exp.lower() in resume_lower)
        domain_match = (matched_domain / len(jd_domain)) * 100

    # Calculate overall weighted score
    # Technical: 50%, Leadership: 30%, Domain: 20%
    weights = {"technical": 0.5, "leadership": 0.3, "domain": 0.2}

    overall_score = (
        technical_match * weights["technical"]
        + leadership_match * weights["leadership"]
        + domain_match * weights["domain"]
    )

    return {
        "score": round(overall_score, 2),
        "technical_match": round(technical_match, 2),
        "leadership_match": round(leadership_match, 2),
        "domain_match": round(domain_match, 2),
    }


def calculate_section_structure_score(resume_text: str) -> dict[str, Any]:
    """Calculate section structure score.

    Checks for:
    - Contact information
    - Experience section
    - Education section
    - Skills section
    - Logical ordering

    Args:
        resume_text: Resume content

    Returns:
        Dictionary with section structure score and details
    """
    score = 100.0
    text_upper = resume_text.upper()

    # Check for contact info (email pattern)
    has_contact = bool(re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text_upper))
    if not has_contact:
        score -= 20

    # Check for experience section
    has_experience = any(
        section in text_upper for section in ["EXPERIENCE", "WORK EXPERIENCE", "EMPLOYMENT"]
    )
    if not has_experience:
        score -= 30

    # Check for education section
    has_education = "EDUCATION" in text_upper
    if not has_education:
        score -= 20

    # Check for skills section
    has_skills = any(section in text_upper for section in ["SKILLS", "TECHNICAL SKILLS"])
    if not has_skills:
        score -= 20

    # Check logical order (Experience before Skills is common good practice)
    logical_order = True
    if has_experience and has_skills:
        exp_pos = text_upper.find("EXPERIENCE")
        skills_pos = text_upper.find("SKILLS")
        if skills_pos < exp_pos and skills_pos != -1:
            logical_order = False
            score -= 10

    score = max(0.0, min(100.0, score))

    return {
        "score": round(score, 2),
        "has_contact_info": has_contact,
        "has_experience": has_experience,
        "has_education": has_education,
        "has_skills": has_skills,
        "logical_order": logical_order,
    }


def calculate_overall_score(breakdown: ScoreBreakdown) -> float:
    """Calculate weighted overall ATS score.

    Weights:
    - Keyword match: 50%
    - Formatting: 20%
    - Skills alignment: 20%
    - Section structure: 10%

    Args:
        breakdown: Score breakdown object

    Returns:
        Weighted overall score (0-100)
    """
    weighted = (
        breakdown.keyword_match * 0.5
        + breakdown.formatting * 0.2
        + breakdown.skills_alignment * 0.2
        + breakdown.section_structure * 0.1
    )

    return round(weighted, 2)


def generate_recommendations(
    resume_text: str,
    jd_analysis: dict[str, Any],
    keyword_match_score: float,
    formatting_score: float,
    skills_alignment_score: float,
    resume_keywords: list[str],
) -> list[Recommendation]:
    """Generate actionable recommendations to improve ATS score.

    Args:
        resume_text: Resume content
        jd_analysis: Job description analysis
        keyword_match_score: Current keyword match score
        formatting_score: Current formatting score
        skills_alignment_score: Current skills alignment score
        resume_keywords: Keywords found in resume

    Returns:
        List of prioritized recommendations
    """
    recommendations: list[Recommendation] = []

    # Keyword recommendations
    if keyword_match_score < 80:
        jd_keywords = jd_analysis.get("ats_keywords", [])
        keyword_freq = jd_analysis.get("keyword_frequency", {})
        keyword_importance = jd_analysis.get("keyword_importance", {})

        resume_kw_lower = [k.lower() for k in resume_keywords]
        missing_keywords = [k for k in jd_keywords if k.lower() not in resume_kw_lower]

        # Find top missing keywords by importance and frequency
        missing_with_scores = [
            (kw, keyword_importance.get(kw, 0), keyword_freq.get(kw, 0))
            for kw in missing_keywords
        ]
        missing_with_scores.sort(key=lambda x: (x[1], x[2]), reverse=True)

        # Add recommendations for top missing keywords
        for kw, importance, freq in missing_with_scores[:3]:
            impact = min(importance * 20, 15.0)  # Cap impact at 15
            recommendations.append(
                Recommendation(
                    description=f"Add '{kw}' keyword (appears {freq}x in JD, 0x in resume)",
                    impact=round(impact, 1),
                    category="keyword",
                )
            )

    # Formatting recommendations
    if formatting_score < 80:
        format_details = calculate_formatting_score(resume_text)

        if not format_details["date_format_consistent"]:
            recommendations.append(
                Recommendation(
                    description="Standardize date format to 'YYYY-MM' throughout resume",
                    impact=5.0,
                    category="formatting",
                )
            )

        if not format_details["has_bullet_points"]:
            recommendations.append(
                Recommendation(
                    description="Use bullet points for responsibilities and achievements",
                    impact=4.0,
                    category="formatting",
                )
            )

        if format_details["has_tables"]:
            recommendations.append(
                Recommendation(
                    description="Remove tables and use text formatting (tables are ATS-unfriendly)",
                    impact=6.0,
                    category="formatting",
                )
            )

        if not format_details["has_sections"]:
            recommendations.append(
                Recommendation(
                    description="Add clear section headers (EXPERIENCE, EDUCATION, SKILLS)",
                    impact=8.0,
                    category="formatting",
                )
            )

    # Skills alignment recommendations
    if skills_alignment_score < 75:
        skills_details = calculate_skills_alignment(resume_text, jd_analysis)

        if skills_details["technical_match"] < 70:
            missing_tech = [
                skill
                for skill in jd_analysis.get("technical_skills", [])
                if skill.lower() not in resume_text.lower()
            ]
            if missing_tech:
                recommendations.append(
                    Recommendation(
                        description=f"Add technical skills: {', '.join(missing_tech[:3])}",
                        impact=10.0,
                        category="skills",
                    )
                )

        if skills_details["leadership_match"] < 60:
            recommendations.append(
                Recommendation(
                    description="Add leadership/collaboration examples to experience section",
                    impact=6.0,
                    category="skills",
                )
            )

    # Structure recommendations
    structure_details = calculate_section_structure_score(resume_text)

    if not structure_details["has_contact_info"]:
        recommendations.append(
            Recommendation(
                description="Add contact information (email, phone, LinkedIn)",
                impact=8.0,
                category="structure",
            )
        )

    if not structure_details["has_experience"]:
        recommendations.append(
            Recommendation(
                description="Add EXPERIENCE section with work history",
                impact=15.0,
                category="structure",
            )
        )

    if not structure_details["has_education"]:
        recommendations.append(
            Recommendation(
                description="Add EDUCATION section",
                impact=7.0,
                category="structure",
            )
        )

    # Sort by impact (highest first)
    recommendations.sort(key=lambda r: r.impact, reverse=True)

    # Return top 10 recommendations
    return recommendations[:10]


def score_resume(resume_text: str, job_description: str) -> ATSScore:
    """Score resume against job description for ATS compatibility.

    Args:
        resume_text: Complete resume content
        job_description: Complete job description

    Returns:
        ATSScore object with overall score, breakdown, and recommendations

    Raises:
        ATSScorerError: If inputs are invalid
    """
    # Validate inputs
    if not resume_text or not resume_text.strip():
        raise ATSScorerError("Resume text cannot be empty")

    if not job_description or not job_description.strip():
        raise ATSScorerError("Job description cannot be empty")

    # Analyze job description
    jd_analysis = analyze_job_description(job_description)

    # Extract resume keywords
    resume_keywords = extract_keywords_from_resume(resume_text)

    # Get JD keywords and importance
    jd_keywords = jd_analysis.get("ats_keywords", [])
    jd_importance = jd_analysis.get("keyword_importance", {})

    # Calculate individual scores
    keyword_match = calculate_keyword_match(resume_keywords, jd_keywords, jd_importance)
    formatting = calculate_formatting_score(resume_text)
    skills_alignment = calculate_skills_alignment(resume_text, jd_analysis)
    section_structure = calculate_section_structure_score(resume_text)

    # Create breakdown
    breakdown = ScoreBreakdown(
        keyword_match=keyword_match["score"],
        formatting=formatting["score"],
        skills_alignment=skills_alignment["score"],
        section_structure=section_structure["score"],
    )

    # Calculate overall score
    overall = calculate_overall_score(breakdown)

    # Generate recommendations
    recommendations = generate_recommendations(
        resume_text=resume_text,
        jd_analysis=jd_analysis,
        keyword_match_score=keyword_match["score"],
        formatting_score=formatting["score"],
        skills_alignment_score=skills_alignment["score"],
        resume_keywords=resume_keywords,
    )

    # Create detailed models
    keyword_details = KeywordMatchDetail(
        score=keyword_match["score"],
        matched_required=keyword_match["matched_required"],
        matched_nice_to_have=keyword_match["matched_nice_to_have"],
        matched_keywords=keyword_match["matched_keywords"],
        missing_keywords=keyword_match["missing_keywords"],
    )

    formatting_details = FormattingDetail(
        score=formatting["score"],
        has_sections=formatting["has_sections"],
        has_bullet_points=formatting["has_bullet_points"],
        date_format_consistent=formatting["date_format_consistent"],
        has_tables=formatting["has_tables"],
        found_sections=formatting["found_sections"],
    )

    skills_details = SkillsAlignmentDetail(
        score=skills_alignment["score"],
        technical_match=skills_alignment["technical_match"],
        leadership_match=skills_alignment["leadership_match"],
        domain_match=skills_alignment["domain_match"],
    )

    structure_details = SectionStructureDetail(
        score=section_structure["score"],
        has_contact_info=section_structure["has_contact_info"],
        has_experience=section_structure["has_experience"],
        has_education=section_structure["has_education"],
        has_skills=section_structure["has_skills"],
        logical_order=section_structure["logical_order"],
    )

    return ATSScore(
        overall_score=overall,
        breakdown=breakdown,
        recommendations=recommendations,
        keyword_details=keyword_details,
        formatting_details=formatting_details,
        skills_details=skills_details,
        structure_details=structure_details,
    )
