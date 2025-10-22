"""Cover Letter Generation Engine.

Generates personalized, compelling cover letters based on:
- Job description analysis
- Company research
- Resume anecdotes (STAR format achievements)
"""

import random
import re
from typing import Any


def select_relevant_anecdotes(
    anecdotes: list[dict[str, Any]],
    jd_keywords: dict[str, float],
    max_anecdotes: int = 3,
) -> list[dict[str, Any]]:
    """Select most relevant anecdotes based on JD keyword overlap.

    Args:
        anecdotes: List of anecdote dictionaries with 'skills' and 'content'
        jd_keywords: Dictionary of keywords with importance scores (0-1)
        max_anecdotes: Maximum number of anecdotes to select

    Returns:
        List of selected anecdotes sorted by relevance
    """
    if not anecdotes or not jd_keywords:
        return []

    # Score each anecdote
    scored_anecdotes = []
    for anecdote in anecdotes:
        score = 0.0
        anecdote_skills = set(skill.lower() for skill in anecdote.get("skills", []))
        anecdote_content = anecdote.get("content", "").lower()

        # Calculate relevance score
        for keyword, importance in jd_keywords.items():
            keyword_lower = keyword.lower()
            if keyword_lower in anecdote_skills or keyword_lower in anecdote_content:
                score += importance

        scored_anecdotes.append((score, anecdote))

    # Sort by score descending
    scored_anecdotes.sort(key=lambda x: x[0], reverse=True)

    # Return top N
    return [anecdote for score, anecdote in scored_anecdotes[:max_anecdotes]]


def generate_opening(
    company_research: dict[str, Any],
    position: str,
    tone: str = "professional",
) -> str:
    """Generate opening paragraph with company-specific insights.

    Args:
        company_research: Dictionary with company info (mission, news, values, etc.)
        position: Job position title
        tone: Writing tone (formal, professional, casual)

    Returns:
        Opening paragraph as string
    """
    company_name = company_research.get("company", "the company")
    recent_news = company_research.get("recent_news", [])
    mission = company_research.get("mission", "")
    values = company_research.get("values", [])
    culture = company_research.get("culture", "")

    # Enthusiasm verbs based on tone
    enthusiasm_verbs = {
        "formal": ["pleased to submit my application", "writing to express my interest"],
        "professional": [
            "excited to apply",
            "thrilled to submit my application",
            "delighted to apply",
        ],
        "casual": [
            "excited to apply",
            "really interested in",
            "eager to join",
        ],
    }

    verb = random.choice(enthusiasm_verbs.get(tone, enthusiasm_verbs["professional"]))

    # Build opening with specific company information
    opening_parts = []

    # Start with hook - ensure we reference specific info
    if recent_news and len(recent_news) > 0:
        news_item = recent_news[0]
        if tone == "formal":
            opening_parts.append(
                f"I was {verb} for the {position} position at {company_name}. "
                f"I have been following {company_name}'s recent {news_item} and "
                f"am impressed by the company's growth trajectory and vision"
            )
        else:
            opening_parts.append(
                f"I was {verb} for the {position} position at {company_name}. "
                f"Your recent {news_item} caught my attention and reinforced my interest in joining your team"
            )
    elif mission:
        opening_parts.append(
            f"I am {verb} for the {position} position at {company_name}. "
            f"Your mission to {mission} aligns perfectly with my professional goals"
        )
    elif values and len(values) > 0:
        value = values[0]
        opening_parts.append(
            f"I am {verb} for the {position} position at {company_name}. "
            f"I am particularly drawn to your focus on {value}"
        )
    else:
        opening_parts.append(f"I am {verb} for the {position} position at {company_name}")

    # Add enthusiasm and connection to ensure specific info is referenced
    if culture and not recent_news and not mission:
        opening_parts.append(f" I'm impressed by {company_name}'s {culture}")
    elif mission and recent_news:
        opening_parts.append(" and am excited about the opportunity to contribute to this mission")
    elif not recent_news and not mission and values and len(values) > 1:
        # Add second value for more specificity
        opening_parts.append(f", as well as your commitment to {values[1]}")

    opening = "".join(opening_parts).strip()

    # Ensure proper punctuation
    if not opening.endswith("."):
        opening += "."

    return opening


def generate_body(
    jd_analysis: dict[str, Any],
    anecdotes: list[dict[str, Any]],
    tone: str = "professional",
) -> str:
    """Generate body paragraphs with specific examples and achievements.

    Args:
        jd_analysis: Dictionary with JD analysis (skills, requirements, keywords)
        anecdotes: List of anecdote dictionaries
        tone: Writing tone (formal, professional, casual)

    Returns:
        Body paragraphs as string
    """
    keyword_importance = jd_analysis.get("keyword_importance", {})
    technical_skills = jd_analysis.get("technical_skills", [])
    required_skills = jd_analysis.get("required_skills", [])

    # Select most relevant anecdotes (get 3 for more content)
    selected_anecdotes = select_relevant_anecdotes(anecdotes, keyword_importance, max_anecdotes=3)

    paragraphs = []

    # Get top technical skills for highlighting
    top_skills = list(keyword_importance.keys())[:5]

    # First paragraph: Address key requirements with first anecdote
    if selected_anecdotes and len(selected_anecdotes) > 0:
        anecdote = selected_anecdotes[0]
        impact = anecdote.get("impact", "")
        title = anecdote.get("title", "")
        content = anecdote.get("content", "")

        # Extract key result from content
        result_match = re.search(
            r"(?:Reduced|Increased|Improved|Achieved|Built|Led|Scaled)[^.]+\d+%?[^.]*",
            content,
            re.IGNORECASE,
        )
        result = result_match.group(0) if result_match else impact

        # Get top skills from anecdote that match JD
        anecdote_skills = set(skill.lower() for skill in anecdote.get("skills", []))

        # Find matching skills from top JD skills
        matching_skills = []
        for skill in top_skills:
            if skill.lower() in anecdote_skills:
                matching_skills.append(skill)
            if len(matching_skills) >= 3:
                break

        if matching_skills:
            # Format skills list naturally
            if len(matching_skills) == 1:
                skills_text = matching_skills[0]
            elif len(matching_skills) == 2:
                skills_text = " and ".join(matching_skills)
            else:
                skills_text = ", ".join(matching_skills[:-1]) + ", and " + matching_skills[-1]

            if tone == "formal":
                para = (
                    f"In my current role, I have extensive experience with {skills_text}. "
                    f"{result}. This experience has equipped me with a deep understanding of "
                    f"how to leverage these technologies to deliver high-impact solutions."
                )
            else:
                para = (
                    f"Your job description emphasizes {skills_text}. In my current role, "
                    f"{result.lower()}. This hands-on experience has given me deep insights into "
                    f"building scalable, production-ready systems with these technologies."
                )
            paragraphs.append(para)
        else:
            paragraphs.append(f"In my current role, {result}.")

    # Second paragraph: Additional achievement with different skills
    if selected_anecdotes and len(selected_anecdotes) > 1:
        anecdote = selected_anecdotes[1]
        impact = anecdote.get("impact", "")
        content = anecdote.get("content", "")
        anecdote_skills = set(skill.lower() for skill in anecdote.get("skills", []))

        # Extract another key result
        result_match = re.search(
            r"(?:Reduced|Increased|Improved|Achieved|Built|Led|Scaled)[^.]+\d+%?[^.]*",
            content,
            re.IGNORECASE,
        )
        result = result_match.group(0) if result_match else impact

        # Find additional matching skills not mentioned in first paragraph
        first_para = paragraphs[0] if paragraphs else ""
        additional_skills = []
        for skill in top_skills:
            if skill.lower() in anecdote_skills and skill.lower() not in first_para.lower():
                additional_skills.append(skill)
            if len(additional_skills) >= 2:
                break

        if result:
            if additional_skills:
                skills_mention = " and ".join(additional_skills)
                if tone == "formal":
                    para = f"Additionally, I have demonstrated expertise in {skills_mention}. {result}."
                else:
                    para = f"Beyond this, I've worked extensively with {skills_mention}. {result.lower()}."
            elif tone == "formal":
                para = f"Additionally, {result.lower()}."
            else:
                para = f"I've also {result.lower()}."
            paragraphs.append(para)

    # If no anecdotes, address skills directly
    if not paragraphs and technical_skills:
        skills_list = technical_skills[:4]
        if len(skills_list) > 1:
            skills_text = ", ".join(skills_list[:-1]) + ", and " + skills_list[-1]
        else:
            skills_text = skills_list[0] if skills_list else "the required technologies"
        paragraphs.append(
            f"Your requirements for {skills_text} align well with my expertise. "
            f"I have extensive experience in these technologies and am passionate about building scalable solutions."
        )

    # Third paragraph: Company fit and enthusiasm
    if len(paragraphs) > 0:
        if tone == "formal":
            fit_para = (
                "I am particularly drawn to this opportunity because it combines "
                "technical challenges with meaningful impact. I am confident that my background "
                "in delivering results aligns well with your team's objectives."
            )
        else:
            fit_para = (
                "I'm particularly excited about this role because it combines "
                "the technical challenges I love with the opportunity to make a real impact. "
                "I'm confident my experience delivering measurable results would be valuable to your team."
            )
        paragraphs.append(fit_para)

    return "\n\n".join(paragraphs)


def generate_closing(
    company_name: str,
    position: str,
    tone: str = "professional",
) -> str:
    """Generate closing paragraph with call to action.

    Args:
        company_name: Name of the company
        position: Job position title
        tone: Writing tone (formal, professional, casual)

    Returns:
        Closing paragraph as string
    """
    # Call to action variations by tone
    cta_templates = {
        "formal": [
            f"I would welcome the opportunity to discuss how my experience and skills align with the {position} role at {company_name}. "
            f"I am confident that I can make meaningful contributions to your team and help drive your initiatives forward. "
            "Thank you for considering my application.",
        ],
        "professional": [
            f"I'd love to discuss how my experience in these areas can contribute to {company_name}'s goals. "
            f"I'm confident that my track record of delivering results would be valuable to your team. "
            "Thank you for considering my application.",
            f"I would welcome the opportunity to discuss how I can contribute to {company_name}'s success. "
            f"I believe my background and passion for innovation would make me a strong addition to your team. "
            "Thank you for your time and consideration.",
        ],
        "casual": [
            f"I'd love to chat about how I can help {company_name} achieve its goals. "
            f"I think my experience and enthusiasm would be a great fit for your team. "
            "Thanks for considering my application!",
            f"I'm excited about the possibility of joining {company_name} and would love to discuss this opportunity further. "
            f"I believe I could make a real impact on your team. "
            "Thanks for your consideration!",
        ],
    }

    templates = cta_templates.get(tone, cta_templates["professional"])
    return random.choice(templates)


def generate_cover_letter(
    user_info: dict[str, Any],
    company_research: dict[str, Any],
    jd_analysis: dict[str, Any],
    anecdotes: list[dict[str, Any]],
    position: str,
    tone: str = "professional",
    custom_notes: str | None = None,
) -> str:
    """Generate complete cover letter.

    Args:
        user_info: Dictionary with user contact information
        company_research: Dictionary with company research
        jd_analysis: Dictionary with JD analysis
        anecdotes: List of anecdote dictionaries
        position: Job position title
        tone: Writing tone (formal, professional, casual)
        custom_notes: Optional custom notes to include

    Returns:
        Complete cover letter as markdown string
    """
    company_name = company_research.get("company", "Hiring Manager")

    # Header with contact information
    header = f"""{user_info.get("name", "")}
{user_info.get("email", "")}
{user_info.get("phone", "")}
{user_info.get("linkedin", "")}"""

    # Date (placeholder for actual date)
    date = ""

    # Recipient
    recipient = f"""{company_name}"""

    # Salutation
    salutation = "Dear Hiring Manager,"

    # Generate sections
    opening = generate_opening(company_research, position, tone)
    body = generate_body(jd_analysis, anecdotes, tone)

    # Add transition paragraph if needed for length
    tech_stack = company_research.get("tech_stack", [])
    if tech_stack:
        transition = f"I'm also excited about {company_name}'s use of {', '.join(tech_stack[:2])} in your tech stack, as I've worked extensively with these technologies."
        body = body + "\n\n" + transition

    closing = generate_closing(company_name, position, tone)

    # Signature
    signature_word = "Sincerely," if tone == "formal" else "Best regards,"
    signature = f"""{signature_word}
{user_info.get("name", "")}"""

    # Combine all sections
    sections = [
        header.strip(),
        "",
        recipient.strip(),
        "",
        salutation,
        "",
        opening,
        "",
        body,
        "",
        closing,
        "",
        signature,
    ]

    # Add custom notes if provided
    if custom_notes:
        # Insert custom notes before closing
        sections.insert(-4, custom_notes)
        sections.insert(-4, "")

    cover_letter = "\n".join(sections)

    return cover_letter
