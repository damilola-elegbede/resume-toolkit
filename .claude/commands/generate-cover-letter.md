# Generate Cover Letter Command

Generate personalized, compelling cover letters based on job description analysis, company research, and your resume anecdotes.

## Usage

```bash
resume-toolkit generate-cover-letter <job-url> [options]
```

## Arguments

- `<job-url>` - Job description URL (LinkedIn, Greenhouse, Lever, Indeed, Workday)

## Options

- `-c, --company <name>` - Company name (if different from JD)
- `-t, --tone <tone>` - Writing tone: `formal`, `professional` (default), or `casual`
- `-n, --notes <notes>` - Custom notes to include (e.g., referral information)
- `-u, --user-info <path>` - Path to user info JSON file (default: `.resume-toolkit/user-info.json`)
- `-a, --anecdotes <path>` - Path to anecdotes directory (default: `.resume-toolkit/anecdotes`)

## Examples

### Basic Usage

```bash
resume-toolkit generate-cover-letter https://www.linkedin.com/jobs/view/1234567890
```

### With Custom Tone

```bash
# Formal tone (traditional corporate)
resume-toolkit generate-cover-letter https://jobs.lever.co/company/role --tone formal

# Professional tone (balanced - default)
resume-toolkit generate-cover-letter https://boards.greenhouse.io/company/jobs/123

# Casual tone (startup-friendly)
resume-toolkit generate-cover-letter https://jobs.lever.co/startup/role --tone casual
```

### With Custom Notes

```bash
# Mention a referral
resume-toolkit generate-cover-letter https://www.linkedin.com/jobs/view/123 \
  --notes "Jane Smith from the engineering team referred me to this position"

# Mention specific interest
resume-toolkit generate-cover-letter https://jobs.lever.co/company/role \
  --notes "I'm particularly interested in this role because of your work on distributed systems"
```

### With Custom Paths

```bash
resume-toolkit generate-cover-letter https://www.linkedin.com/jobs/view/123 \
  --user-info ~/my-info.json \
  --anecdotes ~/my-anecdotes
```

## Prerequisites

### 1. User Info File

Create `.resume-toolkit/user-info.json` with your contact information:

```json
{
  "name": "Your Name",
  "email": "your.email@example.com",
  "phone": "+1 (555) 123-4567",
  "linkedin": "linkedin.com/in/yourprofile"
}
```

### 2. Anecdotes Directory

Create `.resume-toolkit/anecdotes/` with markdown files containing your achievements:

Example: `.resume-toolkit/anecdotes/kubernetes-migration.md`

```markdown
---
title: Led Kubernetes Migration
skills: [kubernetes, docker, devops, leadership, ci/cd]
impact: Reduced deployment time by 70%
date: 2023-06
company: TechCorp
---

Led the migration of our monolithic application to a Kubernetes-based microservices architecture.

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
```

### 3. Company Research (Optional but Recommended)

After running the command once, edit `applications/YYYY-MM-DD-company-role/company-research.json` to add specific company information for a more personalized letter:

```json
{
  "company": "TechCorp",
  "mission": "To build innovative cloud solutions that scale globally",
  "values": ["Innovation", "Collaboration", "Customer Focus"],
  "recent_news": [
    "Announced $50M Series B funding",
    "Launched new AWS partnership program"
  ],
  "culture": "Fast-paced startup environment with strong engineering culture",
  "tech_stack": ["Python", "React", "AWS", "Kubernetes"]
}
```

Then run the command again to regenerate with more context.

## Output

The command generates:

1. **Cover Letter** - `applications/YYYY-MM-DD-company-role/cover-letter.md`
2. **JD Analysis** - `applications/YYYY-MM-DD-company-role/jd-analysis.json` (auto-generated)
3. **Company Research Template** - `applications/YYYY-MM-DD-company-role/company-research.json`

### Example Output

```
Cover Letter Generated Successfully!

Details:
  Company: TechCorp
  Position: Senior Software Engineer
  Tone: professional
  Word Count: 387

Saved to: applications/2024-10-21-techcorp-senior-software-engineer/cover-letter.md
```

## Cover Letter Structure

The generated cover letter follows best practices:

1. **Header** - Your contact information
2. **Opening** (1 paragraph) - Company-specific hook with enthusiasm
3. **Body** (2-3 paragraphs) - Relevant achievements with metrics
4. **Closing** (1 paragraph) - Call to action and gratitude
5. **Signature** - Professional closing

### Quality Features

- **Personalized** - References specific company information
- **Achievement-focused** - Uses STAR-format examples with metrics
- **Natural keywords** - Integrates JD keywords organically (no stuffing)
- **Optimal length** - 350-500 words (optimal for readability)
- **Tone-appropriate** - Matches company culture
- **Error-free** - Professional grammar and formatting

## Tone Guide

### Formal

- Traditional corporate environments
- Executive roles
- Conservative industries (finance, law, healthcare)
- More reserved language
- Proper business letter format

**Example opening:**
> "I was pleased to submit my application for the Senior Software Engineer position at TechCorp. I have been following TechCorp's recent Series B funding announcement and am impressed by the company's growth trajectory and vision."

### Professional (Default)

- Tech companies
- Growth-stage startups
- Most modern companies
- Balanced tone - professional but warm
- Standard for most applications

**Example opening:**
> "I was excited to apply for the Senior Software Engineer position at TechCorp. Your recent Series B funding announcement caught my attention and reinforced my interest in joining your team."

### Casual

- Early-stage startups
- Creative companies
- Companies with explicitly casual culture
- Conversational but still professional
- Use sparingly and only when appropriate

**Example opening:**
> "I'm excited to apply for the Software Engineer position at TechCorp. Your recent Series B announcement caught my attention - the growth trajectory is impressive!"

## Tips for Customization

### 1. Add Company Research

The more specific information you provide in `company-research.json`, the better:

- Recent news (funding, product launches, partnerships)
- Mission and values
- Culture insights
- Tech stack
- Notable achievements

### 2. Create Rich Anecdotes

Each anecdote should:

- Use STAR format (Situation, Task, Action, Result)
- Include specific metrics (70% improvement, $1M savings, etc.)
- Tag with relevant skills
- Be concise but impactful

### 3. Use Custom Notes Strategically

Good uses for `--notes`:

- Referral mentions
- Specific project interest
- Conference/event connections
- Shared connections
- Unique value propositions

### 4. Match Tone to Company

Research the company culture:

- Check their careers page language
- Read employee reviews
- Look at social media presence
- Consider industry norms

## Workflow Integration

### Recommended Application Workflow

1. **Analyze JD** - `resume-toolkit analyze-jd <url>`
2. **Research Company** - Edit `company-research.json`
3. **Generate Cover Letter** - `resume-toolkit generate-cover-letter <url>`
4. **Review and Edit** - Personalize the generated letter
5. **Optimize Resume** - `resume-toolkit optimize-resume <url>`
6. **Apply** - Submit through company portal

### Iterative Improvement

1. Generate initial version
2. Review output
3. Add more company research
4. Regenerate for improvements
5. Manual final polish

## Common Issues

### "User info not found"

Create `.resume-toolkit/user-info.json` with your contact information.

### "No anecdotes found"

Create `.resume-toolkit/anecdotes/` directory and add markdown files with your achievements.

### "Cover letter too generic"

Add company-specific information to `company-research.json` and regenerate.

### "Tone doesn't match"

Try different tone options: `--tone formal`, `--tone professional`, or `--tone casual`.

## Best Practices

1. **Always customize** - Use the generated letter as a starting point, not the final version
2. **Add company research** - Spend 15-30 minutes researching the company
3. **Reference specific details** - Mention specific products, news, or initiatives
4. **Keep it concise** - 350-500 words is optimal
5. **Proofread** - Always review for typos and errors
6. **Be genuine** - Ensure enthusiasm feels authentic
7. **Match tone** - Align with company culture
8. **Update anecdotes** - Keep your achievement library current

## See Also

- `analyze-jd` - Analyze job descriptions
- `optimize-resume` - Tailor resume to job description
- `score-ats` - Score ATS compatibility
