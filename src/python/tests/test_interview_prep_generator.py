"""Tests for Interview Prep Generator."""

import pytest


class TestInterviewPrepGenerator:
    """Test suite for interview preparation generation functionality."""

    @pytest.fixture
    def sample_jd_analysis(self) -> dict:
        """Sample JD analysis for testing."""
        return {
            "technical_skills": [
                "kubernetes",
                "python",
                "react",
                "aws",
                "docker",
                "postgresql",
                "microservices",
            ],
            "leadership_skills": [
                "mentoring",
                "team leadership",
                "cross-functional collaboration",
                "stakeholder management",
            ],
            "domain_expertise": [
                "distributed systems",
                "architecture",
                "scalability",
                "system design",
            ],
            "required_skills": [
                "5+ years of experience with Python and modern web frameworks",
                "Strong knowledge of React and TypeScript",
                "Experience with AWS, Docker, and Kubernetes",
                "Proven track record of leading engineering teams",
            ],
            "nice_to_have_skills": [
                "Experience with GraphQL",
                "Knowledge of machine learning systems",
            ],
            "ats_keywords": [
                "python",
                "react",
                "aws",
                "kubernetes",
                "leadership",
                "architecture",
            ],
            "seniority_level": "director",
        }

    @pytest.fixture
    def sample_company_research(self) -> dict:
        """Sample company research for testing."""
        return {
            "company": "TechCorp",
            "mission": "To build innovative cloud solutions that scale globally",
            "values": ["Innovation", "Collaboration", "Customer Focus", "Excellence"],
            "recent_news": [
                "Announced $50M Series B funding",
                "Launched new AWS partnership program",
                "Expanded engineering team to 200+ engineers",
            ],
            "culture": "Fast-paced startup environment with strong engineering culture and focus on work-life balance",
            "tech_stack": ["Python", "React", "AWS", "Kubernetes", "PostgreSQL"],
        }

    @pytest.fixture
    def sample_anecdotes(self) -> list[dict]:
        """Sample anecdotes for testing."""
        return [
            {
                "title": "Led Kubernetes Migration",
                "skills": ["kubernetes", "docker", "leadership", "aws", "devops"],
                "impact": "Reduced deployment time by 70%",
                "content": """Led the migration of our monolithic application to a Kubernetes-based microservices architecture.

**Context:**
- Legacy monolithic application with 2-hour deployment cycles
- Team of 5 engineers unfamiliar with container orchestration

**Actions:**
- Designed microservices architecture with 12 independent services
- Implemented Kubernetes cluster on AWS EKS with auto-scaling
- Trained team on Docker containerization and Kubernetes best practices

**Results:**
- Reduced deployment time from 2 hours to 20 minutes (70% improvement)
- Improved system uptime from 99.5% to 99.9%
- Enabled independent service scaling, reducing infrastructure costs by 30%
""",
            },
            {
                "title": "Resolved Team Conflict",
                "skills": ["leadership", "conflict resolution", "communication"],
                "impact": "Restored team productivity and morale",
                "content": """Resolved a major conflict between frontend and backend teams that was blocking project delivery.

**Situation:**
- Frontend and backend teams had conflicting API design approaches
- Project was 2 weeks behind schedule
- Team morale was declining

**Task:**
- Needed to mediate the conflict and get project back on track

**Action:**
- Facilitated joint design session with both teams
- Established clear API contract and documentation standards
- Created cross-functional pairs for remaining work

**Result:**
- Delivered project 1 week ahead of revised timeline
- Improved team collaboration scores by 40%
- Established lasting cross-team communication practices
""",
            },
            {
                "title": "Managed Underperforming Engineer",
                "skills": ["leadership", "mentoring", "performance management"],
                "impact": "Turned around performance or made difficult personnel decision",
                "content": """Addressed performance issues with a senior engineer on my team.

**Situation:**
- Senior engineer missing deadlines and producing buggy code
- Team members expressing frustration
- Engineer had strong technical skills but lacked focus

**Task:**
- Improve performance or make personnel decision

**Action:**
- Had honest 1-on-1 conversation about expectations
- Created 30-day performance improvement plan with clear goals
- Provided daily check-ins and support
- Identified personal issues affecting work

**Result:**
- Engineer improved performance and met all goals
- Became one of top performers within 2 months
- Strengthened team trust in my leadership
""",
            },
            {
                "title": "Built Real-Time Analytics Platform",
                "skills": [
                    "python",
                    "react",
                    "system design",
                    "architecture",
                    "postgresql",
                ],
                "impact": "Processed 10M events daily with sub-second latency",
                "content": """Architected and built a real-time analytics platform for user behavior tracking.

**Context:**
- Needed to process millions of events daily for product analytics
- Existing batch processing had 24-hour delay

**Actions:**
- Designed event streaming architecture using Kafka and PostgreSQL
- Built Python backend API with async processing
- Created React dashboard with real-time WebSocket updates
- Implemented data aggregation and caching strategies

**Results:**
- Processed 10M+ events daily with sub-second latency
- Reduced data processing delay from 24 hours to real-time
- Increased product team velocity by 35% with faster insights
""",
            },
            {
                "title": "Scaled Database to 10x Traffic",
                "skills": ["postgresql", "aws", "architecture", "performance"],
                "impact": "Handled 10x traffic increase",
                "content": """Scaled database infrastructure to support 10x traffic growth.

**Context:**
- Database performance degrading under increasing load
- Query times exceeding 5 seconds during peak hours
- Business growth projecting 10x traffic in 6 months

**Actions:**
- Implemented PostgreSQL read replicas on AWS RDS
- Optimized slow queries and added strategic indexes
- Set up connection pooling and Redis caching layer
- Implemented database sharding for largest tables

**Results:**
- Reduced query time from 5s to 200ms (96% improvement)
- Handled 10x traffic increase without additional hardware costs
- Achieved 99.99% uptime during high-growth period
""",
            },
        ]

    @pytest.fixture
    def sample_user_info(self) -> dict:
        """Sample user information for testing."""
        return {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1 (555) 123-4567",
            "linkedin": "linkedin.com/in/johndoe",
        }

    def test_technical_question_generation(
        self, sample_jd_analysis: dict, sample_anecdotes: list[dict]
    ) -> None:
        """Test technical question generation from JD requirements."""
        from interview_prep_generator.generator import generate_technical_questions

        questions = generate_technical_questions(
            jd_analysis=sample_jd_analysis,
            anecdotes=sample_anecdotes,
        )

        # Should generate multiple questions
        assert len(questions) >= 3

        # Should include questions about key technical skills
        question_text = " ".join([q["question"] for q in questions])
        assert "kubernetes" in question_text.lower() or "k8s" in question_text.lower()
        assert (
            "python" in question_text.lower()
            or "distributed" in question_text.lower()
            or "microservices" in question_text.lower()
        )

        # Each question should have an answer template
        for question in questions:
            assert "question" in question
            assert "answer" in question
            assert len(question["answer"]) > 50  # Substantial answer

    def test_behavioral_question_generation(
        self, sample_jd_analysis: dict, sample_anecdotes: list[dict]
    ) -> None:
        """Test behavioral question generation."""
        from interview_prep_generator.generator import generate_behavioral_questions

        questions = generate_behavioral_questions(
            jd_analysis=sample_jd_analysis,
            anecdotes=sample_anecdotes,
        )

        # Should generate multiple behavioral questions
        assert len(questions) >= 3

        # Should include leadership questions for senior roles
        question_text = " ".join([q["question"] for q in questions])
        has_leadership = any(
            term in question_text.lower()
            for term in [
                "team",
                "lead",
                "conflict",
                "manage",
                "underperform",
                "difficult",
            ]
        )
        assert has_leadership

        # Each question should have STAR-format answer
        for question in questions:
            assert "question" in question
            assert "answer" in question
            answer = question["answer"]
            # STAR format indicators
            has_star_elements = any(
                marker in answer for marker in ["Situation:", "Task:", "Action:", "Result:"]
            )
            assert has_star_elements or len(answer) > 100

    def test_star_answer_from_anecdote(self, sample_anecdotes: list[dict]) -> None:
        """Test STAR answer preparation from anecdotes."""
        from interview_prep_generator.generator import format_star_answer

        anecdote = sample_anecdotes[1]  # Conflict resolution anecdote

        star_answer = format_star_answer(anecdote)

        # Should have STAR structure
        assert "Situation:" in star_answer or "Situation" in star_answer
        assert "Task:" in star_answer or "Task" in star_answer
        assert "Action:" in star_answer or "Action" in star_answer
        assert "Result:" in star_answer or "Result" in star_answer

        # Should be substantial but concise (150-250 words optimal)
        word_count = len(star_answer.split())
        assert 100 <= word_count <= 400

    def test_company_specific_questions(
        self, sample_company_research: dict, sample_jd_analysis: dict
    ) -> None:
        """Test company-specific question generation."""
        from interview_prep_generator.generator import (
            generate_company_specific_questions,
        )

        questions = generate_company_specific_questions(
            company_research=sample_company_research,
            jd_analysis=sample_jd_analysis,
        )

        # Should generate company-specific questions
        assert len(questions) >= 1

        # Should reference company details
        for question in questions:
            assert "question" in question
            assert "answer" in question

        # At least one should mention company specifics
        all_text = " ".join([q["question"] + " " + q["answer"] for q in questions])
        has_company_specifics = any(
            term in all_text
            for term in [
                sample_company_research["company"],
                "Series B",
                "AWS partnership",
            ]
        )
        assert has_company_specifics

    def test_questions_to_ask_generation(
        self, sample_company_research: dict, sample_jd_analysis: dict
    ) -> None:
        """Test questions-to-ask generation."""
        from interview_prep_generator.generator import generate_questions_to_ask

        questions = generate_questions_to_ask(
            company_research=sample_company_research,
            jd_analysis=sample_jd_analysis,
        )

        # Should have multiple categories
        assert "technical" in questions
        assert "culture" in questions
        assert "strategic" in questions

        # Each category should have questions
        assert len(questions["technical"]) >= 2
        assert len(questions["culture"]) >= 2
        assert len(questions["strategic"]) >= 2

        # Questions should be specific and thoughtful
        all_questions = questions["technical"] + questions["culture"] + questions["strategic"]
        for q in all_questions:
            assert len(q) > 20  # Not trivial questions
            assert "?" in q  # Actual questions

    def test_anecdote_matching_to_questions(
        self, sample_jd_analysis: dict, sample_anecdotes: list[dict]
    ) -> None:
        """Test that anecdotes are matched to relevant questions."""
        from interview_prep_generator.generator import match_anecdotes_to_questions

        behavioral_questions = [
            "Tell me about a time you resolved a conflict",
            "Describe a situation where you managed an underperforming team member",
            "Give an example of a difficult technical decision you made",
        ]

        matches = match_anecdotes_to_questions(
            questions=behavioral_questions,
            anecdotes=sample_anecdotes,
        )

        # Should match anecdotes to questions
        assert len(matches) == len(behavioral_questions)

        # Conflict question should match conflict anecdote
        conflict_match = matches[0]
        assert "conflict" in conflict_match["anecdote"]["title"].lower()

        # Underperformer question should match performance management anecdote
        underperformer_match = matches[1]
        assert (
            "underperform" in underperformer_match["anecdote"]["title"].lower()
            or "performance" in underperformer_match["anecdote"]["title"].lower()
        )

    def test_system_design_questions_for_senior_roles(self, sample_jd_analysis: dict) -> None:
        """Test system design question generation for senior roles."""
        from interview_prep_generator.generator import generate_technical_questions

        # Director-level role should include system design
        questions = generate_technical_questions(
            jd_analysis=sample_jd_analysis,
            anecdotes=[],
        )

        question_text = " ".join([q["question"] for q in questions])

        # Should include system design questions
        has_system_design = any(
            term in question_text.lower()
            for term in [
                "design",
                "architect",
                "scale",
                "system",
                "build",
                "how would you",
            ]
        )
        assert has_system_design

    def test_key_talking_points_extraction(
        self, sample_anecdotes: list[dict], sample_jd_analysis: dict
    ) -> None:
        """Test extraction of key talking points."""
        from interview_prep_generator.generator import extract_key_talking_points

        talking_points = extract_key_talking_points(
            anecdotes=sample_anecdotes,
            jd_analysis=sample_jd_analysis,
        )

        # Should extract multiple talking points
        assert len(talking_points) >= 3

        # Should include metrics
        points_text = " ".join(talking_points)
        has_metrics = any(char in points_text for char in ["%", "x", "M", "ms", "hours"])
        assert has_metrics

        # Should be concise
        for point in talking_points:
            assert len(point) < 200  # Brief talking points

    def test_complete_interview_prep_generation(
        self,
        sample_company_research: dict,
        sample_jd_analysis: dict,
        sample_anecdotes: list[dict],
    ) -> None:
        """Test complete interview prep document generation."""
        from interview_prep_generator.generator import generate_interview_prep

        prep = generate_interview_prep(
            company_research=sample_company_research,
            jd_analysis=sample_jd_analysis,
            anecdotes=sample_anecdotes,
            position="Director of Engineering",
        )

        # Should be markdown format
        assert "# Interview Prep:" in prep or "#" in prep

        # Should include all major sections
        assert "Technical Questions" in prep or "technical" in prep.lower()
        assert "Behavioral Questions" in prep or "behavioral" in prep.lower()
        assert (
            "Questions to Ask" in prep
            or "questions to ask" in prep.lower()
            or "ask interviewers" in prep.lower()
        )

        # Should include company name
        assert sample_company_research["company"] in prep

        # Should include position
        assert "Director" in prep or "Engineering" in prep

    def test_answer_length_control(self, sample_anecdotes: list[dict]) -> None:
        """Test that answers are appropriate length (150-250 words for 2-3 min)."""
        from interview_prep_generator.generator import format_star_answer

        for anecdote in sample_anecdotes[:3]:
            answer = format_star_answer(anecdote)
            word_count = len(answer.split())

            # Should be in reasonable range for verbal delivery
            assert 50 <= word_count <= 400, f"Answer should be 50-400 words, got {word_count}"

    def test_handles_missing_company_research(
        self, sample_jd_analysis: dict, sample_anecdotes: list[dict]
    ) -> None:
        """Test handling of missing company research."""
        from interview_prep_generator.generator import generate_interview_prep

        minimal_research = {
            "company": "Unknown Corp",
            "mission": "",
            "values": [],
            "recent_news": [],
            "culture": "",
            "tech_stack": [],
        }

        prep = generate_interview_prep(
            company_research=minimal_research,
            jd_analysis=sample_jd_analysis,
            anecdotes=sample_anecdotes,
            position="Software Engineer",
        )

        # Should still generate valid prep
        assert len(prep) > 500
        assert "Unknown Corp" in prep

        # Should have technical and behavioral sections
        assert "question" in prep.lower()

    def test_handles_no_anecdotes(
        self, sample_company_research: dict, sample_jd_analysis: dict
    ) -> None:
        """Test handling when no anecdotes are available."""
        from interview_prep_generator.generator import generate_interview_prep

        prep = generate_interview_prep(
            company_research=sample_company_research,
            jd_analysis=sample_jd_analysis,
            anecdotes=[],
            position="Software Engineer",
        )

        # Should still generate questions
        assert len(prep) > 300
        assert "question" in prep.lower()

        # May have generic answer templates instead of specific examples
        assert "Technical" in prep or "technical" in prep

    def test_question_relevance_to_role_level(self) -> None:
        """Test that questions are appropriate for role level."""
        from interview_prep_generator.generator import generate_behavioral_questions

        # Junior role
        junior_jd = {
            "seniority_level": "junior",
            "leadership_skills": [],
            "technical_skills": ["python", "react"],
        }

        junior_questions = generate_behavioral_questions(
            jd_analysis=junior_jd,
            anecdotes=[],
        )

        junior_text = " ".join([q["question"] for q in junior_questions])

        # Should focus on individual contribution
        # Less likely to ask about managing teams
        assert len(junior_questions) >= 2

        # Director role
        director_jd = {
            "seniority_level": "director",
            "leadership_skills": ["team leadership", "mentoring", "strategy"],
            "technical_skills": ["architecture", "system design"],
        }

        director_questions = generate_behavioral_questions(
            jd_analysis=director_jd,
            anecdotes=[],
        )

        director_text = " ".join([q["question"] for q in director_questions])

        # Should include leadership questions
        has_leadership = any(
            term in director_text.lower()
            for term in ["team", "lead", "manage", "organization", "strategy"]
        )
        assert has_leadership

    def test_metrics_included_in_answers(self, sample_anecdotes: list[dict]) -> None:
        """Test that metrics are included in answers."""
        from interview_prep_generator.generator import format_star_answer

        anecdote = sample_anecdotes[0]  # Kubernetes migration with metrics

        answer = format_star_answer(anecdote)

        # Should include specific metrics
        has_metrics = any(
            metric in answer for metric in ["70%", "99.9%", "30%", "2 hours", "20 minutes"]
        )
        assert has_metrics

    def test_markdown_formatting(
        self,
        sample_company_research: dict,
        sample_jd_analysis: dict,
        sample_anecdotes: list[dict],
    ) -> None:
        """Test that output uses proper markdown formatting."""
        from interview_prep_generator.generator import generate_interview_prep

        prep = generate_interview_prep(
            company_research=sample_company_research,
            jd_analysis=sample_jd_analysis,
            anecdotes=sample_anecdotes,
            position="Director of Engineering",
        )

        # Should have headings
        assert prep.count("#") >= 3

        # Should have proper structure
        assert prep.count("\n\n") >= 5  # Multiple sections

        # Should use bold for emphasis
        assert "**" in prep or "*" in prep

    def test_includes_specific_metrics_in_talking_points(
        self, sample_anecdotes: list[dict], sample_jd_analysis: dict
    ) -> None:
        """Test that talking points include specific metrics."""
        from interview_prep_generator.generator import extract_key_talking_points

        talking_points = extract_key_talking_points(
            anecdotes=sample_anecdotes,
            jd_analysis=sample_jd_analysis,
        )

        # Should include numbers and metrics
        points_text = " ".join(talking_points)

        # Check for various metric formats
        has_numbers = any(char.isdigit() for char in points_text)
        assert has_numbers

        # Should include specific achievements
        assert len(talking_points) >= 3
