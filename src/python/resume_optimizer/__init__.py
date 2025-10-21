"""Resume Optimizer Module.

Iteratively optimizes resumes to maximize ATS score for specific job descriptions.
"""

from resume_optimizer.optimizer import (
    calculate_ats_score,
    generate_resume_markdown,
    identify_keyword_gaps,
    load_anecdotes,
    optimize_iteration,
    optimize_resume_iteratively,
    parse_resume_markdown,
    reorder_experiences,
    rewrite_bullet_with_keywords,
    save_optimization_report,
    score_anecdote_relevance,
    select_diverse_anecdotes,
    select_top_anecdotes,
)

__all__ = [
    "calculate_ats_score",
    "generate_resume_markdown",
    "identify_keyword_gaps",
    "load_anecdotes",
    "optimize_iteration",
    "optimize_resume_iteratively",
    "parse_resume_markdown",
    "reorder_experiences",
    "rewrite_bullet_with_keywords",
    "save_optimization_report",
    "score_anecdote_relevance",
    "select_diverse_anecdotes",
    "select_top_anecdotes",
]
