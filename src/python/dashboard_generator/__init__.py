"""
Application Dashboard Generator Module.

Generates analytics dashboards showing:
- Application pipeline metrics
- Success rates and conversion funnels
- Keyword performance analysis
- Time-based metrics
- Actionable recommendations
"""

from dashboard_generator.generator import (
    analyze_keyword_performance,
    calculate_pipeline_funnel,
    calculate_success_metrics,
    calculate_time_metrics,
    filter_applications_by_date,
    filter_applications_by_status,
    generate_dashboard,
    generate_funnel_visualization,
    generate_keyword_chart,
    generate_metrics_table,
    generate_recommendations,
    parse_date_filter,
)

__all__ = [
    "analyze_keyword_performance",
    "calculate_pipeline_funnel",
    "calculate_success_metrics",
    "calculate_time_metrics",
    "filter_applications_by_date",
    "filter_applications_by_status",
    "generate_dashboard",
    "generate_funnel_visualization",
    "generate_keyword_chart",
    "generate_metrics_table",
    "generate_recommendations",
    "parse_date_filter",
]
