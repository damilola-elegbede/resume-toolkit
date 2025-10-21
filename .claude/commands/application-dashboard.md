# Application Dashboard Command

Generate comprehensive analytics dashboards for job application tracking, including pipeline metrics, success rates, and keyword performance analysis.

## Usage

```bash
# Generate dashboard for all applications
resume-toolkit application-dashboard

# Filter by date range
resume-toolkit application-dashboard --filter "last 3 months"
resume-toolkit application-dashboard --filter "last 30 days"
resume-toolkit application-dashboard --filter "this year"

# Custom date range
resume-toolkit application-dashboard --filter "2025-01-01:2025-03-31"

# Export to file
resume-toolkit application-dashboard --export dashboard.md
resume-toolkit application-dashboard --export dashboard.json

# Verbose output
resume-toolkit application-dashboard --verbose
```

## What It Shows

### Pipeline Funnel
- **Total Applications**: Overall count
- **Applied**: Applications in initial state
- **Screening**: Under company review
- **Interviewing**: Active interview process
- **Offer**: Offer received
- **Rejected**: Unfortunately declined

Visualized as ASCII bars showing counts and percentages.

### Success Metrics
- **Response Rate**: % of applications that got responses (moved beyond "applied")
- **Interview Rate**: % that reached interview stage
- **Offer Rate**: % that resulted in offers

Each metric includes benchmark comparison:
- ✓ Above average (>10% above benchmark)
- → Average (within 10% of benchmark)
- ✗ Below average (>10% below benchmark)

**Industry Benchmarks**:
- Response Rate: 50%
- Interview Rate: 15%
- Offer Rate: 5%

### Time Analysis
- **Avg time to response**: Days from application to first company response
- **Avg time to interview**: Days from application to first interview
- **Avg time to offer**: Days from application to offer received

Helps you understand typical timelines and when to follow up.

### Keyword Performance
Top keywords ranked by response rate, showing:
- Keyword name
- Response rate percentage
- Usage count (responses/total uses)

Identifies which skills and terms resonate best with employers.

### Recommendations
Actionable insights based on your data:
- High-performing keywords to emphasize
- Conversion strengths and weaknesses
- Follow-up timing suggestions
- Strategic focus areas

## Examples

### Example Output

```
Application Pipeline Dashboard
============================================================

Pipeline:
Total Applications: 42
  Applied         ████████████████ 15 (36%)
  Screening       █████████████ 12 (29%)
  Interview       ███████████ 10 (24%)
  Offer           ███ 3 (7%)
  Rejected        ██ 2 (5%)

Success Metrics:
  Response Rate:  64%  ✓ Above (50%)
  Interview Rate: 24%  ✓ Strong (15%)
  Offer Rate:      7%  → Average (5%)

Time Analysis:
  Avg time to response:  5.2 days
  Avg time to interview: 18.4 days
  Avg time to offer:     28.5 days

Top Keywords (by response rate):
  1. distributed systems - 85% (12/15)
  2. team leadership     - 80% (9/12)
  3. kubernetes          - 75% (14/20)
  4. python              - 65% (18/25)
  5. microservices       - 60% (10/18)

Recommendations:
  → Emphasize 'distributed systems' in future applications - 85% response rate
  → Your interview conversion is strong - focus on getting more interviews
  → Consider following up after 7 days if no response
```

### JSON Export

When exported to JSON, the dashboard includes structured data:

```json
{
  "funnel": {
    "total": 42,
    "applied": 15,
    "screening": 12,
    "interviewing": 10,
    "offer": 3,
    "rejected": 2
  },
  "metrics": {
    "responseRate": 64.0,
    "interviewRate": 24.0,
    "offerRate": 7.0
  },
  "timeMetrics": {
    "avgResponseTimeDays": 5.2,
    "avgTimeToInterviewDays": 18.4,
    "avgTimeToOfferDays": 28.5
  },
  "keywords": [
    {
      "keyword": "distributed systems",
      "response_rate": 85.0,
      "total_uses": 15,
      "response_count": 12
    }
  ],
  "recommendations": [
    "Emphasize 'distributed systems' in future applications - 85% response rate"
  ]
}
```

## Interpreting Your Dashboard

### Pipeline Health
- **High % in "Applied"**: May need to follow up or improve application quality
- **Low % in "Screening"**: Could indicate ATS filtering issues - review keywords
- **High "Interview" → "Offer" conversion**: Strong interviewing skills
- **Low "Screening" → "Interview"**: May need better phone screen preparation

### Response Rate Analysis
- **Below 40%**: Review resume keywords, formatting, and targeting
- **40-60%**: Solid, but room for improvement
- **Above 60%**: Excellent - you're getting through ATS and initial screening

### Interview Rate Significance
- **Below 10%**: Focus on screening calls and initial conversations
- **10-20%**: Good, average performance
- **Above 20%**: Strong conversion - companies are impressed

### Keyword Insights
- **High response rate (>70%)**: Emphasize these in your resume and applications
- **Medium response rate (40-70%)**: Include but don't over-emphasize
- **Low response rate (<40%)**: Consider if these are relevant or if you're targeting wrong roles

### Time Patterns
- **Quick responses (< 5 days)**: Company is actively hiring, high priority
- **Slow responses (> 14 days)**: May be on back burner, consider following up
- **Long interview process (> 30 days)**: Typical for senior roles and large companies

## Integration with Other Commands

The dashboard pulls data from applications tracked with:

```bash
# Track applications
resume-toolkit track-application --company "Tech Corp" --position "Senior Engineer"

# Update status
resume-toolkit update-application 1 --status "screening"
resume-toolkit update-application 1 --status "interviewing"
resume-toolkit update-application 1 --status "offer"
```

Keywords are automatically tracked when you use:

```bash
# Optimize resume (tracks keywords used)
resume-toolkit optimize-resume -r resume.md -j job-description.txt

# Score ATS (analyzes keyword matches)
resume-toolkit score-ats -r resume.md -j job-description.txt
```

## Tips for Better Analytics

1. **Consistent Tracking**: Update application statuses promptly for accurate metrics
2. **Tag Keywords**: Include `keywords_targeted` when tracking applications
3. **Regular Reviews**: Generate dashboard weekly to spot trends
4. **Compare Periods**: Use filters to compare performance over time
5. **Act on Recommendations**: Adjust strategy based on what's working

## Troubleshooting

### "No applications found"
- Ensure you've tracked applications: `resume-toolkit track-application`
- Check database connection (TURSO_DATABASE_URL, TURSO_AUTH_TOKEN)

### Empty keyword data
- Keywords are populated when you use optimize-resume or score-ats commands
- Manually add keywords when tracking: `--keywords '["python", "kubernetes"]'`

### Inaccurate time metrics
- Time metrics require stage history tracking
- Ensure you're updating application status, not just final status

## Related Commands

- `track-application` - Add new applications to tracking
- `update-application` - Update application status
- `list-applications` - View all tracked applications
- `score-ats` - Analyze keyword matching
- `optimize-resume` - Get keyword recommendations
