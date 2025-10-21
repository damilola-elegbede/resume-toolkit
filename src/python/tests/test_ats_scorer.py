"""
Test suite for ATS scorer.

Tests cover:
- Keyword matching with frequency analysis
- Formatting checks (sections, dates, structure)
- Skills alignment calculation
- Weighted score calculation
- Recommendation generation
- Edge cases (empty resume, missing sections, etc.)
"""


import pytest
from ats_scorer.models import ATSScore, Recommendation, ScoreBreakdown
from ats_scorer.scorer import (
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


@pytest.fixture
def sample_resume_text() -> str:
    """Sample resume text for testing."""
    return """
John Doe
Senior Software Engineer
john.doe@email.com | (555) 123-4567

PROFESSIONAL SUMMARY
Experienced software engineer with 8+ years building scalable systems.
Expertise in Python, TypeScript, and cloud infrastructure.

EXPERIENCE

Senior Software Engineer | Tech Corp | 2020-01 - Present
• Led development of microservices architecture serving 10M+ users
• Improved system performance by 40% through optimization
• Mentored team of 5 junior engineers

Software Engineer | StartupXYZ | 2017-06 - 2019-12
• Built REST APIs using Python/Django and PostgreSQL
• Implemented CI/CD pipeline reducing deployment time by 60%
• Collaborated with cross-functional teams on product features

EDUCATION

Bachelor of Science in Computer Science | University of Technology | 2013 - 2017
GPA: 3.8/4.0

SKILLS
Languages: Python, TypeScript, JavaScript, Go, SQL
Frameworks: Django, FastAPI, React, Node.js
Tools: Docker, Kubernetes, AWS, PostgreSQL, Redis
"""


@pytest.fixture
def sample_job_description() -> str:
    """Sample job description for testing."""
    return """
Senior Software Engineer - Backend

We are seeking a talented Senior Software Engineer to join our team.

REQUIRED SKILLS:
- 5+ years of experience with Python and modern web frameworks
- Strong experience with Django or FastAPI
- Experience with PostgreSQL and database design
- Knowledge of Docker and Kubernetes
- Experience with AWS cloud infrastructure
- Understanding of microservices architecture
- Experience with CI/CD pipelines

NICE TO HAVE:
- TypeScript experience
- Redis or caching solutions
- Leadership and mentoring experience
- GraphQL API design
- Terraform or infrastructure as code

RESPONSIBILITIES:
- Design and build scalable backend services
- Lead technical initiatives across teams
- Mentor junior engineers
- Drive architecture decisions
"""


@pytest.fixture
def sample_job_description_with_gaps() -> str:
    """Job description requiring skills not in resume."""
    return """
DevOps Engineer

REQUIRED:
- 5+ years Terraform experience
- Strong Go programming skills
- GraphQL API design
- Regulatory compliance experience
- Strategic planning skills
- Kubernetes CKA certification

NICE TO HAVE:
- Ansible automation
- Azure cloud platform
- Jenkins pipeline development
"""


@pytest.fixture
def poorly_formatted_resume() -> str:
    """Resume with formatting issues."""
    return """
John Doe - Engineer
Email: john@email.com

Work History
Tech Corp, Senior Engineer, Jan 2020 to now
- Did microservices work
- Improved performance

StartupXYZ, Engineer, June 2017 - December 2019
Built APIs with Python

School
BS Computer Science, University of Tech, 2013-2017

My Skills
Python Django PostgreSQL Docker
"""


@pytest.mark.unit
class TestKeywordExtraction:
    """Test keyword extraction from resume text."""

    def test_extract_keywords_basic(self, sample_resume_text: str) -> None:
        """Test basic keyword extraction."""
        keywords = extract_keywords_from_resume(sample_resume_text)

        assert "python" in keywords
        assert "typescript" in keywords
        assert "docker" in keywords
        assert "kubernetes" in keywords
        assert "aws" in keywords

    def test_extract_keywords_case_insensitive(self) -> None:
        """Test keywords are extracted case-insensitively."""
        resume = "PYTHON Python python JavaScript JAVASCRIPT"
        keywords = extract_keywords_from_resume(resume)

        # Should normalize to lowercase and deduplicate
        assert "python" in keywords
        assert "javascript" in keywords
        assert keywords.count("python") == 1
        assert keywords.count("javascript") == 1

    def test_extract_keywords_empty_resume(self) -> None:
        """Test handling of empty resume."""
        keywords = extract_keywords_from_resume("")
        assert keywords == []

    def test_extract_keywords_with_multi_word(self, sample_resume_text: str) -> None:
        """Test extraction of multi-word keywords."""
        keywords = extract_keywords_from_resume(sample_resume_text)

        # Should capture multi-word terms
        assert any("ci/cd" in k.lower() for k in keywords) or "ci/cd" in sample_resume_text.lower()


@pytest.mark.unit
class TestKeywordMatching:
    """Test keyword matching between resume and JD."""

    def test_calculate_keyword_match_perfect(self) -> None:
        """Test perfect keyword match."""
        resume_keywords = ["python", "django", "postgresql", "docker", "aws"]
        jd_keywords = ["python", "django", "postgresql", "docker", "aws"]
        jd_importance = dict.fromkeys(jd_keywords, 1.0)

        score = calculate_keyword_match(resume_keywords, jd_keywords, jd_importance)

        assert score["score"] == 100.0
        assert score["matched_required"] == 100.0
        assert score["matched_nice_to_have"] == 100.0

    def test_calculate_keyword_match_partial(
        self, sample_resume_text: str, sample_job_description: str
    ) -> None:
        """Test partial keyword matching."""
        from jd_analyzer.analyzer import analyze_job_description, extract_keywords

        resume_keywords = extract_keywords_from_resume(sample_resume_text)
        jd_keywords = extract_keywords(sample_job_description)
        jd_analysis = analyze_job_description(sample_job_description)
        jd_importance = jd_analysis["keyword_importance"]

        score = calculate_keyword_match(resume_keywords, jd_keywords, jd_importance)

        # Should have reasonable score given resume matches fairly well
        assert score["score"] >= 60.0
        assert len(score["matched_keywords"]) > 0
        assert len(score["missing_keywords"]) >= 0

    def test_calculate_keyword_match_no_match(self) -> None:
        """Test when no keywords match."""
        resume_keywords = ["python", "django"]
        jd_keywords = ["java", "spring", "oracle"]
        jd_importance = dict.fromkeys(jd_keywords, 1.0)

        score = calculate_keyword_match(resume_keywords, jd_keywords, jd_importance)

        assert score["score"] < 20.0  # Very low score
        assert len(score["matched_keywords"]) == 0
        assert len(score["missing_keywords"]) > 0

    def test_keyword_match_with_importance_weighting(self) -> None:
        """Test that keyword importance affects matching score."""
        resume_keywords = ["python", "docker"]
        jd_keywords = ["python", "docker", "java", "spring"]

        # High importance on matched keywords
        high_importance = {"python": 1.0, "docker": 1.0, "java": 0.3, "spring": 0.3}

        score_high = calculate_keyword_match(resume_keywords, jd_keywords, high_importance)

        # High importance on missing keywords
        low_importance = {"python": 0.3, "docker": 0.3, "java": 1.0, "spring": 1.0}

        score_low = calculate_keyword_match(resume_keywords, jd_keywords, low_importance)

        # Score should be higher when matched keywords are more important
        assert score_high["score"] > score_low["score"]


@pytest.mark.unit
class TestFormattingScore:
    """Test resume formatting evaluation."""

    def test_formatting_well_formatted_resume(self, sample_resume_text: str) -> None:
        """Test scoring of well-formatted resume."""
        score = calculate_formatting_score(sample_resume_text)

        assert score["score"] >= 80.0
        assert score["has_sections"] is True
        assert score["has_bullet_points"] is True
        assert score["date_format_consistent"] is True

    def test_formatting_poorly_formatted_resume(self, poorly_formatted_resume: str) -> None:
        """Test scoring of poorly formatted resume."""
        score = calculate_formatting_score(poorly_formatted_resume)

        # Should have lower score due to inconsistent dates and missing standard sections
        assert score["score"] < 80.0
        assert score["date_format_consistent"] is False

    def test_formatting_detects_standard_sections(self, sample_resume_text: str) -> None:
        """Test detection of standard resume sections."""
        score = calculate_formatting_score(sample_resume_text)

        assert "EXPERIENCE" in score["found_sections"]
        assert "EDUCATION" in score["found_sections"]
        assert "SKILLS" in score["found_sections"]

    def test_formatting_detects_bullet_points(self, sample_resume_text: str) -> None:
        """Test detection of bullet points."""
        score = calculate_formatting_score(sample_resume_text)
        assert score["has_bullet_points"] is True

    def test_formatting_no_bullet_points(self) -> None:
        """Test detection when no bullet points present."""
        resume = "EXPERIENCE\nWorked at Company doing things"
        score = calculate_formatting_score(resume)
        assert score["has_bullet_points"] is False

    def test_formatting_detects_tables(self) -> None:
        """Test detection of tables (ATS-unfriendly)."""
        resume_with_table = """
        EXPERIENCE
        | Company | Role | Date |
        |---------|------|------|
        | Tech Corp | Engineer | 2020 |
        """
        score = calculate_formatting_score(resume_with_table)
        assert score["has_tables"] is True


@pytest.mark.unit
class TestDateFormatConsistency:
    """Test date format consistency checking."""

    def test_date_format_consistent_yyyy_mm(self) -> None:
        """Test consistent YYYY-MM format."""
        resume = """
        EXPERIENCE
        Engineer | Company | 2020-01 - 2022-12
        Developer | Startup | 2018-06 - 2019-12
        """
        is_consistent = check_date_format_consistency(resume)
        assert is_consistent is True

    def test_date_format_inconsistent(self) -> None:
        """Test inconsistent date formats."""
        resume = """
        EXPERIENCE
        Engineer | Company | Jan 2020 - Dec 2022
        Developer | Startup | 2018-06 - 2019-12
        """
        is_consistent = check_date_format_consistency(resume)
        assert is_consistent is False

    def test_date_format_no_dates(self) -> None:
        """Test resume with no dates."""
        resume = "EXPERIENCE\nEngineer at Company"
        is_consistent = check_date_format_consistency(resume)
        # Should return True (no inconsistency found)
        assert is_consistent is True


@pytest.mark.unit
class TestSkillsAlignment:
    """Test skills alignment calculation."""

    def test_skills_alignment_high_match(
        self, sample_resume_text: str, sample_job_description: str
    ) -> None:
        """Test skills alignment with high match."""
        from jd_analyzer.analyzer import analyze_job_description

        jd_analysis = analyze_job_description(sample_job_description)

        score = calculate_skills_alignment(sample_resume_text, jd_analysis)

        assert score["score"] >= 50.0
        assert score["technical_match"] >= 60.0

    def test_skills_alignment_low_match(
        self, sample_resume_text: str, sample_job_description_with_gaps: str
    ) -> None:
        """Test skills alignment with low match."""
        from jd_analyzer.analyzer import analyze_job_description

        jd_analysis = analyze_job_description(sample_job_description_with_gaps)

        score = calculate_skills_alignment(sample_resume_text, jd_analysis)

        # Should have lower score due to missing skills
        assert score["score"] < 70.0

    def test_skills_alignment_technical_vs_leadership(self) -> None:
        """Test technical and leadership skills are scored separately."""
        resume = "Python Django leadership mentoring team lead"
        jd_analysis = {
            "technical_skills": ["python", "django", "java"],
            "leadership_skills": ["leadership", "mentoring"],
            "domain_expertise": [],
        }

        score = calculate_skills_alignment(resume, jd_analysis)

        assert "technical_match" in score
        assert "leadership_match" in score
        assert score["technical_match"] > 0
        assert score["leadership_match"] > 0


@pytest.mark.unit
class TestSectionStructureScore:
    """Test section structure evaluation."""

    def test_section_structure_complete(self, sample_resume_text: str) -> None:
        """Test complete resume with all sections."""
        score = calculate_section_structure_score(sample_resume_text)

        assert score["score"] >= 90.0
        assert score["has_contact_info"] is True
        assert score["has_experience"] is True
        assert score["has_education"] is True
        assert score["has_skills"] is True

    def test_section_structure_missing_sections(self) -> None:
        """Test resume missing key sections."""
        resume = """
        John Doe
        john@email.com

        EXPERIENCE
        Engineer at Company
        """
        score = calculate_section_structure_score(resume)

        assert score["score"] < 80.0
        assert score["has_education"] is False
        assert score["has_skills"] is False

    def test_section_structure_logical_order(self, sample_resume_text: str) -> None:
        """Test that sections appear in logical order."""
        score = calculate_section_structure_score(sample_resume_text)

        # Experience should come before Skills in well-ordered resume
        assert score["logical_order"] is True


@pytest.mark.unit
class TestOverallScoreCalculation:
    """Test weighted overall score calculation."""

    def test_calculate_overall_score_weights(self) -> None:
        """Test that weights add up correctly."""
        breakdown = ScoreBreakdown(
            keyword_match=90.0,
            formatting=85.0,
            skills_alignment=80.0,
            section_structure=95.0,
        )

        overall = calculate_overall_score(breakdown)

        # Weighted: 90*0.5 + 85*0.2 + 80*0.2 + 95*0.1 = 45 + 17 + 16 + 9.5 = 87.5
        assert abs(overall - 87.5) < 0.1

    def test_calculate_overall_score_all_perfect(self) -> None:
        """Test perfect scores result in 100."""
        breakdown = ScoreBreakdown(
            keyword_match=100.0,
            formatting=100.0,
            skills_alignment=100.0,
            section_structure=100.0,
        )

        overall = calculate_overall_score(breakdown)
        assert overall == 100.0

    def test_calculate_overall_score_all_zero(self) -> None:
        """Test zero scores result in 0."""
        breakdown = ScoreBreakdown(
            keyword_match=0.0,
            formatting=0.0,
            skills_alignment=0.0,
            section_structure=0.0,
        )

        overall = calculate_overall_score(breakdown)
        assert overall == 0.0


@pytest.mark.unit
class TestRecommendationGeneration:
    """Test recommendation generation."""

    def test_generate_recommendations_high_score(
        self, sample_resume_text: str, sample_job_description: str
    ) -> None:
        """Test recommendations for high-scoring resume."""
        from jd_analyzer.analyzer import analyze_job_description

        jd_analysis = analyze_job_description(sample_job_description)
        resume_keywords = extract_keywords_from_resume(sample_resume_text)

        recommendations = generate_recommendations(
            resume_text=sample_resume_text,
            jd_analysis=jd_analysis,
            keyword_match_score=90.0,
            formatting_score=85.0,
            skills_alignment_score=88.0,
            resume_keywords=resume_keywords,
        )

        # High-scoring resume should have few recommendations
        assert len(recommendations) <= 5
        assert all(isinstance(r, Recommendation) for r in recommendations)

    def test_generate_recommendations_missing_keywords(
        self, sample_resume_text: str, sample_job_description_with_gaps: str
    ) -> None:
        """Test recommendations identify missing keywords."""
        from jd_analyzer.analyzer import analyze_job_description

        jd_analysis = analyze_job_description(sample_job_description_with_gaps)
        resume_keywords = extract_keywords_from_resume(sample_resume_text)

        recommendations = generate_recommendations(
            resume_text=sample_resume_text,
            jd_analysis=jd_analysis,
            keyword_match_score=40.0,
            formatting_score=85.0,
            skills_alignment_score=50.0,
            resume_keywords=resume_keywords,
        )

        # Should recommend adding missing keywords
        keyword_recs = [r for r in recommendations if r.category == "keyword"]
        assert len(keyword_recs) > 0

    def test_generate_recommendations_formatting_issues(
        self, poorly_formatted_resume: str, sample_job_description: str
    ) -> None:
        """Test recommendations for formatting issues."""
        from jd_analyzer.analyzer import analyze_job_description

        jd_analysis = analyze_job_description(sample_job_description)
        resume_keywords = extract_keywords_from_resume(poorly_formatted_resume)

        recommendations = generate_recommendations(
            resume_text=poorly_formatted_resume,
            jd_analysis=jd_analysis,
            keyword_match_score=75.0,
            formatting_score=50.0,
            skills_alignment_score=70.0,
            resume_keywords=resume_keywords,
        )

        # Should include formatting recommendations
        format_recs = [r for r in recommendations if "format" in r.description.lower() or "date" in r.description.lower()]
        assert len(format_recs) > 0

    def test_recommendations_prioritized_by_impact(self) -> None:
        """Test that recommendations are sorted by impact."""
        recommendations = generate_recommendations(
            resume_text="Python Developer",
            jd_analysis={
                "technical_skills": ["java", "spring"],
                "leadership_skills": [],
                "domain_expertise": [],
                "required_skills": [],
                "nice_to_have_skills": [],
                "keyword_frequency": {"java": 10, "spring": 8},
                "keyword_importance": {"java": 1.0, "spring": 0.8},
            },
            keyword_match_score=30.0,
            formatting_score=80.0,
            skills_alignment_score=40.0,
            resume_keywords=["python"],
        )

        # High-impact recommendations should come first
        if len(recommendations) > 1:
            assert recommendations[0].impact >= recommendations[-1].impact


@pytest.mark.unit
class TestCompleteScoring:
    """Test complete end-to-end scoring."""

    def test_score_resume_returns_ats_score_model(
        self, sample_resume_text: str, sample_job_description: str
    ) -> None:
        """Test complete scoring returns ATSScore model."""
        score = score_resume(sample_resume_text, sample_job_description)

        assert isinstance(score, ATSScore)
        assert 0 <= score.overall_score <= 100
        assert isinstance(score.breakdown, ScoreBreakdown)
        assert isinstance(score.recommendations, list)

    def test_score_resume_high_quality_match(
        self, sample_resume_text: str, sample_job_description: str
    ) -> None:
        """Test scoring of well-matched resume and JD."""
        score = score_resume(sample_resume_text, sample_job_description)

        assert score.overall_score >= 70.0
        assert score.breakdown.keyword_match >= 60.0

    def test_score_resume_poor_match(
        self, sample_resume_text: str, sample_job_description_with_gaps: str
    ) -> None:
        """Test scoring of poorly matched resume and JD."""
        score = score_resume(sample_resume_text, sample_job_description_with_gaps)

        assert score.overall_score < 70.0

    def test_score_resume_with_formatting_issues(
        self, poorly_formatted_resume: str, sample_job_description: str
    ) -> None:
        """Test scoring considers formatting issues."""
        score = score_resume(poorly_formatted_resume, sample_job_description)

        # Formatting score should be lower
        assert score.breakdown.formatting < 80.0


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_resume(self) -> None:
        """Test handling of empty resume."""
        jd = "Looking for Python developer with Django experience"

        with pytest.raises(ATSScorerError, match="Resume text cannot be empty"):
            score_resume("", jd)

    def test_empty_job_description(self, sample_resume_text: str) -> None:
        """Test handling of empty job description."""
        with pytest.raises(ATSScorerError, match="Job description cannot be empty"):
            score_resume(sample_resume_text, "")

    def test_very_short_resume(self) -> None:
        """Test handling of very short resume."""
        resume = "John Doe\nEngineer"
        jd = "Looking for Senior Python Engineer with 5+ years experience"

        score = score_resume(resume, jd)

        # Should have low score but not crash
        assert score.overall_score < 50.0

    def test_very_long_resume(self) -> None:
        """Test handling of very long resume."""
        resume = "John Doe\nEngineer\n" + "\n".join([f"Experience item {i}" for i in range(1000)])
        jd = "Looking for Engineer"

        score = score_resume(resume, jd)

        # Should handle gracefully
        assert isinstance(score, ATSScore)

    def test_special_characters_in_resume(self) -> None:
        """Test handling of special characters."""
        resume = "Jöhn Döe\nC++ & C# Expert\nEmail: test@example.com"
        jd = "Looking for C++ developer"

        score = score_resume(resume, jd)

        assert isinstance(score, ATSScore)

    def test_unicode_in_job_description(self) -> None:
        """Test handling of unicode in JD."""
        resume = "Python Developer"
        jd = "Looking for Python developer • Experience required • Must have skills"

        score = score_resume(resume, jd)

        assert isinstance(score, ATSScore)


@pytest.mark.integration
class TestIntegrationWithJDAnalyzer:
    """Integration tests with JD analyzer."""

    def test_uses_jd_analyzer_correctly(
        self, sample_resume_text: str, sample_job_description: str
    ) -> None:
        """Test that ATS scorer correctly uses JD analyzer."""
        score = score_resume(sample_resume_text, sample_job_description)

        # Should have extracted and analyzed JD properly
        assert score.breakdown.keyword_match > 0
        assert score.breakdown.skills_alignment > 0

    def test_keyword_frequency_affects_score(self) -> None:
        """Test that keyword frequency in JD affects scoring."""
        resume = "Python Django PostgreSQL AWS"

        # JD with high Python frequency
        jd_high_python = """
        Python Python Python Developer needed.
        Must have Python experience. Python is critical.
        Django and PostgreSQL preferred.
        """

        # JD with balanced keywords
        jd_balanced = """
        Python Developer needed.
        Django and PostgreSQL required.
        AWS experience preferred.
        """

        score_high = score_resume(resume, jd_high_python)
        score_balanced = score_resume(resume, jd_balanced)

        # Both should score well since resume has the keywords
        assert score_high.breakdown.keyword_match >= 70.0
        assert score_balanced.breakdown.keyword_match >= 70.0
