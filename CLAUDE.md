# Resume Toolkit

**Complete Job Application Workflow System**

## Project Overview

### What It Is

Resume Toolkit is a comprehensive job application automation system that streamlines the entire job search process from resume optimization to application tracking. Built as a hybrid TypeScript/Python system integrated with Claude Code, it provides intelligent automation for resume parsing, job description analysis, ATS optimization, cover letter generation, and application tracking.

### Why It Exists

Job searching is time-consuming and repetitive. Applicants spend hours tailoring resumes, writing cover letters, researching companies, and tracking applications. Resume Toolkit automates these tasks while maintaining personalization and quality, allowing job seekers to focus on strategic activities like networking and interview preparation.

### Key Features

- Resume Intelligence: Parse, analyze, and optimize resumes for ATS compatibility
- Job Description Analysis: Extract key requirements, skills, and company culture indicators
- Smart Optimization: Automatically tailor resumes to specific job descriptions
- ATS Scoring: Predict how well your resume matches job requirements
- Cover Letter Generation: Create personalized, compelling cover letters
- Company Research: Gather intelligence on potential employers
- Application Tracking: Monitor status, deadlines, and follow-ups
- Interview Preparation: Generate likely questions and talking points
- Master Orchestration: `/apply` command executes the entire workflow

### Architecture Overview

```text
User Interface (Claude Code + CLI)
          ↓
TypeScript CLI Layer (Command Router & Validation)
          ↓
Python Backend Layer (PDF/DOCX Parsing, NLP, ATS Scoring)
          ↓
Turso Database (resumes, jobs, applications, companies)
          ↓
File System Storage (.resume-toolkit/ directory)
```

## Architecture

### Hybrid TypeScript/Python Design

**TypeScript CLI Layer**:
- Rapid development with modern tooling and type safety
- MCP integration with Claude Code slash commands
- Rich terminal UI with progress indicators

**Python Backend Layer**:
- Superior NLP libraries (spaCy, NLTK)
- Robust PDF/DOCX parsing (PyPDF2, pdfplumber, python-docx)
- Data science tools (NumPy, Pandas) for analytics

**Benefits**: Best tool for each job, clear separation of concerns, easy to test and maintain.

### Technology Stack

**CLI**: TypeScript, Commander.js, Chalk, Vitest
**Backend**: Python 3.11+, PyPDF2, pdfplumber, spaCy, BeautifulSoup4, pytest
**Database**: Turso (libSQL/SQLite), Drizzle ORM
**Development**: Git, GitHub Actions, Husky, ESLint, Prettier, pre-commit hooks

### Data Flow

```text
User Request → CLI validates → Python processes → Store in Turso DB
                                              → Cache in .resume-toolkit/
```

### Directory Structure

See [full directory structure in project README](./README.md#directory-structure).

Key directories:
- `src/cli/commands/` - TypeScript command implementations
- `src/python/` - Python processing modules
- `tests/` - Test suites (TypeScript and Python)
- `.resume-toolkit/` - User data (gitignored)

## Quick Start

### Prerequisites

- Node.js v18.0.0+
- Python 3.11+
- Git
- Turso Account (free tier at turso.tech)

### Installation

```bash
# Clone and install dependencies
git clone https://github.com/yourusername/resume-toolkit.git
cd resume-toolkit
npm install
pip install -e ".[dev]"

# Build
npm run build
```

### Turso Database Setup

```bash
# Install Turso CLI
brew install tursodatabase/tap/turso

# Authenticate and create database
turso auth login
turso db create resume-toolkit
turso db show resume-toolkit --url
turso db tokens create resume-toolkit

# Configure environment
cat > .env << EOF
TURSO_DATABASE_URL=<your-database-url>
TURSO_AUTH_TOKEN=<your-auth-token>
ANTHROPIC_API_KEY=<your-claude-api-key>
EOF

# Initialize schema
npm run db:push
```

### First Command

```bash
# Parse your resume
npm run cli parse-resume ./path/to/your/resume.pdf

# Verify installation
npm run cli -- --help
npm test
```

## Commands Reference

### Core Commands

| Command | Purpose |
|---------|---------|
| `/parse-resume` | Extract structured data from resume files (PDF, DOCX, TXT, MD) |
| `/analyze-jd` | Analyze job descriptions to extract requirements and keywords |
| `/optimize-resume` | Tailor resume to specific job description for ATS |
| `/score-ats` | Calculate ATS compatibility score |
| `/generate-cover-letter` | Create personalized cover letters |
| `/research-company` | Gather intelligence on potential employers |
| `/track-application` | Add application to tracking system |
| `/application-dashboard` | View all applications with status and analytics |
| `/interview-prep` | Generate interview questions and talking points |
| `/apply` | Master orchestrator - execute entire workflow |

### `/parse-resume`

Extract structured data from resume files.

```bash
npm run cli parse-resume <file-path> [options]

Options:
  --format <type>    Output format (json, yaml, table) - default: table
  --save            Save to database - default: true
  --output <path>   Write to file

Example:
npm run cli parse-resume ./resume.pdf
```

### `/analyze-jd`

Analyze job descriptions to extract requirements and skills.

```bash
npm run cli analyze-jd <file-or-url> [options]

Options:
  --url <url>          Analyze job posting URL
  --file <path>        Analyze local file
  --save              Save to database - default: true
  --compare <resume>  Compare with specific resume

Example:
npm run cli analyze-jd --url https://jobs.company.com/posting/12345
```

### `/optimize-resume`

Tailor resume to specific job description for maximum ATS compatibility.

```bash
npm run cli optimize-resume <resume> <job-description> [options]

Options:
  --template <name>   Use specific template (modern, classic, ats-friendly)
  --output <path>    Output file path
  --format <type>    Output format (pdf, docx, md) - default: pdf
  --preview          Show changes before saving

Example:
npm run cli optimize-resume base-resume.md job-desc.txt --output optimized.pdf
```

### `/score-ats`

Calculate ATS compatibility score between resume and job description.

```bash
npm run cli score-ats <resume> <job-description> [options]

Options:
  --detailed            Show detailed breakdown
  --suggestions        Include improvement suggestions
  --threshold <number> Minimum acceptable score (default: 75)

Example:
npm run cli score-ats resume.pdf job-desc.txt --detailed --suggestions
```

### `/generate-cover-letter`

Create personalized cover letters.

```bash
npm run cli generate-cover-letter <job-description> [options]

Options:
  --resume <path>     Resume to base letter on (default: base-resume.md)
  --tone <style>      Writing tone (professional, enthusiastic, conversational)
  --length <words>    Target length (default: 300-400)
  --template <name>   Template to use (formal, modern, creative)

Example:
npm run cli generate-cover-letter job-desc.txt --tone enthusiastic
```

### `/research-company`

Gather intelligence on potential employers.

```bash
npm run cli research-company <company-name-or-url> [options]

Options:
  --deep              Include detailed analysis (slower)
  --sections <list>   Specific sections (culture,tech,news,financials,reviews)
  --output <path>     Save research report

Example:
npm run cli research-company "TechCorp Inc" --deep --sections culture,tech,news
```

### `/track-application`

Add application to tracking system.

```bash
npm run cli track-application [options]

Options:
  --company <name>      Company name (required)
  --position <title>    Job title (required)
  --url <link>          Job posting URL
  --status <state>      Status (applied, screening, interview, offer, rejected)
  --resume <path>       Link to resume version used
  --cover-letter <path> Link to cover letter used

Example:
npm run cli track-application --company "TechCorp" --position "Director of Engineering"
```

### `/application-dashboard`

View all applications with status, timeline, and analytics.

```bash
npm run cli application-dashboard [options]

Options:
  --status <state>    Filter by status
  --company <name>   Filter by company
  --days <number>    Show applications from last N days
  --export <path>    Export to CSV/JSON

Example:
npm run cli application-dashboard --status applied,screening,interview
```

### `/interview-prep`

Generate interview questions and talking points.

```bash
npm run cli interview-prep <application-id-or-company> [options]

Options:
  --type <category>     Question type (technical, behavioral, cultural, all)
  --difficulty <level>  Difficulty (junior, mid, senior, staff)
  --include-answers    Include suggested answer frameworks

Example:
npm run cli interview-prep "TechCorp" --include-answers
```

### `/apply`

Master orchestrator - executes entire application workflow.

```bash
npm run cli apply <job-url-or-file> [options]

Options:
  --resume <path>      Base resume to optimize (default: base-resume.md)
  --auto              Run without confirmations (use with caution)
  --skip <steps>      Skip specific steps (comma-separated)

Example:
npm run cli apply https://jobs.techcorp.com/posting/12345

Workflow Steps:
1. Analyze job description
2. Research company
3. Optimize resume for job
4. Calculate ATS score
5. Generate cover letter
6. Create application folder
7. Track application
8. Generate interview prep
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

**Relationships**:
```text
resumes (1) ──< (many) applications
jobs (1) ──< (many) applications
companies (1) ──< (many) jobs
companies (1) ──< (many) applications
resumes (1) ──< (many) cover_letters
jobs (1) ──< (many) cover_letters
```

For complete SQL schema definitions, see [docs/DATABASE_SCHEMA.md](./docs/DATABASE_SCHEMA.md).

## Data Directory Structure

### `.resume-toolkit/` Overview

Local data storage for resumes, applications, and analytics.

```text
.resume-toolkit/
├── base-resume.md              # Master resume (source of truth)
├── config.json                 # User preferences
├── anecdotes/                  # Achievement stories (STAR format)
├── templates/                  # Resume templates for different roles
├── applications/               # One folder per application
│   └── company-YYYYMMDD/
│       ├── job-description.txt
│       ├── optimized-resume.pdf
│       ├── cover-letter.pdf
│       ├── company-research.md
│       ├── interview-prep.md
│       └── metadata.json
└── analytics/                  # Performance tracking
```

For example files and detailed formats, see [docs/examples/](./docs/examples/).

## Development

### Setting Up Development Environment

```bash
# Clone and install
git clone https://github.com/yourusername/resume-toolkit.git
cd resume-toolkit
npm install
pip install -e ".[dev]"

# Configure pre-commit hooks
npm run prepare
pre-commit install

# Run tests
npm test
npm run test:python

# Build
npm run build
```

### Code Quality

**TypeScript**: ESLint, Prettier, strict type checking
**Python**: Ruff, Black, MyPy type checking

### Testing

```bash
# TypeScript tests (Vitest)
npm test
npm run test:watch
npm run test:coverage

# Python tests (pytest)
pytest
pytest --cov=python --cov-report=html
```

**Coverage Requirements**: 80%+ overall, 100% for critical paths

For detailed development guidelines, TDD examples, and testing best practices, see [docs/DEVELOPMENT.md](./docs/DEVELOPMENT.md).

## CI/CD Pipeline

### GitHub Actions

**Continuous Integration** (`.github/workflows/ci.yml`):
- Triggers: Push to main/develop, pull requests
- Jobs: lint, type-check, test, build
- Requirements: All checks pass, 80%+ coverage

**Quality Gates for Merge**:
- All tests passing (TypeScript + Python)
- Code coverage 80%+
- No linting errors
- No type errors
- Successful build

## Troubleshooting

### Common Issues

| Issue | Quick Fix |
|-------|-----------|
| `SQLITE_AUTH: not authorized` | Regenerate Turso auth token |
| `table "resumes" does not exist` | Run `npm run db:push` |
| `UnicodeDecodeError` | Install pdfplumber: `pip install pdfplumber` |
| `Command not found` | Use `npm run cli <command>` |
| `Permission denied` | Run `chmod +x dist/index.js` |
| Connection timeout | Check network, use local DB for dev |

### Debug Mode

```bash
# Enable verbose logging
export DEBUG=resume-toolkit:*
npm run cli <command>

# Check system status
npm run cli doctor
```

For comprehensive troubleshooting guide with detailed solutions, see [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md).

## Contributing

We welcome contributions! Before contributing:

1. Read [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines
2. Review [docs/DEVELOPMENT.md](./docs/DEVELOPMENT.md) for development setup
3. Check [docs/DATABASE_SCHEMA.md](./docs/DATABASE_SCHEMA.md) for database structure

### Quick Contribution Checklist

- [ ] All tests passing locally
- [ ] Code coverage 80%+
- [ ] Linting checks pass
- [ ] Type checking clean
- [ ] Documentation updated
- [ ] Commit messages follow convention (feat:, fix:, docs:, test:)

## Additional Resources

- **Examples**: See [docs/examples/](./docs/examples/) for resume templates and anecdotes
- **Development**: See [docs/DEVELOPMENT.md](./docs/DEVELOPMENT.md) for detailed development guide
- **Troubleshooting**: See [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) for common issues
- **Database**: See [docs/DATABASE_SCHEMA.md](./docs/DATABASE_SCHEMA.md) for schema details
- **Contributing**: See [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution guidelines

## License

MIT License - see LICENSE file for details.

---

**Documentation Version**: 1.0
For questions or issues, please file a GitHub issue or consult the troubleshooting guide.
