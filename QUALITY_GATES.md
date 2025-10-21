# Quality Gates

This document describes the quality gates that must pass before code can be merged into the main branch.

## Overview

All code changes must pass **four mandatory quality gates**:

1. **Linting** - Code must be free of linting errors
2. **Type Checking** - Code must be fully type-safe (zero type errors)
3. **Testing** - All tests must pass
4. **Coverage** - **Commands must maintain 85%+ test coverage** ✨

## Coverage Quality Gate (85% Minimum)

### Why 85%?

We enforce a minimum of **85% test coverage** on all command files to ensure:
- High code quality and reliability
- Confidence in refactoring
- Early bug detection
- Comprehensive test documentation
- Production-ready code

### What Gets Measured?

Coverage is measured across **four metrics**:
- **Lines**: % of executable lines covered by tests
- **Branches**: % of conditional branches covered
- **Functions**: % of functions called by tests
- **Statements**: % of statements executed

**All four metrics must be ≥85% for each command file.**

### Enforcement Levels

#### 1. Local Development
```bash
# Check coverage before committing
npm run test:coverage:check

# View detailed coverage report
npm run test:coverage
open coverage/index.html
```

#### 2. Pre-Commit Hooks
```bash
# Automatically runs on git commit
git commit -m "feat: add new feature"
# Coverage check runs automatically
```

#### 3. CI/CD Pipeline
```yaml
# Runs on every PR and push
- Dedicated coverage-check.yml workflow
- Integrated into main ci.yml pipeline
- Fails build if coverage drops below 85%
```

## Running Quality Gates

### All Gates at Once
```bash
npm run quality-gates
```

This runs:
1. ESLint
2. TypeScript type check
3. Vitest with coverage
4. Coverage threshold check

### Individual Gates

**Linting:**
```bash
npm run lint           # Check for issues
npm run lint:fix       # Auto-fix issues
```

**Type Checking:**
```bash
npm run type-check
```

**Testing:**
```bash
npm test                    # Run tests
npm run test:watch          # Watch mode
npm run test:coverage       # With coverage report
npm run test:coverage:check # With 85% enforcement
```

## Coverage Report Examples

### ✅ Passing Example
```
📊 Overall Command Coverage:
   Lines:      92.50% (740/800)
   Branches:   88.30% (350/396)
   Functions:  91.20% (115/126)
   Statements: 92.50% (740/800)

✅ QUALITY GATE PASSED! All commands have 85%+ coverage.
```

### ❌ Failing Example
```
❌ QUALITY GATE FAILED! 2 command(s) below 85% threshold:

   parse-resume.ts:
     Lines:      82.50%
     Branches:   80.00%
     Functions:  85.00%
     Statements: 82.50%

   optimize-resume.ts:
     Lines:      83.20%
     Branches:   81.50%
     Functions:  86.00%
     Statements: 83.20%

💡 Fix: Add more tests to increase coverage above 85%
   Run: npm run test:watch
```

## How to Improve Coverage

### 1. Identify Uncovered Code
```bash
# Generate HTML coverage report
npm run test:coverage

# Open in browser
open coverage/index.html
```

The HTML report highlights:
- **Green**: Covered lines
- **Red**: Uncovered lines
- **Yellow**: Partially covered branches

### 2. Add Tests for Uncovered Code

**Example: Uncovered error handling**
```typescript
// Uncovered code
if (!file.exists()) {
  throw new Error('File not found');
}
```

**Add test:**
```typescript
it('should throw error when file does not exist', () => {
  expect(() => parseResume('nonexistent.pdf'))
    .toThrow('File not found');
});
```

### 3. Test Edge Cases
- Error conditions
- Boundary values
- Empty inputs
- Invalid inputs
- Async failures

### 4. Test All Code Paths
```typescript
// Test all branches
if (status === 'applied') {
  // Test case 1
} else if (status === 'interview') {
  // Test case 2
} else {
  // Test case 3 (don't forget this!)
}
```

## Exemptions

### When to Request Exemption
Coverage requirements can be relaxed for:
- Experimental features (with explicit TODO)
- External integrations (mocked)
- Legacy code undergoing refactoring

### How to Request Exemption
1. Add `/* istanbul ignore next */` comment
2. Document reason in PR description
3. Get approval from maintainer

**Example:**
```typescript
/* istanbul ignore next - External API, tested via integration tests */
async function callExternalAPI() {
  // This code is covered by integration tests
}
```

## CI/CD Integration

### GitHub Actions Workflows

**Main CI Pipeline** (`.github/workflows/ci.yml`):
- Runs on every push and PR
- Includes coverage check as part of test job
- Uploads coverage reports to Codecov

**Dedicated Coverage Check** (`.github/workflows/coverage-check.yml`):
- Runs in parallel with main CI
- Posts coverage report as PR comment
- Fails if coverage drops below 85%
- Provides detailed breakdown per file

### Coverage Badges

Add to README.md:
```markdown
![Coverage](https://img.shields.io/codecov/c/github/your-org/resume-toolkit)
```

## Best Practices

### 1. Write Tests First (TDD)
```bash
# Red: Write failing test
npm run test:watch

# Green: Make test pass
# (write minimal code)

# Refactor: Improve code quality
# (tests keep you safe)
```

### 2. Aim for 90%+
While 85% is the minimum, aim for 90%+ coverage for critical commands like:
- `/apply` (master orchestrator)
- `/optimize-resume` (core algorithm)
- `/score-ats` (scoring logic)

### 3. Focus on Quality, Not Quantity
- Test behavior, not implementation
- Use meaningful test descriptions
- Avoid redundant tests
- Test edge cases thoroughly

### 4. Monitor Coverage Trends
```bash
# Check coverage before making changes
npm run test:coverage

# After changes, verify coverage maintained or improved
npm run test:coverage:check
```

## Troubleshooting

### Coverage Check Fails Locally But Not in CI
```bash
# Clear coverage cache
npm run clean
npm install

# Regenerate coverage
npm run test:coverage:check
```

### Coverage Report Not Generating
```bash
# Ensure vitest is installed
npm install

# Ensure v8 provider is available
npm list @vitest/coverage-v8
```

### Coverage Below 85% on Existing Code
```bash
# Generate coverage report
npm run test:coverage

# Identify gaps
open coverage/index.html

# Add tests incrementally
npm run test:watch
```

## Summary

| Quality Gate | Threshold | Check Command | Required |
|--------------|-----------|---------------|----------|
| Linting | 0 errors | `npm run lint` | ✅ Yes |
| Type Check | 0 errors | `npm run type-check` | ✅ Yes |
| Tests | 100% pass | `npm test` | ✅ Yes |
| **Coverage** | **≥85%** | `npm run test:coverage:check` | **✅ Yes** |

All four gates must pass before code can be merged. No exceptions without explicit approval.

---

**Remember:** Quality gates exist to maintain high standards and protect production code. They're not obstacles—they're safety nets! 🛡️
