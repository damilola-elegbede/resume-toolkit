# Research Company Command

## Overview

The `research-company` command performs comprehensive company research by scraping company websites, aggregating news, and analyzing data to provide interview preparation insights.

## Usage

```bash
# Basic usage with company domain
resume-toolkit research-company example.com

# With company name
resume-toolkit research-company "TechCorp"

# With research depth
resume-toolkit research-company example.com --depth deep

# With role specification
resume-toolkit research-company example.com --role "Software Engineer"

# Quick research (fewer sources)
resume-toolkit research-company startup.io --depth quick
```

## Options

- `<company>` (required): Company name or domain
  - Examples: `google.com`, `Google`, `https://techcorp.com`
  - The tool will attempt to normalize the input to a valid URL

- `--depth, -d <level>`: Research depth level (default: `standard`)
  - `quick`: Fast research with minimal sources (3 news articles)
  - `standard`: Balanced research (5 news articles)
  - `deep`: Comprehensive research (10 news articles)

- `--role, -r <role>`: Role you're applying for
  - Used for folder organization
  - Example: `--role "Senior Frontend Developer"`

## Output

The command generates a comprehensive Markdown report saved to:
```
applications/YYYY-MM-DD-company-role/company-research.md
```

### Report Structure

1. **Overview**: Industry, size, founded, headquarters
2. **Mission & Values**: Company mission extracted from website
3. **Recent News**: Latest news articles (last 6 months)
4. **Green Flags**: Positive indicators (funding, awards, growth)
5. **Red Flags**: Warning signs (layoffs, lawsuits, culture issues)
6. **Culture & Work Environment**: Insights about company culture
7. **Talk Track Ideas**: 5-7 specific talking points for interviews
8. **Questions to Ask**: Smart questions based on research
9. **Next Steps**: Action items for interview preparation

## Features

### Web Scraping
- Scrapes company website using Playwright
- Extracts meta information, content, and structured data
- Respects rate limits (2-5 seconds between requests)
- Handles anti-bot protection gracefully

### News Aggregation
- Fetches recent news from Google News RSS
- Filters for relevance to the company
- Includes source attribution and dates

### Intelligent Analysis
- **Green Flag Detection**:
  - Recent funding rounds
  - Industry awards and recognition
  - Growth indicators (hiring, expansion)
  - Positive culture signals

- **Red Flag Detection**:
  - Layoffs or workforce reductions
  - Legal issues or lawsuits
  - Financial troubles
  - Culture concerns

- **Talking Point Generation**:
  - Generates 5-7 specific, contextual talking points
  - Aligns with recent news and company values
  - Demonstrates genuine research

- **Interview Insights**:
  - Culture analysis
  - Expectation synthesis
  - Smart question generation

## Privacy & Ethics

- Only scrapes publicly available data
- Respects robots.txt (where applicable)
- Implements rate limiting to avoid overload
- No authentication bypass or private data access
- Graceful degradation when sources are unavailable

## Error Handling

The command handles various error scenarios:

- **Invalid URL**: Provides clear error message
- **403 Forbidden**: Suggests alternative research methods
- **404 Not Found**: Indicates website may not exist
- **Timeout**: Adjusts for slow-loading pages
- **Python Errors**: Guides user to install dependencies

## Examples

### Quick Research for Startup
```bash
resume-toolkit research-company startup.io --depth quick --role "Founding Engineer"
```

### Deep Research for FAANG
```bash
resume-toolkit research-company google.com --depth deep --role "Senior SWE"
```

### Standard Research
```bash
resume-toolkit research-company techcorp.com
```

## Technical Details

### Architecture
```
User Input → CompanyResearcher (TS) → Raw Data → CompanyAnalyzer (Python) → Markdown Report
```

### Technology Stack
- **TypeScript**: Web scraping, orchestration
- **Playwright**: Browser automation for website scraping
- **Axios + Cheerio**: News fetching and HTML parsing
- **Python**: Data analysis and insights generation

### Dependencies
- `playwright`: Browser automation
- `axios`: HTTP client
- `cheerio`: HTML parsing
- Python modules: Standard library only

## Testing

The command includes comprehensive test coverage:

- **Unit Tests**: 37+ tests across TypeScript and Python
- **Integration Tests**: Full workflow testing
- **Error Handling**: Edge case coverage
- **Mock Data**: Realistic test scenarios

Run tests:
```bash
# TypeScript tests
npm test -- company-researcher
npm test -- research-company

# Python tests
pytest src/python/tests/test_company_analyzer.py -v
```

## Tips for Best Results

1. **Use Full Domain**: `techcorp.com` works better than just `TechCorp`
2. **Check Output Directory**: Review generated report before interview
3. **Combine with Other Research**: Supplement with Glassdoor, Blind, LinkedIn
4. **Update Before Interview**: Run again closer to interview date for latest news
5. **Customize Talking Points**: Use generated points as inspiration, personalize them

## Known Limitations

- Some websites have anti-bot protection (Cloudflare, etc.)
- News availability varies by company size and media coverage
- Analysis quality depends on public information availability
- Rate limiting may slow down deep research mode

## Troubleshooting

### "403 Forbidden" Error
Some websites block automated access. Try:
- Using a different company URL (careers site, blog)
- Manual research as fallback
- Checking if domain is correct

### "Python analyzer failed"
Ensure Python dependencies are installed:
```bash
pip install -r requirements.txt
```

### No News Articles Found
- Company may have limited media coverage
- Try adjusting company name
- Supplement with manual Googling

## Future Enhancements

Potential improvements for future versions:
- LinkedIn company page integration
- Glassdoor review analysis
- Crunchbase funding data
- GitHub organization activity
- Employee sentiment analysis
- Competitive landscape mapping

## Related Commands

- `analyze-jd`: Analyze job descriptions
- `score-ats`: Score resume against job requirements
- `optimize-resume`: Optimize resume for specific role
- `generate-cover-letter`: Generate personalized cover letter

## Support

For issues or questions:
1. Check error message and suggestions
2. Verify company domain is correct
3. Ensure dependencies are installed
4. Review test suite for examples
