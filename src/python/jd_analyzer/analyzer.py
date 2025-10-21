"""Job Description Analysis Engine.

Analyzes job descriptions to extract keywords, categorize requirements,
identify skills, and generate ATS-optimized keyword lists.
"""

import re
from collections import Counter
from typing import Any

# Comprehensive technology and skill keywords database
TECHNICAL_KEYWORDS = {
    # Programming Languages
    "python",
    "javascript",
    "typescript",
    "java",
    "c++",
    "c#",
    "go",
    "golang",
    "rust",
    "ruby",
    "php",
    "swift",
    "kotlin",
    "scala",
    "r",
    "matlab",
    # Frontend
    "react",
    "vue",
    "angular",
    "svelte",
    "next.js",
    "nuxt",
    "redux",
    "html",
    "css",
    "sass",
    "tailwind",
    "webpack",
    "vite",
    # Backend
    "node.js",
    "express",
    "django",
    "flask",
    "fastapi",
    "spring",
    "spring boot",
    ".net",
    "asp.net",
    "rails",
    "laravel",
    # Databases
    "postgresql",
    "postgres",
    "mysql",
    "mongodb",
    "redis",
    "cassandra",
    "dynamodb",
    "elasticsearch",
    "oracle",
    "sql server",
    "sqlite",
    # Cloud & DevOps
    "aws",
    "azure",
    "gcp",
    "google cloud",
    "docker",
    "kubernetes",
    "k8s",
    "terraform",
    "ansible",
    "jenkins",
    "gitlab",
    "github actions",
    "circleci",
    "ci/cd",
    # Data & ML
    "pandas",
    "numpy",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "spark",
    "hadoop",
    "airflow",
    "kafka",
    "machine learning",
    "deep learning",
    "nlp",
    "computer vision",
    # Mobile
    "ios",
    "android",
    "react native",
    "flutter",
    # Other Tools
    "git",
    "linux",
    "graphql",
    "rest",
    "restful",
    "api",
    "microservices",
    "agile",
    "scrum",
}

LEADERSHIP_KEYWORDS = {
    "leadership",
    "mentor",
    "mentoring",
    "coach",
    "coaching",
    "lead",
    "leading",
    "manage",
    "management",
    "team lead",
    "tech lead",
    "technical lead",
    "collaboration",
    "communication",
    "stakeholder",
    "cross-functional",
    "drive",
    "initiative",
    "ownership",
    "influence",
    "strategic",
}

DOMAIN_KEYWORDS = {
    "architecture",
    "design",
    "system design",
    "scalability",
    "performance",
    "optimization",
    "security",
    "testing",
    "debugging",
    "troubleshooting",
    "api design",
    "database design",
    "distributed systems",
    "microservices",
}


def extract_keywords(text: str) -> list[str]:
    """Extract relevant keywords from job description text.

    Args:
        text: Job description text

    Returns:
        List of extracted keywords (preserves original case when found)
    """
    if not text:
        return []

    text_lower = text.lower()
    keywords = []
    keyword_map = {}  # Map lowercase to original case

    # Build a map of keywords found in original text
    words = re.findall(r"\b\w+(?:[.\-/+#]\w+)*\b", text)
    for word in words:
        keyword_map[word.lower()] = word

    # Extract technical keywords (preserve original case)
    for keyword in TECHNICAL_KEYWORDS:
        if keyword in text_lower:
            # Try to preserve original case from text
            original = keyword_map.get(keyword, keyword)
            keywords.append(original)

    # Extract leadership keywords
    for keyword in LEADERSHIP_KEYWORDS:
        if keyword in text_lower:
            original = keyword_map.get(keyword, keyword)
            keywords.append(original)

    # Extract domain keywords
    for keyword in DOMAIN_KEYWORDS:
        if keyword in text_lower:
            original = keyword_map.get(keyword, keyword)
            keywords.append(original)

    # Also extract years of experience patterns
    experience_patterns = re.findall(
        r"(\d+\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience)", text_lower
    )
    keywords.extend(experience_patterns)

    return list(set(keywords))  # Remove duplicates


def calculate_keyword_frequency(text: str) -> dict[str, int]:
    """Calculate frequency of important keywords in text.

    Args:
        text: Job description text

    Returns:
        Dictionary mapping keywords to their frequency counts
    """
    if not text:
        return {}

    text_lower = text.lower()

    # Tokenize text (simple word splitting, preserve special chars)
    words = re.findall(r"\b\w+(?:[.\-/+#]\w+)*\b", text_lower)

    # Count all words
    word_counts = Counter(words)

    # Filter to keep only meaningful keywords
    all_keywords = TECHNICAL_KEYWORDS | LEADERSHIP_KEYWORDS | DOMAIN_KEYWORDS

    frequency = {}
    for word, count in word_counts.items():
        if word in all_keywords:
            frequency[word] = count

    # Also check multi-word phrases
    for keyword in all_keywords:
        if " " in keyword or "." in keyword or "/" in keyword:
            count = text_lower.count(keyword)
            if count > 0:
                frequency[keyword] = count

    # Also track common words like "experience" even if not in keyword sets
    common_important_words = ["experience", "required", "preferred", "skills", "knowledge"]
    for word in common_important_words:
        count = word_counts.get(word, 0)
        if count > 0:
            frequency[word] = count

    return dict(sorted(frequency.items(), key=lambda x: x[1], reverse=True))


def categorize_requirements(text: str) -> dict[str, list[str]]:
    """Categorize requirements into required vs nice-to-have.

    Args:
        text: Job description text

    Returns:
        Dictionary with 'required' and 'nice_to_have' lists
    """
    if not text:
        return {"required": [], "nice_to_have": []}

    required = []
    nice_to_have = []

    # Split text into lines
    lines = text.split("\n")

    in_required_section = False
    in_nice_to_have_section = False

    for line in lines:
        line_lower = line.lower().strip()

        # Detect section headers
        if re.match(
            r"^(?:required\s*skills?|requirements?|qualifications?|must have|you have)", line_lower
        ):
            in_required_section = True
            in_nice_to_have_section = False
            continue
        if re.match(
            r"^(?:nice\s*to\s*have|preferred|bonus|plus|optional|desired)", line_lower
        ):
            in_nice_to_have_section = True
            in_required_section = False
            continue
        if re.match(r"^(?:responsibilities|about|benefits)", line_lower):
            in_required_section = False
            in_nice_to_have_section = False
            continue

        # Extract bullet points or list items
        bullet_match = re.match(r"^[•\-\*\d+\.]\s*(.+)", line.strip())
        if bullet_match:
            item = bullet_match.group(1).strip()
            if item and len(item) > 5:  # Filter out empty or too short items
                if in_required_section:
                    required.append(item)
                elif in_nice_to_have_section:
                    nice_to_have.append(item)

    # If no clear sections found, use heuristics
    if not required and not nice_to_have:
        # Look for patterns indicating required vs optional
        required_patterns = [
            r"(\d+\+?\s*years?\s+(?:of\s+)?experience\s+(?:with|in)\s+[^\n.,]+)",
            r"(strong\s+(?:knowledge|understanding|experience)\s+(?:of|with|in)\s+[^\n.,]+)",
            r"(must\s+have\s+[^\n.,]+)",
            r"(required[:\s]+[^\n.,]+)",
        ]

        nice_patterns = [
            r"(nice\s+to\s+have[:\s]+[^\n.,]+)",
            r"(preferred[:\s]+[^\n.,]+)",
            r"(bonus[:\s]+[^\n.,]+)",
            r"(familiarity\s+with\s+[^\n.,]+)",
        ]

        for pattern in required_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            required.extend(m.strip() for m in matches if m.strip())

        for pattern in nice_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            nice_to_have.extend(m.strip() for m in matches if m.strip())

    return {"required": required, "nice_to_have": nice_to_have}


def identify_technical_skills(text: str) -> list[str]:
    """Identify technical skills mentioned in the job description.

    Args:
        text: Job description text

    Returns:
        List of technical skills found
    """
    if not text:
        return []

    text_lower = text.lower()
    found_skills = []

    for skill in TECHNICAL_KEYWORDS:
        if skill in text_lower:
            found_skills.append(skill)

    return sorted(found_skills)


def identify_leadership_skills(text: str) -> list[str]:
    """Identify leadership and soft skills mentioned in the job description.

    Args:
        text: Job description text

    Returns:
        List of leadership skills found
    """
    if not text:
        return []

    text_lower = text.lower()
    found_skills = []

    for skill in LEADERSHIP_KEYWORDS:
        if skill in text_lower:
            found_skills.append(skill)

    # Also extract full sentences containing leadership keywords
    leadership_sentences = []
    sentences = re.split(r"[.!?]+", text)

    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in LEADERSHIP_KEYWORDS):
            leadership_sentences.append(sentence.strip())

    # Combine keyword matches with relevant sentences
    found_skills.extend(leadership_sentences[:3])  # Limit to top 3 sentences

    return found_skills


def identify_domain_expertise(text: str) -> list[str]:
    """Identify domain-specific expertise requirements.

    Args:
        text: Job description text

    Returns:
        List of domain expertise areas
    """
    if not text:
        return []

    text_lower = text.lower()
    found_expertise = []

    for expertise in DOMAIN_KEYWORDS:
        if expertise in text_lower:
            found_expertise.append(expertise)

    return sorted(found_expertise)


def generate_ats_keywords(text: str) -> list[str]:
    """Generate ATS-optimized keyword list.

    Args:
        text: Job description text

    Returns:
        List of ATS keywords sorted by importance
    """
    if not text:
        return []

    # Combine all keyword types
    all_keywords = extract_keywords(text)

    # Calculate frequency
    frequency = calculate_keyword_frequency(text)

    # Sort by frequency (most frequent first)
    sorted_keywords = sorted(all_keywords, key=lambda k: frequency.get(k, 0), reverse=True)

    return sorted_keywords


def calculate_keyword_importance(text: str) -> dict[str, float]:
    """Calculate importance scores for keywords (0-1 normalized).

    Args:
        text: Job description text

    Returns:
        Dictionary mapping keywords to importance scores
    """
    if not text:
        return {}

    frequency = calculate_keyword_frequency(text)

    if not frequency:
        return {}

    # Get max frequency for normalization
    max_freq = max(frequency.values())

    # Calculate normalized scores
    importance = {}
    for keyword, count in frequency.items():
        # Base score on frequency (normalized)
        freq_score = count / max_freq

        # Boost score for keywords in key sections
        text_lower = text.lower()
        boost = 1.0

        # Check if in "required" section
        if re.search(
            rf"(?:required|must have)[\s\S]{{0,200}}\b{re.escape(keyword)}\b",
            text_lower,
        ):
            boost *= 1.5

        # Check if appears in title/header
        first_200_chars = text_lower[:200]
        if keyword in first_200_chars:
            boost *= 1.3

        importance[keyword] = min(freq_score * boost, 1.0)  # Cap at 1.0

    return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))


def analyze_job_description(text: str) -> dict[str, Any]:
    """Perform comprehensive analysis of job description.

    Args:
        text: Job description text

    Returns:
        Dictionary containing complete analysis
    """
    if not text:
        return {
            "technical_skills": [],
            "leadership_skills": [],
            "domain_expertise": [],
            "required_skills": [],
            "nice_to_have_skills": [],
            "ats_keywords": [],
            "keyword_importance": {},
            "keyword_frequency": {},
        }

    # Perform all analyses
    technical_skills = identify_technical_skills(text)
    leadership_skills = identify_leadership_skills(text)
    domain_expertise = identify_domain_expertise(text)

    requirements = categorize_requirements(text)
    ats_keywords = generate_ats_keywords(text)
    keyword_importance = calculate_keyword_importance(text)
    keyword_frequency = calculate_keyword_frequency(text)

    return {
        "technical_skills": technical_skills,
        "leadership_skills": leadership_skills,
        "domain_expertise": domain_expertise,
        "required_skills": requirements["required"],
        "nice_to_have_skills": requirements["nice_to_have"],
        "ats_keywords": ats_keywords,
        "keyword_importance": keyword_importance,
        "keyword_frequency": keyword_frequency,
    }
