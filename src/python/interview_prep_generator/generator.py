"""Interview Prep Generator.

Generates comprehensive interview preparation materials including:
- Technical questions with answer templates
- Behavioral questions with STAR answers
- Company-specific questions
- Questions to ask interviewers
- Key talking points
"""

import re


def calculate_skill_overlap(skills1: list[str], skills2: list[str]) -> float:
    """Calculate overlap between two skill sets."""
    if not skills1 or not skills2:
        return 0.0

    skills1_lower = {s.lower() for s in skills1}
    skills2_lower = {s.lower() for s in skills2}

    overlap = len(skills1_lower & skills2_lower)
    total = len(skills1_lower | skills2_lower)

    return overlap / total if total > 0 else 0.0


def extract_metrics(text: str) -> list[str]:
    """Extract metrics from text (percentages, numbers, etc.)."""
    metrics = []

    # Find percentages
    percentages = re.findall(r"\d+%", text)
    metrics.extend(percentages)

    # Find "Nx" patterns (10x, 5x, etc.)
    multipliers = re.findall(r"\d+x", text, re.IGNORECASE)
    metrics.extend(multipliers)

    # Find time improvements
    time_patterns = re.findall(
        r"\d+\s*(hours?|minutes?|seconds?|days?|weeks?|months?)", text
    )
    metrics.extend(time_patterns)

    # Find dollar amounts
    dollars = re.findall(r"\$\d+[MKB]?", text)
    metrics.extend(dollars)

    # Find uptime percentages
    uptime = re.findall(r"99\.\d+%", text)
    metrics.extend(uptime)

    return metrics


def format_star_answer(anecdote: dict) -> str:
    """Format anecdote as STAR answer."""
    content = anecdote.get("content", "")

    # Check if already in STAR format
    has_star_markers = all(
        marker in content
        for marker in ["Situation:", "Task:", "Action:", "Result:"]
    )

    if has_star_markers:
        # Already formatted, just clean up
        lines = []
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("**Context:**"):
                # Convert **Context:** to Situation if present
                if line.startswith("**") and line.endswith("**"):
                    continue
                lines.append(line)
        return "\n".join(lines)

    # Parse content sections
    situation = ""
    task = ""
    action = ""
    result = ""

    # Look for context section
    if "**Context:**" in content:
        parts = content.split("**Context:**")
        if len(parts) > 1:
            context_section = parts[1].split("**")[0].strip()
            situation = context_section

    # Look for actions section
    if "**Actions:**" in content or "**Action:**" in content:
        marker = "**Actions:**" if "**Actions:**" in content else "**Action:**"
        parts = content.split(marker)
        if len(parts) > 1:
            action_section = parts[1].split("**")[0].strip()
            action = action_section

    # Look for results section
    if "**Results:**" in content or "**Result:**" in content:
        marker = "**Results:**" if "**Results:**" in content else "**Result:**"
        parts = content.split(marker)
        if len(parts) > 1:
            result_section = parts[1].split("**")[0].strip()
            result = result_section

    # Build STAR answer
    star_parts = []

    if situation:
        star_parts.append(f"**Situation:** {situation}")

    if task or anecdote.get("title"):
        task_text = task or anecdote.get("title", "")
        star_parts.append(f"**Task:** {task_text}")

    if action:
        star_parts.append(f"**Action:** {action}")

    if result or anecdote.get("impact"):
        result_text = result or anecdote.get("impact", "")
        star_parts.append(f"**Result:** {result_text}")

    return "\n\n".join(star_parts)


def match_anecdotes_to_questions(
    questions: list[str], anecdotes: list[dict]
) -> list[dict]:
    """Match anecdotes to behavioral questions based on relevance."""
    matches = []

    for question in questions:
        question_lower = question.lower()
        best_match = None
        best_score = 0.0

        for anecdote in anecdotes:
            score = 0.0

            # Check title match
            title = anecdote.get("title", "").lower()
            if any(word in title for word in question_lower.split()):
                score += 2.0

            # Check skills match
            skills = [s.lower() for s in anecdote.get("skills", [])]
            question_words = set(question_lower.split())
            skill_matches = len([s for s in skills if s in question_words])
            score += skill_matches * 1.5

            # Check content match
            content = anecdote.get("content", "").lower()
            keyword_matches = sum(
                1 for word in question_lower.split() if word in content
            )
            score += keyword_matches * 0.5

            if score > best_score:
                best_score = score
                best_match = anecdote

        matches.append(
            {
                "question": question,
                "anecdote": best_match or anecdotes[0] if anecdotes else None,
                "score": best_score,
            }
        )

    return matches


def generate_technical_questions(
    jd_analysis: dict, anecdotes: list[dict]
) -> list[dict]:
    """Generate technical questions based on JD requirements."""
    questions = []

    technical_skills = jd_analysis.get("technical_skills", [])
    domain_expertise = jd_analysis.get("domain_expertise", [])
    required_skills = jd_analysis.get("required_skills", [])
    seniority = jd_analysis.get("seniority_level", "mid")

    # Generate experience-based questions for top skills
    for skill in technical_skills[:5]:
        # Find relevant anecdote
        relevant_anecdote = None
        for anecdote in anecdotes:
            anecdote_skills = [s.lower() for s in anecdote.get("skills", [])]
            if skill.lower() in anecdote_skills:
                relevant_anecdote = anecdote
                break

        question_text = f"Describe your experience with {skill}"
        answer = ""

        if relevant_anecdote:
            answer = format_star_answer(relevant_anecdote)
        else:
            answer = f"**Your Answer Template:**\n[Based on your {skill} experience, describe a specific project or achievement]"

        questions.append({"question": question_text, "answer": answer, "type": "experience"})

    # Add system design questions for senior roles
    if seniority in ["senior", "lead", "staff", "principal", "director", "vp"]:
        # System design question
        if "distributed systems" in domain_expertise or "architecture" in domain_expertise:
            question_text = "How would you design a real-time data pipeline that processes millions of events per day?"

            # Find relevant architecture anecdote
            arch_anecdote = None
            for anecdote in anecdotes:
                skills = [s.lower() for s in anecdote.get("skills", [])]
                if any(
                    s in skills
                    for s in ["architecture", "system design", "distributed", "scalability"]
                ):
                    arch_anecdote = anecdote
                    break

            if arch_anecdote:
                answer = f"**Your Answer Template (based on similar experience):**\n\n{format_star_answer(arch_anecdote)}"
            else:
                answer = "**Your Answer Template:**\n[Describe your approach: requirements gathering, architecture decisions, technology choices, scalability considerations, and trade-offs]"

            questions.append({"question": question_text, "answer": answer, "type": "system_design"})

        # Scalability question
        if "scalability" in domain_expertise or "performance" in domain_expertise:
            question_text = "Tell me about a time you improved system performance or scalability"

            # Find performance anecdote
            perf_anecdote = None
            for anecdote in anecdotes:
                content = anecdote.get("content", "").lower()
                impact = anecdote.get("impact", "").lower()
                if any(
                    term in content or term in impact
                    for term in ["scale", "performance", "latency", "throughput", "optimize"]
                ):
                    perf_anecdote = anecdote
                    break

            if perf_anecdote:
                answer = format_star_answer(perf_anecdote)
            else:
                answer = "**Your Answer Template:**\n[Describe the performance challenge, your approach, specific optimizations, and measurable results]"

            questions.append({"question": question_text, "answer": answer, "type": "performance"})

    # Add domain-specific questions
    for domain in domain_expertise[:2]:
        question_text = f"What's your approach to {domain}?"

        # Find relevant anecdote
        domain_anecdote = None
        for anecdote in anecdotes:
            skills = [s.lower() for s in anecdote.get("skills", [])]
            content = anecdote.get("content", "").lower()
            if domain.lower() in skills or domain.lower() in content:
                domain_anecdote = anecdote
                break

        if domain_anecdote:
            answer = f"**Your Answer Template:**\n\n{format_star_answer(domain_anecdote)}"
        else:
            answer = f"**Your Answer Template:**\n[Share your philosophy and approach to {domain}, backed by specific examples]"

        questions.append({"question": question_text, "answer": answer, "type": "domain"})

    return questions[:8]  # Return top 8 technical questions


def generate_behavioral_questions(
    jd_analysis: dict, anecdotes: list[dict]
) -> list[dict]:
    """Generate behavioral questions with STAR answers."""
    questions = []

    leadership_skills = jd_analysis.get("leadership_skills", [])
    seniority = jd_analysis.get("seniority_level", "mid")

    # Common behavioral questions
    behavioral_prompts = [
        "Tell me about a time you resolved a conflict",
        "Describe a situation where you had to handle a difficult team member",
        "Give an example of a project that didn't go as planned and how you handled it",
        "Tell me about a time you had to make a difficult technical decision",
    ]

    # Add leadership questions for senior roles
    if seniority in ["senior", "lead", "staff", "principal", "director", "vp"]:
        behavioral_prompts.extend([
            "Describe your experience managing underperforming team members",
            "Tell me about a time you had to influence without authority",
            "How do you handle disagreements with other leaders or stakeholders?",
        ])

    # Match questions to anecdotes
    matches = match_anecdotes_to_questions(behavioral_prompts, anecdotes)

    for match in matches[:7]:  # Top 7 behavioral questions
        question_text = match["question"]
        matched_anecdote = match["anecdote"]

        if matched_anecdote:
            answer = f"**STAR Answer:**\n\n{format_star_answer(matched_anecdote)}"
        else:
            answer = "**STAR Answer:**\n[Prepare a specific example using the STAR format]"

        questions.append({"question": question_text, "answer": answer})

    return questions


def generate_company_specific_questions(
    company_research: dict, jd_analysis: dict
) -> list[dict]:
    """Generate company-specific questions."""
    questions = []

    company = company_research.get("company", "the company")
    mission = company_research.get("mission", "")
    recent_news = company_research.get("recent_news", [])
    values = company_research.get("values", [])

    # Why this company?
    answer_parts = ["**Your Answer:**\n"]

    if recent_news:
        answer_parts.append(
            f"\"I'm excited about {company}'s recent {recent_news[0].lower()}. "
        )
    else:
        answer_parts.append(f"\"I'm excited about the opportunity at {company}. ")

    if mission:
        answer_parts.append(
            f"Your mission to {mission.lower()} aligns perfectly with my passion for building impactful solutions. "
        )

    if values:
        answer_parts.append(
            f"I'm particularly drawn to your values around {', '.join(values[:2])}, which resonate with my own professional values. "
        )

    answer_parts.append(
        "Having followed your growth, I'm impressed by [specific aspect] and excited to contribute to [specific goal].\""
    )

    questions.append(
        {"question": f"Why {company}?", "answer": "".join(answer_parts)}
    )

    # What interests you about this role?
    if jd_analysis.get("domain_expertise"):
        domains = jd_analysis.get("domain_expertise", [])[:2]
        role_answer = f"**Your Answer:**\n\"This role combines my strengths in {' and '.join(domains)}. I'm particularly excited about the opportunity to [specific responsibility from JD]. Based on my experience with [relevant achievement], I know I can make an immediate impact.\""
        questions.append(
            {"question": "What interests you about this role?", "answer": role_answer}
        )

    return questions


def generate_questions_to_ask(
    company_research: dict, jd_analysis: dict
) -> dict[str, list[str]]:
    """Generate thoughtful questions to ask interviewers."""
    questions: dict[str, list[str]] = {"technical": [], "culture": [], "strategic": []}

    seniority = jd_analysis.get("seniority_level", "mid")

    # Technical questions
    questions["technical"] = [
        "What's your current deployment frequency and what are the main blockers to deploying more often?",
        "How does the team handle on-call and incident management?",
        "What's the balance between new feature development and technical debt?",
        "Can you walk me through a recent technical challenge the team faced and how you solved it?",
        "How do you approach testing and quality assurance?",
    ]

    # Culture questions
    questions["culture"] = [
        "What does work-life balance look like for this role?",
        "How does the team collaborate - what does a typical day look like?",
        "What are the biggest opportunities for professional growth in this role?",
        "How do you support continuous learning and development?",
        "How are decisions made between engineering and product?",
    ]

    # Strategic questions (tailored by seniority)
    if seniority in ["director", "vp", "principal", "staff"]:
        questions["strategic"] = [
            "What are the top 3 technical challenges for this role in the next year?",
            "How do you see the engineering organization evolving over the next 2-3 years?",
            "What does success look like in the first 90 days?",
            "How does engineering partner with product and other teams?",
            "What's the company's approach to technical strategy and architecture decisions?",
        ]
    else:
        questions["strategic"] = [
            "What does success look like in this role in the first 6 months?",
            "How does this role contribute to the team's larger goals?",
            "What are the biggest challenges the team is facing right now?",
            "What opportunities are there to take on additional responsibility?",
        ]

    # Add company-specific questions if we have recent news
    if company_research.get("recent_news"):
        news = company_research["recent_news"][0]
        if "funding" in news.lower():
            questions["strategic"].insert(
                0, "How will the recent funding impact the engineering team's priorities?"
            )
        elif "partnership" in news.lower():
            questions["strategic"].insert(
                0, "How does the recent partnership affect the technical roadmap?"
            )

    return questions


def extract_key_talking_points(
    anecdotes: list[dict], jd_analysis: dict
) -> list[str]:
    """Extract key talking points from anecdotes."""
    talking_points = []

    # Get top skills from JD
    top_skills = set(
        [s.lower() for s in jd_analysis.get("technical_skills", [])[:5]]
        + [s.lower() for s in jd_analysis.get("leadership_skills", [])[:3]]
    )

    # Find anecdotes that match top skills
    relevant_anecdotes = []
    for anecdote in anecdotes:
        anecdote_skills = {s.lower() for s in anecdote.get("skills", [])}
        overlap = len(top_skills & anecdote_skills)
        if overlap > 0:
            relevant_anecdotes.append((anecdote, overlap))

    # Sort by relevance
    relevant_anecdotes.sort(key=lambda x: x[1], reverse=True)

    # Extract talking points
    for anecdote, _ in relevant_anecdotes[:5]:
        impact = anecdote.get("impact", "")
        title = anecdote.get("title", "")

        # Create concise talking point
        if impact:
            talking_point = f"{title}: {impact}"
        else:
            # Extract metric from content
            content = anecdote.get("content", "")
            metrics = extract_metrics(content)
            if metrics:
                talking_point = f"{title} ({metrics[0]})"
            else:
                talking_point = title

        talking_points.append(talking_point)

    return talking_points


def generate_interview_prep(
    company_research: dict,
    jd_analysis: dict,
    anecdotes: list[dict],
    position: str,
) -> str:
    """Generate complete interview preparation document."""
    company = company_research.get("company", "Company")

    # Generate all sections
    technical_questions = generate_technical_questions(jd_analysis, anecdotes)
    behavioral_questions = generate_behavioral_questions(jd_analysis, anecdotes)
    company_questions = generate_company_specific_questions(
        company_research, jd_analysis
    )
    questions_to_ask = generate_questions_to_ask(company_research, jd_analysis)
    talking_points = extract_key_talking_points(anecdotes, jd_analysis)

    # Build markdown document
    sections = []

    # Header
    sections.append(f"# Interview Prep: {position} @ {company}\n")

    # Technical Questions
    sections.append("## Likely Technical Questions\n")
    for i, q in enumerate(technical_questions, 1):
        sections.append(f"### {i}. {q['question']}\n")
        sections.append(f"{q['answer']}\n")

    # Behavioral Questions
    sections.append("## Behavioral Questions\n")
    for i, q in enumerate(behavioral_questions, 1):
        sections.append(f"### {i}. {q['question']}\n")
        sections.append(f"{q['answer']}\n")

    # Company-Specific Questions
    if company_questions:
        sections.append("## Company-Specific Questions\n")
        for i, q in enumerate(company_questions, 1):
            sections.append(f"### {i}. {q['question']}\n")
            sections.append(f"{q['answer']}\n")

    # Questions to Ask
    sections.append("## Questions to Ask Interviewers\n")

    sections.append("### Technical Questions\n")
    for question in questions_to_ask.get("technical", [])[:5]:
        sections.append(f"- {question}\n")
    sections.append("")

    sections.append("### Culture Questions\n")
    for question in questions_to_ask.get("culture", [])[:5]:
        sections.append(f"- {question}\n")
    sections.append("")

    sections.append("### Strategic Questions\n")
    for question in questions_to_ask.get("strategic", [])[:5]:
        sections.append(f"- {question}\n")
    sections.append("")

    # Key Talking Points
    if talking_points:
        sections.append("## Key Talking Points\n")
        for point in talking_points:
            sections.append(f"- {point}\n")
        sections.append("")

    return "\n".join(sections)
