"""Company Analyzer Tests.

Test company data analysis and report generation.
"""

import pytest
from company_analyzer.analyzer import (
    analyze_company_data,
    detect_green_flags,
    detect_red_flags,
    generate_talking_points,
    synthesize_interview_insights,
)


class TestCompanyAnalyzer:
    """Test suite for company analysis functionality."""

    @pytest.fixture
    def sample_company_data(self) -> dict:
        """Sample company data for testing."""
        return {
            "name": "TechCorp Inc.",
            "industry": "Technology",
            "size": "500-1000 employees",
            "founded": "2010",
            "location": "San Francisco, CA",
            "description": "Leading SaaS company building innovative solutions",
            "website_content": "We value innovation, diversity, and work-life balance",
            "news": [
                {
                    "title": "TechCorp raises $50M Series C",
                    "url": "https://news.com/techcorp-funding",
                    "publishedAt": "2025-10-15",
                    "source": "TechCrunch",
                },
                {
                    "title": "TechCorp wins Best Place to Work award",
                    "url": "https://news.com/techcorp-award",
                    "publishedAt": "2025-09-20",
                    "source": "Forbes",
                },
            ],
        }

    def test_analyze_company_data_success(self, sample_company_data: dict) -> None:
        """Test successful company data analysis."""
        result = analyze_company_data(sample_company_data)

        assert "overview" in result
        assert "mission_values" in result
        assert "recent_news" in result
        assert "green_flags" in result
        assert "red_flags" in result
        assert "talking_points" in result
        assert "interview_insights" in result

    def test_analyze_empty_data(self) -> None:
        """Test analysis with empty data."""
        result = analyze_company_data({})

        assert result["overview"] == {}
        assert result["green_flags"] == []
        assert result["red_flags"] == []
        assert result["talking_points"] == []

    def test_detect_green_flags_funding(self, sample_company_data: dict) -> None:
        """Test detection of funding green flags."""
        green_flags = detect_green_flags(sample_company_data)

        assert len(green_flags) > 0
        funding_flags = [f for f in green_flags if "funding" in f.lower() or "series" in f.lower()]
        assert len(funding_flags) > 0

    def test_detect_green_flags_awards(self, sample_company_data: dict) -> None:
        """Test detection of award green flags."""
        green_flags = detect_green_flags(sample_company_data)

        award_flags = [f for f in green_flags if "award" in f.lower() or "best place" in f.lower()]
        assert len(award_flags) > 0

    def test_detect_green_flags_growth(self) -> None:
        """Test detection of growth indicators."""
        data = {
            "news": [
                {
                    "title": "Company expands to 5 new markets",
                    "url": "https://example.com",
                    "publishedAt": "2025-10-01",
                    "source": "News",
                }
            ],
            "website_content": "Growing team, hiring for 50+ positions",
        }

        green_flags = detect_green_flags(data)

        growth_flags = [
            f
            for f in green_flags
            if "growth" in f.lower() or "expand" in f.lower() or "hiring" in f.lower()
        ]
        assert len(growth_flags) > 0

    def test_detect_red_flags_layoffs(self) -> None:
        """Test detection of layoff red flags."""
        data = {
            "news": [
                {
                    "title": "Company announces 20% workforce reduction",
                    "url": "https://example.com",
                    "publishedAt": "2025-10-01",
                    "source": "News",
                }
            ]
        }

        red_flags = detect_red_flags(data)

        layoff_flags = [f for f in red_flags if "layoff" in f.lower() or "reduction" in f.lower()]
        assert len(layoff_flags) > 0

    def test_detect_red_flags_lawsuits(self) -> None:
        """Test detection of lawsuit red flags."""
        data = {
            "news": [
                {
                    "title": "Company faces discrimination lawsuit",
                    "url": "https://example.com",
                    "publishedAt": "2025-09-15",
                    "source": "News",
                }
            ]
        }

        red_flags = detect_red_flags(data)

        lawsuit_flags = [f for f in red_flags if "lawsuit" in f.lower() or "legal" in f.lower()]
        assert len(lawsuit_flags) > 0

    def test_detect_red_flags_negative_reviews(self) -> None:
        """Test detection of negative review patterns."""
        data = {
            "website_content": "High turnover rate, poor management, toxic culture",
        }

        red_flags = detect_red_flags(data)

        culture_flags = [
            f
            for f in red_flags
            if "turnover" in f.lower() or "culture" in f.lower() or "management" in f.lower()
        ]
        assert len(culture_flags) > 0

    def test_detect_red_flags_empty_data(self) -> None:
        """Test red flag detection with empty data."""
        red_flags = detect_red_flags({})

        assert red_flags == []

    def test_generate_talking_points_funding(self, sample_company_data: dict) -> None:
        """Test talking point generation for funding."""
        points = generate_talking_points(sample_company_data)

        assert len(points) > 0
        assert len(points) <= 7
        funding_points = [
            p for p in points if "50M" in p or "Series C" in p or "funding" in p.lower()
        ]
        assert len(funding_points) > 0

    def test_generate_talking_points_values(self, sample_company_data: dict) -> None:
        """Test talking point generation for company values."""
        points = generate_talking_points(sample_company_data)

        value_points = [
            p
            for p in points
            if "innovation" in p.lower()
            or "diversity" in p.lower()
            or "work-life balance" in p.lower()
        ]
        assert len(value_points) > 0

    def test_generate_talking_points_limit(self, sample_company_data: dict) -> None:
        """Test that talking points are limited to 5-7."""
        points = generate_talking_points(sample_company_data)

        assert len(points) >= 5
        assert len(points) <= 7

    def test_generate_talking_points_empty_data(self) -> None:
        """Test talking point generation with minimal data."""
        points = generate_talking_points({})

        assert isinstance(points, list)

    def test_synthesize_interview_insights(self, sample_company_data: dict) -> None:
        """Test interview insights synthesis."""
        insights = synthesize_interview_insights(sample_company_data)

        assert "culture" in insights
        assert "expectations" in insights
        assert "questions_to_ask" in insights

    def test_synthesize_interview_insights_culture(self, sample_company_data: dict) -> None:
        """Test culture insights extraction."""
        insights = synthesize_interview_insights(sample_company_data)

        culture = insights["culture"]
        assert isinstance(culture, str)
        assert len(culture) > 0

    def test_synthesize_interview_insights_questions(self, sample_company_data: dict) -> None:
        """Test question generation."""
        insights = synthesize_interview_insights(sample_company_data)

        questions = insights["questions_to_ask"]
        assert isinstance(questions, list)
        assert len(questions) >= 3
        assert len(questions) <= 7

    def test_synthesize_interview_insights_expectations(self, sample_company_data: dict) -> None:
        """Test expectations extraction."""
        insights = synthesize_interview_insights(sample_company_data)

        expectations = insights["expectations"]
        assert isinstance(expectations, str)
        assert len(expectations) > 0

    def test_full_analysis_integration(self, sample_company_data: dict) -> None:
        """Test full analysis pipeline integration."""
        result = analyze_company_data(sample_company_data)

        # Verify all sections are present and properly formatted
        assert result["overview"]["name"] == "TechCorp Inc."
        assert result["overview"]["industry"] == "Technology"
        assert len(result["recent_news"]) == 2
        assert len(result["green_flags"]) > 0
        assert len(result["talking_points"]) >= 5
        assert "culture" in result["interview_insights"]

    def test_handles_partial_data(self) -> None:
        """Test analysis with partial data."""
        partial_data = {
            "name": "StartupCo",
            "website_content": "We're building the future",
        }

        result = analyze_company_data(partial_data)

        assert result["overview"]["name"] == "StartupCo"
        assert isinstance(result["green_flags"], list)
        assert isinstance(result["red_flags"], list)
        assert isinstance(result["talking_points"], list)

    def test_detect_green_flags_culture_signals(self) -> None:
        """Test detection of various culture signals."""
        data = {
            "website_content": "We offer remote work, equity, and competitive salary with focus on professional development",
        }

        green_flags = detect_green_flags(data)

        assert len(green_flags) >= 3
        assert any("remote" in flag.lower() for flag in green_flags)
        assert any("equity" in flag.lower() for flag in green_flags)

    def test_detect_red_flags_financial_trouble(self) -> None:
        """Test detection of financial trouble signals."""
        data = {
            "news": [
                {
                    "title": "Company files for bankruptcy protection",
                    "url": "https://example.com",
                    "publishedAt": "2025-10-01",
                    "source": "News",
                }
            ]
        }

        red_flags = detect_red_flags(data)

        financial_flags = [
            f for f in red_flags if "financial" in f.lower() or "bankruptcy" in f.lower()
        ]
        assert len(financial_flags) > 0

    def test_generate_talking_points_with_industry(self) -> None:
        """Test talking points generation with industry info."""
        data = {
            "name": "TechCo",
            "industry": "Artificial Intelligence",
            "website_content": "Building the future with AI",
        }

        points = generate_talking_points(data)

        assert len(points) >= 5
        assert any("artificial intelligence" in p.lower() for p in points)

    def test_synthesize_interview_insights_empty_culture(self) -> None:
        """Test interview insights with minimal data."""
        data = {"name": "MinimalCo"}

        insights = synthesize_interview_insights(data)

        assert "culture" in insights
        assert "expectations" in insights
        assert isinstance(insights["questions_to_ask"], list)
        assert len(insights["questions_to_ask"]) >= 3

    def test_synthesize_interview_insights_with_news_context(self) -> None:
        """Test interview insights with news context."""
        data = {
            "news": [
                {
                    "title": "Company launches new AI product",
                    "url": "https://example.com",
                    "publishedAt": "2025-10-15",
                    "source": "News",
                }
            ],
            "website_content": "Fast-paced innovation with product focus, ownership, impact, and collaboration",
        }

        insights = synthesize_interview_insights(data)

        assert "fast-paced" in insights["culture"].lower()
        assert len(insights["questions_to_ask"]) >= 4
        # Should have news-related question
        assert any(
            "product" in q.lower() or "ai" in q.lower() for q in insights["questions_to_ask"]
        )
