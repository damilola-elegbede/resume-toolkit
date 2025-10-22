# Development Guide

Detailed guide for developers working on Resume Toolkit.

## How to Add New Commands

### Step 1: Create Command File

Create a new TypeScript command file in `src/cli/commands/`:

```typescript
// src/cli/commands/new-command.ts

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

### Step 2: Create Python Handler

Create the corresponding Python handler in `src/python/`:

```python
# src/python/new_module/handler.py

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

### Step 3: Register Command

Add the command to the CLI entry point:

```typescript
// src/cli/index.ts

import { registerNewCommand } from './commands/new-command';

const program = new Command();

// ... existing commands
registerNewCommand(program);

program.parse();
```

### Step 4: Add Tests

Create TypeScript tests:

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

Create Python tests:

```python
# src/python/tests/test_new_handler.py

import pytest
from python.new_module.handler import handle_new_command

class TestNewHandler:
    def test_basic_functionality(self):
        result = handle_new_command({'required': 'value'})
        assert result['success'] is True
```

## Test-Driven Development (TDD)

### TDD Workflow

```text
1. Write failing test
2. Run test (should fail)
3. Write minimal code to pass
4. Run test (should pass)
5. Refactor
6. Repeat
```

### TypeScript TDD Example

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

### Python TDD Example

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

## Running Tests

### TypeScript Tests (Vitest)

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

### Python Tests (pytest)

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

### Integration Tests

```bash
# Run integration tests
npm run test:integration

# Requires:
# - Running database
# - Test fixtures
# - Environment variables
```

## Unit Testing Best Practices

### Test Isolation

- Each test should be independent
- Use mocks for external dependencies
- Test one behavior per test case
- Follow AAA pattern: Arrange, Act, Assert

### TypeScript Unit Tests

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

### Python Unit Tests

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

## Integration Testing

### Test Real Workflows

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

## Test Coverage Requirements

### Minimum Coverage Targets

- **Overall**: 80%+ coverage
- **Critical Paths**: 100% coverage (parse, optimize, score)
- **Error Handling**: All error paths tested
- **Edge Cases**: Boundary conditions covered

### Checking Coverage

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

## Development Workflow

### Daily Development Cycle

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

### CI/CD Testing

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

## Code Quality Standards

### TypeScript Standards

- **Style**: Prettier with 2-space indentation
- **Linting**: ESLint with strict rules
- **Type Safety**: strict mode enabled in tsconfig.json
- **Naming**: camelCase for variables, PascalCase for types/classes
- **File Structure**: One component/function per file
- **Comments**: JSDoc for public APIs

### Python Standards

- **Style**: Black formatter (88 char line length)
- **Linting**: Ruff (faster than Flake8)
- **Type Hints**: All function signatures typed
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Docstrings**: Google style
- **Imports**: Sorted with isort

### Example TypeScript

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

### Example Python

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

## Pre-commit Hooks

### Automatic Checks Before Commit

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

### Manual Hook Execution

```bash
# Run pre-commit hooks manually
npm run pre-commit

# Skip hooks (not recommended)
git commit --no-verify -m "message"
```

## Setting Up Development Environment

### 1. Clone and Install

```bash
# Clone repository
git clone https://github.com/yourusername/resume-toolkit.git
cd resume-toolkit

# Install dependencies
npm install
pip install -e ".[dev]"
```

### 2. Configure Pre-commit Hooks

```bash
# Install Husky
npm run prepare

# Install Python pre-commit
pre-commit install
```

### 3. Set Up Database

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

### 4. Verify Setup

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

## Additional Resources

- See [CLAUDE.md](../CLAUDE.md) for project overview and commands reference
- See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common development issues
- See [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) for database structure
