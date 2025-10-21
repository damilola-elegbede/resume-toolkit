# Resume Toolkit

**Complete Job Application Workflow System**

## Project Overview

### What It Is

Resume Toolkit is a comprehensive job application automation system that streamlines the entire job search process from resume optimization to application tracking. Built as a hybrid TypeScript/Python system integrated with Claude Code, it provides intelligent automation for resume parsing, job description analysis, ATS optimization, cover letter generation, and application tracking.

### Why It Exists

Job searching is time-consuming and repetitive. Applicants spend hours:

- Tailoring resumes for each position
- Writing customized cover letters
- Researching companies
- Tracking application status
- Preparing for interviews
- Managing multiple versions of documents

Resume Toolkit automates these tasks while maintaining personalization and quality, allowing job seekers to focus on strategic activities like networking and interview preparation.

### Key Features and Capabilities

- **Resume Intelligence**: Parse, analyze, and optimize resumes for ATS compatibility
- **Job Description Analysis**: Extract key requirements, skills, and company culture indicators
- **Smart Optimization**: Automatically tailor resumes to specific job descriptions
- **ATS Scoring**: Predict how well your resume matches job requirements
- **Cover Letter Generation**: Create personalized, compelling cover letters
- **Company Research**: Gather intelligence on potential employers
- **Application Tracking**: Monitor status, deadlines, and follow-ups
- **Interview Preparation**: Generate likely questions and talking points
- **Master Orchestration**: `/apply` command executes the entire workflow
- **Data Persistence**: Turso DB for reliable, scalable storage

### Architecture Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                    (Claude Code + CLI)                       │
└───────────────────────┬─────────────────────────────────────┘
                        │ Slash Commands
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   TypeScript CLI Layer                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Command Router & Validation                         │   │
│  │  - /parse-resume    - /generate-cover-letter        │   │
│  │  - /analyze-jd      - /research-company             │   │
│  │  - /optimize-resume - /track-application            │   │
│  │  - /score-ats       - /application-dashboard        │   │
│  │  - /interview-prep  - /apply                        │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │ Process Spawning
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Python Backend Layer                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Core Processing Modules                             │   │
│  │  - PDF/DOCX Parsing    - NLP Analysis               │   │
│  │  - ATS Scoring Engine  - Web Scraping               │   │
│  │  - Template Rendering  - Company Research           │   │
│  │  - Data Validation     - AI Integration             │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │ SQL Queries
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                      Turso Database                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Tables: resumes, jobs, applications,                │   │
│  │          cover_letters, companies, analytics         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  File System Storage                         │
│              (.resume-toolkit/ directory)                    │
│  - base-resume.md      - templates/                         │
│  - anecdotes/          - applications/                      │
│  - analytics/                                               │
└─────────────────────────────────────────────────────────────┘
```

## Architecture

### Hybrid TypeScript/Python Design Rationale

**TypeScript CLI Layer**:

- **Rapid Development**: Fast iteration with modern tooling
- **Type Safety**: Catch errors at compile time
- **MCP Integration**: Seamless integration with Claude Code slash commands
- **User Experience**: Rich terminal UI with progress indicators
- **Package Ecosystem**: Access to npm ecosystem for utilities

**Python Backend Layer**:

- **NLP Libraries**: Superior text processing with spaCy, NLTK
- **PDF Processing**: Robust document parsing with PyPDF2, pdfplumber
- **Data Science**: NumPy, Pandas for analytics and scoring
- **AI/ML Integration**: Easy integration with ML models
- **Web Scraping**: Beautiful Soup, Scrapy for company research
- **Mature Ecosystem**: Battle-tested libraries for document processing

**Benefits of Hybrid Approach**:

- Best tool for each job
- TypeScript handles user interaction and orchestration
- Python handles heavy computation and document processing
- Clear separation of concerns
- Easy to test and maintain

### Technology Stack

**Frontend/CLI**:

- **TypeScript**: Type-safe JavaScript for CLI
- **Commander.js**: Command-line interface framework
- **Chalk**: Terminal styling and colors
- **Ora**: Elegant terminal spinners
- **Inquirer**: Interactive command-line prompts
- **Vitest**: Fast unit testing framework

**Backend/Processing**:

- **Python 3.11+**: Core processing language
- **PyPDF2/pdfplumber**: PDF parsing
- **python-docx**: DOCX parsing
- **spaCy**: Natural language processing
- **BeautifulSoup4**: Web scraping
- **Jinja2**: Template rendering
- **pytest**: Testing framework
- **black**: Code formatting
- **ruff**: Fast Python linter

**Database**:

- **Turso**: Edge database (libSQL/SQLite)
- **Drizzle ORM**: Type-safe database queries
- **SQLite**: Local development database

**AI Integration**:

- **Anthropic Claude API**: LLM capabilities
- **MCP (Model Context Protocol)**: Claude Code integration

**Development Tools**:

- **Git**: Version control
- **GitHub Actions**: CI/CD pipeline
- **Husky**: Git hooks
- **ESLint**: JavaScript/TypeScript linting
- **Prettier**: Code formatting
- **pre-commit**: Python pre-commit hooks

### Data Flow

**User Request Flow**:

```text
1. User → Slash Command (/optimize-resume job.pdf)
2. CLI → Validate inputs & parse arguments
3. CLI → Spawn Python process with parameters
4. Python → Process documents (parse PDF, analyze text)
5. Python → Query/Update Turso DB
6. Python → Return structured JSON to CLI
7. CLI → Format output for user
8. CLI → Update local file system (.resume-toolkit/)
9. User → Receive formatted results
```

**Data Persistence Flow**:

```text
Input Documents → Parse → Extract Structured Data → Store in Turso DB
                                                    → Cache in .resume-toolkit/

Retrieve Data ← Query Turso DB ← User Request
              ← Read Cache (.resume-toolkit/) ← Quick Access
```

### Directory Structure

```text
resume-toolkit/
├── src/                          # TypeScript source code
│   ├── commands/                 # Slash command implementations
│   │   ├── parse-resume.ts       # Resume parsing command
│   │   ├── analyze-jd.ts         # Job description analysis
│   │   ├── optimize-resume.ts    # Resume optimization
│   │   ├── score-ats.ts          # ATS scoring
│   │   ├── generate-cover-letter.ts
│   │   ├── research-company.ts
│   │   ├── track-application.ts
│   │   ├── application-dashboard.ts
│   │   ├── interview-prep.ts
│   │   └── apply.ts              # Master orchestrator
│   ├── lib/                      # Shared utilities
│   │   ├── db/                   # Database client and schema
│   │   ├── python-bridge.ts      # TypeScript-Python interface
│   │   ├── file-manager.ts       # File system operations
│   │   └── validators.ts         # Input validation
│   ├── types/                    # TypeScript type definitions
│   └── index.ts                  # CLI entry point
├── python/                       # Python backend
│   ├── parsers/                  # Document parsing modules
│   │   ├── resume_parser.py      # Resume extraction
│   │   ├── jd_parser.py          # Job description extraction
│   │   └── pdf_parser.py         # Generic PDF parsing
│   ├── analyzers/                # Analysis engines
│   │   ├── ats_scorer.py         # ATS compatibility scoring
│   │   ├── keyword_matcher.py    # Keyword analysis
│   │   └── skills_extractor.py   # Skills identification
│   ├── generators/               # Content generation
│   │   ├── resume_optimizer.py   # Resume tailoring
│   │   ├── cover_letter.py       # Cover letter generation
│   │   └── templates/            # Jinja2 templates
│   ├── research/                 # Company research
│   │   ├── company_scraper.py    # Web scraping
│   │   └── data_enrichment.py    # Data enhancement
│   ├── db/                       # Database operations
│   │   ├── models.py             # Data models
│   │   └── queries.py            # SQL queries
│   ├── utils/                    # Shared utilities
│   └── main.py                   # Python CLI entry point
├── tests/                        # Test suites
│   ├── unit/                     # Unit tests
│   │   ├── ts/                   # TypeScript tests (Vitest)
│   │   └── py/                   # Python tests (pytest)
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test data
├── .github/                      # GitHub configuration
│   └── workflows/                # CI/CD pipelines
│       ├── ci.yml                # Continuous integration
│       └── release.yml           # Release automation
├── .husky/                       # Git hooks
│   ├── pre-commit                # Pre-commit checks
│   └── pre-push                  # Pre-push validation
├── dist/                         # Compiled TypeScript output
├── .resume-toolkit/              # User data directory (gitignored)
│   ├── base-resume.md            # Master resume
│   ├── anecdotes/                # Achievement stories
│   ├── templates/                # Resume templates
│   ├── applications/             # Application tracking
│   └── analytics/                # Performance metrics
├── package.json                  # Node.js dependencies
├── tsconfig.json                 # TypeScript configuration
├── pyproject.toml                # Python dependencies
├── vitest.config.ts              # Vitest configuration
├── .eslintrc.json                # ESLint rules
├── .prettierrc                   # Prettier configuration
├── .pre-commit-config.yaml       # Pre-commit hooks
├── turso.config.json             # Turso database configuration
├── README.md                     # Project overview
└── CLAUDE.md                     # This file
```

## Quick Start

### Prerequisites

**Required Software**:

- **Node.js**: v18.0.0 or higher
- **Python**: 3.11 or higher
- **Git**: Latest version
- **Turso Account**: Free tier available at turso.tech

**Optional Tools**:

- **pnpm**: Faster package manager (recommended)
- **pyenv**: Python version management
- **nvm**: Node.js version management

### Installation Steps

**1. Clone Repository**:

```bash
git clone https://github.com/yourusername/resume-toolkit.git
cd resume-toolkit
```

**2. Install Node Dependencies**:

```bash
# Using npm
npm install

# Or using pnpm (recommended)
pnpm install
```

**3. Install Python Dependencies**:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

**4. Build TypeScript**:

```bash
npm run build
```

### Turso Database Setup

**1. Install Turso CLI**:

```bash
# macOS/Linux
curl -sSfL https://get.tur.so/install.sh | bash

# Or using Homebrew
brew install tursodatabase/tap/turso
```

**2. Authenticate**:

```bash
turso auth login
```

**3. Create Database**:

```bash
# Create new database
turso db create resume-toolkit

# Get database URL
turso db show resume-toolkit --url

# Create auth token
turso db tokens create resume-toolkit
```

**4. Configure Environment**:

```bash
# Create .env file
cat > .env << EOF
TURSO_DATABASE_URL=<your-database-url>
TURSO_AUTH_TOKEN=<your-auth-token>
ANTHROPIC_API_KEY=<your-claude-api-key>
EOF
```

**5. Initialize Schema**:

```bash
npm run db:push
```

### First Command to Try

**Parse Your Resume**:

```bash
# Parse resume and extract structured data
npm run cli parse-resume ./path/to/your/resume.pdf

# Expected output:
# ✓ Parsing resume...
# ✓ Extracted contact information
# ✓ Found 5 work experiences
# ✓ Identified 23 skills
# ✓ Saved to database
#
# Summary:
# Name: John Doe
# Email: john@example.com
# Skills: JavaScript, Python, React, Node.js, ...
# Experience: 5 positions, 8 years total
```

**Verify Installation**:

```bash
# Check version
npm run cli -- --version

# List available commands
npm run cli -- --help

# Run tests
npm test
```

## Commands Reference

### `/parse-resume`

**Purpose**: Extract structured data from resume files (PDF, DOCX, TXT, MD)

**Syntax**:

```bash
npm run cli parse-resume <file-path> [options]
```

**Options**:

- `--format <type>`: Output format (json, yaml, table) - default: table
- `--save`: Save to database - default: true
- `--output <path>`: Write to file

**Example**:

```bash
# Parse PDF resume
npm run cli parse-resume ./resume.pdf

# Parse and export to JSON
npm run cli parse-resume ./resume.pdf --format json --output resume-data.json
```

**Output**:

```text
✓ Parsing resume...
Contact Information:
  Name: Jane Smith
  Email: jane.smith@email.com
  Phone: (555) 123-4567
  LinkedIn: linkedin.com/in/janesmith

Work Experience: 4 positions
  - Senior Software Engineer at TechCorp (2020-Present)
  - Software Engineer at StartupXYZ (2018-2020)
  ...

Skills: 28 identified
  Technical: Python, TypeScript, React, AWS, Docker
  Soft: Leadership, Communication, Project Management

Education: 2 degrees
  - M.S. Computer Science, Stanford University (2018)
  - B.S. Computer Science, UC Berkeley (2016)
```

### `/analyze-jd`

**Purpose**: Analyze job descriptions to extract requirements, skills, and keywords

**Syntax**:

```bash
npm run cli analyze-jd <file-or-url> [options]
```

**Options**:

- `--url <url>`: Analyze job posting URL
- `--file <path>`: Analyze local file
- `--save`: Save to database - default: true
- `--compare <resume-id>`: Compare with specific resume

**Example**:

```bash
# Analyze from URL
npm run cli analyze-jd --url https://jobs.company.com/posting/12345

# Analyze from file
npm run cli analyze-jd job-description.txt

# Analyze and compare with resume
npm run cli analyze-jd job-description.txt --compare latest
```

**Output**:

```text
✓ Analyzing job description...
Job Title: Senior Full Stack Engineer
Company: TechCorp Inc.
Location: San Francisco, CA (Hybrid)

Required Skills (10):
  - JavaScript/TypeScript ⭐⭐⭐
  - React.js ⭐⭐⭐
  - Node.js ⭐⭐⭐
  - PostgreSQL ⭐⭐
  - AWS ⭐⭐

Preferred Skills (8):
  - Python, Docker, Kubernetes, GraphQL...

Experience Required: 5+ years
Education: Bachelor's in Computer Science or equivalent

Key Responsibilities:
  - Design and build scalable web applications
  - Lead technical architecture decisions
  - Mentor junior engineers

Company Culture Indicators:
  - Collaborative team environment
  - Fast-paced startup culture
  - Focus on innovation

ATS Keywords: full stack, microservices, agile, CI/CD, REST API
```

### `/optimize-resume`

**Purpose**: Tailor resume to specific job description for maximum ATS compatibility

**Syntax**:

```bash
npm run cli optimize-resume <resume> <job-description> [options]
```

**Options**:

- `--template <name>`: Use specific template (modern, classic, ats-friendly)
- `--output <path>`: Output file path
- `--format <type>`: Output format (pdf, docx, md) - default: pdf
- `--preview`: Show changes before saving

**Example**:

```bash
# Optimize for specific job
npm run cli optimize-resume base-resume.md job-desc.txt --output optimized-resume.pdf

# Preview changes first
npm run cli optimize-resume base-resume.md job-desc.txt --preview

# Use ATS-friendly template
npm run cli optimize-resume base-resume.md job-desc.txt --template ats-friendly
```

**Output**:

```text
✓ Analyzing job requirements...
✓ Matching skills and experience...
✓ Optimizing content...

Changes Made:
  + Added 12 relevant keywords
  ~ Reordered experience to highlight relevant roles
  + Added 3 matching skills to skills section
  ~ Rephrased 5 bullet points for better keyword matching
  - Removed 2 less relevant experiences

ATS Score: 87/100 (+23 from original)

Keyword Match: 18/20 (90%)
Skills Match: 8/10 required, 5/8 preferred

Saved to: ./optimized-resume.pdf
```

### `/score-ats`

**Purpose**: Calculate ATS compatibility score between resume and job description

**Syntax**:

```bash
npm run cli score-ats <resume> <job-description> [options]
```

**Options**:

- `--detailed`: Show detailed breakdown
- `--suggestions`: Include improvement suggestions
- `--threshold <number>`: Minimum acceptable score (default: 75)

**Example**:

```bash
# Basic scoring
npm run cli score-ats resume.pdf job-desc.txt

# Detailed analysis with suggestions
npm run cli score-ats resume.pdf job-desc.txt --detailed --suggestions
```

**Output**:

```text
✓ Calculating ATS compatibility...

Overall Score: 78/100 (Good Match)

Breakdown:
  Keyword Match:        82/100 ⭐⭐⭐⭐
  Skills Coverage:      85/100 ⭐⭐⭐⭐
  Experience Match:     75/100 ⭐⭐⭐⭐
  Education Match:      90/100 ⭐⭐⭐⭐⭐
  Format Compatibility: 95/100 ⭐⭐⭐⭐⭐

Strengths:
  ✓ Strong skills alignment (8/10 required skills)
  ✓ Relevant experience (6+ years matching requirement)
  ✓ Clean, ATS-friendly format
  ✓ Education meets requirements

Gaps:
  ✗ Missing 2 required skills: Kubernetes, GraphQL
  ✗ 5 important keywords not found in resume
  ⚠ Experience with "microservices" not clearly stated

Suggestions:
  1. Add Kubernetes and GraphQL to skills section
  2. Include these keywords: "scalable", "distributed systems", "CI/CD pipeline"
  3. Rephrase project descriptions to emphasize microservices architecture
  4. Quantify achievements with metrics (current: 3, recommended: 8+)
```

### `/generate-cover-letter`

**Purpose**: Create personalized cover letters based on resume and job description

**Syntax**:

```bash
npm run cli generate-cover-letter <job-description> [options]
```

**Options**:

- `--resume <path>`: Resume to base letter on (default: base-resume.md)
- `--tone <style>`: Writing tone (professional, enthusiastic, conversational)
- `--length <words>`: Target length (default: 300-400)
- `--template <name>`: Template to use (formal, modern, creative)
- `--output <path>`: Output file path

**Example**:

```bash
# Generate with defaults
npm run cli generate-cover-letter job-desc.txt

# Custom tone and length
npm run cli generate-cover-letter job-desc.txt --tone enthusiastic --length 350

# Specify resume and output
npm run cli generate-cover-letter job-desc.txt --resume my-resume.pdf --output cover-letter.pdf
```

**Output**:

```text
✓ Analyzing job requirements...
✓ Extracting relevant experiences...
✓ Generating personalized content...
✓ Formatting letter...

Cover Letter Generated (387 words)

Preview:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Dear Hiring Manager,

I am writing to express my strong interest in the Senior
Full Stack Engineer position at TechCorp Inc. With over 6
years of experience building scalable web applications and
a proven track record of leading technical initiatives, I am
excited about the opportunity to contribute to your team.

In my current role at StartupXYZ, I architected and deployed
a microservices-based platform that handles 2M+ daily active
users, directly aligning with your need for scalable system
design...

[Full letter saved to: ./cover-letter.pdf]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Highlights Included:
  ✓ 3 relevant technical achievements
  ✓ 2 leadership examples
  ✓ Company-specific research points
  ✓ Clear call-to-action

Tone Analysis: Professional, confident
Readability: Grade 12 (appropriate for technical role)
```

### `/research-company`

**Purpose**: Gather intelligence on potential employers (culture, news, tech stack)

**Syntax**:

```bash
npm run cli research-company <company-name-or-url> [options]
```

**Options**:

- `--deep`: Include detailed analysis (slower)
- `--sections <list>`: Specific sections (culture,tech,news,financials,reviews)
- `--output <path>`: Save research report
- `--format <type>`: Output format (md, pdf, json)

**Example**:

```bash
# Basic research
npm run cli research-company "TechCorp Inc"

# Deep analysis with specific sections
npm run cli research-company "TechCorp Inc" --deep --sections culture,tech,news

# From company URL
npm run cli research-company https://www.techcorp.com --output research-report.md
```

**Output**:

```text
✓ Researching TechCorp Inc...
✓ Gathering company information...
✓ Analyzing tech stack...
✓ Collecting recent news...
✓ Reviewing employee feedback...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPANY RESEARCH REPORT: TechCorp Inc.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overview:
  Industry: Enterprise SaaS
  Founded: 2015
  Size: 500-1000 employees
  HQ: San Francisco, CA
  Funding: Series C ($150M raised)

Tech Stack:
  Frontend: React, TypeScript, Next.js
  Backend: Node.js, Python, Go
  Database: PostgreSQL, Redis
  Infrastructure: AWS, Kubernetes, Terraform
  Tools: GitHub, Datadog, PagerDuty

Company Culture:
  Work Style: Hybrid (3 days in office)
  Values: Innovation, Collaboration, Customer-First
  Benefits: Unlimited PTO, Equity, Health Insurance
  Glassdoor: 4.2/5 (based on 87 reviews)

Recent News:
  • Raised $50M Series C (2 months ago)
  • Launched new AI-powered features (1 month ago)
  • Expanded to European market (3 weeks ago)
  • Featured in TechCrunch for rapid growth

Employee Insights:
  Pros:
    - Cutting-edge technology
    - Smart, collaborative team
    - Good work-life balance
  Cons:
    - Fast-paced environment
    - Some ambiguity in processes

Interview Tips:
  - Prepare for technical system design questions
  - Emphasize experience with microservices
  - Ask about their AI product roadmap
  - Highlight scalability achievements

Report saved to: .resume-toolkit/research/techcorp-inc.md
```

### `/track-application`

**Purpose**: Add application to tracking system with status and follow-up reminders

**Syntax**:

```bash
npm run cli track-application [options]
```

**Options**:

- `--company <name>`: Company name (required)
- `--position <title>`: Job title (required)
- `--url <link>`: Job posting URL
- `--status <state>`: Status (applied, screening, interview, offer, rejected)
- `--date <date>`: Application date (default: today)
- `--notes <text>`: Additional notes
- `--resume <path>`: Link to resume version used
- `--cover-letter <path>`: Link to cover letter used

**Example**:

```bash
# Quick track
npm run cli track-application --company "TechCorp" --position "Senior Engineer"

# Full details
npm run cli track-application \
  --company "TechCorp Inc" \
  --position "Senior Full Stack Engineer" \
  --url "https://jobs.techcorp.com/123" \
  --status applied \
  --notes "Referred by John Doe" \
  --resume ./applications/techcorp/resume.pdf \
  --cover-letter ./applications/techcorp/cover-letter.pdf
```

**Output**:

```text
✓ Creating application record...
✓ Saving documents...
✓ Setting reminders...

Application Tracked Successfully!

Company: TechCorp Inc
Position: Senior Full Stack Engineer
Status: Applied
Date: 2025-10-21

Documents:
  Resume: ./applications/techcorp-20251021/resume.pdf
  Cover Letter: ./applications/techcorp-20251021/cover-letter.pdf

Next Steps:
  → Follow up in 1 week (2025-10-28)
  → Check status in 2 weeks (2025-11-04)

Application ID: app_abc123
View dashboard: npm run cli application-dashboard
```

### `/application-dashboard`

**Purpose**: View all applications with status, timeline, and analytics

**Syntax**:

```bash
npm run cli application-dashboard [options]
```

**Options**:

- `--status <state>`: Filter by status
- `--company <name>`: Filter by company
- `--days <number>`: Show applications from last N days
- `--sort <field>`: Sort by (date, status, company)
- `--export <path>`: Export to CSV/JSON

**Example**:

```bash
# View all applications
npm run cli application-dashboard

# Filter active applications
npm run cli application-dashboard --status applied,screening,interview

# Recent applications
npm run cli application-dashboard --days 30

# Export to CSV
npm run cli application-dashboard --export applications.csv
```

**Output**:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
APPLICATION DASHBOARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary (Last 30 Days):
  Total Applications: 24
  Response Rate: 62% (15/24)
  Interview Rate: 33% (8/24)
  Offer Rate: 12% (3/24)

Status Breakdown:
  🟡 Applied (7)
  🔵 Screening (4)
  🟢 Interview (4)
  ⭐ Offer (3)
  🔴 Rejected (6)

Recent Applications:
┌──────────────┬─────────────────────────┬────────────┬────────────┐
│ Company      │ Position                │ Status     │ Date       │
├──────────────┼─────────────────────────┼────────────┼────────────┤
│ TechCorp     │ Senior Full Stack Eng   │ 🟢 Interview│ 2025-10-21 │
│ StartupXYZ   │ Staff Engineer          │ ⭐ Offer    │ 2025-10-18 │
│ BigTech Co   │ Principal Engineer      │ 🔵 Screening│ 2025-10-15 │
│ InnovateLab  │ Tech Lead               │ 🟡 Applied │ 2025-10-12 │
│ CloudSys     │ Senior Backend Eng      │ 🔴 Rejected│ 2025-10-10 │
└──────────────┴─────────────────────────┴────────────┴────────────┘

Action Items:
  ⚠ Follow up with TechCorp (due today)
  ⚠ Interview prep for BigTech Co (tomorrow)
  ⚠ Respond to StartupXYZ offer (deadline: 2025-10-25)

Performance Metrics:
  Average Response Time: 5.2 days
  Fastest Response: 1 day (StartupXYZ)
  Top Skills Requested: TypeScript (18), React (15), AWS (12)
```

### `/interview-prep`

**Purpose**: Generate interview questions and talking points for specific positions

**Syntax**:

```bash
npm run cli interview-prep <application-id-or-company> [options]
```

**Options**:

- `--type <category>`: Question type (technical, behavioral, cultural, all)
- `--difficulty <level>`: Difficulty (junior, mid, senior, staff)
- `--count <number>`: Number of questions to generate
- `--include-answers`: Include suggested answer frameworks
- `--resume <path>`: Resume to base answers on

**Example**:

```bash
# Prep for specific application
npm run cli interview-prep app_abc123

# Generate technical questions
npm run cli interview-prep "TechCorp" --type technical --difficulty senior

# Full prep with answers
npm run cli interview-prep "TechCorp" --include-answers
```

**Output**:

```text
✓ Analyzing job requirements...
✓ Reviewing your experience...
✓ Generating interview questions...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INTERVIEW PREP: Senior Full Stack Engineer @ TechCorp
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TECHNICAL QUESTIONS (10):

1. System Design:
   Q: How would you design a scalable notification system
      that handles 10M+ daily active users?

   Your Talking Points:
   - Mention your experience with event-driven architecture
   - Reference your work on messaging systems at StartupXYZ
   - Discuss trade-offs: Push vs Pull, Real-time vs Batch

2. Problem Solving:
   Q: Design a rate limiter for our API gateway.

   Your Talking Points:
   - Token bucket algorithm experience
   - Distributed systems considerations (Redis)
   - Your API optimization work (mention 40% latency reduction)

BEHAVIORAL QUESTIONS (8):

1. Leadership:
   Q: Tell me about a time you had to make a difficult
      technical decision with incomplete information.

   Your STAR Answer:
   Situation: Migration to microservices at StartupXYZ
   Task: Decide between gradual vs full migration
   Action: Created POC, gathered metrics, consulted team
   Result: Successful gradual rollout, zero downtime

2. Conflict Resolution:
   Q: Describe a situation where you disagreed with a
      colleague's technical approach.

   Your Talking Points:
   - REST vs GraphQL debate (use your GraphQL migration story)
   - Emphasize data-driven decision making
   - Highlight collaboration and compromise

CULTURAL FIT QUESTIONS (5):

1. Company Values:
   Q: TechCorp values "customer-first" approach. How does
      this align with your development philosophy?

   Your Answer Framework:
   - Your user feedback integration process
   - Example: Feature A/B testing that improved retention 25%
   - Metrics-driven development approach

QUESTIONS TO ASK THEM (8):

Technical:
  - What's your approach to technical debt management?
  - How do you balance innovation with system stability?
  - What's the biggest technical challenge the team faces?

Team/Culture:
  - How does the team collaborate on architecture decisions?
  - What does growth look like for senior engineers here?
  - How do you support learning and development?

Saved detailed prep guide to:
  .resume-toolkit/applications/techcorp-20251021/interview-prep.md
```

### `/apply`

**Purpose**: Master orchestrator - executes entire application workflow

**Syntax**:

```bash
npm run cli apply <job-url-or-file> [options]
```

**Options**:

- `--resume <path>`: Base resume to optimize (default: base-resume.md)
- `--auto`: Run without confirmations (use with caution)
- `--skip <steps>`: Skip specific steps (comma-separated)
- `--template <name>`: Resume template to use
- `--output-dir <path>`: Directory for generated files

**Example**:

```bash
# Interactive full workflow
npm run cli apply https://jobs.techcorp.com/posting/12345

# Automated with custom resume
npm run cli apply job-desc.txt --resume senior-eng-resume.md --auto

# Skip cover letter generation
npm run cli apply job-url --skip cover-letter
```

**Workflow Steps**:

1. Analyze job description
2. Research company
3. Optimize resume for job
4. Calculate ATS score
5. Generate cover letter
6. Create application folder
7. Track application
8. Generate interview prep

**Output**:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPLETE APPLICATION WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/8] Analyzing Job Description...
✓ Company: TechCorp Inc
✓ Position: Senior Full Stack Engineer
✓ Required Skills: 10 identified
✓ Preferred Skills: 8 identified

[2/8] Researching Company...
✓ Tech stack mapped
✓ Culture insights gathered
✓ Recent news collected
✓ Interview tips prepared

[3/8] Optimizing Resume...
✓ Tailored for job requirements
✓ Added 12 relevant keywords
✓ Highlighted matching experiences
✓ Optimized formatting for ATS

[4/8] Calculating ATS Score...
✓ Score: 87/100 (Excellent Match!)
✓ Keyword coverage: 90%
✓ Skills match: 8/10 required

[5/8] Generating Cover Letter...
✓ Personalized content created
✓ Incorporated company research
✓ Highlighted relevant achievements
✓ Length: 385 words

[6/8] Creating Application Folder...
✓ Created: .resume-toolkit/applications/techcorp-20251021/
✓ Saved optimized resume
✓ Saved cover letter
✓ Saved company research
✓ Saved job description

[7/8] Tracking Application...
✓ Added to dashboard
✓ Set follow-up reminders
✓ Linked all documents

[8/8] Preparing Interview Materials...
✓ Generated 23 likely questions
✓ Created talking points
✓ Prepared STAR stories

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
APPLICATION PACKAGE READY!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Location: .resume-toolkit/applications/techcorp-20251021/

Files Generated:
  ✓ optimized-resume.pdf (ATS Score: 87/100)
  ✓ cover-letter.pdf (385 words)
  ✓ company-research.md (Full intelligence report)
  ✓ job-description.txt (Original posting)
  ✓ interview-prep.md (23 questions with answers)
  ✓ application-checklist.md (Next steps)

Next Steps:
  1. Review optimized resume for accuracy
  2. Personalize cover letter opening paragraph
  3. Submit application through company portal
  4. Run: npm run cli track-application --status applied
  5. Schedule follow-up for 1 week from now

Good luck! 🚀
```

## Database Schema

### Tables Overview

**Core Tables**:

- **resumes**: Parsed resume data and versions
- **jobs**: Job descriptions and requirements
- **applications**: Application tracking and status
- **cover_letters**: Generated cover letters
- **companies**: Company research and intelligence
- **analytics**: Performance metrics and insights

### Schema Details

**resumes**:

```sql
CREATE TABLE resumes (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  filename TEXT NOT NULL,
  parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  -- Contact Information
  full_name TEXT,
  email TEXT,
  phone TEXT,
  linkedin_url TEXT,
  github_url TEXT,
  portfolio_url TEXT,
  location TEXT,

  -- Structured Data
  summary TEXT,
  skills JSON,              -- ["JavaScript", "Python", ...]
  experiences JSON,         -- [{ company, title, dates, bullets }, ...]
  education JSON,           -- [{ school, degree, dates }, ...]
  certifications JSON,      -- [{ name, issuer, date }, ...]
  projects JSON,            -- [{ name, description, tech }, ...]

  -- Metadata
  total_experience_years INTEGER,
  file_path TEXT,
  file_hash TEXT,
  is_base_resume BOOLEAN DEFAULT false,

  -- Version Control
  version INTEGER DEFAULT 1,
  parent_resume_id TEXT,

  FOREIGN KEY (parent_resume_id) REFERENCES resumes(id)
);
```

**jobs**:

```sql
CREATE TABLE jobs (
  id TEXT PRIMARY KEY,
  company_id TEXT,

  -- Job Details
  title TEXT NOT NULL,
  company_name TEXT NOT NULL,
  location TEXT,
  remote_type TEXT,         -- remote, hybrid, onsite
  salary_range TEXT,
  job_url TEXT,

  -- Parsed Content
  description TEXT,
  required_skills JSON,     -- [{ skill, importance }, ...]
  preferred_skills JSON,
  responsibilities JSON,
  qualifications JSON,

  -- Requirements
  min_experience_years INTEGER,
  education_requirement TEXT,

  -- Analysis
  keywords JSON,            -- ATS keywords
  culture_indicators JSON,  -- Detected values/culture

  -- Metadata
  posted_date DATE,
  analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  source TEXT,              -- url, file, manual

  FOREIGN KEY (company_id) REFERENCES companies(id)
);
```

**applications**:

```sql
CREATE TABLE applications (
  id TEXT PRIMARY KEY,

  -- References
  resume_id TEXT NOT NULL,
  job_id TEXT NOT NULL,
  cover_letter_id TEXT,
  company_id TEXT,

  -- Application Info
  applied_date DATE NOT NULL DEFAULT CURRENT_DATE,
  status TEXT NOT NULL,     -- applied, screening, interview, offer, rejected
  status_updated_at TIMESTAMP,

  -- Tracking
  application_url TEXT,
  confirmation_number TEXT,
  referral_source TEXT,

  -- Timeline
  screening_date DATE,
  interview_dates JSON,     -- [{ date, type, interviewer }, ...]
  offer_date DATE,
  offer_deadline DATE,
  rejection_date DATE,

  -- Follow-up
  last_followup_date DATE,
  next_followup_date DATE,
  followup_count INTEGER DEFAULT 0,

  -- Documents
  resume_file_path TEXT,
  cover_letter_file_path TEXT,

  -- Notes
  notes TEXT,
  interview_feedback JSON,

  -- Metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (resume_id) REFERENCES resumes(id),
  FOREIGN KEY (job_id) REFERENCES jobs(id),
  FOREIGN KEY (cover_letter_id) REFERENCES cover_letters(id),
  FOREIGN KEY (company_id) REFERENCES companies(id)
);
```

**cover_letters**:

```sql
CREATE TABLE cover_letters (
  id TEXT PRIMARY KEY,

  -- References
  resume_id TEXT NOT NULL,
  job_id TEXT NOT NULL,

  -- Content
  content TEXT NOT NULL,
  tone TEXT,                -- professional, enthusiastic, conversational
  word_count INTEGER,

  -- Generation
  template_used TEXT,
  highlights JSON,          -- Key points highlighted
  generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  -- File
  file_path TEXT,
  file_format TEXT,         -- pdf, docx, txt

  FOREIGN KEY (resume_id) REFERENCES resumes(id),
  FOREIGN KEY (job_id) REFERENCES jobs(id)
);
```

**companies**:

```sql
CREATE TABLE companies (
  id TEXT PRIMARY KEY,

  -- Basic Info
  name TEXT NOT NULL,
  website TEXT,
  industry TEXT,
  size TEXT,                -- 1-50, 51-200, 201-500, etc.
  headquarters TEXT,

  -- Research Data
  tech_stack JSON,          -- [{ technology, category }, ...]
  culture JSON,             -- { values, workStyle, benefits }
  recent_news JSON,         -- [{ title, date, source, url }, ...]
  employee_reviews JSON,    -- { glassdoor, indeed, ... }

  -- Financials
  funding_stage TEXT,       -- seed, series-a, public, etc.
  funding_amount TEXT,

  -- Social
  linkedin_url TEXT,
  twitter_url TEXT,
  github_url TEXT,

  -- Metadata
  researched_at TIMESTAMP,
  data_freshness DATE,      -- When to refresh research

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**analytics**:

```sql
CREATE TABLE analytics (
  id TEXT PRIMARY KEY,

  -- Time Range
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,

  -- Metrics
  applications_count INTEGER,
  responses_count INTEGER,
  interviews_count INTEGER,
  offers_count INTEGER,
  rejections_count INTEGER,

  -- Rates
  response_rate REAL,       -- responses / applications
  interview_rate REAL,      -- interviews / applications
  offer_rate REAL,          -- offers / applications

  -- Timing
  avg_response_time_days REAL,
  avg_interview_time_days REAL,

  -- Skills Analysis
  top_skills_requested JSON,    -- [{ skill, count }, ...]
  skill_gaps JSON,              -- Skills in jobs but not in resume

  -- ATS Performance
  avg_ats_score REAL,
  ats_score_trend JSON,         -- [{ date, score }, ...]

  -- Company Insights
  top_companies JSON,           -- [{ company, count }, ...]
  top_industries JSON,

  generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Key Relationships

```text
users (1) ──< (many) resumes
resumes (1) ──< (many) applications
jobs (1) ──< (many) applications
companies (1) ──< (many) jobs
companies (1) ──< (many) applications
resumes (1) ──< (many) cover_letters
jobs (1) ──< (many) cover_letters
```

### Data Flow Through System

**Application Creation Flow**:

```text
1. Parse Resume → INSERT into resumes table
2. Analyze Job → INSERT into jobs table
3. Research Company → INSERT/UPDATE companies table
4. Optimize Resume → INSERT new resume (version++) with parent_resume_id
5. Generate Cover Letter → INSERT into cover_letters table
6. Track Application → INSERT into applications table
7. Calculate Analytics → INSERT/UPDATE analytics table
```

**Query Patterns**:

```sql
-- Get all applications with related data
SELECT a.*, j.title, c.name as company_name, r.full_name
FROM applications a
JOIN jobs j ON a.job_id = j.id
JOIN companies c ON a.company_id = c.id
JOIN resumes r ON a.resume_id = r.id
WHERE a.status IN ('applied', 'screening', 'interview')
ORDER BY a.applied_date DESC;

-- Calculate success metrics
SELECT
  COUNT(*) as total_applications,
  SUM(CASE WHEN status != 'rejected' THEN 1 ELSE 0 END) as active,
  SUM(CASE WHEN status = 'interview' THEN 1 ELSE 0 END) as interviews,
  SUM(CASE WHEN status = 'offer' THEN 1 ELSE 0 END) as offers,
  ROUND(AVG(CASE WHEN status = 'interview' THEN 1.0 ELSE 0.0 END) * 100, 2) as interview_rate
FROM applications
WHERE applied_date >= date('now', '-30 days');

-- Find skill gaps
SELECT DISTINCT skill
FROM (
  SELECT json_each.value as skill
  FROM jobs, json_each(required_skills)
  WHERE id IN (SELECT job_id FROM applications WHERE status != 'rejected')
)
WHERE skill NOT IN (
  SELECT json_each.value
  FROM resumes, json_each(skills)
  WHERE is_base_resume = true
);
```

## Development Workflow

### Setting Up Development Environment

**1. Clone and Install**:

```bash
# Clone repository
git clone https://github.com/yourusername/resume-toolkit.git
cd resume-toolkit

# Install dependencies
npm install
pip install -e ".[dev]"
```

**2. Configure Pre-commit Hooks**:

```bash
# Install Husky
npm run prepare

# Install Python pre-commit
pre-commit install
```

**3. Set Up Database**:

```bash
# Development (local SQLite)
export NODE_ENV=development
npm run db:push

# Production (Turso)
export NODE_ENV=production
export TURSO_DATABASE_URL="..."
export TURSO_AUTH_TOKEN="..."
npm run db:push
```

**4. Verify Setup**:

```bash
# Run tests
npm test
npm run test:python

# Check linting
npm run lint
npm run lint:python

# Build project
npm run build
```

### TDD Process (Write Tests First)

**Test-Driven Development Workflow**:

```text
1. Write failing test
2. Run test (should fail)
3. Write minimal code to pass
4. Run test (should pass)
5. Refactor
6. Repeat
```

**Example TypeScript TDD**:

```typescript
// tests/unit/ts/parsers/resume-parser.test.ts

import { describe, it, expect } from 'vitest';
import { parseResume } from '@/lib/parsers/resume-parser';

describe('parseResume', () => {
  it('should extract contact information from PDF', async () => {
    // Arrange
    const pdfPath = './tests/fixtures/sample-resume.pdf';

    // Act
    const result = await parseResume(pdfPath);

    // Assert
    expect(result.email).toBe('john@example.com');
    expect(result.phone).toBe('(555) 123-4567');
    expect(result.fullName).toBe('John Doe');
  });

  it('should extract work experiences with dates', async () => {
    const pdfPath = './tests/fixtures/sample-resume.pdf';
    const result = await parseResume(pdfPath);

    expect(result.experiences).toHaveLength(3);
    expect(result.experiences[0]).toMatchObject({
      company: 'TechCorp',
      title: 'Senior Engineer',
      startDate: '2020-01',
      endDate: 'present'
    });
  });
});
```

**Example Python TDD**:

```python
# tests/unit/py/test_ats_scorer.py

import pytest
from python.analyzers.ats_scorer import calculate_ats_score

class TestATSScorer:
    def test_perfect_match_scores_100(self):
        """Resume with all required skills should score 100"""
        resume = {
            'skills': ['Python', 'JavaScript', 'React', 'AWS']
        }
        job = {
            'required_skills': ['Python', 'JavaScript', 'React', 'AWS']
        }

        score = calculate_ats_score(resume, job)

        assert score == 100

    def test_partial_match_scores_proportionally(self):
        """Resume with 2/4 skills should score ~50"""
        resume = {
            'skills': ['Python', 'JavaScript']
        }
        job = {
            'required_skills': ['Python', 'JavaScript', 'React', 'AWS']
        }

        score = calculate_ats_score(resume, job)

        assert 45 <= score <= 55  # Allow some variance
```

### Running Tests

**TypeScript Tests (Vitest)**:

```bash
# Run all tests
npm test

# Watch mode
npm run test:watch

# Coverage report
npm run test:coverage

# Specific test file
npm test resume-parser.test.ts

# Specific test suite
npm test -- --grep "parseResume"
```

**Python Tests (pytest)**:

```bash
# Run all tests
npm run test:python
# Or directly:
pytest

# Watch mode
ptw  # pytest-watch

# Coverage report
pytest --cov=python --cov-report=html

# Specific test file
pytest tests/unit/py/test_ats_scorer.py

# Specific test class
pytest tests/unit/py/test_ats_scorer.py::TestATSScorer

# Verbose output
pytest -v
```

**Integration Tests**:

```bash
# Run integration tests
npm run test:integration

# Requires:
# - Running database
# - Test fixtures
# - Environment variables
```

### Pre-commit Hooks

**Automatic Checks Before Commit**:

```bash
# .husky/pre-commit
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# TypeScript linting and formatting
npm run lint
npm run format:check

# TypeScript tests
npm test

# Python linting
ruff check python/
black --check python/

# Python tests
pytest
```

**Manual Hook Execution**:

```bash
# Run pre-commit hooks manually
npm run pre-commit

# Skip hooks (not recommended)
git commit --no-verify -m "message"
```

### Code Quality Standards

**TypeScript Standards**:

- **Style**: Prettier with 2-space indentation
- **Linting**: ESLint with strict rules
- **Type Safety**: strict mode enabled in tsconfig.json
- **Naming**: camelCase for variables, PascalCase for types/classes
- **File Structure**: One component/function per file
- **Comments**: JSDoc for public APIs

**Python Standards**:

- **Style**: Black formatter (88 char line length)
- **Linting**: Ruff (faster than Flake8)
- **Type Hints**: All function signatures typed
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Docstrings**: Google style
- **Imports**: Sorted with isort

**Example TypeScript**:

```typescript
/**
 * Parse resume file and extract structured data
 *
 * @param filePath - Path to resume file (PDF, DOCX, TXT, MD)
 * @param options - Parsing options
 * @returns Parsed resume data
 * @throws {Error} If file format not supported
 */
export async function parseResume(
  filePath: string,
  options: ParseOptions = {}
): Promise<ResumeData> {
  const extension = path.extname(filePath).toLowerCase();

  if (!SUPPORTED_FORMATS.includes(extension)) {
    throw new Error(`Unsupported format: ${extension}`);
  }

  // Implementation...
}
```

**Example Python**:

```python
def calculate_ats_score(
    resume: Dict[str, Any],
    job: Dict[str, Any]
) -> float:
    """Calculate ATS compatibility score between resume and job.

    Args:
        resume: Parsed resume data with skills, experience, etc.
        job: Parsed job description with requirements.

    Returns:
        Score from 0-100 indicating compatibility.

    Raises:
        ValueError: If required fields missing from inputs.
    """
    if 'skills' not in resume or 'required_skills' not in job:
        raise ValueError("Missing required fields")

    # Implementation...
```

## Testing Guide

### Unit Testing Approach

**Test Isolation**:

- Each test should be independent
- Use mocks for external dependencies
- Test one behavior per test case
- Follow AAA pattern: Arrange, Act, Assert

**TypeScript Unit Tests**:

```typescript
// tests/unit/ts/commands/optimize-resume.test.ts

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { optimizeResume } from '@/commands/optimize-resume';
import * as pythonBridge from '@/lib/python-bridge';

describe('optimizeResume command', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should call Python optimizer with correct arguments', async () => {
    // Arrange
    const mockPythonCall = vi.spyOn(pythonBridge, 'callPython')
      .mockResolvedValue({ success: true, score: 85 });

    // Act
    await optimizeResume('resume.pdf', 'job.txt');

    // Assert
    expect(mockPythonCall).toHaveBeenCalledWith(
      'optimize',
      expect.objectContaining({
        resume: 'resume.pdf',
        job: 'job.txt'
      })
    );
  });

  it('should handle Python process errors gracefully', async () => {
    // Arrange
    vi.spyOn(pythonBridge, 'callPython')
      .mockRejectedValue(new Error('Python error'));

    // Act & Assert
    await expect(optimizeResume('resume.pdf', 'job.txt'))
      .rejects.toThrow('Failed to optimize resume');
  });
});
```

**Python Unit Tests**:

```python
# tests/unit/py/test_resume_parser.py

import pytest
from unittest.mock import Mock, patch
from python.parsers.resume_parser import ResumeParser

class TestResumeParser:
    @pytest.fixture
    def parser(self):
        return ResumeParser()

    @pytest.fixture
    def sample_pdf_content(self):
        return """
        John Doe
        john@example.com | (555) 123-4567

        Senior Software Engineer
        TechCorp, 2020 - Present
        - Built scalable systems
        - Led team of 5 engineers
        """

    def test_extract_email(self, parser, sample_pdf_content):
        """Should extract email from resume text"""
        result = parser.extract_email(sample_pdf_content)
        assert result == 'john@example.com'

    def test_extract_phone(self, parser, sample_pdf_content):
        """Should extract phone number in various formats"""
        result = parser.extract_phone(sample_pdf_content)
        assert result == '(555) 123-4567'

    @patch('python.parsers.resume_parser.pdfplumber')
    def test_parse_pdf_calls_pdfplumber(self, mock_pdfplumber, parser):
        """Should use pdfplumber to extract PDF text"""
        mock_pdf = Mock()
        mock_pdf.pages = [Mock(extract_text=Mock(return_value="text"))]
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

        parser.parse_pdf('resume.pdf')

        mock_pdfplumber.open.assert_called_once_with('resume.pdf')
```

### Integration Testing

**Test Real Workflows**:

```typescript
// tests/integration/apply-workflow.test.ts

import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { executeApplyWorkflow } from '@/commands/apply';
import { setupTestDatabase, cleanupTestDatabase } from './helpers/db';

describe('Complete Apply Workflow', () => {
  beforeAll(async () => {
    await setupTestDatabase();
  });

  afterAll(async () => {
    await cleanupTestDatabase();
  });

  it('should execute full application workflow', async () => {
    // Arrange
    const jobUrl = 'https://jobs.example.com/posting/123';
    const resumePath = './tests/fixtures/resume.pdf';

    // Act
    const result = await executeApplyWorkflow(jobUrl, {
      resume: resumePath,
      auto: true
    });

    // Assert - Verify all steps completed
    expect(result.steps).toHaveLength(8);
    expect(result.steps[0].name).toBe('analyze-jd');
    expect(result.steps[0].status).toBe('completed');

    // Verify database records created
    expect(result.applicationId).toBeDefined();
    expect(result.resumeId).toBeDefined();
    expect(result.coverLetterId).toBeDefined();

    // Verify files created
    expect(result.files).toContain('optimized-resume.pdf');
    expect(result.files).toContain('cover-letter.pdf');
  }, 30000); // 30 second timeout for full workflow
});
```

### Test Coverage Requirements

**Minimum Coverage Targets**:

- **Overall**: 80%+ coverage
- **Critical Paths**: 100% coverage (parse, optimize, score)
- **Error Handling**: All error paths tested
- **Edge Cases**: Boundary conditions covered

**Checking Coverage**:

```bash
# TypeScript coverage
npm run test:coverage
# View report: open coverage/index.html

# Python coverage
pytest --cov=python --cov-report=html
# View report: open htmlcov/index.html

# Coverage thresholds in vitest.config.ts:
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      lines: 80,
      functions: 80,
      branches: 80,
      statements: 80
    }
  }
});
```

### How to Run Tests

**Development Workflow**:

```bash
# 1. Write test first (TDD)
# 2. Run test in watch mode
npm run test:watch

# 3. Write code until test passes
# 4. Run all tests
npm test && npm run test:python

# 5. Check coverage
npm run test:coverage

# 6. Commit (pre-commit hook runs tests)
git commit -m "Add feature X"
```

**CI/CD Testing**:

```bash
# Run exactly what CI runs
npm run ci:test

# Includes:
# - TypeScript tests with coverage
# - Python tests with coverage
# - Linting checks
# - Type checking
# - Build verification
```

## CI/CD Pipeline

### GitHub Actions Workflows

**Continuous Integration** (`.github/workflows/ci.yml`):

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test-typescript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npm run type-check

      - name: Test
        run: npm run test:coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
          flags: typescript

  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Lint
        run: |
          ruff check python/
          black --check python/

      - name: Test
        run: pytest --cov=python --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: python

  build:
    runs-on: ubuntu-latest
    needs: [test-typescript, test-python]
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Build
        run: |
          npm ci
          npm run build

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist/
```

**Release Workflow** (`.github/workflows/release.yml`):

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install and build
        run: |
          npm ci
          npm run build

      - name: Publish to npm
        run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}

      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

### Quality Gates

**Required Checks for Merge**:

- All tests passing (TypeScript + Python)
- Code coverage 80%+
- No linting errors
- No type errors
- Successful build
- All dependencies up to date

**Branch Protection Rules**:

```yaml
# .github/branch-protection.yml
main:
  required_status_checks:
    - test-typescript
    - test-python
    - build
  required_reviews: 1
  enforce_admins: false
  required_linear_history: true
```

### How to Interpret CI Failures

**Test Failures**:

```text
❌ test-typescript / Test (Node 18)
   → Click "Details" to see which tests failed
   → Look for red ✗ marks in test output
   → Check error messages and stack traces
   → Fix locally: npm test -- <test-name>
```

**Linting Failures**:

```text
❌ test-typescript / Lint
   → ESLint or Prettier errors
   → Fix locally: npm run lint:fix
   → Commit and push
```

**Coverage Failures**:

```text
❌ test-python / Test
   ERROR: Coverage below 80% (current: 76%)
   → Add tests for uncovered lines
   → Check coverage report: pytest --cov-report=html
   → Open htmlcov/index.html to see gaps
```

**Build Failures**:

```text
❌ build / Build
   → TypeScript compilation errors
   → Fix type errors: npm run type-check
   → Verify build locally: npm run build
```

**Dependency Issues**:

```text
❌ test-typescript / Install dependencies
   ERROR: npm ERR! peer dependency conflicts
   → Update package.json peer dependencies
   → Or use --legacy-peer-deps flag
```

## Data Directory Structure

### `.resume-toolkit/` Overview

**Purpose**: Local data storage for resumes, applications, and analytics

**Location**: `~/.resume-toolkit/` or project-local `.resume-toolkit/`

**Structure**:

```text
.resume-toolkit/
├── base-resume.md              # Master resume (source of truth)
├── config.json                 # User preferences and settings
├── anecdotes/                  # Achievement stories (STAR format)
│   ├── backend-optimization.md
│   ├── team-leadership.md
│   └── migration-project.md
├── templates/                  # Resume templates for different roles
│   ├── senior-engineer.md
│   ├── tech-lead.md
│   ├── staff-engineer.md
│   └── custom/
│       └── fintech-specialist.md
├── applications/               # One folder per application
│   ├── techcorp-20251021/
│   │   ├── job-description.txt
│   │   ├── optimized-resume.pdf
│   │   ├── cover-letter.pdf
│   │   ├── company-research.md
│   │   ├── interview-prep.md
│   │   ├── application-notes.md
│   │   └── metadata.json
│   ├── startupxyz-20251018/
│   └── bigtech-20251015/
└── analytics/                  # Performance tracking
    ├── weekly-summary.json
    ├── monthly-report.md
    └── skill-trends.json
```

### base-resume.md Format

**Master Resume Template**:

```markdown
# John Doe

**Senior Software Engineer**

San Francisco, CA | john.doe@email.com | (555) 123-4567
[LinkedIn](https://linkedin.com/in/johndoe) | [GitHub](https://github.com/johndoe)

## Summary

Experienced full-stack engineer with 8+ years building scalable web applications.
Specialized in TypeScript, React, Node.js, and cloud architecture. Track record
of leading technical initiatives and mentoring engineers.

## Skills

**Languages**: JavaScript, TypeScript, Python, Go, SQL
**Frontend**: React, Next.js, Vue.js, TailwindCSS
**Backend**: Node.js, Express, FastAPI, GraphQL
**Database**: PostgreSQL, MongoDB, Redis
**Cloud**: AWS (EC2, Lambda, S3, RDS), GCP, Docker, Kubernetes
**Tools**: Git, GitHub Actions, Datadog, Terraform

## Experience

### Senior Software Engineer | TechCorp Inc.
**2020 - Present** | San Francisco, CA

- Architected microservices platform handling 2M+ daily active users
- Led migration from monolith to microservices, reducing deployment time by 70%
- Implemented CI/CD pipeline cutting release cycle from 2 weeks to daily deploys
- Mentored team of 5 junior engineers through code reviews and pair programming
- Technologies: TypeScript, React, Node.js, PostgreSQL, AWS, Kubernetes

*Anecdotes: backend-optimization, team-leadership, migration-project*

### Software Engineer | StartupXYZ
**2018 - 2020** | Remote

- Built real-time analytics dashboard processing 100K events/second
- Optimized API response times by 60% through query optimization and caching
- Developed GraphQL API serving mobile and web clients
- Implemented feature flag system enabling safe progressive rollouts
- Technologies: JavaScript, React, Node.js, MongoDB, Redis, AWS

### Junior Software Engineer | ConsultingCo
**2016 - 2018** | New York, NY

- Developed client-facing web applications for Fortune 500 companies
- Contributed to open-source UI component library (5K+ GitHub stars)
- Reduced page load times by 40% through performance optimization
- Technologies: JavaScript, React, Node.js, MySQL

## Education

### M.S. Computer Science | Stanford University
**2016** | GPA: 3.9/4.0
Specialization: Distributed Systems

### B.S. Computer Science | UC Berkeley
**2014** | GPA: 3.8/4.0
Dean's List, CS Honor Society

## Projects

### OpenSource Toolkit (Personal)
- Built developer productivity CLI with 10K+ npm downloads
- TypeScript, Node.js, Commander.js
- [GitHub](https://github.com/johndoe/opensource-toolkit)

### TechBlog (Side Project)
- Technical blog on system design and architecture
- 50K+ monthly readers, featured in DailyDev
- [Website](https://johndoe.dev)

## Certifications

- AWS Certified Solutions Architect (2023)
- Certified Kubernetes Administrator (2022)
```

### anecdotes/ Structure

**STAR Format Stories**:

```markdown
<!-- anecdotes/backend-optimization.md -->

# Backend API Optimization

**Situation**:
API response times were degrading as user base grew, with p95 latency
exceeding 2 seconds. Customer complaints increasing, risk of churn.

**Task**:
Reduce API latency to under 500ms p95 while maintaining reliability.
Had 3 weeks before major customer renewal deadline.

**Action**:
- Profiled API endpoints to identify bottlenecks (N+1 queries, slow joins)
- Implemented Redis caching layer for frequently accessed data
- Optimized database queries and added proper indexes
- Introduced connection pooling to reduce database overhead
- Set up monitoring dashboards to track improvements

**Result**:
- Reduced p95 latency from 2.1s to 320ms (85% improvement)
- Decreased database load by 60%
- Customer renewed contract, citing improved performance
- Solution scaled to 3x user growth without degradation

**Technologies**: Node.js, PostgreSQL, Redis, Datadog
**Tags**: performance, databases, monitoring, leadership
**Date**: 2023-Q2
**Company**: TechCorp Inc.

**Usage**: Best for questions about performance optimization, database
expertise, handling production issues, customer focus.
```

### templates/ for Different Roles

**Senior Engineer Template** (templates/senior-engineer.md):

```markdown
# John Doe - Senior Software Engineer

Focus: Technical execution, mentorship, system design

[Contact info same as base]

## Summary
[Emphasize technical depth and mentorship]

## Technical Skills
[Comprehensive skills list]

## Experience
[All positions, focus on technical achievements]

## Projects
[Technical side projects]
```

**Tech Lead Template** (templates/tech-lead.md):

```markdown
# John Doe - Engineering Tech Lead

Focus: Technical leadership, architecture, team coordination

[Contact info same as base]

## Summary
[Emphasize leadership and architecture decisions]

## Leadership Experience
[Reorganized to highlight leadership first]

## Technical Skills
[Skills relevant to tech lead role]

## Experience
[Emphasize team leadership, architecture, cross-functional work]
```

### applications/ Folder Per Application

**Application Folder Structure**:

```text
applications/techcorp-20251021/
├── metadata.json               # Application tracking data
├── job-description.txt         # Original job posting
├── job-analysis.json           # Parsed requirements
├── optimized-resume.pdf        # Tailored resume
├── optimized-resume.md         # Source markdown
├── cover-letter.pdf            # Final cover letter
├── cover-letter.md             # Source markdown
├── company-research.md         # Intelligence report
├── interview-prep.md           # Questions and answers
├── application-notes.md        # Personal notes
├── correspondence/             # Email threads
│   ├── initial-application.txt
│   ├── screening-invite.txt
│   └── interview-followup.txt
└── interview-feedback/         # Post-interview notes
    ├── technical-round-1.md
    └── behavioral-round.md
```

**metadata.json**:

```json
{
  "applicationId": "app_abc123",
  "company": "TechCorp Inc.",
  "position": "Senior Full Stack Engineer",
  "appliedDate": "2025-10-21",
  "status": "interview",
  "jobUrl": "https://jobs.techcorp.com/posting/12345",
  "resumeVersion": "resume_v23",
  "atsScore": 87,
  "timeline": [
    { "date": "2025-10-21", "event": "Applied", "notes": "Via company portal" },
    { "date": "2025-10-23", "event": "Screening scheduled", "notes": "Phone screen with recruiter" },
    { "date": "2025-10-25", "event": "Screening completed", "notes": "Positive feedback" },
    { "date": "2025-10-28", "event": "Technical interview scheduled", "notes": "System design focus" }
  ],
  "nextSteps": [
    { "action": "Prepare system design", "dueDate": "2025-10-27" },
    { "action": "Research interviewer", "dueDate": "2025-10-27" }
  ],
  "contacts": [
    { "name": "Sarah Johnson", "role": "Recruiter", "email": "sarah@techcorp.com" },
    { "name": "Mike Chen", "role": "Hiring Manager", "email": "mike@techcorp.com" }
  ]
}
```

### analytics/ for Tracking

**weekly-summary.json**:

```json
{
  "weekOf": "2025-10-14",
  "applications": {
    "submitted": 5,
    "responses": 3,
    "interviews": 2,
    "rejections": 1
  },
  "metrics": {
    "avgAtsScore": 82.4,
    "avgResponseTime": 4.2,
    "responseRate": 0.6
  },
  "topSkills": [
    { "skill": "TypeScript", "count": 4 },
    { "skill": "React", "count": 4 },
    { "skill": "AWS", "count": 3 }
  ],
  "insights": [
    "Response rate improved from 50% to 60%",
    "ATS scores consistently above 80",
    "TypeScript and React most in-demand"
  ]
}
```

**monthly-report.md**:

```markdown
# Job Search Report - October 2025

## Summary
- Applications: 24
- Responses: 15 (62.5%)
- Interviews: 8 (33.3%)
- Offers: 2 (8.3%)

## Performance Trends
- ATS scores trending up (avg 84, was 76)
- Response time improving (5.2 days, was 7.1)
- Interview conversion stable (50% of responses)

## Skill Demand Analysis
Most requested skills:
1. TypeScript (18 positions)
2. React (15 positions)
3. AWS (12 positions)
4. Node.js (11 positions)
5. Python (8 positions)

Skills gaps to address:
- Kubernetes (in 8 JDs, not in resume)
- GraphQL (in 6 JDs, minimal experience)

## Company Insights
Top industries applied to:
- SaaS (12)
- FinTech (6)
- E-commerce (4)

## Next Steps
1. Add Kubernetes certification to resume
2. Build GraphQL side project
3. Focus on FinTech companies (highest offer rate)
```

## Troubleshooting

### Common Issues and Solutions

#### Installation Problems

**Issue: npm install fails with peer dependency errors**

```bash
# Error
npm ERR! Could not resolve dependency:
npm ERR! peer react@"^18.0.0" from react-dom@18.2.0

# Solution 1: Use --legacy-peer-deps
npm install --legacy-peer-deps

# Solution 2: Update package.json to match peer dependencies
npm install react@^18.0.0 react-dom@^18.0.0
```

**Issue: Python dependencies fail to install**

```bash
# Error
ERROR: Failed building wheel for some-package

# Solution: Install build tools
# macOS:
brew install python@3.11
xcode-select --install

# Ubuntu:
sudo apt-get update
sudo apt-get install python3-dev build-essential

# Then retry:
pip install -e ".[dev]"
```

#### Turso Connection Problems

**Issue: Cannot connect to Turso database**

```bash
# Error
Error: Failed to connect to database
LibsqlError: SQLITE_AUTH: not authorized

# Solution: Verify environment variables
echo $TURSO_DATABASE_URL
echo $TURSO_AUTH_TOKEN

# If empty, reconfigure:
turso db show resume-toolkit --url
turso db tokens create resume-toolkit

# Update .env file
cat > .env << EOF
TURSO_DATABASE_URL=libsql://your-db.turso.io
TURSO_AUTH_TOKEN=your-token-here
EOF
```

**Issue: Database schema not initialized**

```bash
# Error
Error: table "resumes" does not exist

# Solution: Push schema
npm run db:push

# Or manually initialize:
turso db shell resume-toolkit < schema.sql
```

**Issue: Database connection timeout**

```bash
# Error
Error: Connection timeout after 5000ms

# Solution 1: Check network connectivity
curl https://your-db.turso.io

# Solution 2: Increase timeout
# In database config:
{
  "connectionTimeout": 10000
}

# Solution 3: Use local development database
export NODE_ENV=development
npm run db:push
```

#### PDF Parsing Errors

**Issue: PDF parsing fails with encoding errors**

```bash
# Error
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x89

# Solution: Install additional dependencies
pip install pdfplumber chardet

# Or try alternative parser:
npm run cli parse-resume --parser pypdf2 resume.pdf
```

**Issue: Corrupted or scanned PDF**

```bash
# Error
Error: No text extracted from PDF

# Solution 1: Check if PDF is scanned image
# Use OCR parser:
pip install pytesseract
npm run cli parse-resume --ocr resume.pdf

# Solution 2: Convert to text first
# macOS:
pdftotext resume.pdf resume.txt
npm run cli parse-resume resume.txt

# Solution 3: Re-export PDF from source document
```

**Issue: PDF parsing extracts garbled text**

```bash
# Symptom: Text appears as random characters

# Solution: Try different extraction method
# In Python code:
from pdfminer.high_level import extract_text
text = extract_text('resume.pdf', codec='utf-8')

# Or use pdfplumber with layout:
import pdfplumber
with pdfplumber.open('resume.pdf') as pdf:
    text = pdf.pages[0].extract_text(layout=True)
```

#### Web Scraping Failures

**Issue: Company research returns no data**

```bash
# Error
Error: Failed to fetch company data: 403 Forbidden

# Solution 1: Website blocking automated requests
# Add user agent:
headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; ResumeToolkit/1.0)'
}

# Solution 2: Rate limiting
# Add delay between requests:
import time
time.sleep(2)  # 2 second delay

# Solution 3: Use API instead of scraping
# Check if company has public API
```

**Issue: Job description URL returns 404**

```bash
# Error
Error: Job posting not found (404)

# Solution 1: Job may have been removed
# Use cached version or saved text file instead

# Solution 2: URL requires authentication
# Download HTML manually and parse from file:
npm run cli analyze-jd --file job-posting.html

# Solution 3: Use Internet Archive
https://web.archive.org/save/[original-url]
```

**Issue: Cloudflare or bot protection**

```bash
# Error
Error: Cloudflare security check detected

# Solution: Not recommended to bypass
# Instead, save page manually:
# 1. Open URL in browser
# 2. Save page as HTML
# 3. Parse from file:
npm run cli research-company --file company-page.html
```

#### Command Execution Issues

**Issue: Command not found**

```bash
# Error
bash: resume-toolkit: command not found

# Solution: Use npm script instead
npm run cli <command>

# Or install globally:
npm install -g .
resume-toolkit <command>
```

**Issue: Permission denied**

```bash
# Error
EACCES: permission denied, open '/Users/...'

# Solution 1: Fix file permissions
chmod +x dist/index.js

# Solution 2: Run with proper permissions
sudo npm run cli <command>  # Not recommended

# Solution 3: Fix ownership
sudo chown -R $USER:$USER .resume-toolkit/
```

**Issue: Python process fails silently**

```bash
# Error: Command succeeds but no output

# Solution: Check Python logs
# Enable debug mode:
export DEBUG=true
npm run cli <command>

# Check Python error output:
python python/main.py <args> 2>&1 | tee error.log

# Verify Python environment:
which python
python --version
```

#### Database Issues

**Issue: Duplicate key error**

```bash
# Error
UNIQUE constraint failed: resumes.id

# Solution 1: Check for existing record
npm run cli parse-resume --force resume.pdf

# Solution 2: Use update instead of insert
# Or delete old record:
turso db shell resume-toolkit "DELETE FROM resumes WHERE id='...'"
```

**Issue: Database locked**

```bash
# Error
Error: database is locked

# Solution 1: Close other connections
# Check for running processes:
ps aux | grep turso

# Solution 2: Use Turso cloud instead of local
export NODE_ENV=production

# Solution 3: Increase timeout
# In database config:
{
  "busyTimeout": 5000
}
```

#### Performance Issues

**Issue: Commands running very slowly**

```bash
# Symptom: Commands take >30 seconds

# Solution 1: Check network connectivity
ping turso.io

# Solution 2: Use local database for development
export NODE_ENV=development

# Solution 3: Enable caching
# In config.json:
{
  "cache": {
    "enabled": true,
    "ttl": 3600
  }
}

# Solution 4: Profile performance
npm run cli <command> --profile
```

**Issue: High memory usage**

```bash
# Symptom: Process killed by OS

# Solution 1: Process smaller files
# Split large resume into sections

# Solution 2: Increase Node memory limit
export NODE_OPTIONS="--max-old-space-size=4096"
npm run cli <command>

# Solution 3: Use streaming for large files
# Enable in config:
{
  "streaming": true
}
```

### Getting Help

**Debug Mode**:

```bash
# Enable verbose logging
export DEBUG=resume-toolkit:*
npm run cli <command>

# Save logs to file
npm run cli <command> 2>&1 | tee debug.log
```

**Check System Status**:

```bash
# Verify installation
npm run cli doctor

# Output:
✓ Node.js version: 18.17.0
✓ Python version: 3.11.5
✓ Database connection: OK
✓ Required dependencies: OK
⚠ Optional dependencies: 1 missing (pytesseract)
```

**Report Issues**:

```bash
# Generate diagnostic report
npm run cli diagnose > diagnostic-report.txt

# Submit issue with:
# 1. Diagnostic report
# 2. Error messages
# 3. Steps to reproduce
# 4. Expected vs actual behavior
```

## Contributing Guidelines

### How to Add New Commands

**1. Create Command File**:

```typescript
// src/commands/new-command.ts

import { Command } from 'commander';
import { callPython } from '@/lib/python-bridge';

export function registerNewCommand(program: Command): void {
  program
    .command('new-command')
    .description('Description of what this command does')
    .argument('<required-arg>', 'Description of required argument')
    .option('-o, --optional <value>', 'Optional parameter')
    .action(async (requiredArg, options) => {
      try {
        console.log('Processing...');

        const result = await callPython('new_command', {
          required: requiredArg,
          optional: options.optional
        });

        console.log('Success:', result);
      } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
      }
    });
}
```

**2. Create Python Handler**:

```python
# python/handlers/new_handler.py

from typing import Dict, Any

def handle_new_command(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle new command logic.

    Args:
        args: Command arguments from TypeScript

    Returns:
        Result dictionary to return to TypeScript
    """
    required = args['required']
    optional = args.get('optional')

    # Implementation here
    result = process_data(required, optional)

    return {
        'success': True,
        'data': result
    }
```

**3. Register Command**:

```typescript
// src/index.ts

import { registerNewCommand } from './commands/new-command';

const program = new Command();

// ... existing commands
registerNewCommand(program);

program.parse();
```

**4. Add Tests**:

```typescript
// tests/unit/ts/commands/new-command.test.ts

import { describe, it, expect, vi } from 'vitest';
import * as pythonBridge from '@/lib/python-bridge';

describe('new-command', () => {
  it('should call Python with correct args', async () => {
    const mockCall = vi.spyOn(pythonBridge, 'callPython')
      .mockResolvedValue({ success: true });

    // Test implementation
  });
});
```

```python
# tests/unit/py/test_new_handler.py

import pytest
from python.handlers.new_handler import handle_new_command

class TestNewHandler:
    def test_basic_functionality(self):
        result = handle_new_command({'required': 'value'})
        assert result['success'] is True
```

**5. Update Documentation**:

```markdown
<!-- Add to CLAUDE.md Commands Reference section -->

### `/new-command`

**Purpose**: Brief description

**Syntax**:
```bash
npm run cli new-command <required-arg> [options]
```

**Example**:
```bash
npm run cli new-command example-value --optional flag
```
```

### Code Style Expectations

**TypeScript Style**:

```typescript
// ✅ Good
export async function parseResume(
  filePath: string,
  options: ParseOptions = {}
): Promise<ResumeData> {
  // Clear function signature
  // Proper error handling
  // JSDoc comments
}

// ❌ Bad
export async function parseResume(filePath, options) {
  // No types
  // No error handling
  // No documentation
}
```

**Python Style**:

```python
# ✅ Good
def calculate_score(
    resume: Dict[str, Any],
    job: Dict[str, Any]
) -> float:
    """Calculate compatibility score.

    Args:
        resume: Parsed resume data
        job: Parsed job description

    Returns:
        Score from 0-100
    """
    # Implementation with type hints
    # Proper docstring
    # Error handling

# ❌ Bad
def calculate_score(resume, job):
    # No type hints
    # No docstring
    # No error handling
    return score
```

**Commit Message Style**:

```text
✅ Good:
feat: add job description analyzer
fix: resolve PDF parsing encoding issue
docs: update installation instructions
test: add coverage for ATS scorer

❌ Bad:
fixed stuff
updates
WIP
asdf
```

### PR Requirements

**Before Submitting PR**:

1. All tests passing locally
2. Code coverage 80%+
3. Linting checks pass
4. Type checking clean
5. Documentation updated
6. Commit messages follow convention

**PR Template**:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing
- [ ] Coverage maintained/improved

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Dependent changes merged

## Related Issues
Fixes #123
```

**Review Process**:

1. Automated CI checks must pass
2. At least one approving review required
3. No unresolved conversations
4. Branch up to date with main
5. All commits squashed (optional)

**After Approval**:

```bash
# Squash commits if needed
git rebase -i main

# Update branch
git pull origin main --rebase

# Merge
# GitHub will handle merge via UI
```

### Development Best Practices

**General Principles**:

- Write tests before implementation (TDD)
- Keep functions small and focused
- Use meaningful variable names
- Add comments for complex logic
- Handle errors gracefully
- Log important operations
- Validate inputs
- Clean up resources

**Error Handling**:

```typescript
// ✅ Good
try {
  const result = await riskyOperation();
  return result;
} catch (error) {
  if (error instanceof ValidationError) {
    console.error('Invalid input:', error.message);
    throw new Error(`Validation failed: ${error.message}`);
  }

  console.error('Unexpected error:', error);
  throw error;
}

// ❌ Bad
try {
  const result = await riskyOperation();
  return result;
} catch (e) {
  console.log(e);
}
```

**Resource Cleanup**:

```typescript
// ✅ Good
async function processFile(path: string): Promise<void> {
  const file = await fs.open(path);

  try {
    await processContent(file);
  } finally {
    await file.close();
  }
}

// ❌ Bad
async function processFile(path: string): Promise<void> {
  const file = await fs.open(path);
  await processContent(file);
  // File never closed if error occurs
}
```

**Validation**:

```typescript
// ✅ Good
function parseEmail(email: string): string {
  if (!email || typeof email !== 'string') {
    throw new ValidationError('Email must be a non-empty string');
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    throw new ValidationError('Invalid email format');
  }

  return email.toLowerCase().trim();
}

// ❌ Bad
function parseEmail(email) {
  return email.toLowerCase();
  // No validation, crashes if email is null
}
```

---

**Documentation Complete** - Resume Toolkit v1.0

For questions or issues, please file a GitHub issue or consult the troubleshooting section.
