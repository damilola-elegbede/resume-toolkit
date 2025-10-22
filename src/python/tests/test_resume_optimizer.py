"""Tests for Resume Optimizer.

This module tests the iterative resume optimization workflow:
1. Anecdote selection based on JD keywords
2. Bullet point rewriting with keyword injection
3. Section ordering optimization
4. Iterative improvement loop
5. Convergence criteria (90% score or max 3 iterations)
"""

from pathlib import Path
from typing import Any

import pytest


class TestAnecdoteSelection:
    """Test anecdote selection based on JD keyword relevance."""

    @pytest.fixture
    def sample_anecdotes(self) -> list[dict[str, Any]]:
        """Sample anecdotes for testing."""
        return [
            {
                "id": "anecdote_1",
                "title": "Led Kubernetes Migration",
                "content": "Led migration of monolithic application to Kubernetes, reducing deployment time by 70%",
                "skills": ["kubernetes", "docker", "devops", "leadership"],
                "metrics": {"deployment_time_reduction": "70%"},
            },
            {
                "id": "anecdote_2",
                "title": "Built Distributed System",
                "content": "Architected distributed system handling 1M requests/day using Python and Redis",
                "skills": ["python", "redis", "distributed systems", "architecture"],
                "metrics": {"requests_per_day": "1M"},
            },
            {
                "id": "anecdote_3",
                "title": "Mentored Engineering Team",
                "content": "Mentored team of 5 junior engineers, improving code quality by 40%",
                "skills": ["mentoring", "leadership", "code review"],
                "metrics": {"team_size": 5, "quality_improvement": "40%"},
            },
            {
                "id": "anecdote_4",
                "title": "React Performance Optimization",
                "content": "Optimized React application, reducing load time from 5s to 1s",
                "skills": ["react", "javascript", "performance", "frontend"],
                "metrics": {"load_time_before": "5s", "load_time_after": "1s"},
            },
        ]

    @pytest.fixture
    def jd_keywords(self) -> dict[str, float]:
        """Sample JD keywords with importance scores."""
        return {
            "kubernetes": 0.95,
            "python": 0.90,
            "distributed systems": 0.85,
            "leadership": 0.80,
            "redis": 0.75,
            "docker": 0.70,
            "mentoring": 0.65,
            "architecture": 0.60,
        }

    def test_anecdote_relevance_scoring(
        self, sample_anecdotes: list[dict[str, Any]], jd_keywords: dict[str, float]
    ) -> None:
        """Test anecdote relevance scoring based on keyword overlap."""
        from resume_optimizer.optimizer import score_anecdote_relevance

        scores = {}
        for anecdote in sample_anecdotes:
            score = score_anecdote_relevance(anecdote, jd_keywords)
            scores[anecdote["id"]] = score

        # Anecdote 1 (Kubernetes) should have highest score
        assert scores["anecdote_1"] > scores["anecdote_4"]
        # Anecdote 2 (Python, Redis, Distributed) should also score high
        assert scores["anecdote_2"] > scores["anecdote_4"]
        # All scores should be normalized 0-1
        for score in scores.values():
            assert 0 <= score <= 1

    def test_select_top_anecdotes(
        self, sample_anecdotes: list[dict[str, Any]], jd_keywords: dict[str, float]
    ) -> None:
        """Test selection of top N most relevant anecdotes."""
        from resume_optimizer.optimizer import select_top_anecdotes

        # Select top 2 anecdotes
        selected = select_top_anecdotes(sample_anecdotes, jd_keywords, top_n=2)

        assert len(selected) == 2
        # Should include Kubernetes and Distributed System anecdotes
        selected_ids = [a["id"] for a in selected]
        assert "anecdote_1" in selected_ids or "anecdote_2" in selected_ids

    def test_anecdote_diversity(
        self, sample_anecdotes: list[dict[str, Any]], jd_keywords: dict[str, float]
    ) -> None:
        """Test that selected anecdotes are diverse (different skill categories)."""
        from resume_optimizer.optimizer import select_diverse_anecdotes

        # Select 3 diverse anecdotes
        selected = select_diverse_anecdotes(sample_anecdotes, jd_keywords, top_n=3)

        assert len(selected) <= 3
        # Should not have too much skill overlap
        all_skills = []
        for anecdote in selected:
            all_skills.extend(anecdote["skills"])

        # Diversity check: should have variety of skills
        unique_skills = set(all_skills)
        assert len(unique_skills) >= len(all_skills) * 0.6  # At least 60% unique


class TestBulletRewriting:
    """Test bullet point rewriting with keyword injection."""

    @pytest.fixture
    def sample_bullet(self) -> str:
        """Sample resume bullet point."""
        return "Led migration of application to container platform, reducing deployment time"

    @pytest.fixture
    def missing_keywords(self) -> list[str]:
        """Keywords missing from bullet point."""
        return ["kubernetes", "docker", "CI/CD"]

    def test_identify_missing_keywords(self, sample_bullet: str) -> None:
        """Test identification of missing keywords in bullet."""
        from resume_optimizer.optimizer import identify_missing_keywords

        jd_keywords = ["kubernetes", "python", "docker", "leadership"]
        missing = identify_missing_keywords(sample_bullet, jd_keywords)

        # Should identify keywords not present in bullet
        assert "kubernetes" in missing
        assert "docker" in missing

    def test_rewrite_bullet_with_keywords(
        self, sample_bullet: str, missing_keywords: list[str]
    ) -> None:
        """Test rewriting bullet to include missing keywords naturally."""
        from resume_optimizer.optimizer import rewrite_bullet_with_keywords

        rewritten = rewrite_bullet_with_keywords(sample_bullet, missing_keywords[:2])

        # Should include at least one missing keyword
        assert any(keyword.lower() in rewritten.lower() for keyword in missing_keywords[:2])
        # Should maintain original meaning
        assert "migration" in rewritten.lower() or "migrat" in rewritten.lower()
        assert "deployment" in rewritten.lower() or "deploy" in rewritten.lower()
        # Should preserve metrics if present
        assert len(rewritten) > len(sample_bullet) * 0.7  # Not too short

    def test_preserve_star_format(self) -> None:
        """Test that rewritten bullets maintain STAR format."""
        from resume_optimizer.optimizer import rewrite_bullet_with_keywords

        star_bullet = "Led team of 5 engineers to implement new feature, resulting in 40% increase in user engagement"
        keywords = ["react", "typescript"]

        rewritten = rewrite_bullet_with_keywords(star_bullet, keywords)

        # Should preserve action verb
        assert rewritten[0].isupper()
        # Should preserve metrics
        assert "40%" in rewritten or "5" in rewritten
        # Should preserve result/impact
        assert "increase" in rewritten.lower() or "improv" in rewritten.lower()

    def test_avoid_keyword_stuffing(self) -> None:
        """Test that keyword injection doesn't create unnatural stuffing."""
        from resume_optimizer.optimizer import rewrite_bullet_with_keywords

        bullet = "Developed API endpoints"
        keywords = ["python", "django", "postgresql", "redis", "docker", "kubernetes"]

        rewritten = rewrite_bullet_with_keywords(bullet, keywords)

        # Should not include all keywords unnaturally
        keyword_count = sum(1 for kw in keywords if kw.lower() in rewritten.lower())
        assert keyword_count <= 3  # Max 3 keywords for natural flow

    def test_preserve_authenticity(self) -> None:
        """Test that rewriting preserves truthfulness."""
        from resume_optimizer.optimizer import rewrite_bullet_with_keywords

        bullet = "Built dashboard using JavaScript"
        keywords = ["react"]  # Related, can add

        rewritten = rewrite_bullet_with_keywords(bullet, keywords)

        # Should only add related/compatible keywords
        # Original tech (JavaScript) should still be present or implied
        assert "javascript" in rewritten.lower() or "react" in rewritten.lower()


class TestSectionOptimization:
    """Test section ordering and optimization."""

    @pytest.fixture
    def sample_resume_sections(self) -> dict[str, Any]:
        """Sample resume sections."""
        return {
            "summary": "Senior Software Engineer with 8 years experience",
            "experience": [
                {
                    "title": "Senior Engineer",
                    "company": "TechCorp",
                    "bullets": ["Led backend development", "Managed team of 3"],
                    "skills": ["python", "leadership"],
                },
                {
                    "title": "Software Engineer",
                    "company": "StartupXYZ",
                    "bullets": ["Built React frontend", "Implemented CI/CD"],
                    "skills": ["react", "javascript", "ci/cd"],
                },
            ],
            "skills": {
                "languages": ["Python", "JavaScript", "TypeScript"],
                "frameworks": ["React", "Django", "Node.js"],
                "tools": ["Docker", "Git", "AWS"],
            },
        }

    def test_reorder_experiences_by_relevance(self, sample_resume_sections: dict[str, Any]) -> None:
        """Test reordering experience entries by JD relevance."""
        from resume_optimizer.optimizer import reorder_experiences

        jd_keywords = {"python": 0.9, "leadership": 0.85, "backend": 0.8}

        reordered = reorder_experiences(sample_resume_sections["experience"], jd_keywords)

        # First experience should be most relevant
        assert reordered[0]["title"] == "Senior Engineer"
        assert len(reordered) == len(sample_resume_sections["experience"])

    def test_prioritize_matching_skills(self, sample_resume_sections: dict[str, Any]) -> None:
        """Test prioritization of skills matching JD."""
        from resume_optimizer.optimizer import prioritize_skills

        jd_keywords = {"python": 0.9, "docker": 0.85, "react": 0.7}

        prioritized = prioritize_skills(sample_resume_sections["skills"], jd_keywords)

        # Matching skills should appear first
        all_skills = prioritized["languages"] + prioritized["frameworks"] + prioritized["tools"]
        top_3 = all_skills[:3]
        assert "Python" in top_3 or "Docker" in top_3 or "React" in top_3

    def test_adjust_summary_tone(self) -> None:
        """Test adjusting summary to match JD tone."""
        from resume_optimizer.optimizer import adjust_summary

        original_summary = "Software engineer with experience in web development"
        jd_keywords = {"leadership": 0.9, "architecture": 0.85, "mentoring": 0.8}

        adjusted = adjust_summary(original_summary, jd_keywords)

        # Should incorporate leadership themes
        assert any(word in adjusted.lower() for word in ["lead", "architect", "mentor", "senior"])


class TestIterativeOptimization:
    """Test iterative optimization loop."""

    @pytest.fixture
    def base_resume(self) -> dict[str, Any]:
        """Base resume for optimization."""
        return {
            "summary": "Software Engineer with 5 years experience",
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "TechCorp",
                    "bullets": [
                        "Developed web applications",
                        "Collaborated with team",
                    ],
                    "skills": ["python", "javascript"],
                }
            ],
            "skills": {
                "languages": ["Python", "JavaScript"],
                "frameworks": ["Django"],
                "tools": ["Git"],
            },
        }

    @pytest.fixture
    def jd_analysis(self) -> dict[str, Any]:
        """JD analysis result."""
        return {
            "technical_skills": ["kubernetes", "python", "docker", "redis"],
            "leadership_skills": ["leadership", "mentoring"],
            "ats_keywords": ["kubernetes", "python", "docker", "leadership"],
            "keyword_importance": {
                "kubernetes": 0.95,
                "python": 0.90,
                "docker": 0.85,
                "leadership": 0.80,
            },
        }

    def test_optimization_iteration(
        self, base_resume: dict[str, Any], jd_analysis: dict[str, Any]
    ) -> None:
        """Test single optimization iteration."""
        from resume_optimizer.optimizer import optimize_iteration

        optimized, score = optimize_iteration(base_resume, jd_analysis)

        # Should return optimized resume and score
        assert isinstance(optimized, dict)
        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_iterative_improvement(
        self, base_resume: dict[str, Any], jd_analysis: dict[str, Any]
    ) -> None:
        """Test iterative improvement loop."""
        from resume_optimizer.optimizer import optimize_resume_iteratively

        result = optimize_resume_iteratively(
            base_resume, jd_analysis, target_score=90, max_iterations=3
        )

        # Should return optimization history
        assert "iterations" in result
        assert "final_resume" in result
        assert "final_score" in result

        # Should track improvement
        iterations = result["iterations"]
        assert len(iterations) <= 3
        # Scores should improve or stay same (never decrease)
        for i in range(1, len(iterations)):
            assert iterations[i]["score"] >= iterations[i - 1]["score"]

    def test_convergence_at_target_score(
        self, base_resume: dict[str, Any], jd_analysis: dict[str, Any]
    ) -> None:
        """Test that optimization stops when target score is reached."""
        from resume_optimizer.optimizer import optimize_resume_iteratively

        # Mock high initial score scenario
        result = optimize_resume_iteratively(
            base_resume, jd_analysis, target_score=90, max_iterations=3
        )

        # Should stop early if target reached
        if result["final_score"] >= 90:
            assert len(result["iterations"]) <= 3

    def test_max_iterations_limit(
        self, base_resume: dict[str, Any], jd_analysis: dict[str, Any]
    ) -> None:
        """Test that optimization respects max iterations limit."""
        from resume_optimizer.optimizer import optimize_resume_iteratively

        result = optimize_resume_iteratively(
            base_resume, jd_analysis, target_score=100, max_iterations=2
        )

        # Should not exceed max iterations
        assert len(result["iterations"]) <= 2

    def test_iteration_feedback_loop(
        self, base_resume: dict[str, Any], jd_analysis: dict[str, Any]
    ) -> None:
        """Test that each iteration uses feedback from previous scoring."""
        from resume_optimizer.optimizer import optimize_resume_iteratively

        result = optimize_resume_iteratively(
            base_resume, jd_analysis, target_score=90, max_iterations=3
        )

        # Each iteration should identify gaps from previous attempt
        for iteration in result["iterations"]:
            assert "score" in iteration
            assert "gaps" in iteration  # Missing keywords
            assert "improvements" in iteration  # Actions taken


class TestATSScoring:
    """Test ATS scoring integration."""

    def test_calculate_ats_score(self) -> None:
        """Test ATS score calculation."""
        from resume_optimizer.optimizer import calculate_ats_score

        resume_text = "Python engineer with Kubernetes and Docker experience"
        jd_keywords = {
            "python": 0.9,
            "kubernetes": 0.85,
            "docker": 0.8,
            "react": 0.7,  # Missing
        }

        score = calculate_ats_score(resume_text, jd_keywords)

        # Should return percentage score
        assert isinstance(score, float)
        assert 0 <= score <= 100
        # Should be > 0 since some keywords match
        assert score > 50

    def test_identify_keyword_gaps(self) -> None:
        """Test identification of missing keywords."""
        from resume_optimizer.optimizer import identify_keyword_gaps

        resume_text = "Python developer with Django experience"
        jd_keywords = {
            "python": 0.9,
            "django": 0.8,
            "kubernetes": 0.85,  # Missing
            "docker": 0.75,  # Missing
        }

        gaps = identify_keyword_gaps(resume_text, jd_keywords)

        # Should identify missing high-value keywords
        assert "kubernetes" in [g.lower() for g in gaps]
        assert "docker" in [g.lower() for g in gaps]
        # Should not include present keywords
        assert "python" not in [g.lower() for g in gaps]


class TestResumeLoading:
    """Test loading resume and anecdotes from files."""

    def test_parse_resume_markdown(self, tmp_path: Path) -> None:
        """Test parsing resume from markdown with YAML frontmatter."""
        from resume_optimizer.optimizer import parse_resume_markdown

        resume_content = """---
name: John Doe
title: Senior Software Engineer
email: john@example.com
---

# Summary
Senior Software Engineer with 8 years experience

# Experience
## Software Engineer - TechCorp
- Led backend development
- Managed team of 3
"""
        resume_file = tmp_path / "resume.md"
        resume_file.write_text(resume_content)

        resume = parse_resume_markdown(resume_file)

        # Should extract frontmatter
        assert resume["metadata"]["name"] == "John Doe"
        # Should parse experience sections
        assert "experience" in resume or "content" in resume

    def test_load_anecdotes_from_directory(self, tmp_path: Path) -> None:
        """Test loading anecdotes from directory."""
        from resume_optimizer.optimizer import load_anecdotes

        # Create anecdotes directory
        anecdotes_dir = tmp_path / "anecdotes"
        anecdotes_dir.mkdir()

        # Create sample anecdote file
        anecdote_content = """---
title: Led Kubernetes Migration
skills: [kubernetes, docker, devops]
impact: Reduced deployment time by 70%
---

Led migration of monolithic application to Kubernetes cluster.
Implemented CI/CD pipeline with automated testing.
"""
        (anecdotes_dir / "kubernetes-migration.md").write_text(anecdote_content)

        anecdotes = load_anecdotes(anecdotes_dir)

        assert len(anecdotes) >= 1
        assert any("kubernetes" in a.get("skills", []) for a in anecdotes)


class TestOutputGeneration:
    """Test optimized resume output generation."""

    def test_generate_optimized_resume(self) -> None:
        """Test generating optimized resume markdown."""
        from resume_optimizer.optimizer import generate_resume_markdown

        optimized_resume = {
            "metadata": {"name": "John Doe", "title": "Senior Engineer"},
            "summary": "Senior Software Engineer with Kubernetes expertise",
            "experience": [
                {
                    "title": "Senior Engineer",
                    "company": "TechCorp",
                    "bullets": [
                        "Led Kubernetes migration reducing deployment time by 70%",
                        "Mentored team of 5 engineers",
                    ],
                }
            ],
            "skills": {
                "languages": ["Python", "Go"],
                "tools": ["Kubernetes", "Docker"],
            },
        }

        markdown = generate_resume_markdown(optimized_resume)

        # Should generate valid markdown
        assert "# Summary" in markdown or "Summary" in markdown
        assert "John Doe" in markdown
        assert "Kubernetes" in markdown

    def test_save_optimization_report(self, tmp_path: Path) -> None:
        """Test saving optimization report with iteration history."""
        from resume_optimizer.optimizer import save_optimization_report

        optimization_result = {
            "iterations": [
                {
                    "iteration": 1,
                    "score": 75,
                    "gaps": ["kubernetes"],
                    "improvements": ["Added K8s experience"],
                },
                {
                    "iteration": 2,
                    "score": 88,
                    "gaps": ["docker"],
                    "improvements": ["Added Docker mention"],
                },
                {"iteration": 3, "score": 92, "gaps": [], "improvements": ["Reordered sections"]},
            ],
            "final_score": 92,
            "final_resume": {},
        }

        output_path = tmp_path / "optimization-report.md"
        save_optimization_report(optimization_result, output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "Iteration 1" in content or "iteration" in content.lower()
        assert "92" in content  # Final score


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_anecdotes_list(self) -> None:
        """Test handling empty anecdotes list."""
        from resume_optimizer.optimizer import select_top_anecdotes

        result = select_top_anecdotes([], {"python": 0.9}, top_n=3)

        assert result == []

    def test_no_keyword_overlap(self) -> None:
        """Test handling when resume has no keyword overlap with JD."""
        from resume_optimizer.optimizer import calculate_ats_score

        resume_text = "Accountant with Excel and QuickBooks experience"
        jd_keywords = {"python": 0.9, "kubernetes": 0.85}

        score = calculate_ats_score(resume_text, jd_keywords)

        # Should return low but valid score
        assert 0 <= score <= 100
        assert score < 20

    def test_malformed_resume_markdown(self, tmp_path: Path) -> None:
        """Test handling malformed resume markdown."""
        from resume_optimizer.optimizer import parse_resume_markdown

        malformed = "This is not valid markdown with frontmatter"
        resume_file = tmp_path / "malformed.md"
        resume_file.write_text(malformed)

        # Should handle gracefully without crashing
        try:
            resume = parse_resume_markdown(resume_file)
            assert isinstance(resume, dict)
        except Exception as e:
            # If it raises, should be a clear error
            assert "frontmatter" in str(e).lower() or "parse" in str(e).lower()
