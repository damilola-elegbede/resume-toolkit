# Contributing Guide

## Development Setup

### Prerequisites

- Node.js 20.11.0+ (use `.nvmrc` for version management)
- Python 3.12.0+ (use `.python-version` for version management)
- Git with pre-commit hooks support

### Initial Setup

```bash
# Use correct Node version
nvm use

# Install Node dependencies
npm install

# Install Python dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Development Workflow

### Code Quality Commands

```bash
# TypeScript/JavaScript
npm run lint              # Run ESLint
npm run lint:fix          # Auto-fix ESLint issues
npm run type-check        # Run TypeScript type checking
npm run format            # Format code with Prettier
npm run format:check      # Check code formatting

# Python
ruff check .              # Run Ruff linter
ruff check . --fix        # Auto-fix Ruff issues
ruff format .             # Format with Ruff
mypy .                    # Run MyPy type checking
```

### Testing Commands

```bash
# TypeScript/JavaScript (Vitest)
npm run test              # Run tests
npm run test:watch        # Run tests in watch mode
npm run test:coverage     # Run tests with coverage
npm run test:ui           # Open Vitest UI

# Python (pytest)
pytest                    # Run tests
pytest --cov              # Run tests with coverage
pytest -v                 # Verbose output
pytest -k "test_name"     # Run specific test
pytest -m unit            # Run unit tests only
pytest -m integration     # Run integration tests only
```

### Build Commands

```bash
# TypeScript
npm run build             # Build TypeScript

# Python
python -m build           # Build Python package

# Clean
npm run clean             # Remove build artifacts
```

## Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`. They check:

- Trailing whitespace
- File endings
- YAML/JSON syntax
- Merge conflicts
- Large files
- TypeScript linting (ESLint)
- TypeScript type checking (tsc)
- TypeScript formatting (Prettier)
- Python linting (Ruff)
- Python type checking (MyPy)

To run hooks manually:

```bash
pre-commit run --all-files
```

To bypass hooks (not recommended):

```bash
git commit --no-verify
```

## CI/CD Pipeline

### GitHub Actions Workflows

1. **CI Pipeline** (`.github/workflows/ci.yml`)
   - Triggers: Push to main/develop, PRs
   - Jobs: lint, type-check, test, build
   - Matrix: Node 20.x, Python 3.11/3.12

2. **Fast Lint** (`.github/workflows/lint.yml`)
   - Triggers: PRs
   - Quick feedback on code quality

### CI Requirements

All checks must pass before merging:

- ESLint (max-warnings=0)
- Prettier formatting
- TypeScript type checking
- Ruff linting and formatting
- MyPy type checking
- Vitest tests (80% coverage)
- Pytest tests (80% coverage)
- Successful build

## Project Structure

```
resume-toolkit/
├── src/                      # Source code
│   ├── python/              # Python modules
│   └── cli/                 # TypeScript CLI
├── tests/                   # Test files
├── .github/workflows/       # CI/CD workflows
├── .tmp/                    # Temporary files (gitignored)
├── dist/                    # Build output (gitignored)
└── coverage/               # Coverage reports (gitignored)
```

## Code Standards

### TypeScript

- Strict mode enabled
- No `any` types
- Explicit return types
- Import ordering (alphabetical)
- 100 character line limit

### Python

- Type hints required
- Ruff linting
- MyPy strict mode
- 100 character line limit
- Pathlib for file operations

## Testing Standards

### TypeScript (Vitest)

- Place tests next to source: `src/module.test.ts`
- Or in tests directory: `tests/module.test.ts`
- Use descriptive test names
- Aim for 80%+ coverage

### Python (pytest)

- Tests in `src/python/tests/`
- Naming: `test_*.py` or `*_test.py`
- Use markers: `@pytest.mark.unit`, `@pytest.mark.integration`
- Aim for 80%+ coverage

## Git Workflow

1. Create feature branch from `main`
2. Make changes with clear commits
3. Pre-commit hooks run automatically
4. Push and create PR
5. CI pipeline runs
6. Request review
7. Merge when all checks pass

## Troubleshooting

### Pre-commit Hook Failures

```bash
# Update hooks
pre-commit autoupdate

# Clear cache
pre-commit clean

# Reinstall
pre-commit uninstall
pre-commit install
```

### TypeScript Issues

```bash
# Clear build cache
rm -rf dist node_modules/.cache

# Rebuild
npm run build
```

### Python Issues

```bash
# Recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

## Getting Help

- Check CI logs for detailed error messages
- Run failing checks locally: `npm run lint`, `pytest`, etc.
- Ensure pre-commit hooks are installed: `pre-commit install`
- Verify correct Node/Python versions: `node --version`, `python --version`
