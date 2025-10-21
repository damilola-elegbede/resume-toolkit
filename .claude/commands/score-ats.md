# Score ATS Command

Calculate ATS (Applicant Tracking System) compatibility score for a resume against a job description.

## Usage

```bash
# Basic usage
npm run dev score-ats -r path/to/resume.md -j path/to/jd.txt

# With output report
npm run dev score-ats -r resume.md -j jd.txt -o ats-report.md

# Verbose mode (detailed breakdown)
npm run dev score-ats -r resume.md -j jd.txt -v

# JSON output
npm run dev score-ats -r resume.md -j jd.txt --json
```

## Options

- `-r, --resume <path>` - Path to resume file (markdown or text) **[Required]**
- `-j, --jd <path>` - Path to job description file **[Required]**
- `-o, --output <path>` - Path to save detailed report as markdown
- `-v, --verbose` - Show detailed breakdown of all scoring components
- `--json` - Output results as JSON

## How It Works

The ATS scorer analyzes your resume against a job description using a weighted algorithm:

### Scoring Algorithm

```
Overall Score = (
  Keyword Match × 50% +
  Formatting × 20% +
  Skills Alignment × 20% +
  Section Structure × 10%
)
```

### 1. Keyword Match (50% weight)

Compares keywords between resume and job description:

- **Required Skills**: High-importance keywords (70% weight)
- **Nice-to-Have**: Lower-importance keywords (30% weight)
- Analyzes keyword frequency and importance
- Identifies missing critical keywords

### 2. Formatting (20% weight)

Checks resume structure for ATS compatibility:

- ✓ Standard section headers (EXPERIENCE, EDUCATION, SKILLS)
- ✓ Bullet points usage
- ✓ Consistent date formats (YYYY-MM preferred)
- ✗ No tables or complex formatting (ATS-unfriendly)

### 3. Skills Alignment (20% weight)

Matches skills across categories:

- **Technical Skills** (50%): Programming languages, frameworks, tools
- **Leadership Skills** (30%): Mentoring, collaboration, communication
- **Domain Expertise** (20%): Architecture, design, system knowledge

### 4. Section Structure (10% weight)

Ensures all key sections are present:

- Contact information
- Experience/Work history
- Education
- Skills
- Logical section ordering

## Output Format

### Standard Output

```
════════════════════════════════════════════════════════════
  ATS Compatibility Score: 87%
════════════════════════════════════════════════════════════

Score Breakdown:
  Keyword Match       : 92% ✓
  Formatting          : 85% ⚠
  Skills Alignment    : 84% ⚠
  Section Structure   : 90% ✓

Recommendations to reach 95%:
  1. Keyword (+5%): Add 'regulatory compliance' keyword (appears 5x in JD, 0x in resume)
  2. Formatting (+3%): Standardize date format to 'YYYY-MM'
  3. Skills (+2%): Add leadership/collaboration examples to experience section
```

### Verbose Output

Shows detailed breakdowns:

```
Keyword Details:
  Required skills match: 95%
  Nice-to-have match: 85%
  Matched keywords: 45
  Missing keywords: 8

Skills Alignment Details:
  Technical skills: 90%
  Leadership skills: 80%
  Domain expertise: 75%
```

## Interpreting Scores

### Score Ranges

| Score | Rating | Meaning |
|-------|--------|---------|
| 90-100% | ✓ Excellent | Very high chance of passing ATS |
| 75-89% | ⚠ Good | Likely to pass, minor improvements needed |
| 60-74% | ⚠ Fair | May pass, significant improvements recommended |
| <60% | ✗ Poor | Unlikely to pass, major revisions needed |

### Score Indicators

- **✓ Green (90-100%)**: Excellent match, minimal changes needed
- **⚠ Yellow (75-89%)**: Good match, optimization recommended
- **✗ Red (<75%)**: Poor match, significant improvements required

## Recommendations

The scorer provides actionable recommendations prioritized by impact:

### Recommendation Categories

1. **🔑 Keyword** - Add missing important keywords
2. **📝 Formatting** - Fix ATS-unfriendly formatting
3. **💡 Skills** - Align skills with job requirements
4. **🏗 Structure** - Add or reorganize sections

### Impact Scores

Each recommendation shows expected score improvement:
- High impact (+10-15%): Critical missing elements
- Medium impact (+5-9%): Important improvements
- Low impact (+1-4%): Minor optimizations

## Examples

### Example 1: Basic Scoring

```bash
npm run dev score-ats \
  -r applications/2025-10-21-tech-corp-senior-engineer/resume.md \
  -j applications/2025-10-21-tech-corp-senior-engineer/jd-analysis.md
```

### Example 2: Generate Full Report

```bash
npm run dev score-ats \
  -r resume.md \
  -j job-description.txt \
  -o ats-compatibility-report.md \
  -v
```

The report will include:
- Overall score and breakdown
- Detailed keyword analysis
- Skills alignment details
- Complete recommendations list

### Example 3: JSON Output for Automation

```bash
npm run dev score-ats \
  -r resume.md \
  -j jd.txt \
  --json > score.json
```

Use JSON output for:
- Tracking scores over time
- Automated workflows
- Integration with other tools

## Tips for Improving ATS Scores

### High-Impact Improvements

1. **Add Missing Keywords**
   - Focus on required skills (high importance)
   - Include exact keyword phrases from JD
   - Use both full terms and abbreviations (e.g., "Kubernetes" and "K8s")

2. **Fix Formatting Issues**
   - Use standard section headers in ALL CAPS
   - Apply bullet points consistently
   - Standardize all dates to YYYY-MM format
   - Remove tables, columns, text boxes

3. **Improve Skills Alignment**
   - Mirror technical skills from JD
   - Add leadership/soft skills examples
   - Include domain-specific terminology

### Best Practices

- **Target Score**: Aim for 85%+ for competitive positions
- **Iterate**: Score → Improve → Re-score until satisfied
- **Context Matters**: A 75% score might be sufficient for some roles
- **Don't Keyword Stuff**: Add keywords naturally in context

## Integration Workflow

Typical workflow using score-ats:

```bash
# 1. Analyze job description
npm run dev analyze-jd https://jobs.company.com/12345

# 2. Parse your resume
npm run dev parse-resume path/to/resume.pdf

# 3. Score ATS compatibility
npm run dev score-ats \
  -r applications/DATE-COMPANY-ROLE/resume.md \
  -j applications/DATE-COMPANY-ROLE/jd-analysis.md \
  -o applications/DATE-COMPANY-ROLE/ats-score.md

# 4. Review recommendations and optimize resume

# 5. Re-score to verify improvements
npm run dev score-ats -r updated-resume.md -j jd.txt
```

## Technical Details

### Algorithm Details

The scorer uses:
- **NLP-based keyword extraction** from job descriptions
- **Frequency analysis** for keyword importance weighting
- **Pattern matching** for date formats and structures
- **Section detection** using case-insensitive regex
- **Weighted scoring** for balanced evaluation

### Limitations

- Cannot parse images or scanned PDFs
- Best with text/markdown resumes
- Requires English language content
- Cannot assess visual design quality

## Troubleshooting

### Common Issues

**"Resume text cannot be empty"**
- Ensure resume file exists and contains text
- Check file path is correct

**"Job description cannot be empty"**
- Verify JD file exists and has content
- Use `analyze-jd` first if fetching from URL

**Low scores despite good resume**
- Check resume uses standard section names
- Ensure keywords from JD are present
- Verify formatting is ATS-friendly

### Getting Help

For issues or questions:
1. Check this documentation
2. Review example outputs
3. Examine recommendations for specific guidance
4. File an issue in the project repository

## Related Commands

- `analyze-jd` - Analyze job description and extract keywords
- `parse-resume` - Convert PDF resume to markdown
- `optimize-resume` - AI-powered resume optimization

---

*Generated by Resume Toolkit v0.1.0*
