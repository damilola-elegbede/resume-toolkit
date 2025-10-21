# /optimize-resume - Iterative Resume Optimization

Tailors a base resume to a specific job description through intelligent, iterative optimization to maximize ATS score.

## Overview

This command implements a sophisticated optimization workflow that:
1. Analyzes job description requirements
2. Selects most relevant anecdotes from your library
3. Rewrites bullets to naturally incorporate JD keywords
4. Reorders sections to prioritize relevant experiences
5. Iteratively improves until 90%+ ATS score (or max 3 iterations)

## Usage

```bash
npm run cli optimize-resume <jd-url> [options]
```

### Arguments

- `<jd-url>` - Job description URL (LinkedIn, Greenhouse, Lever, Indeed, Workday)

### Options

- `-b, --base-resume <path>` - Path to base resume markdown file (default: `.resume-toolkit/base-resume.md`)
- `-a, --anecdotes <path>` - Path to anecdotes directory (default: `.resume-toolkit/anecdotes`)
- `-o, --output <path>` - Output path for optimized resume
- `-t, --target-score <score>` - Target ATS score percentage (default: 90)
- `-i, --max-iterations <count>` - Maximum optimization iterations (default: 3)

## Examples

### Basic Usage

```bash
# Optimize for a job posting
npm run cli optimize-resume https://jobs.example.com/senior-engineer

# Output:
# ✓ Job description analyzed
# ✓ Resources loaded
#
# Optimization Progress:
# Iteration 1: Score 78% → Adding keywords: kubernetes, distributed systems
# Iteration 2: Score 86% → Adding keywords: redis, microservices
# Iteration 3: Score 92% → Reordering sections
#
# ✓ Target reached! Final score: 92%
#
# Optimized resume saved to: applications/2025-10-21-techcorp-director/tailored-resume.md
# Optimization report: applications/2025-10-21-techcorp-director/optimization-report.md
```

### Custom Target Score

```bash
# Aim for 95% ATS score
npm run cli optimize-resume <url> --target-score 95 --max-iterations 5
```

### Custom Base Resume

```bash
# Use a different base resume template
npm run cli optimize-resume <url> --base-resume ~/resumes/executive-template.md
```

## Optimization Strategy

### 1. Anecdote Selection

The optimizer scores each anecdote in your library based on:
- **Keyword Overlap**: Matching JD keywords with anecdote skills
- **Importance Weighting**: Higher scores for high-value JD keywords
- **Diversity**: Ensures variety of experiences (avoids redundancy)

**Example:**
```
JD Keywords: kubernetes (0.95), python (0.90), leadership (0.80)

Anecdote Scores:
- "Led Kubernetes Migration" → 0.88 (high match)
- "Built Python API" → 0.75 (good match)
- "React Optimization" → 0.20 (low match)

Selected: Top 2 anecdotes for inclusion
```

### 2. Bullet Rewriting

Bullets are enhanced to include missing keywords while maintaining:
- **STAR Format**: Situation, Task, Action, Result
- **Authenticity**: Only add relevant, truthful details
- **Natural Flow**: Avoid keyword stuffing (max 2-3 keywords per bullet)
- **Metrics**: Preserve quantifiable achievements

**Example:**
```
Original:
"Led migration of application, reducing deployment time"

Enhanced:
"Led migration of application to Kubernetes using Docker, reducing deployment time by 70%"

Added: kubernetes, docker (from JD)
Preserved: action (led), metric (70%)
```

### 3. Section Optimization

- **Experience Ordering**: Most relevant roles first
- **Skills Prioritization**: JD-matching skills at the top
- **Summary Adjustment**: Incorporate leadership/technical themes from JD

### 4. Iterative Loop

Each iteration:
1. **Generate** optimized resume
2. **Score** with ATS analyzer
3. **Identify gaps** (missing high-value keywords)
4. **Optimize** to address gaps
5. **Repeat** until target score or max iterations

**Convergence:**
- Stops at 90% score (customizable)
- Max 3 iterations (prevents over-optimization)
- Tracks improvement per iteration

## Output Structure

The command creates an application directory with:

```
applications/YYYY-MM-DD-company-role/
├── jd-analysis.md          # JD keyword analysis
├── tailored-resume.md      # Optimized resume
└── optimization-report.md  # Iteration history
```

### Optimization Report Example

```markdown
# Resume Optimization Report

**Final Score:** 92%
**Iterations:** 3

## Iteration History

### Iteration 1
- **Score:** 78%
- **Gaps:** kubernetes, docker, distributed systems
- **Improvements:** Added K8s migration anecdote, enhanced bullets

### Iteration 2
- **Score:** 86%
- **Gaps:** redis, microservices
- **Improvements:** Added caching anecdote, reordered experiences

### Iteration 3
- **Score:** 92%
- **Gaps:** None
- **Improvements:** Prioritized skills section, adjusted summary
```

## Setup Requirements

### 1. Base Resume

Create a base resume in markdown with YAML frontmatter:

```markdown
---
name: John Doe
title: Senior Software Engineer
email: john@example.com
phone: (555) 123-4567
---

# Summary
Senior Software Engineer with 8 years of experience...

# Experience

## Senior Engineer - TechCorp
*Jan 2020 - Present*

- Led backend development for microservices platform
- Managed team of 5 engineers
- Improved system performance by 40%

# Skills

**Languages:** Python, JavaScript, TypeScript, Go
**Frameworks:** React, Django, Node.js, FastAPI
**Tools:** Docker, Kubernetes, AWS, PostgreSQL
```

### 2. Anecdotes Library

Create anecdotes in `.resume-toolkit/anecdotes/`:

```markdown
---
title: Led Kubernetes Migration
skills: [kubernetes, docker, devops, leadership]
impact: Reduced deployment time by 70%
date: 2023-06
company: TechCorp
---

Led the migration of our monolithic application to a Kubernetes-based
microservices architecture. Coordinated with DevOps team to implement
CI/CD pipelines using GitLab. Trained team of 5 engineers on container
orchestration best practices.

**Results:**
- Reduced deployment time from 2 hours to 20 minutes (70% improvement)
- Improved system uptime to 99.9%
- Enabled independent service scaling
```

## Workflow Integration

### Typical Usage Flow

```bash
# 1. Analyze job description
npm run cli analyze-jd <url>

# 2. Optimize resume for that JD
npm run cli optimize-resume <url>

# 3. Review optimized resume
cat applications/*/tailored-resume.md

# 4. Fine-tune manually if needed
code applications/*/tailored-resume.md

# 5. Generate PDF for submission
npm run cli generate-pdf applications/*/tailored-resume.md
```

## Best Practices

### ✓ Do's

- **Maintain Anecdotes**: Keep your anecdote library updated with recent achievements
- **Review Output**: Always review optimized resume for accuracy and natural flow
- **Track Versions**: Keep original base resume separate from tailored versions
- **Preserve Truth**: Never add skills or experiences you don't have
- **Target Appropriately**: 90% score is excellent; 100% may indicate over-optimization

### ✗ Don'ts

- **Don't Keyword Stuff**: Quality over quantity - natural integration is key
- **Don't Over-Iterate**: Max 3-5 iterations; more may create unnatural content
- **Don't Copy Blindly**: Review each optimized bullet for accuracy
- **Don't Ignore Context**: Some JD keywords may not apply to your experience

## Technical Details

### Optimization Algorithm

1. **Anecdote Selection:**
   - Relevance scoring: `score = Σ(keyword_importance * match)`
   - Diversity penalty for overlapping skills
   - Top N selection (default: 5)

2. **Bullet Rewriting:**
   - Identify missing keywords via set difference
   - Natural language insertion using templates
   - STAR format preservation
   - Metric extraction and retention

3. **ATS Scoring:**
   - Weighted keyword matching
   - Importance-based scoring: `score = (matched_weight / total_weight) * 100`
   - Normalization to 0-100 scale

4. **Convergence Criteria:**
   - Target score reached: `score >= target_score`
   - Maximum iterations: `iteration >= max_iterations`
   - Diminishing returns: `improvement < 2%` for 2 consecutive iterations

### Performance

- **Average Runtime:** 30-60 seconds
- **JD Analysis:** ~5 seconds
- **Optimization Iteration:** ~10 seconds each
- **Total:** ~3 iterations = 30-40 seconds + analysis

## Troubleshooting

### "Base resume not found"

Create a base resume:
```bash
mkdir -p .resume-toolkit
touch .resume-toolkit/base-resume.md
```

### "No anecdotes found"

Add anecdotes to your library:
```bash
mkdir -p .resume-toolkit/anecdotes
# Create anecdote files in this directory
```

### "Score not improving"

- Ensure anecdotes match JD keywords
- Add more diverse anecdotes to library
- Check JD analysis for actual requirements
- Consider manual review of gaps

### "Unnatural keyword integration"

- Reduce max iterations
- Review and manually edit bullets
- Ensure anecdotes are detailed and context-rich
- Lower target score slightly (85-90% is excellent)

## Related Commands

- `/analyze-jd` - Analyze job description keywords
- `/parse-resume` - Extract resume data
- `/generate-pdf` - Create PDF from markdown

## Implementation

**Python Backend:**
- `src/python/resume_optimizer/optimizer.py` - Core optimization logic
- Anecdote selection and scoring
- Bullet rewriting with NLP
- Iterative improvement loop

**TypeScript CLI:**
- `src/cli/commands/optimize-resume.ts` - Command interface
- Python process orchestration
- Progress display and reporting

**Tests:**
- `src/python/tests/test_resume_optimizer.py` - Python unit tests
- `src/cli/__tests__/commands/optimize-resume.test.ts` - CLI integration tests

## Future Enhancements

- AI-powered bullet rewriting (GPT-4)
- Resume template selection
- A/B testing optimization
- Cover letter generation
- Interview prep suggestions based on gaps
