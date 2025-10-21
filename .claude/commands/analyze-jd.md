# Analyze Job Description

Fetches and analyzes a job description from a URL, extracting key information and generating an ATS-optimized keyword list.

## Usage

```bash
/analyze-jd <job-url>
```

## Supported Job Boards

- **LinkedIn**: `linkedin.com/jobs/view/`
- **Greenhouse**: `boards.greenhouse.io/`
- **Lever**: `jobs.lever.co/`
- **Indeed**: `indeed.com/viewjob`
- **Workday**: `.myworkdayjobs.com/`

## What It Does

1. **Scrapes** the job description from the provided URL
2. **Extracts** key information:
   - Company name
   - Position title
   - Job description
   - Requirements
   - Benefits
3. **Analyzes** the content:
   - Technical skills required
   - Leadership/soft skills
   - Domain expertise
   - Required vs nice-to-have skills
4. **Generates** ATS-optimized keyword list with importance scores
5. **Saves** analysis to `applications/YYYY-MM-DD-company-role/jd-analysis.md`

## Output

The command creates a comprehensive Markdown report including:

- Technical skills breakdown
- Leadership skills identified
- Domain expertise requirements
- Prioritized ATS keywords with importance scores
- Keyword frequency analysis
- Original job description
- Extracted requirements and benefits

## Examples

```bash
# Analyze a LinkedIn job posting
/analyze-jd https://www.linkedin.com/jobs/view/1234567890

# Analyze a Greenhouse posting
/analyze-jd https://boards.greenhouse.io/company/jobs/1234567890

# Analyze a Lever posting
/analyze-jd https://jobs.lever.co/company/role-name
```

## Error Handling

The command handles common errors gracefully:

- **403 Forbidden**: Some sites use Cloudflare protection
- **404 Not Found**: Job posting may have been removed
- **Timeout**: Page took too long to load
- **Invalid URL**: URL format is not recognized

## Tips

- Use the analysis to optimize your resume with the right keywords
- Focus on high-importance keywords (score > 0.8)
- Review the required vs nice-to-have sections to prioritize skills
- Check technical skills list to ensure resume alignment
- Use ATS keywords in your cover letter and resume

## Integration

This command integrates with other Resume Toolkit commands:

- Use with `/tailor-resume` to optimize your resume for the job
- Combine with `/ats-score` to check resume match percentage
- Reference when writing cover letters
