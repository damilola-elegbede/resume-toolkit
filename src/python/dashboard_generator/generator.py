"""
Dashboard generator implementation.

Generates comprehensive analytics dashboards for job applications.
"""

import json
from datetime import datetime, timedelta
from typing import Any

# Industry benchmarks (based on typical job search metrics)
BENCHMARK_RESPONSE_RATE = 50.0  # 50% of applications get a response
BENCHMARK_INTERVIEW_RATE = 15.0  # 15% reach interview stage
BENCHMARK_OFFER_RATE = 5.0  # 5% result in offers


def calculate_pipeline_funnel(applications: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Calculate pipeline funnel metrics.

    Args:
        applications: List of application records

    Returns:
        Dict with counts, percentages, and conversion rates
    """
    if not applications:
        return {
            "total": 0,
            "applied": 0,
            "screening": 0,
            "interviewing": 0,
            "offer": 0,
            "rejected": 0,
            "withdrawn": 0,
            "accepted": 0,
            "applied_pct": 0.0,
            "screening_pct": 0.0,
            "interviewing_pct": 0.0,
            "offer_pct": 0.0,
            "rejected_pct": 0.0,
            "withdrawn_pct": 0.0,
            "accepted_pct": 0.0,
            "response_rate": 0.0,
        }

    total = len(applications)
    status_counts = {
        "applied": 0,
        "screening": 0,
        "interviewing": 0,
        "offer": 0,
        "rejected": 0,
        "withdrawn": 0,
        "accepted": 0,
    }

    for app in applications:
        status = app.get("status", "applied")
        if status in status_counts:
            status_counts[status] += 1

    # Calculate percentages
    percentages = {
        f"{status}_pct": (count / total) * 100.0 for status, count in status_counts.items()
    }

    # Calculate response rate (applications that moved beyond "applied")
    responded = total - status_counts["applied"]
    response_rate = (responded / total) * 100.0 if total > 0 else 0.0

    return {
        "total": total,
        **status_counts,
        **percentages,
        "response_rate": response_rate,
    }


def calculate_success_metrics(
    applications: list[dict[str, Any]], stages: list[dict[str, Any]]
) -> dict[str, Any]:
    """
    Calculate success rate metrics with benchmarks.

    Args:
        applications: List of application records
        stages: List of stage history records (unused but kept for compatibility)

    Returns:
        Dict with success rates and benchmark comparisons
    """
    if not applications:
        return {
            "response_rate": 0.0,
            "interview_rate": 0.0,
            "offer_rate": 0.0,
            "response_rate_benchmark": BENCHMARK_RESPONSE_RATE,
            "interview_rate_benchmark": BENCHMARK_INTERVIEW_RATE,
            "offer_rate_benchmark": BENCHMARK_OFFER_RATE,
            "response_rate_status": "average",
            "interview_rate_status": "average",
            "offer_rate_status": "average",
        }

    total = len(applications)

    # Count applications at each stage
    responded = sum(1 for app in applications if app.get("status") not in ["applied"])
    interviewed = sum(
        1 for app in applications if app.get("status") in ["interviewing", "offer", "accepted"]
    )
    offered = sum(1 for app in applications if app.get("status") in ["offer", "accepted"])

    # Calculate rates
    response_rate = (responded / total) * 100.0 if total > 0 else 0.0
    interview_rate = (interviewed / total) * 100.0 if total > 0 else 0.0
    offer_rate = (offered / total) * 100.0 if total > 0 else 0.0

    # Compare to benchmarks
    def get_status(rate: float, benchmark: float) -> str:
        if rate >= benchmark * 1.1:  # 10% above
            return "above"
        if rate <= benchmark * 0.9:  # 10% below
            return "below"
        return "average"

    return {
        "response_rate": response_rate,
        "interview_rate": interview_rate,
        "offer_rate": offer_rate,
        "response_rate_benchmark": BENCHMARK_RESPONSE_RATE,
        "interview_rate_benchmark": BENCHMARK_INTERVIEW_RATE,
        "offer_rate_benchmark": BENCHMARK_OFFER_RATE,
        "response_rate_status": get_status(response_rate, BENCHMARK_RESPONSE_RATE),
        "interview_rate_status": get_status(interview_rate, BENCHMARK_INTERVIEW_RATE),
        "offer_rate_status": get_status(offer_rate, BENCHMARK_OFFER_RATE),
    }


def calculate_time_metrics(
    applications: list[dict[str, Any]], stages: list[dict[str, Any]]
) -> dict[str, float]:
    """
    Calculate average time spent at each stage.

    Args:
        applications: List of application records
        stages: List of stage history records

    Returns:
        Dict with average times in days
    """
    if not stages:
        return {
            "avg_response_time_days": 0.0,
            "avg_time_to_interview_days": 0.0,
            "avg_time_to_offer_days": 0.0,
        }

    # Group stages by application
    app_stages: dict[int, list[dict[str, Any]]] = {}
    for stage in stages:
        app_id = stage["application_id"]
        if app_id not in app_stages:
            app_stages[app_id] = []
        app_stages[app_id].append(stage)

    # Calculate time deltas
    response_times = []
    interview_times = []
    offer_times = []

    for app_id, app_stage_list in app_stages.items():
        # Sort by date
        sorted_stages = sorted(app_stage_list, key=lambda s: s["stage_date"])

        if not sorted_stages:
            continue

        applied_date = None
        screening_date = None
        interview_date = None
        offer_date = None

        for stage in sorted_stages:
            status = stage["status"]
            date = datetime.fromisoformat(stage["stage_date"])

            if status == "applied":
                applied_date = date
            elif status == "screening" and not screening_date:
                screening_date = date
            elif status == "interviewing" and not interview_date:
                interview_date = date
            elif status == "offer" and not offer_date:
                offer_date = date

        # Calculate deltas
        if applied_date and screening_date:
            response_times.append((screening_date - applied_date).days)

        if applied_date and interview_date:
            interview_times.append((interview_date - applied_date).days)

        if applied_date and offer_date:
            offer_times.append((offer_date - applied_date).days)

    return {
        "avg_response_time_days": sum(response_times) / len(response_times)
        if response_times
        else 0.0,
        "avg_time_to_interview_days": sum(interview_times) / len(interview_times)
        if interview_times
        else 0.0,
        "avg_time_to_offer_days": sum(offer_times) / len(offer_times) if offer_times else 0.0,
    }


def analyze_keyword_performance(keyword_performance: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Analyze keyword effectiveness.

    Args:
        keyword_performance: List of keyword performance records

    Returns:
        Dict with ranked keywords and analysis
    """
    if not keyword_performance:
        return {
            "top_keywords_by_response": [],
            "high_performers": [],
            "low_performers": [],
            "combinations": [],
        }

    # Sort by response rate
    sorted_keywords = sorted(keyword_performance, key=lambda k: k["response_rate"], reverse=True)

    # Identify high and low performers
    high_performers = [kw for kw in sorted_keywords if kw["response_rate"] >= 70.0]
    low_performers = [kw for kw in sorted_keywords if kw["response_rate"] < 50.0]

    return {
        "top_keywords_by_response": sorted_keywords,
        "high_performers": high_performers,
        "low_performers": low_performers,
        "combinations": [],  # Could be enhanced to identify keyword pairs
    }


def generate_funnel_visualization(applications: list[dict[str, Any]], color: bool = False) -> str:
    """
    Generate ASCII funnel visualization.

    Args:
        applications: List of application records
        color: Whether to include ANSI color codes (optional)

    Returns:
        ASCII art string
    """
    funnel = calculate_pipeline_funnel(applications)

    if funnel["total"] == 0:
        return "No applications to display.\n"

    total = funnel["total"]
    max_width = 50

    def make_bar(count: int, percentage: float) -> str:
        width = int((count / total) * max_width) if total > 0 else 0
        bar = "█" * width
        return f"{bar} {count} ({percentage:.0f}%)"

    lines = [
        "Application Pipeline",
        "=" * 60,
        "",
        f"Total Applications: {total}",
        f"├─ Applied:       {make_bar(funnel['applied'], funnel['applied_pct'])}",
        f"├─ Screening:     {make_bar(funnel['screening'], funnel['screening_pct'])}",
        f"├─ Interview:     {make_bar(funnel['interviewing'], funnel['interviewing_pct'])}",
        f"├─ Offer:         {make_bar(funnel['offer'], funnel['offer_pct'])}",
        f"└─ Rejected:      {make_bar(funnel['rejected'], funnel['rejected_pct'])}",
        "",
    ]

    return "\n".join(lines)


def generate_metrics_table(applications: list[dict[str, Any]], stages: list[dict[str, Any]]) -> str:
    """
    Generate success metrics table.

    Args:
        applications: List of application records
        stages: List of stage history records

    Returns:
        Formatted table string
    """
    metrics = calculate_success_metrics(applications, stages)

    def format_metric(rate: float, benchmark: float, status: str) -> str:
        symbol = "✓" if status == "above" else "→" if status == "average" else "✗"
        return f"{rate:.0f}%  {symbol} {status.capitalize()} ({benchmark:.0f}%)"

    lines = [
        "Success Metrics:",
        f"- Response Rate:  {format_metric(metrics['response_rate'], metrics['response_rate_benchmark'], metrics['response_rate_status'])}",
        f"- Interview Rate: {format_metric(metrics['interview_rate'], metrics['interview_rate_benchmark'], metrics['interview_rate_status'])}",
        f"- Offer Rate:     {format_metric(metrics['offer_rate'], metrics['offer_rate_benchmark'], metrics['offer_rate_status'])}",
        "",
    ]

    return "\n".join(lines)


def generate_keyword_chart(keyword_performance: list[dict[str, Any]]) -> str:
    """
    Generate keyword performance chart.

    Args:
        keyword_performance: List of keyword performance records

    Returns:
        Formatted chart string
    """
    analysis = analyze_keyword_performance(keyword_performance)

    if not analysis["top_keywords_by_response"]:
        return "No keyword data available.\n"

    lines = [
        "Top Keywords (by response rate):",
    ]

    for i, kw in enumerate(analysis["top_keywords_by_response"][:10], 1):
        usage = f"({kw['response_count']}/{kw['total_uses']} responses)"
        lines.append(f"{i}. {kw['keyword']:30s} - {kw['response_rate']:.0f}% {usage}")

    lines.append("")
    return "\n".join(lines)


def generate_recommendations(
    funnel: dict[str, Any],
    metrics: dict[str, Any],
    keyword_analysis: dict[str, Any],
    time_metrics: dict[str, float],
) -> list[str]:
    """
    Generate actionable recommendations.

    Args:
        funnel: Pipeline funnel data
        metrics: Success metrics
        keyword_analysis: Keyword performance analysis
        time_metrics: Time-based metrics

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # Keyword recommendations
    if keyword_analysis and "high_performers" in keyword_analysis:
        high_performers = keyword_analysis["high_performers"]
        if high_performers:
            top_keyword = high_performers[0]["keyword"]
            top_rate = high_performers[0]["response_rate"]
            recommendations.append(
                f"→ Emphasize '{top_keyword}' in future applications - {top_rate:.0f}% response rate"
            )

    # Conversion recommendations
    if metrics:
        response_rate = metrics.get("response_rate", 0)
        interview_rate = metrics.get("interview_rate", 0)
        offer_rate = metrics.get("offer_rate", 0)

        if response_rate < 50:
            recommendations.append(
                "→ Response rate below average - review resume keywords and formatting"
            )
        elif interview_rate > 25:
            recommendations.append(
                "→ Your interview conversion is strong - focus on getting more interviews"
            )

        if interview_rate < 15 and response_rate > 50:
            recommendations.append(
                "→ Strong response rate but low interview rate - improve screening call performance"
            )

    # Timing recommendations
    if time_metrics:
        avg_response = time_metrics.get("avg_response_time_days", 0)
        if avg_response > 0:
            followup_days = int(avg_response + 2)
            recommendations.append(
                f"→ Consider following up after {followup_days} days if no response"
            )

    # Generic recommendations if none generated
    if not recommendations:
        recommendations.append("→ Continue applying consistently and track your progress")

    return recommendations


def filter_applications_by_date(
    applications: list[dict[str, Any]], start_date: str, end_date: str
) -> list[dict[str, Any]]:
    """
    Filter applications by date range.

    Args:
        applications: List of application records
        start_date: ISO format start date
        end_date: ISO format end date

    Returns:
        Filtered list of applications
    """
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    filtered = []
    for app in applications:
        app_date = datetime.fromisoformat(app["applied_date"])
        if start <= app_date <= end:
            filtered.append(app)

    return filtered


def filter_applications_by_status(
    applications: list[dict[str, Any]],
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Filter applications by status.

    Args:
        applications: List of application records
        include: List of statuses to include (if None, include all)
        exclude: List of statuses to exclude

    Returns:
        Filtered list of applications
    """
    filtered = []

    for app in applications:
        status = app.get("status", "applied")

        if exclude and status in exclude:
            continue

        if include is None or status in include:
            filtered.append(app)

    return filtered


def parse_date_filter(filter_string: str | None) -> tuple[str | None, str | None]:
    """
    Parse date filter string into start and end dates.

    Args:
        filter_string: Filter like "last 3 months", "last 30 days", "this year", or "YYYY-MM-DD:YYYY-MM-DD"

    Returns:
        Tuple of (start_date, end_date) in ISO format
    """
    if not filter_string:
        return (None, None)

    today = datetime.now()

    # Handle "last N months"
    if "last" in filter_string and "month" in filter_string:
        parts = filter_string.split()
        try:
            n_months = int(parts[1])
            start_date = today - timedelta(days=n_months * 30)
            return (start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
        except (IndexError, ValueError):
            pass

    # Handle "last N days"
    if "last" in filter_string and "day" in filter_string:
        parts = filter_string.split()
        try:
            n_days = int(parts[1])
            start_date = today - timedelta(days=n_days)
            return (start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
        except (IndexError, ValueError):
            pass

    # Handle "this year"
    if "this year" in filter_string:
        start_date = datetime(today.year, 1, 1)
        return (start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))

    # Handle custom range "YYYY-MM-DD:YYYY-MM-DD"
    if ":" in filter_string:
        parts = filter_string.split(":")
        if len(parts) == 2:
            return (parts[0], parts[1])

    return (None, None)


def generate_dashboard(
    applications: list[dict[str, Any]],
    stages: list[dict[str, Any]],
    keyword_performance: list[dict[str, Any]],
    format: str = "terminal",
    date_filter: str | None = None,
) -> str:
    """
    Generate complete dashboard.

    Args:
        applications: List of application records
        stages: List of stage history records
        keyword_performance: List of keyword performance records
        format: Output format ("terminal", "markdown", "json")
        date_filter: Optional date filter string

    Returns:
        Formatted dashboard string
    """
    # Apply date filter if specified
    if date_filter:
        start_date, end_date = parse_date_filter(date_filter)
        if start_date and end_date:
            applications = filter_applications_by_date(applications, start_date, end_date)
            # Also filter stages
            stages = [
                s for s in stages if s["application_id"] in [app["id"] for app in applications]
            ]

    # Calculate all metrics
    funnel = calculate_pipeline_funnel(applications)
    metrics = calculate_success_metrics(applications, stages)
    time_metrics = calculate_time_metrics(applications, stages)
    keyword_analysis = analyze_keyword_performance(keyword_performance)

    # Generate recommendations
    recommendations = generate_recommendations(funnel, metrics, keyword_analysis, time_metrics)

    # Format output
    if format == "json":
        return json.dumps(
            {
                "funnel": funnel,
                "metrics": metrics,
                "time_metrics": time_metrics,
                "keywords": keyword_analysis["top_keywords_by_response"],
                "recommendations": recommendations,
            },
            indent=2,
        )

    # Terminal or markdown format
    sections = [
        "Application Pipeline Dashboard",
        "=" * 60,
        "",
        generate_funnel_visualization(applications),
        generate_metrics_table(applications, stages),
    ]

    # Time analysis
    if time_metrics["avg_response_time_days"] > 0:
        sections.append("Time Analysis:")
        sections.append(
            f"- Avg time to response:  {time_metrics['avg_response_time_days']:.1f} days"
        )
        if time_metrics["avg_time_to_interview_days"] > 0:
            sections.append(
                f"- Avg time to interview: {time_metrics['avg_time_to_interview_days']:.1f} days"
            )
        if time_metrics["avg_time_to_offer_days"] > 0:
            sections.append(
                f"- Avg time to offer:     {time_metrics['avg_time_to_offer_days']:.1f} days"
            )
        sections.append("")

    # Keywords
    sections.append(generate_keyword_chart(keyword_performance))

    # Recommendations
    if recommendations:
        sections.append("Recommendations:")
        for rec in recommendations:
            sections.append(rec)
        sections.append("")

    return "\n".join(sections)
