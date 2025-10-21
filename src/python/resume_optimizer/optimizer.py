"""Resume Optimization Engine.

Provides iterative resume optimization to maximize ATS scores through:
- Intelligent anecdote selection
- Natural keyword integration
- Section ordering optimization
- Iterative improvement with feedback loops
"""

import re
from pathlib import Path
from typing import Any

import yaml


def score_anecdote_relevance(anecdote: dict[str, Any], jd_keywords: dict[str, float]) -> float:
    """Score anecdote relevance based on keyword overlap with JD.

    Args:
        anecdote: Anecdote dictionary with 'skills' and 'content'
        jd_keywords: Dictionary of keywords with importance scores (0-1)

    Returns:
        Relevance score (0-1) normalized
    """
    if not anecdote or not jd_keywords:
        return 0.0

    anecdote_skills = set(skill.lower() for skill in anecdote.get("skills", []))
    anecdote_content = anecdote.get("content", "").lower()

    total_score = 0.0
    max_possible_score = sum(jd_keywords.values())

    for keyword, importance in jd_keywords.items():
        keyword_lower = keyword.lower()
        # Check if keyword in skills or content
        if keyword_lower in anecdote_skills or keyword_lower in anecdote_content:
            total_score += importance

    # Normalize to 0-1
    if max_possible_score > 0:
        return min(total_score / max_possible_score, 1.0)

    return 0.0


def select_top_anecdotes(
    anecdotes: list[dict[str, Any]], jd_keywords: dict[str, float], top_n: int = 5
) -> list[dict[str, Any]]:
    """Select top N most relevant anecdotes based on JD keywords.

    Args:
        anecdotes: List of anecdote dictionaries
        jd_keywords: Dictionary of keywords with importance scores
        top_n: Number of top anecdotes to select

    Returns:
        List of top N most relevant anecdotes
    """
    if not anecdotes:
        return []

    # Score each anecdote
    scored_anecdotes = []
    for anecdote in anecdotes:
        score = score_anecdote_relevance(anecdote, jd_keywords)
        scored_anecdotes.append((score, anecdote))

    # Sort by score descending
    scored_anecdotes.sort(key=lambda x: x[0], reverse=True)

    # Return top N
    return [anecdote for score, anecdote in scored_anecdotes[:top_n]]


def select_diverse_anecdotes(
    anecdotes: list[dict[str, Any]], jd_keywords: dict[str, float], top_n: int = 5
) -> list[dict[str, Any]]:
    """Select diverse anecdotes to avoid skill overlap.

    Args:
        anecdotes: List of anecdote dictionaries
        jd_keywords: Dictionary of keywords with importance scores
        top_n: Number of anecdotes to select

    Returns:
        List of diverse, high-relevance anecdotes
    """
    if not anecdotes:
        return []

    # First, score all anecdotes
    scored_anecdotes = []
    for anecdote in anecdotes:
        score = score_anecdote_relevance(anecdote, jd_keywords)
        scored_anecdotes.append((score, anecdote))

    # Sort by score descending
    scored_anecdotes.sort(key=lambda x: x[0], reverse=True)

    # Select with diversity penalty for skill overlap
    selected: list[dict[str, Any]] = []
    covered_skills: set[str] = set()

    for score, anecdote in scored_anecdotes:
        if len(selected) >= top_n:
            break

        # Calculate diversity score (penalize overlap)
        anecdote_skills = set(skill.lower() for skill in anecdote.get("skills", []))
        overlap = len(anecdote_skills & covered_skills)
        unique_skills = len(anecdote_skills - covered_skills)

        # Select if high relevance or brings unique skills
        if score > 0.3 or unique_skills > 0:
            selected.append(anecdote)
            covered_skills.update(anecdote_skills)

    return selected[:top_n]


def identify_missing_keywords(text: str, jd_keywords: list[str]) -> list[str]:
    """Identify keywords from JD that are missing in text.

    Args:
        text: Resume text or bullet point
        jd_keywords: List of keywords from job description

    Returns:
        List of missing keywords
    """
    if not text or not jd_keywords:
        return jd_keywords if jd_keywords else []

    text_lower = text.lower()
    missing = []

    for keyword in jd_keywords:
        if keyword.lower() not in text_lower:
            missing.append(keyword)

    return missing


def rewrite_bullet_with_keywords(bullet: str, keywords: list[str]) -> str:
    """Rewrite bullet point to naturally incorporate missing keywords.

    Maintains STAR format and authenticity while adding relevant keywords.

    Args:
        bullet: Original bullet point
        keywords: Keywords to incorporate (max 2-3 for natural flow)

    Returns:
        Rewritten bullet point with keywords
    """
    if not bullet:
        return bullet

    # Limit keywords to avoid stuffing
    keywords_to_add = keywords[:2]

    if not keywords_to_add:
        return bullet

    # Extract action verb (first word)
    words = bullet.split()
    if not words:
        return bullet

    action_verb = words[0]

    # Extract metrics if present
    metrics = re.findall(r"\d+[%xX]|\d+\+|[\d,]+\s*(?:users|requests|days)", bullet)

    # Build enhanced bullet maintaining STAR format
    # Try to incorporate keywords naturally in the context

    # If bullet is short, expand it
    if len(bullet) < 50:
        # Add keywords as technologies used
        keyword_str = ", ".join(keywords_to_add)
        enhanced = f"{bullet} using {keyword_str}"
    # Insert keywords naturally into existing bullet
    # Find good insertion point (after action, before result)
    elif " to " in bullet or " for " in bullet:
        # Insert after purpose clause
        parts = re.split(r"(\s+(?:to|for)\s+)", bullet, maxsplit=1)
        if len(parts) >= 3:
            enhanced = (
                f"{parts[0]}{parts[1]}{parts[2]} leveraging {', '.join(keywords_to_add)}"
            )
        else:
            enhanced = f"{bullet} using {', '.join(keywords_to_add)}"
    else:
        # Append keywords naturally
        # Remove trailing period if present
        bullet_clean = bullet.rstrip(".")
        enhanced = f"{bullet_clean} using {', '.join(keywords_to_add)}"

    return enhanced


def adjust_summary(summary: str, jd_keywords: dict[str, float]) -> str:
    """Adjust summary to incorporate top JD keywords and match tone.

    Args:
        summary: Original summary text
        jd_keywords: Keywords with importance scores

    Returns:
        Adjusted summary incorporating key themes
    """
    if not summary or not jd_keywords:
        return summary

    # Get top 3 keywords
    top_keywords = sorted(jd_keywords.items(), key=lambda x: x[1], reverse=True)[:3]

    # Check for leadership keywords
    leadership_terms = ["leadership", "lead", "mentor", "architect", "senior", "principal"]
    has_leadership = any(kw.lower() in jd_keywords for kw in leadership_terms)

    # Enhance summary with key themes
    enhancements = []

    for keyword, score in top_keywords:
        if keyword.lower() not in summary.lower():
            enhancements.append(keyword)

    if enhancements and not has_leadership:
        # Add technical focus
        tech_str = " and ".join(enhancements[:2])
        enhanced = f"{summary} with expertise in {tech_str}"
    elif enhancements and has_leadership:
        # Add leadership + technical focus
        enhanced = summary.replace(
            "Software Engineer", "Senior Software Engineer with leadership experience"
        )
        if enhancements:
            enhanced = f"{enhanced} specializing in {enhancements[0]}"
    else:
        enhanced = summary

    return enhanced


def prioritize_skills(
    skills: dict[str, list[str]], jd_keywords: dict[str, float]
) -> dict[str, list[str]]:
    """Prioritize skills to match JD requirements.

    Args:
        skills: Dictionary of skill categories (languages, frameworks, tools)
        jd_keywords: Keywords with importance scores

    Returns:
        Reordered skills dictionary with matching skills first
    """
    if not skills or not jd_keywords:
        return skills

    prioritized = {}

    for category, skill_list in skills.items():
        # Score each skill
        scored_skills = []
        for skill in skill_list:
            # Check if skill matches any JD keyword
            score = jd_keywords.get(skill.lower(), 0.0)
            # Also check partial matches
            for keyword in jd_keywords:
                if keyword.lower() in skill.lower() or skill.lower() in keyword.lower():
                    score = max(score, jd_keywords[keyword])
            scored_skills.append((score, skill))

        # Sort by score descending, maintain original order for ties
        scored_skills.sort(key=lambda x: x[0], reverse=True)
        prioritized[category] = [skill for score, skill in scored_skills]

    return prioritized


def reorder_experiences(
    experiences: list[dict[str, Any]], jd_keywords: dict[str, float]
) -> list[dict[str, Any]]:
    """Reorder experience entries by relevance to JD.

    Args:
        experiences: List of experience dictionaries
        jd_keywords: Keywords with importance scores

    Returns:
        Reordered experiences with most relevant first
    """
    if not experiences or not jd_keywords:
        return experiences

    # Score each experience
    scored_experiences = []
    for exp in experiences:
        # Calculate relevance based on skills and bullets
        skills = exp.get("skills", [])
        bullets = exp.get("bullets", [])

        score = 0.0
        for skill in skills:
            score += jd_keywords.get(skill.lower(), 0.0)

        # Also score based on bullet content
        bullets_text = " ".join(bullets).lower()
        for keyword, importance in jd_keywords.items():
            if keyword.lower() in bullets_text:
                score += importance * 0.5  # Weight bullet mentions lower

        scored_experiences.append((score, exp))

    # Sort by score descending
    scored_experiences.sort(key=lambda x: x[0], reverse=True)

    return [exp for score, exp in scored_experiences]


def calculate_ats_score(resume_text: str, jd_keywords: dict[str, float]) -> float:
    """Calculate ATS score based on keyword match.

    Args:
        resume_text: Full resume text
        jd_keywords: Keywords with importance scores

    Returns:
        ATS score as percentage (0-100)
    """
    if not resume_text or not jd_keywords:
        return 0.0

    resume_lower = resume_text.lower()

    # Calculate weighted keyword match
    matched_score = 0.0
    total_score = sum(jd_keywords.values())

    for keyword, importance in jd_keywords.items():
        if keyword.lower() in resume_lower:
            matched_score += importance

    # Calculate percentage
    if total_score > 0:
        percentage = (matched_score / total_score) * 100
        return min(percentage, 100.0)

    return 0.0


def identify_keyword_gaps(resume_text: str, jd_keywords: dict[str, float]) -> list[str]:
    """Identify high-value missing keywords.

    Args:
        resume_text: Full resume text
        jd_keywords: Keywords with importance scores

    Returns:
        List of missing high-value keywords
    """
    if not resume_text or not jd_keywords:
        return list(jd_keywords.keys()) if jd_keywords else []

    resume_lower = resume_text.lower()
    gaps = []

    # Sort keywords by importance
    sorted_keywords = sorted(jd_keywords.items(), key=lambda x: x[1], reverse=True)

    for keyword, importance in sorted_keywords:
        if keyword.lower() not in resume_lower and importance > 0.5:
            gaps.append(keyword)

    return gaps


def parse_resume_markdown(resume_path: Path) -> dict[str, Any]:
    """Parse resume from markdown file with YAML frontmatter.

    Args:
        resume_path: Path to resume markdown file

    Returns:
        Dictionary with metadata and content sections
    """
    if not resume_path.exists():
        raise FileNotFoundError(f"Resume file not found: {resume_path}")

    content = resume_path.read_text(encoding="utf-8")

    # Extract YAML frontmatter
    frontmatter_match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)

    if not frontmatter_match:
        # No frontmatter, return basic structure
        return {"metadata": {}, "content": content, "raw": content}

    frontmatter_text = frontmatter_match.group(1)
    body_text = frontmatter_match.group(2)

    metadata = yaml.safe_load(frontmatter_text) or {}

    # Parse sections from body
    sections = {}
    current_section = None
    current_content: list[str] = []

    for line in body_text.split("\n"):
        if line.startswith("# "):
            # Save previous section
            if current_section:
                sections[current_section] = "\n".join(current_content).strip()
            # Start new section
            current_section = line[2:].strip().lower()
            current_content = []
        else:
            current_content.append(line)

    # Save last section
    if current_section:
        sections[current_section] = "\n".join(current_content).strip()

    # Add content field for backward compatibility
    result = {"metadata": metadata, "sections": sections, "raw": content}

    # Also create individual section fields for easier access
    if "experience" in sections:
        result["experience"] = sections["experience"]
    if "summary" in sections:
        result["summary"] = sections["summary"]

    return result


def load_anecdotes(anecdotes_dir: Path) -> list[dict[str, Any]]:
    """Load anecdotes from directory.

    Args:
        anecdotes_dir: Path to anecdotes directory

    Returns:
        List of anecdote dictionaries
    """
    if not anecdotes_dir.exists():
        return []

    anecdotes = []

    for anecdote_file in anecdotes_dir.glob("*.md"):
        content = anecdote_file.read_text(encoding="utf-8")

        # Extract frontmatter
        frontmatter_match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)

        if frontmatter_match:
            frontmatter_text = frontmatter_match.group(1)
            body_text = frontmatter_match.group(2)

            metadata = yaml.safe_load(frontmatter_text) or {}

            anecdote = {
                "id": anecdote_file.stem,
                "title": metadata.get("title", anecdote_file.stem),
                "skills": metadata.get("skills", []),
                "impact": metadata.get("impact", ""),
                "content": body_text.strip(),
                "metadata": metadata,
            }

            anecdotes.append(anecdote)

    return anecdotes


def optimize_iteration(
    resume: dict[str, Any], jd_analysis: dict[str, Any]
) -> tuple[dict[str, Any], float]:
    """Perform single optimization iteration.

    Args:
        resume: Resume dictionary
        jd_analysis: JD analysis result

    Returns:
        Tuple of (optimized_resume, ats_score)
    """
    # Extract keyword importance
    jd_keywords = jd_analysis.get("keyword_importance", {})

    # Generate resume text for scoring
    resume_text = resume.get("raw", "")
    if not resume_text:
        # Build text from sections
        sections = resume.get("sections", {})
        resume_text = "\n\n".join(f"# {k}\n{v}" for k, v in sections.items())

    # Calculate current score
    current_score = calculate_ats_score(resume_text, jd_keywords)

    # Identify gaps
    gaps = identify_keyword_gaps(resume_text, jd_keywords)

    # Create optimized copy
    optimized = resume.copy()

    # Enhance with missing keywords (simple approach for now)
    # In real implementation, would rewrite bullets, adjust sections, etc.

    return optimized, current_score


def optimize_resume_iteratively(
    base_resume: dict[str, Any],
    jd_analysis: dict[str, Any],
    target_score: float = 90.0,
    max_iterations: int = 3,
) -> dict[str, Any]:
    """Iteratively optimize resume to reach target ATS score.

    Args:
        base_resume: Base resume dictionary
        jd_analysis: JD analysis result
        target_score: Target ATS score (0-100)
        max_iterations: Maximum optimization iterations

    Returns:
        Dictionary with iteration history and final resume
    """
    iterations = []
    current_resume = base_resume

    for i in range(max_iterations):
        optimized, score = optimize_iteration(current_resume, jd_analysis)

        # Identify gaps and improvements
        jd_keywords = jd_analysis.get("keyword_importance", {})
        resume_text = current_resume.get("raw", "")
        gaps = identify_keyword_gaps(resume_text, jd_keywords)

        iteration_result = {
            "iteration": i + 1,
            "score": score,
            "gaps": gaps[:5],  # Top 5 gaps
            "improvements": [],  # Would track specific changes
        }

        iterations.append(iteration_result)

        # Check convergence
        if score >= target_score:
            break

        current_resume = optimized

    return {
        "iterations": iterations,
        "final_resume": current_resume,
        "final_score": iterations[-1]["score"] if iterations else 0.0,
    }


def generate_resume_markdown(resume: dict[str, Any]) -> str:
    """Generate resume markdown from dictionary.

    Args:
        resume: Resume dictionary with metadata and sections

    Returns:
        Markdown formatted resume
    """
    metadata = resume.get("metadata", {})
    sections = resume.get("sections", {})

    # Build frontmatter
    frontmatter_lines = ["---"]
    for key, value in metadata.items():
        frontmatter_lines.append(f"{key}: {value}")
    frontmatter_lines.append("---")
    frontmatter_lines.append("")

    # Build sections - handle both dict and direct fields
    section_lines = []

    # Handle sections dictionary
    if sections:
        for section_name, section_content in sections.items():
            section_lines.append(f"# {section_name.title()}")
            section_lines.append(section_content)
            section_lines.append("")
    else:
        # Fallback: build from individual fields
        for field in ["summary", "experience", "skills", "education"]:
            if resume.get(field):
                section_lines.append(f"# {field.title()}")
                section_lines.append(str(resume[field]))
                section_lines.append("")

    return "\n".join(frontmatter_lines + section_lines)


def save_optimization_report(result: dict[str, Any], output_path: Path) -> None:
    """Save optimization report with iteration history.

    Args:
        result: Optimization result dictionary
        output_path: Path to save report
    """
    iterations = result.get("iterations", [])
    final_score = result.get("final_score", 0)

    report_lines = [
        "# Resume Optimization Report",
        "",
        f"**Final Score:** {final_score:.1f}%",
        f"**Iterations:** {len(iterations)}",
        "",
        "## Iteration History",
        "",
    ]

    for iteration in iterations:
        report_lines.append(f"### Iteration {iteration['iteration']}")
        report_lines.append(f"- **Score:** {iteration['score']:.1f}%")
        report_lines.append(f"- **Gaps:** {', '.join(iteration['gaps'])}")
        if iteration.get("improvements"):
            report_lines.append(f"- **Improvements:** {', '.join(iteration['improvements'])}")
        report_lines.append("")

    output_path.write_text("\n".join(report_lines), encoding="utf-8")
