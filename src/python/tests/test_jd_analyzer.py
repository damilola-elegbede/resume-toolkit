"""Tests for Job Description Analyzer."""

import pytest


# These will be implemented in the analyzer module
class TestJDAnalyzer:
    """Test suite for JD analysis functionality."""

    @pytest.fixture
    def sample_jd_text(self) -> str:
        """Sample job description text for testing."""
        return """
        Senior Software Engineer

        We are looking for an experienced Senior Software Engineer to join our team.

        Required Skills:
        - 5+ years of experience with Python and TypeScript
        - Strong knowledge of React and Node.js
        - Experience with PostgreSQL and Redis
        - Understanding of AWS and Docker
        - Excellent communication skills

        Nice to Have:
        - Experience with Kubernetes
        - Knowledge of GraphQL
        - Familiarity with CI/CD pipelines

        Responsibilities:
        - Design and implement scalable backend services
        - Lead technical discussions and architecture decisions
        - Mentor junior developers
        - Collaborate with product team

        Benefits:
        - Competitive salary
        - Remote work flexibility
        - Health insurance
        - 401k matching
        """

    @pytest.fixture
    def expected_keywords(self) -> list[str]:
        """Expected keywords from sample JD."""
        return [
            "Python",
            "TypeScript",
            "React",
            "Node.js",
            "PostgreSQL",
            "Redis",
            "AWS",
            "Docker",
            "Kubernetes",
            "GraphQL",
        ]

    def test_keyword_extraction(self, sample_jd_text: str, expected_keywords: list[str]) -> None:
        """Test that keywords are correctly extracted from JD text."""
        # Will implement extract_keywords function
        from jd_analyzer.analyzer import extract_keywords

        keywords = extract_keywords(sample_jd_text)

        # Should extract technical keywords
        for keyword in expected_keywords:
            assert keyword in keywords, f"Expected keyword '{keyword}' not found"

    def test_keyword_frequency_calculation(self, sample_jd_text: str) -> None:
        """Test keyword frequency analysis."""
        from jd_analyzer.analyzer import calculate_keyword_frequency

        frequencies = calculate_keyword_frequency(sample_jd_text)

        # Should return a dictionary with keywords and counts
        assert isinstance(frequencies, dict)
        assert len(frequencies) > 0

        # High-frequency keywords should be identified
        assert "experience" in frequencies or "Experience" in frequencies
        assert frequencies.get("Python", 0) >= 1 or frequencies.get("python", 0) >= 1

    def test_requirements_categorization(self, sample_jd_text: str) -> None:
        """Test categorization of required vs nice-to-have skills."""
        from jd_analyzer.analyzer import categorize_requirements

        categories = categorize_requirements(sample_jd_text)

        # Should have required and nice-to-have sections
        assert "required" in categories
        assert "nice_to_have" in categories

        # Required should include core skills
        required = categories["required"]
        assert any("Python" in skill for skill in required)
        assert any("TypeScript" in skill for skill in required)

        # Nice-to-have should include optional skills
        nice_to_have = categories["nice_to_have"]
        assert any("Kubernetes" in skill for skill in nice_to_have)
        assert any("GraphQL" in skill for skill in nice_to_have)

    def test_technical_skills_identification(self, sample_jd_text: str) -> None:
        """Test identification of technical skills."""
        from jd_analyzer.analyzer import identify_technical_skills

        technical_skills = identify_technical_skills(sample_jd_text)

        # Should identify programming languages
        assert "Python" in technical_skills or "python" in technical_skills
        assert "TypeScript" in technical_skills or "typescript" in technical_skills

        # Should identify frameworks/libraries
        assert "React" in technical_skills or "react" in technical_skills
        assert "Node.js" in technical_skills or "node.js" in technical_skills

        # Should identify databases
        assert "PostgreSQL" in technical_skills or "postgresql" in technical_skills
        assert "Redis" in technical_skills or "redis" in technical_skills

        # Should identify cloud/DevOps tools
        assert "AWS" in technical_skills or "aws" in technical_skills
        assert "Docker" in technical_skills or "docker" in technical_skills

    def test_leadership_skills_identification(self, sample_jd_text: str) -> None:
        """Test identification of leadership/soft skills."""
        from jd_analyzer.analyzer import identify_leadership_skills

        leadership_skills = identify_leadership_skills(sample_jd_text)

        # Should identify leadership keywords
        assert any(
            "mentor" in skill.lower() or "lead" in skill.lower() for skill in leadership_skills
        )
        assert any("communication" in skill.lower() for skill in leadership_skills)

    def test_domain_expertise_identification(self, sample_jd_text: str) -> None:
        """Test identification of domain-specific expertise."""
        from jd_analyzer.analyzer import identify_domain_expertise

        domain_skills = identify_domain_expertise(sample_jd_text)

        # Should identify architecture/design skills
        assert any("architecture" in skill.lower() for skill in domain_skills)
        assert any("design" in skill.lower() for skill in domain_skills)

    def test_ats_keyword_generation(self, sample_jd_text: str) -> None:
        """Test generation of ATS-optimized keyword list."""
        from jd_analyzer.analyzer import generate_ats_keywords

        ats_keywords = generate_ats_keywords(sample_jd_text)

        # Should return a list of keywords
        assert isinstance(ats_keywords, list)
        assert len(ats_keywords) > 0

        # Should include key technical terms
        keywords_lower = [k.lower() for k in ats_keywords]
        assert "python" in keywords_lower
        assert "typescript" in keywords_lower
        assert "react" in keywords_lower

    def test_keyword_importance_scoring(self, sample_jd_text: str) -> None:
        """Test calculation of keyword importance scores."""
        from jd_analyzer.analyzer import calculate_keyword_importance

        importance_scores = calculate_keyword_importance(sample_jd_text)

        # Should return a dictionary with keywords and scores
        assert isinstance(importance_scores, dict)
        assert len(importance_scores) > 0

        # Scores should be numeric
        for keyword, score in importance_scores.items():
            assert isinstance(score, (int, float))
            assert 0 <= score <= 1  # Normalized scores

    def test_comprehensive_analysis(self, sample_jd_text: str) -> None:
        """Test comprehensive JD analysis."""
        from jd_analyzer.analyzer import analyze_job_description

        analysis = analyze_job_description(sample_jd_text)

        # Should return a comprehensive analysis object
        assert "technical_skills" in analysis
        assert "leadership_skills" in analysis
        assert "domain_expertise" in analysis
        assert "required_skills" in analysis
        assert "nice_to_have_skills" in analysis
        assert "ats_keywords" in analysis
        assert "keyword_importance" in analysis

        # All sections should have content
        assert len(analysis["technical_skills"]) > 0
        assert len(analysis["ats_keywords"]) > 0

    def test_empty_jd_handling(self) -> None:
        """Test handling of empty job description."""
        from jd_analyzer.analyzer import analyze_job_description

        result = analyze_job_description("")

        # Should handle gracefully
        assert isinstance(result, dict)
        # Should return empty or minimal results
        assert len(result.get("technical_skills", [])) == 0

    def test_malformed_jd_handling(self) -> None:
        """Test handling of malformed job description."""
        from jd_analyzer.analyzer import analyze_job_description

        malformed_jd = "Random text without any structure or keywords"

        result = analyze_job_description(malformed_jd)

        # Should not crash
        assert isinstance(result, dict)

    def test_multiple_language_keywords(self) -> None:
        """Test extraction of multiple programming languages."""
        jd_text = """
        We need developers with Python, JavaScript, TypeScript, Go, and Rust experience.
        """

        from jd_analyzer.analyzer import identify_technical_skills

        skills = identify_technical_skills(jd_text)

        # Should identify all languages
        skills_lower = [s.lower() for s in skills]
        assert "python" in skills_lower
        assert "javascript" in skills_lower or "js" in skills_lower
        assert "typescript" in skills_lower
        assert "go" in skills_lower or "golang" in skills_lower
        assert "rust" in skills_lower
