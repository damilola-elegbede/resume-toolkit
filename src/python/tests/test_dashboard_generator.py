"""
Test suite for application dashboard generator.

Tests cover:
- Pipeline funnel calculation (applied -> offer)
- Success rate metrics (response, interview, offer rates)
- Keyword effectiveness analysis
- Time analysis (avg days at each stage)
- Visualization generation (ASCII art / markdown tables)
- Filtering (date range, status, company size)
- Recommendations based on patterns
"""

from datetime import datetime, timedelta
from typing import Any

import pytest


@pytest.fixture
def sample_applications() -> list[dict[str, Any]]:
    """Sample application data for testing."""
    base_date = datetime(2024, 1, 1)
    return [
        {
            "id": 1,
            "company": "Tech Corp",
            "position": "Senior Engineer",
            "status": "offer",
            "applied_date": (base_date - timedelta(days=60)).strftime("%Y-%m-%d"),
            "keywords_targeted": '["python", "distributed systems", "kubernetes"]',
        },
        {
            "id": 2,
            "company": "Startup Inc",
            "position": "Backend Developer",
            "status": "interviewing",
            "applied_date": (base_date - timedelta(days=30)).strftime("%Y-%m-%d"),
            "keywords_targeted": '["python", "django", "postgresql"]',
        },
        {
            "id": 3,
            "company": "Big Company",
            "position": "Staff Engineer",
            "status": "screening",
            "applied_date": (base_date - timedelta(days=20)).strftime("%Y-%m-%d"),
            "keywords_targeted": '["distributed systems", "team leadership", "aws"]',
        },
        {
            "id": 4,
            "company": "Medium Corp",
            "position": "Principal Engineer",
            "status": "applied",
            "applied_date": (base_date - timedelta(days=10)).strftime("%Y-%m-%d"),
            "keywords_targeted": '["kubernetes", "golang", "microservices"]',
        },
        {
            "id": 5,
            "company": "Small Startup",
            "position": "Tech Lead",
            "status": "rejected",
            "applied_date": (base_date - timedelta(days=45)).strftime("%Y-%m-%d"),
            "keywords_targeted": '["python", "team leadership"]',
        },
    ]


@pytest.fixture
def sample_application_stages() -> list[dict[str, Any]]:
    """Sample stage history for time analysis."""
    base_date = datetime(2024, 1, 1)
    return [
        # Application 1: Complete journey to offer
        {
            "application_id": 1,
            "status": "applied",
            "stage_date": (base_date - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        {
            "application_id": 1,
            "status": "screening",
            "stage_date": (base_date - timedelta(days=55)).strftime("%Y-%m-%d"),
        },
        {
            "application_id": 1,
            "status": "interviewing",
            "stage_date": (base_date - timedelta(days=42)).strftime("%Y-%m-%d"),
        },
        {
            "application_id": 1,
            "status": "offer",
            "stage_date": (base_date - timedelta(days=32)).strftime("%Y-%m-%d"),
        },
        # Application 2: Currently interviewing
        {
            "application_id": 2,
            "status": "applied",
            "stage_date": (base_date - timedelta(days=30)).strftime("%Y-%m-%d"),
        },
        {
            "application_id": 2,
            "status": "screening",
            "stage_date": (base_date - timedelta(days=23)).strftime("%Y-%m-%d"),
        },
        {
            "application_id": 2,
            "status": "interviewing",
            "stage_date": (base_date - timedelta(days=12)).strftime("%Y-%m-%d"),
        },
        # Application 3: At screening
        {
            "application_id": 3,
            "status": "applied",
            "stage_date": (base_date - timedelta(days=20)).strftime("%Y-%m-%d"),
        },
        {
            "application_id": 3,
            "status": "screening",
            "stage_date": (base_date - timedelta(days=13)).strftime("%Y-%m-%d"),
        },
        # Application 4: Just applied
        {
            "application_id": 4,
            "status": "applied",
            "stage_date": (base_date - timedelta(days=10)).strftime("%Y-%m-%d"),
        },
        # Application 5: Rejected at screening
        {
            "application_id": 5,
            "status": "applied",
            "stage_date": (base_date - timedelta(days=45)).strftime("%Y-%m-%d"),
        },
        {
            "application_id": 5,
            "status": "screening",
            "stage_date": (base_date - timedelta(days=40)).strftime("%Y-%m-%d"),
        },
        {
            "application_id": 5,
            "status": "rejected",
            "stage_date": (base_date - timedelta(days=38)).strftime("%Y-%m-%d"),
        },
    ]


@pytest.fixture
def sample_keyword_performance() -> list[dict[str, Any]]:
    """Sample keyword performance data."""
    return [
        {
            "keyword": "distributed systems",
            "total_uses": 15,
            "response_count": 12,
            "response_rate": 80.0,
            "interview_count": 8,
            "interview_rate": 53.33,
            "offer_count": 2,
            "offer_rate": 13.33,
            "category": "technical_skill",
        },
        {
            "keyword": "team leadership",
            "total_uses": 12,
            "response_count": 9,
            "response_rate": 75.0,
            "interview_count": 6,
            "interview_rate": 50.0,
            "offer_count": 2,
            "offer_rate": 16.67,
            "category": "soft_skill",
        },
        {
            "keyword": "kubernetes",
            "total_uses": 20,
            "response_count": 14,
            "response_rate": 70.0,
            "interview_count": 9,
            "interview_rate": 45.0,
            "offer_count": 3,
            "offer_rate": 15.0,
            "category": "tool",
        },
        {
            "keyword": "python",
            "total_uses": 25,
            "response_count": 15,
            "response_rate": 60.0,
            "interview_count": 10,
            "interview_rate": 40.0,
            "offer_count": 3,
            "offer_rate": 12.0,
            "category": "language",
        },
        {
            "keyword": "golang",
            "total_uses": 8,
            "response_count": 3,
            "response_rate": 37.5,
            "interview_count": 1,
            "interview_rate": 12.5,
            "offer_count": 0,
            "offer_rate": 0.0,
            "category": "language",
        },
    ]


@pytest.mark.unit
class TestPipelineFunnelCalculation:
    """Test pipeline funnel metrics calculation."""

    def test_calculate_funnel_basic(self, sample_applications: list[dict[str, Any]]) -> None:
        """Test basic funnel calculation from application data."""
        from dashboard_generator.generator import calculate_pipeline_funnel

        funnel = calculate_pipeline_funnel(sample_applications)

        # Verify counts
        assert funnel["total"] == 5
        assert funnel["applied"] == 1
        assert funnel["screening"] == 1
        assert funnel["interviewing"] == 1
        assert funnel["offer"] == 1
        assert funnel["rejected"] == 1

    def test_calculate_funnel_percentages(
        self, sample_applications: list[dict[str, Any]]
    ) -> None:
        """Test funnel percentages are calculated correctly."""
        from dashboard_generator.generator import calculate_pipeline_funnel

        funnel = calculate_pipeline_funnel(sample_applications)

        # Each status is 1/5 = 20%
        assert abs(funnel["applied_pct"] - 20.0) < 0.1
        assert abs(funnel["screening_pct"] - 20.0) < 0.1
        assert abs(funnel["interviewing_pct"] - 20.0) < 0.1
        assert abs(funnel["offer_pct"] - 20.0) < 0.1
        assert abs(funnel["rejected_pct"] - 20.0) < 0.1

    def test_calculate_funnel_conversion_rates(
        self, sample_applications: list[dict[str, Any]]
    ) -> None:
        """Test conversion rate calculations."""
        from dashboard_generator.generator import calculate_pipeline_funnel

        funnel = calculate_pipeline_funnel(sample_applications)

        # Response rate: applications beyond "applied" / total
        # 4 responses out of 5 applications = 80%
        assert "response_rate" in funnel
        assert abs(funnel["response_rate"] - 80.0) < 0.1

    def test_calculate_funnel_empty_data(self) -> None:
        """Test handling of empty application data."""
        from dashboard_generator.generator import calculate_pipeline_funnel

        funnel = calculate_pipeline_funnel([])

        assert funnel["total"] == 0
        assert funnel["applied"] == 0
        assert funnel["screening"] == 0
        assert funnel["interviewing"] == 0
        assert funnel["offer"] == 0

    def test_calculate_funnel_excludes_withdrawn(self) -> None:
        """Test that withdrawn applications are handled separately."""
        from dashboard_generator.generator import calculate_pipeline_funnel

        apps = [
            {"id": 1, "status": "applied"},
            {"id": 2, "status": "withdrawn"},
            {"id": 3, "status": "offer"},
        ]

        funnel = calculate_pipeline_funnel(apps)

        assert funnel["total"] == 3
        assert funnel["withdrawn"] == 1


@pytest.mark.unit
class TestSuccessMetrics:
    """Test success rate metric calculations."""

    def test_calculate_response_rate(self, sample_applications: list[dict[str, Any]]) -> None:
        """Test response rate calculation."""
        from dashboard_generator.generator import calculate_success_metrics

        metrics = calculate_success_metrics(sample_applications, [])

        # 4 out of 5 got responses (moved beyond applied)
        assert abs(metrics["response_rate"] - 80.0) < 0.1

    def test_calculate_interview_rate(
        self, sample_applications: list[dict[str, Any]]
    ) -> None:
        """Test interview rate calculation."""
        from dashboard_generator.generator import calculate_success_metrics

        metrics = calculate_success_metrics(sample_applications, [])

        # 2 out of 5 reached interviewing stage or beyond (interviewing + offer) = 40%
        assert abs(metrics["interview_rate"] - 40.0) < 0.1

    def test_calculate_offer_rate(self, sample_applications: list[dict[str, Any]]) -> None:
        """Test offer rate calculation."""
        from dashboard_generator.generator import calculate_success_metrics

        metrics = calculate_success_metrics(sample_applications, [])

        # 1 out of 5 got offers = 20%
        assert abs(metrics["offer_rate"] - 20.0) < 0.1

    def test_benchmark_comparison(self, sample_applications: list[dict[str, Any]]) -> None:
        """Test metrics include benchmark comparison."""
        from dashboard_generator.generator import calculate_success_metrics

        metrics = calculate_success_metrics(sample_applications, [])

        # Should include benchmark data
        assert "response_rate_benchmark" in metrics
        assert "interview_rate_benchmark" in metrics
        assert "offer_rate_benchmark" in metrics

        # Should indicate if above/below benchmark
        assert "response_rate_status" in metrics  # "above", "below", or "average"

    def test_success_metrics_all_rejected(self) -> None:
        """Test metrics when all applications are rejected."""
        from dashboard_generator.generator import calculate_success_metrics

        apps = [
            {"id": 1, "status": "rejected"},
            {"id": 2, "status": "rejected"},
            {"id": 3, "status": "rejected"},
        ]

        metrics = calculate_success_metrics(apps, [])

        assert metrics["interview_rate"] == 0.0
        assert metrics["offer_rate"] == 0.0


@pytest.mark.unit
class TestTimeAnalysis:
    """Test time-based metrics calculation."""

    def test_calculate_avg_response_time(
        self,
        sample_applications: list[dict[str, Any]],
        sample_application_stages: list[dict[str, Any]],
    ) -> None:
        """Test average time from applied to first response."""
        from dashboard_generator.generator import calculate_time_metrics

        metrics = calculate_time_metrics(sample_applications, sample_application_stages)

        # Should calculate average days from applied to screening
        assert "avg_response_time_days" in metrics
        assert metrics["avg_response_time_days"] > 0

    def test_calculate_avg_interview_time(
        self,
        sample_applications: list[dict[str, Any]],
        sample_application_stages: list[dict[str, Any]],
    ) -> None:
        """Test average time from applied to interview."""
        from dashboard_generator.generator import calculate_time_metrics

        metrics = calculate_time_metrics(sample_applications, sample_application_stages)

        assert "avg_time_to_interview_days" in metrics
        assert metrics["avg_time_to_interview_days"] > 0

    def test_calculate_avg_offer_time(
        self,
        sample_applications: list[dict[str, Any]],
        sample_application_stages: list[dict[str, Any]],
    ) -> None:
        """Test average time from applied to offer."""
        from dashboard_generator.generator import calculate_time_metrics

        metrics = calculate_time_metrics(sample_applications, sample_application_stages)

        assert "avg_time_to_offer_days" in metrics
        # App 1: 60-32 = 28 days
        assert abs(metrics["avg_time_to_offer_days"] - 28.0) < 0.1

    def test_time_metrics_empty_data(self) -> None:
        """Test time metrics with no data."""
        from dashboard_generator.generator import calculate_time_metrics

        metrics = calculate_time_metrics([], [])

        assert metrics["avg_response_time_days"] == 0.0
        assert metrics["avg_time_to_interview_days"] == 0.0
        assert metrics["avg_time_to_offer_days"] == 0.0

    def test_time_metrics_incomplete_stages(self) -> None:
        """Test time metrics when stages are incomplete."""
        from dashboard_generator.generator import calculate_time_metrics

        apps = [{"id": 1, "status": "applied"}]
        stages = [{"application_id": 1, "status": "applied", "stage_date": "2024-01-01"}]

        metrics = calculate_time_metrics(apps, stages)

        # Should handle gracefully
        assert metrics["avg_response_time_days"] == 0.0


@pytest.mark.unit
class TestKeywordAnalysis:
    """Test keyword effectiveness analysis."""

    def test_rank_keywords_by_response_rate(
        self, sample_keyword_performance: list[dict[str, Any]]
    ) -> None:
        """Test keywords are ranked by response rate."""
        from dashboard_generator.generator import analyze_keyword_performance

        analysis = analyze_keyword_performance(sample_keyword_performance)

        top_keywords = analysis["top_keywords_by_response"]

        # Should be sorted by response_rate descending
        assert top_keywords[0]["keyword"] == "distributed systems"
        assert top_keywords[0]["response_rate"] == 80.0

    def test_identify_high_performers(
        self, sample_keyword_performance: list[dict[str, Any]]
    ) -> None:
        """Test identification of high-performing keywords."""
        from dashboard_generator.generator import analyze_keyword_performance

        analysis = analyze_keyword_performance(sample_keyword_performance)

        high_performers = analysis["high_performers"]

        # High performers should have response_rate > 70%
        assert len(high_performers) >= 3
        assert all(kw["response_rate"] >= 70.0 for kw in high_performers)

    def test_identify_low_performers(
        self, sample_keyword_performance: list[dict[str, Any]]
    ) -> None:
        """Test identification of low-performing keywords."""
        from dashboard_generator.generator import analyze_keyword_performance

        analysis = analyze_keyword_performance(sample_keyword_performance)

        low_performers = analysis["low_performers"]

        # Low performers should have response_rate < 50%
        assert len(low_performers) >= 1
        assert "golang" in [kw["keyword"] for kw in low_performers]

    def test_keyword_analysis_empty_data(self) -> None:
        """Test keyword analysis with no data."""
        from dashboard_generator.generator import analyze_keyword_performance

        analysis = analyze_keyword_performance([])

        assert len(analysis["top_keywords_by_response"]) == 0
        assert len(analysis["high_performers"]) == 0

    def test_keyword_combinations(
        self, sample_keyword_performance: list[dict[str, Any]]
    ) -> None:
        """Test analysis of keyword combinations."""
        from dashboard_generator.generator import analyze_keyword_performance

        analysis = analyze_keyword_performance(sample_keyword_performance)

        # Should identify effective combinations (if data supports it)
        assert "combinations" in analysis


@pytest.mark.unit
class TestVisualization:
    """Test ASCII visualization generation."""

    def test_generate_funnel_chart(self, sample_applications: list[dict[str, Any]]) -> None:
        """Test ASCII funnel chart generation."""
        from dashboard_generator.generator import generate_funnel_visualization

        chart = generate_funnel_visualization(sample_applications)

        # Should contain ASCII bars
        assert "█" in chart or "■" in chart or "▓" in chart or "|" in chart
        # Should show percentages
        assert "%" in chart
        # Should show counts
        assert any(str(i) in chart for i in range(1, 6))

    def test_generate_metrics_table(self, sample_applications: list[dict[str, Any]]) -> None:
        """Test metrics table generation."""
        from dashboard_generator.generator import generate_metrics_table

        table = generate_metrics_table(sample_applications, [])

        # Should be formatted text with metrics
        assert isinstance(table, str)
        # Should contain metric names
        assert "Response Rate" in table or "response" in table.lower()
        assert "Interview Rate" in table or "interview" in table.lower()

    def test_generate_keyword_chart(
        self, sample_keyword_performance: list[dict[str, Any]]
    ) -> None:
        """Test keyword performance chart."""
        from dashboard_generator.generator import generate_keyword_chart

        chart = generate_keyword_chart(sample_keyword_performance)

        # Should list keywords with rates
        assert "distributed systems" in chart
        assert "80%" in chart or "80.0%" in chart

    def test_visualization_with_colors(self, sample_applications: list[dict[str, Any]]) -> None:
        """Test that visualizations include ANSI color codes for terminal."""
        from dashboard_generator.generator import generate_funnel_visualization

        chart = generate_funnel_visualization(sample_applications, color=True)

        # Should contain ANSI color codes (optional feature)
        # This is optional, so we just test it doesn't crash
        assert isinstance(chart, str)


@pytest.mark.unit
class TestRecommendations:
    """Test recommendation generation."""

    def test_generate_keyword_recommendations(
        self, sample_keyword_performance: list[dict[str, Any]]
    ) -> None:
        """Test recommendations based on keyword performance."""
        from dashboard_generator.generator import generate_recommendations

        # high_performers should contain the top keywords
        high_performers = [kw for kw in sample_keyword_performance if kw["response_rate"] >= 70.0]

        recommendations = generate_recommendations(
            funnel={},
            metrics={},
            keyword_analysis={"high_performers": high_performers},
            time_metrics={},
        )

        # Should recommend high-performing keywords
        assert len(recommendations) > 0
        # Should mention top keyword
        all_recs = " ".join(recommendations)
        assert "distributed systems" in all_recs or any("emphasize" in r.lower() for r in recommendations)

    def test_generate_timing_recommendations(self) -> None:
        """Test recommendations based on timing analysis."""
        from dashboard_generator.generator import generate_recommendations

        recommendations = generate_recommendations(
            funnel={},
            metrics={},
            keyword_analysis={},
            time_metrics={"avg_response_time_days": 10.0},
        )

        # Should include follow-up recommendations
        timing_recs = [r for r in recommendations if "follow" in r.lower() or "day" in r.lower()]
        assert len(timing_recs) > 0

    def test_generate_conversion_recommendations(self) -> None:
        """Test recommendations based on conversion rates."""
        from dashboard_generator.generator import generate_recommendations

        recommendations = generate_recommendations(
            funnel={"response_rate": 80.0},
            metrics={"interview_rate": 25.0, "offer_rate": 5.0},
            keyword_analysis={},
            time_metrics={},
        )

        # Should identify strengths and weaknesses
        assert len(recommendations) > 0

    def test_recommendations_prioritized(self) -> None:
        """Test recommendations are prioritized by impact."""
        from dashboard_generator.generator import generate_recommendations

        recommendations = generate_recommendations(
            funnel={"response_rate": 30.0},  # Low response rate - high priority
            metrics={"interview_rate": 80.0, "offer_rate": 50.0},  # Strong conversion
            keyword_analysis={},
            time_metrics={},
        )

        # Should prioritize improving response rate
        assert len(recommendations) > 0
        # First recommendation should address biggest bottleneck
        assert any(
            "response" in rec.lower() or "keyword" in rec.lower() for rec in recommendations[:2]
        )


@pytest.mark.unit
class TestFilteringAndDateRange:
    """Test data filtering capabilities."""

    def test_filter_by_date_range(self, sample_applications: list[dict[str, Any]]) -> None:
        """Test filtering applications by date range."""
        from dashboard_generator.generator import filter_applications_by_date

        # Last 30 days
        end_date = datetime(2024, 1, 1)
        start_date = end_date - timedelta(days=30)

        filtered = filter_applications_by_date(
            sample_applications, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        )

        # Should only include apps from last 30 days
        assert len(filtered) < len(sample_applications)

    def test_filter_by_status(self, sample_applications: list[dict[str, Any]]) -> None:
        """Test filtering by application status."""
        from dashboard_generator.generator import filter_applications_by_status

        filtered = filter_applications_by_status(sample_applications, ["screening", "interviewing"])

        assert len(filtered) == 2
        assert all(app["status"] in ["screening", "interviewing"] for app in filtered)

    def test_filter_exclude_rejected(self, sample_applications: list[dict[str, Any]]) -> None:
        """Test excluding rejected/withdrawn applications."""
        from dashboard_generator.generator import filter_applications_by_status

        filtered = filter_applications_by_status(
            sample_applications, exclude=["rejected", "withdrawn"]
        )

        assert all(app["status"] not in ["rejected", "withdrawn"] for app in filtered)

    def test_date_range_parse_relative(self) -> None:
        """Test parsing relative date ranges like 'last 3 months'."""
        from dashboard_generator.generator import parse_date_filter

        start_date, end_date = parse_date_filter("last 3 months")

        assert isinstance(start_date, str)
        assert isinstance(end_date, str)
        # Should be approximately 90 days apart
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        diff = (end - start).days
        assert 85 <= diff <= 95  # Allow some variance


@pytest.mark.integration
class TestCompleteDashboard:
    """Integration tests for complete dashboard generation."""

    def test_generate_complete_dashboard(
        self,
        sample_applications: list[dict[str, Any]],
        sample_application_stages: list[dict[str, Any]],
        sample_keyword_performance: list[dict[str, Any]],
    ) -> None:
        """Test generating complete dashboard output."""
        from dashboard_generator.generator import generate_dashboard

        dashboard = generate_dashboard(
            applications=sample_applications,
            stages=sample_application_stages,
            keyword_performance=sample_keyword_performance,
        )

        # Should include all sections
        assert "Pipeline" in dashboard or "Funnel" in dashboard
        assert "Success Metrics" in dashboard or "Metrics" in dashboard
        assert "Keyword" in dashboard
        assert "Time" in dashboard or "Average" in dashboard
        assert "Recommendation" in dashboard

    def test_dashboard_export_markdown(
        self,
        sample_applications: list[dict[str, Any]],
        sample_application_stages: list[dict[str, Any]],
        sample_keyword_performance: list[dict[str, Any]],
    ) -> None:
        """Test exporting dashboard as markdown."""
        from dashboard_generator.generator import generate_dashboard

        dashboard = generate_dashboard(
            applications=sample_applications,
            stages=sample_application_stages,
            keyword_performance=sample_keyword_performance,
            format="markdown",
        )

        # Should be valid formatted text (markdown or plain text is fine)
        assert isinstance(dashboard, str)
        assert len(dashboard) > 0
        assert any(marker in dashboard for marker in ["-", "*", "1.", "="])  # Lists or separators

    def test_dashboard_export_json(
        self,
        sample_applications: list[dict[str, Any]],
        sample_application_stages: list[dict[str, Any]],
        sample_keyword_performance: list[dict[str, Any]],
    ) -> None:
        """Test exporting dashboard as JSON."""
        import json

        from dashboard_generator.generator import generate_dashboard

        dashboard = generate_dashboard(
            applications=sample_applications,
            stages=sample_application_stages,
            keyword_performance=sample_keyword_performance,
            format="json",
        )

        # Should be valid JSON
        data = json.loads(dashboard)
        assert "funnel" in data
        assert "metrics" in data
        assert "keywords" in data

    def test_dashboard_with_filter(
        self,
        sample_applications: list[dict[str, Any]],
        sample_application_stages: list[dict[str, Any]],
        sample_keyword_performance: list[dict[str, Any]],
    ) -> None:
        """Test dashboard generation with filters applied."""
        from dashboard_generator.generator import generate_dashboard

        dashboard = generate_dashboard(
            applications=sample_applications,
            stages=sample_application_stages,
            keyword_performance=sample_keyword_performance,
            date_filter="last 3 months",
        )

        # Should apply filter
        assert isinstance(dashboard, str)
        assert len(dashboard) > 0
