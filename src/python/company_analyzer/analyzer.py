"""Company Data Analyzer.

Analyzes company data to detect green/red flags, generate talking points,
and synthesize interview insights.
"""

import re
from typing import Any


def detect_green_flags(data: dict[str, Any]) -> list[str]:
    """Detect positive indicators about the company.

    Args:
        data: Company data dictionary

    Returns:
        List of green flag descriptions
    """
    green_flags: list[str] = []

    if not data:
        return green_flags

    # Check news for positive signals
    news = data.get("news", [])
    website_content = data.get("website_content", "").lower()

    # Funding signals
    for article in news:
        title = article.get("title", "").lower()
        if any(
            keyword in title for keyword in ["funding", "raises", "series", "investment", "capital"]
        ):
            green_flags.append(f"Recent funding: {article.get('title', '')}")

    # Award signals
    for article in news:
        title = article.get("title", "").lower()
        if any(
            keyword in title
            for keyword in ["award", "best place to work", "top company", "recognition"]
        ):
            green_flags.append(f"Industry recognition: {article.get('title', '')}")

    # Growth signals
    growth_keywords = ["expand", "growth", "hiring", "new market", "acquisition"]
    for article in news:
        title = article.get("title", "").lower()
        if any(keyword in title for keyword in growth_keywords):
            green_flags.append(f"Growth indicator: {article.get('title', '')}")

    # Check website content for positive culture signals
    culture_signals = [
        ("work-life balance", "Emphasizes work-life balance"),
        ("diversity", "Commitment to diversity and inclusion"),
        ("innovation", "Focus on innovation and creativity"),
        ("remote", "Offers remote work flexibility"),
        ("professional development", "Invests in employee development"),
        ("competitive salary", "Competitive compensation"),
        ("equity", "Offers equity/stock options"),
    ]

    for keyword, description in culture_signals:
        if keyword in website_content:
            green_flags.append(description)

    return green_flags


def detect_red_flags(data: dict[str, Any]) -> list[str]:
    """Detect warning signs about the company.

    Args:
        data: Company data dictionary

    Returns:
        List of red flag descriptions
    """
    red_flags: list[str] = []

    if not data:
        return red_flags

    news = data.get("news", [])
    website_content = data.get("website_content", "").lower()

    # Check news for negative signals
    layoff_keywords = ["layoff", "layoffs", "workforce reduction", "job cuts", "downsizing"]
    for article in news:
        title = article.get("title", "").lower()
        if any(keyword in title for keyword in layoff_keywords):
            red_flags.append(f"Layoffs reported: {article.get('title', '')}")

    # Legal/lawsuit signals
    legal_keywords = ["lawsuit", "sued", "legal action", "discrimination", "settlement"]
    for article in news:
        title = article.get("title", "").lower()
        if any(keyword in title for keyword in legal_keywords):
            red_flags.append(f"Legal concerns: {article.get('title', '')}")

    # Financial trouble
    financial_keywords = ["bankruptcy", "financial trouble", "struggling", "losses"]
    for article in news:
        title = article.get("title", "").lower()
        if any(keyword in title for keyword in financial_keywords):
            red_flags.append(f"Financial concerns: {article.get('title', '')}")

    # Culture red flags from website
    culture_red_flags = [
        ("high turnover", "High employee turnover mentioned"),
        ("toxic", "Workplace culture concerns"),
        ("poor management", "Management issues reported"),
        ("long hours", "Expectation of long work hours"),
        ("no work-life balance", "Work-life balance concerns"),
    ]

    for keyword, description in culture_red_flags:
        if keyword in website_content:
            red_flags.append(description)

    return red_flags


def generate_talking_points(data: dict[str, Any]) -> list[str]:
    """Generate specific talking points for interviews.

    Args:
        data: Company data dictionary

    Returns:
        List of 5-7 talking points
    """
    points: list[str] = []

    if not data:
        return points

    name = data.get("name", "the company")
    website_content = data.get("website_content", "")
    news = data.get("news", [])

    # Point about recent news/achievements
    if news:
        latest_news = news[0]
        points.append(
            f"I noticed {name}'s recent news about {latest_news.get('title', 'recent developments')} - "
            f"this aligns with my interest in {_extract_topic_from_title(latest_news.get('title', ''))}"
        )

    # Point about company values
    value_keywords = {
        "innovation": "innovative approach to problem-solving",
        "customer": "customer-centric philosophy",
        "diversity": "commitment to diversity and inclusion",
        "sustainability": "focus on sustainability",
        "collaboration": "collaborative work environment",
    }

    for keyword, phrase in value_keywords.items():
        if keyword in website_content.lower():
            points.append(
                f"I'm particularly drawn to {name}'s {phrase}, which resonates with my own values"
            )
            if len(points) >= 7:
                break

    # Point about industry position
    industry = data.get("industry", "")
    if industry:
        points.append(
            f"Working in the {industry} sector at {name} would allow me to leverage my expertise while contributing to meaningful impact"
        )

    # Point about growth
    size = data.get("size", "")
    if size:
        points.append(
            f"The company's scale ({size}) offers the perfect balance of resources and opportunity for individual impact"
        )

    # Point about mission alignment
    if "mission" in website_content.lower() or "purpose" in website_content.lower():
        points.append(
            f"I'm excited about {name}'s mission and how my skills can contribute to achieving these goals"
        )

    # Ensure we have 5-7 points
    while len(points) < 5:
        points.append(
            f"I'm impressed by {name}'s position in the industry and eager to contribute to its continued success"
        )

    return points[:7]


def synthesize_interview_insights(data: dict[str, Any]) -> dict[str, Any]:
    """Synthesize insights for interview preparation.

    Args:
        data: Company data dictionary

    Returns:
        Dictionary with culture, expectations, and questions
    """
    insights = {
        "culture": "",
        "expectations": "",
        "questions_to_ask": [],
    }

    if not data:
        return insights

    website_content = data.get("website_content", "").lower()
    news = data.get("news", [])

    # Culture insights
    culture_indicators = []
    if "innovation" in website_content:
        culture_indicators.append("innovative and forward-thinking")
    if "collaboration" in website_content:
        culture_indicators.append("collaborative")
    if "fast-paced" in website_content:
        culture_indicators.append("fast-paced")
    if "work-life balance" in website_content:
        culture_indicators.append("values work-life balance")

    insights["culture"] = (
        f"The company culture appears to be {', '.join(culture_indicators) if culture_indicators else 'professional and growth-oriented'}"
    )

    # Expectations
    expectations = []
    if "ownership" in website_content:
        expectations.append("taking ownership of projects")
    if "impact" in website_content:
        expectations.append("driving meaningful impact")
    if "collaboration" in website_content:
        expectations.append("working cross-functionally")

    insights["expectations"] = (
        f"Likely expectations include {', '.join(expectations) if expectations else 'strong technical skills and team collaboration'}"
    )

    # Generate smart questions to ask
    questions = [
        "What does success look like in this role in the first 6 months?",
        "How does the team approach professional development and learning?",
        "What are the biggest challenges the team is currently facing?",
    ]

    # Add context-specific questions
    if news:
        latest = news[0]
        topic = _extract_topic_from_title(latest.get("title", ""))
        if topic:
            questions.append(
                f"I saw the recent news about {topic} - how will this impact the team's priorities?"
            )

    if "product" in website_content:
        questions.append("What's the product roadmap looking like for the next year?")

    if "growth" in website_content or "scaling" in website_content:
        questions.append("As the company scales, how is the engineering culture being preserved?")

    insights["questions_to_ask"] = questions[:7]

    return insights


def analyze_company_data(data: dict[str, Any]) -> dict[str, Any]:
    """Perform comprehensive analysis of company data.

    Args:
        data: Company data dictionary with name, industry, news, website_content, etc.

    Returns:
        Complete analysis with overview, flags, talking points, and insights
    """
    if not data:
        return {
            "overview": {},
            "mission_values": "",
            "recent_news": [],
            "green_flags": [],
            "red_flags": [],
            "talking_points": [],
            "interview_insights": {},
        }

    # Build overview
    overview = {
        "name": data.get("name", ""),
        "industry": data.get("industry", ""),
        "size": data.get("size", ""),
        "founded": data.get("founded", ""),
        "location": data.get("location", ""),
    }

    # Extract mission and values
    website_content = data.get("website_content", "")
    mission_values = _extract_mission_values(website_content)

    # Process news
    news = data.get("news", [])

    # Run all analyses
    green_flags = detect_green_flags(data)
    red_flags = detect_red_flags(data)
    talking_points = generate_talking_points(data)
    interview_insights = synthesize_interview_insights(data)

    return {
        "overview": overview,
        "mission_values": mission_values,
        "recent_news": news,
        "green_flags": green_flags,
        "red_flags": red_flags,
        "talking_points": talking_points,
        "interview_insights": interview_insights,
    }


# Helper functions


def _extract_topic_from_title(title: str) -> str:
    """Extract main topic from news title."""
    if not title:
        return "recent developments"

    # Remove common prefixes
    clean_title = re.sub(r"^(Company|Startup)\s+", "", title, flags=re.IGNORECASE)

    # Extract key phrases
    if "funding" in title.lower() or "raises" in title.lower():
        return "funding and growth"
    if "product" in title.lower() or "launch" in title.lower():
        return "product innovation"
    if "award" in title.lower():
        return "industry recognition"
    if "hiring" in title.lower():
        return "team expansion"

    return "recent developments"


def _extract_mission_values(content: str) -> str:
    """Extract mission and values from website content."""
    if not content:
        return ""

    # Look for mission/values section
    mission_match = re.search(
        r"(?:mission|our mission|values|our values)[:\s]+(.*?)(?:\.|</|$)",
        content,
        re.IGNORECASE | re.DOTALL,
    )

    if mission_match:
        mission_text = mission_match.group(1).strip()
        # Limit to reasonable length
        if len(mission_text) > 300:
            mission_text = mission_text[:300] + "..."
        return mission_text

    return "Mission and values information not readily available from public sources"
