# /apply - Master Application Orchestrator

## Overview

The `/apply` command is the flagship orchestrator that runs the complete job application workflow end-to-end. It analyzes the job description, researches the company, optimizes your resume, generates a cover letter, calculates ATS score, creates PDFs, tracks the application, and optionally prepares interview materials - all in one seamless workflow.

## Usage

```bash
resume-toolkit apply <job-url> [options]
```

## Options

- `-t, --template <template>` - Resume template to use (executive, director, manager, senior, mid)
- `--with-prep` - Include interview preparation materials
- `--resume` - Resume from previous incomplete workflow
- `--dry-run` - Show what would be done without executing

## Workflow Stages

1. **Analyze Job Description** - Extract company, role, keywords, and requirements
2. **Research Company** - Gather recent news, culture, products, and financials
3. **Optimize Resume** - Iteratively improve resume for 90%+ ATS score
4. **Generate Cover Letter** - Create personalized letter with company insights
5. **Calculate ATS Score** - Final scoring and recommendations
6. **Generate PDF** - Convert markdown resume to professional PDF
7. **Track Application** - Create tracking entry with follow-up reminders
8. **Interview Prep** (optional) - Generate likely questions and STAR answers
9. **Summary** - Display results and next steps

## Examples

### Basic Application

```bash
resume-toolkit apply https://www.linkedin.com/jobs/view/3456789012
```

### With Director Template

```bash
resume-toolkit apply https://jobs.lever.co/company/abc123 --template director
```

### Include Interview Prep

```bash
resume-toolkit apply https://boards.greenhouse.io/company/jobs/5678 --with-prep
```

### Resume From Failure

```bash
# If the workflow fails partway through
resume-toolkit apply <same-url> --resume
```

### Dry Run Mode

```bash
# See what would happen without executing
resume-toolkit apply <url> --dry-run
```

## Output Structure

Creates a comprehensive application folder:

```
applications/
└── 2025-10-21-techcorp-director/
    ├── job-description.md      # Original JD
    ├── jd-analysis.md          # Keyword analysis
    ├── company-research.md     # Company insights
    ├── tailored-resume.md      # Optimized resume
    ├── resume.pdf              # PDF version
    ├── cover-letter.md         # Personalized letter
    ├── ats-score-report.md     # Detailed scoring
    ├── interview-prep.md       # Q&A preparation (if --with-prep)
    └── metadata.yaml           # Application metadata
```

## Features

### Progress Saving

- Automatically saves progress after each stage
- Can resume from failure with `--resume` flag
- Progress stored in `.tmp/apply-progress.json`

### Intelligent Error Handling

- **Critical failures** (JD analysis) abort the workflow
- **Non-critical failures** (company research) continue with warnings
- **PDF failures** fall back to markdown format
- All errors logged with helpful recovery tips

### ATS Optimization Loop

- Automatically retries optimization up to 3 times
- Targets 90%+ ATS score
- Shows iteration progress
- Reports final score achieved

### Smart Context Passing

- Company research enriches cover letter
- JD keywords guide resume optimization
- Analysis results flow between stages
- Context preserved across resume attempts

## Expected Output

```
🚀 Starting application workflow

✓ Analyzing job description... (5s)
  • Keywords identified: 47

✓ Researching company... (12s)
  • Recent news: AWS Partnership Announcement
  • Glassdoor rating: 4.2/5

✓ Optimizing resume... (38s)
  Optimization iteration 1: 78%
  Optimization iteration 2: 92%
✓ Resume optimized: 92% (2 iterations)

✓ Generating cover letter... (6s)
  • Length: 387 words ✓
  • Keywords integrated: 12 ✓

✓ Calculating final ATS score... (2s)
  • Keyword match: 95%
  • Formatting: 90%

✓ Generating PDF resume... (3s)

✓ Creating application tracking entry... (1s)

✓ Preparing interview questions... (8s)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Application package complete! (75 seconds)

📁 Generated Files:
  • applications/2025-10-21-techcorp-director/job-description.md
  • applications/2025-10-21-techcorp-director/jd-analysis.md
  • applications/2025-10-21-techcorp-director/company-research.md
  • applications/2025-10-21-techcorp-director/tailored-resume.md
  • applications/2025-10-21-techcorp-director/resume.pdf
  • applications/2025-10-21-techcorp-director/cover-letter.md
  • applications/2025-10-21-techcorp-director/ats-score-report.md
  • applications/2025-10-21-techcorp-director/interview-prep.md
  • applications/2025-10-21-techcorp-director/metadata.yaml

📊 Metrics:
  • ATS Score: 92%
  • Time to create: 75 seconds
  • Files generated: 9

🎯 Next Steps:
  1. Review the generated resume and cover letter
  2. Submit application via the job posting URL
  3. Follow up date: 2025-10-28
  4. Prepare for interview using interview-prep.md

💡 Pro Tip: Your ATS score is excellent (92%). Consider adding
   "regulatory compliance" for a potential 2% boost.
```

## Troubleshooting

### "Failed to fetch JD"

- Check if the URL is accessible
- Some job boards block automation - try a different link
- Manually save the JD and use other commands individually

### "PDF generation failed"

- Install Pandoc: `brew install pandoc` (macOS) or `apt install pandoc` (Linux)
- Install XeLaTeX for better formatting: `brew install --cask mactex`
- Markdown version is always saved as fallback

### "Resume from different job URL"

- The `--resume` flag only works with the same job URL
- To start fresh, omit the `--resume` flag
- Progress file is at `.tmp/apply-progress.json`

### Low ATS Score

- The optimizer will retry up to 3 times automatically
- Check if your base resume has the fundamental keywords
- Consider using a different template with `--template`
- Review the ATS score report for specific recommendations

## Best Practices

1. **Review Output**: Always review generated materials before submitting
2. **Customize Further**: Use the output as a strong starting point
3. **Track Applications**: The system creates tracking entries automatically
4. **Interview Prep**: Use `--with-prep` for important applications
5. **Template Selection**: Choose template based on seniority level

## Performance

- Full workflow typically completes in 60-120 seconds
- Most time spent on resume optimization (iterative improvement)
- Company research may add 10-15 seconds
- PDF generation depends on Pandoc installation

## Integration

The `/apply` command orchestrates these individual commands:

- `analyze-jd` - Job description analysis
- `research-company` - Company research
- `optimize-resume` - Resume optimization
- `generate-cover-letter` - Cover letter generation
- `score-ats` - ATS scoring
- `track-application` - Application tracking
- `interview-prep` - Interview preparation (optional)

Each can also be run individually for more control.

## Related Commands

- `/optimize-resume` - Run resume optimization standalone
- `/track-application` - Add tracking for manual applications
- `/application-dashboard` - View all applications
- `/interview-prep` - Generate interview prep separately