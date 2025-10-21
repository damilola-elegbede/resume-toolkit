# Track Application Command

Manage job application pipeline tracking in Turso database.

## Overview

The `track-application` command provides comprehensive job application tracking capabilities:

- Add new applications to the tracking system
- Update application status as you progress through stages
- List and filter applications
- Add interview notes and details
- Maintain application folder structure with metadata

## Status Workflow

Applications move through the following stages:

```
applied → screening → interviewing → offer
                  ↓           ↓
              rejected    rejected/accepted/withdrawn
```

**Status Values:**
- `applied` - Application submitted, awaiting response
- `screening` - Phone/recruiter screen scheduled or completed
- `interviewing` - In technical/behavioral interview rounds
- `offer` - Offer received
- `rejected` - Application declined at any stage
- `accepted` - Offer accepted
- `withdrawn` - Candidate withdrew application

## Commands

### Add New Application

```bash
# Interactive mode (prompts for all fields)
resume-toolkit track-application add

# CLI arguments mode
resume-toolkit track-application add \
  --company "TechCorp" \
  --position "Director of Engineering" \
  --url "https://jobs.techcorp.com/123" \
  --applied-date "2025-10-21" \
  --status applied \
  --resume-version "tailored-techcorp-director-v1" \
  --cover-letter \
  --notes "Referred by John Smith"
```

**Options:**
- `-c, --company <company>` - Company name (required)
- `-p, --position <position>` - Position/role title (required)
- `-u, --url <url>` - Job posting URL
- `-d, --applied-date <date>` - Applied date in YYYY-MM-DD format (default: today)
- `-s, --status <status>` - Application status (default: applied)
- `-r, --resume-version <version>` - Resume version identifier
- `--cover-letter` - Flag indicating cover letter was used
- `-n, --notes <notes>` - Additional notes

**Creates:**
- Database record in `applications` table
- Application folder: `applications/YYYY-MM-DD-company-position/`
- Metadata file: `applications/YYYY-MM-DD-company-position/metadata.yaml`

### Update Application

```bash
# Update by ID
resume-toolkit track-application update 123 \
  --status interviewing \
  --notes "First round scheduled for next week"

# Update by company name
resume-toolkit track-application update \
  --company "TechCorp" \
  --status offer \
  --followup "2025-10-25" \
  --notes "Received offer, need to respond by Friday"
```

**Arguments:**
- `[id]` - Application ID (optional if --company provided)

**Options:**
- `-c, --company <company>` - Company name (if ID not provided)
- `-s, --status <status>` - New status
- `-n, --notes <notes>` - Update notes
- `-f, --followup <date>` - Next followup date (YYYY-MM-DD)
- `-l, --last-contact <date>` - Last contact date (YYYY-MM-DD)

### List Applications

```bash
# List all applications
resume-toolkit track-application list

# Filter by status
resume-toolkit track-application list --status interviewing

# Filter by company
resume-toolkit track-application list --company "TechCorp"

# Pagination
resume-toolkit track-application list --limit 10 --offset 0
```

**Options:**
- `-s, --status <status>` - Filter by status
- `-c, --company <company>` - Filter by company (partial match)
- `-l, --limit <number>` - Limit results (default: 100)
- `-o, --offset <number>` - Offset results (default: 0)

### Add Interview Notes

```bash
resume-toolkit track-application interview 123 \
  --date "2025-10-25" \
  --type technical \
  --round 1 \
  --notes "System design interview, went well" \
  --interviewer "Jane Smith" \
  --title "Senior Engineering Manager" \
  --duration 60
```

**Arguments:**
- `<id>` - Application ID (required)

**Options:**
- `-d, --date <date>` - Interview date (YYYY-MM-DD, default: today)
- `-t, --type <type>` - Interview type: phone, video, onsite, technical, behavioral, panel, hr (default: phone)
- `-r, --round <number>` - Round number (default: 1)
- `-n, --notes <notes>` - Interview notes
- `-i, --interviewer <name>` - Interviewer name
- `--title <title>` - Interviewer title
- `--duration <minutes>` - Duration in minutes

## Metadata File Format

Each application gets a `metadata.yaml` file:

```yaml
application_id: app-2025-10-21-001
company: TechCorp
position: Director of Engineering
job_url: https://jobs.techcorp.com/123
applied_date: 2025-10-21
status: applied
resume_version: tailored-techcorp-director-v1
cover_letter_used: yes
created_at: 2025-10-21T12:00:00Z
updated_at: 2025-10-21T12:00:00Z
```

## Folder Structure

```
applications/
├── 2025-10-21-techcorp-director-of-engineering/
│   ├── metadata.yaml
│   ├── jd-analysis.md (if analyze-jd was run)
│   ├── resume.pdf
│   └── cover-letter.pdf
├── 2025-10-20-startupco-engineering-manager/
│   ├── metadata.yaml
│   └── ...
```

## Database Schema

### Applications Table

Stores all application records with comprehensive tracking:

- Company, position, job URL
- Application date and status
- Resume version and cover letter flag
- Contact dates and followup reminders
- Notes and additional metadata

### Interviews Table

Stores interview details linked to applications:

- Interview date, time, type, and round
- Interviewer information
- Questions, topics, technical assessments
- Results and feedback
- Personal notes and improvement areas

### Application Stages Table

Maintains status change history (auto-populated by triggers).

## Examples

### Complete Application Workflow

```bash
# 1. Add new application
resume-toolkit track-application add \
  --company "TechCorp" \
  --position "Director of Engineering" \
  --url "https://jobs.techcorp.com/123"

# 2. Update when you get a response
resume-toolkit track-application update 1 \
  --status screening \
  --notes "Recruiter called to schedule phone screen"

# 3. Add phone screen notes
resume-toolkit track-application interview 1 \
  --type phone \
  --round 1 \
  --notes "30min call with recruiter, discussed background"

# 4. Update to interview stage
resume-toolkit track-application update 1 \
  --status interviewing \
  --notes "Moving to technical rounds"

# 5. Add technical interview notes
resume-toolkit track-application interview 1 \
  --type technical \
  --round 2 \
  --notes "System design: design a distributed cache" \
  --interviewer "Jane Smith" \
  --duration 60

# 6. Update when offer received
resume-toolkit track-application update 1 \
  --status offer \
  --notes "Received verbal offer, awaiting written details"

# 7. List all active applications
resume-toolkit track-application list --status interviewing
```

### Batch Operations

```bash
# List all applications with interviews
resume-toolkit track-application list --status interviewing

# List all rejected applications (for analysis)
resume-toolkit track-application list --status rejected

# Find specific company applications
resume-toolkit track-application list --company "Tech"
```

## Integration with Other Commands

The track-application command integrates with the full toolkit workflow:

1. **analyze-jd** - Analyze job description and save to application folder
2. **optimize-resume** - Create tailored resume for application
3. **generate-cover-letter** - Generate cover letter for application
4. **track-application add** - Add to tracking system with metadata
5. **track-application update** - Track progress through pipeline

## Tips

1. **Consistent Resume Versioning**: Use descriptive version names like `tailored-techcorp-director-v1` to track which resume was used.

2. **Regular Updates**: Update status promptly to maintain accurate pipeline metrics.

3. **Detailed Notes**: Add context to notes - who referred you, key discussion points, salary discussions, etc.

4. **Followup Reminders**: Set `--followup` dates to track when to reach out.

5. **Interview Preparation**: Review interview notes from previous rounds before next interview.

6. **Analytics**: Use `list` with filters to analyze your pipeline and success patterns.

## Error Handling

The command validates:
- Required fields (company, position, date)
- Date format (YYYY-MM-DD)
- Valid status transitions
- Valid interview types
- Database connectivity

Common errors:
```bash
# Missing required fields
Error: Missing required fields: company, position, and appliedDate are required

# Invalid date format
Error: Invalid date format. Use YYYY-MM-DD format

# Database connection issues
Error: Database URL not provided. Set TURSO_DATABASE_URL environment variable
```

## Environment Setup

Ensure Turso credentials are configured:

```bash
# .env file
TURSO_DATABASE_URL=libsql://your-database.turso.io
TURSO_AUTH_TOKEN=your-auth-token
```

See `.env.example` for complete configuration.
