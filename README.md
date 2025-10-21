# Resume Toolkit

Complete Job Application Workflow System - A production-quality hybrid TypeScript/Python platform for managing the entire job application lifecycle with ATS scoring, intelligent PDF parsing, job tracking, and automated application workflows.

## Overview

Resume Toolkit is an internal developer platform that provides self-service capabilities for managing job applications end-to-end. It combines powerful CLI tooling with Python-based document processing and scoring algorithms.

### Key Features

- **ATS Scoring Engine**: Analyze resumes against job descriptions for keyword matching and optimization
- **Intelligent PDF Parser**: Extract structured data from resumes and job postings
- **Job Tracking Database**: Turso/libSQL-powered database for application state management
- **Web Scraping**: Playwright-based automation for job board integration
- **CLI Interface**: Developer-friendly command-line tools for all workflows
- **Full TDD Support**: Comprehensive test coverage with Vitest (TS) and pytest (Python)

## Architecture

### TypeScript Stack (CLI & Orchestration)
- **Runtime**: Node.js 18+
- **Language**: TypeScript 5.6+ with strict mode
- **CLI Framework**: Commander.js
- **Database**: Turso/libSQL (@libsql/client)
- **Validation**: Zod schemas
- **Testing**: Vitest with coverage
- **Web Scraping**: Playwright
- **UX**: Chalk, Ora for beautiful CLI experiences

### Python Stack (Document Processing & Scoring)
- **Runtime**: Python 3.11+ (primary: 3.12)
- **PDF Processing**: pdfplumber, PyPDF2
- **Data Analysis**: pandas, numpy
- **Validation**: Pydantic v2
- **Database**: libsql-client
- **Testing**: pytest with coverage
- **Linting**: Ruff, mypy for type safety

## Project Structure

```
resume-toolkit/
├── src/
│   ├── cli/                 # TypeScript CLI application
│   │   ├── commands/        # CLI command implementations
│   │   ├── lib/             # Shared utilities and helpers
│   │   ├── db/              # Database client and schemas
│   │   └── __tests__/       # Vitest test files
│   └── python/              # Python backend services
│       ├── pdf_parser/      # PDF extraction and parsing
│       ├── ats_scorer/      # ATS scoring algorithms
│       ├── db/              # Database models and queries
│       └── tests/           # pytest test files
├── .claude/
│   └── commands/            # Custom slash commands
├── .github/
│   └── workflows/           # CI/CD pipelines
├── package.json             # Node.js dependencies
├── tsconfig.json            # TypeScript configuration
├── pyproject.toml           # Python project configuration
└── requirements.txt         # Python dependencies

## Getting Started

### Prerequisites

- Node.js 20.0.0 or higher
- Python 3.11 or higher (3.12 recommended)
- npm 9.0.0 or higher

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd resume-toolkit
   ```

2. **Install TypeScript dependencies**
   ```bash
   npm install
   ```

3. **Install Python dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Turso credentials and other config
   ```

### Development

**TypeScript Development**
```bash
npm run dev                  # Run CLI in development mode
npm run test                 # Run tests
npm run test:watch           # Run tests in watch mode
npm run test:ui              # Run tests with UI
npm run test:coverage        # Generate coverage report
npm run test:coverage:check  # Check coverage meets 85% threshold
npm run lint                 # Lint code
npm run lint:fix             # Auto-fix linting issues
npm run format               # Format code
npm run format:check         # Check formatting
npm run type-check           # Type check without emitting
npm run build                # Build for production
npm run quality-gates        # Run all quality gates
```

**Python Development**
```bash
pytest                           # Run tests
pytest --cov                     # Run with coverage
pytest -v                        # Verbose output
ruff check src/python           # Lint code
ruff check --fix src/python     # Auto-fix issues
mypy src/python                 # Type check
```

## Testing

### TypeScript Testing (Vitest)
- Unit tests alongside source files: `*.test.ts`
- Integration tests in `__tests__/` directories
- **Coverage thresholds: 85% minimum for commands** (lines, functions, branches, statements)
- Run: `npm run test:coverage:check`

### Python Testing (pytest)
- Tests in `src/python/tests/`
- Markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- **Coverage threshold: 85% minimum**
- Coverage reports: terminal, HTML, XML

See [QUALITY_GATES.md](./QUALITY_GATES.md) for comprehensive coverage requirements.

## Code Quality

### Quality Gates

All code changes must pass **four mandatory quality gates**:

1. **Linting** - Code must be free of linting errors
2. **Type Checking** - Code must be fully type-safe (zero type errors)
3. **Testing** - All tests must pass
4. **Coverage** - Commands must maintain **85%+ test coverage**

Run all gates at once: `npm run quality-gates`

See [QUALITY_GATES.md](./QUALITY_GATES.md) for detailed requirements.

### TypeScript
- **ESLint v9**: Enforces code standards with flat config (eslint.config.js)
- **Prettier**: Automatic code formatting (100 char line length)
- **TypeScript**: Strict mode with comprehensive type checking

### Python
- **Ruff**: Fast linting and formatting (100 char line length)
- **mypy**: Static type checking with --strict mode
- **pytest**: Test coverage with 85% minimum threshold

## Configuration Files

- `package.json` - Node.js dependencies and scripts
- `tsconfig.json` - TypeScript compiler configuration (strict mode)
- `pyproject.toml` - Python project metadata, dependencies, and tool configs
- `vitest.config.ts` - Vitest test configuration with 85% coverage thresholds
- `eslint.config.js` - ESLint v9 flat config rules and settings
- `.prettierrc` - Prettier formatting rules
- `requirements.txt` - Python dependencies
- `pytest.ini` - pytest configuration
- `ruff.toml` - Ruff linter configuration

## Contributing

1. Follow TDD principles - write tests first
2. **Maintain code coverage above 85%** for all commands
3. Use conventional commit messages
4. Run `npm run quality-gates` before committing
5. Ensure all quality gates pass (linting, type-check, tests, coverage)
6. Pre-commit hooks will automatically enforce quality standards

See [CONTRIBUTING.md](./CONTRIBUTING.md) and [QUALITY_GATES.md](./QUALITY_GATES.md) for detailed guidelines.

## License

MIT
