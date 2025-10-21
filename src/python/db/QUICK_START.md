# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies

**Python:**
```bash
pip install libsql-client pydantic
```

**TypeScript:**
```bash
npm install @libsql/client zod
```

### 2. Create Turso Database

```bash
# Install Turso CLI (if not already installed)
curl -sSfL https://get.tur.so/install.sh | bash

# Create database
turso db create resume-tracker

# Get connection details
turso db show resume-tracker

# Create auth token
turso db tokens create resume-tracker
```

### 3. Configure Environment

```bash
# Copy example file
cp .env.example .env

# Edit .env with your values
# TURSO_DATABASE_URL=libsql://resume-tracker-yourorg.turso.io
# TURSO_AUTH_TOKEN=eyJhbGc...
```

### 4. Initialize Database

```bash
turso db shell resume-tracker < src/python/db/migrations/001_initial_schema.sql
```

### 5. Verify Setup

```bash
turso db shell resume-tracker "SELECT COUNT(*) as table_count FROM sqlite_master WHERE type='table'"
```

Expected output: 5 tables

## Common Operations

### Python Examples

#### Track a Job Application

```python
import asyncio
from src.python.db.client import TursoClient
from src.python.db.models import ApplicationCreate, ApplicationStatus

async def track_application():
    async with TursoClient() as client:
        # Create application
        app = await client.create_application(
            ApplicationCreate(
                company="Google",
                position="Senior Software Engineer",
                applied_date="2025-10-21",
                job_url="https://careers.google.com/jobs/123",
                location="Mountain View, CA",
                salary_range="$180k - $250k",
                source="LinkedIn",
                keywords_targeted='["Python", "Kubernetes", "Distributed Systems"]',
                cover_letter_used=True
            )
        )
        print(f"Application created with ID: {app.id}")
        return app

asyncio.run(track_application())
```

#### Add Interview

```python
from src.python.db.models import InterviewCreate, InterviewType

async def add_interview(application_id: int):
    async with TursoClient() as client:
        interview = await client.create_interview(
            InterviewCreate(
                application_id=application_id,
                interview_date="2025-10-28",
                interview_time="14:00",
                interview_type=InterviewType.TECHNICAL,
                round_number=1,
                interviewer_name="Jane Smith",
                interviewer_title="Engineering Manager",
                duration_minutes=60,
                meeting_link="https://meet.google.com/abc-defg-hij",
                topics_covered="System design, algorithms, culture fit",
                personal_notes="Went well, asked about scale and distributed systems"
            )
        )
        print(f"Interview scheduled: {interview.interview_date}")
```

#### Update Status

```python
from src.python.db.models import ApplicationUpdate

async def update_status(application_id: int):
    async with TursoClient() as client:
        updated = await client.update_application(
            application_id,
            ApplicationUpdate(
                status=ApplicationStatus.OFFER,
                notes="Received offer! Base: $200k, equity: 100k RSUs"
            )
        )
        print(f"Status updated to: {updated.status}")
```

#### View Dashboard

```python
async def view_dashboard():
    async with TursoClient() as client:
        # Pipeline summary
        print("\n=== Pipeline Summary ===")
        pipeline = await client.get_pipeline_summary()
        for item in pipeline:
            print(f"{item.status:15} {item.count:3} ({item.percentage:5.1f}%)")

        # Active applications
        print("\n=== Active Applications ===")
        active = await client.get_active_applications(limit=5)
        for app in active:
            print(f"{app.company:20} {app.position:30} ({app.interview_count} interviews)")

        # Top keywords
        print("\n=== Top Keywords ===")
        keywords = await client.get_top_keywords(limit=10)
        for kw in keywords:
            print(f"{kw.keyword:20} {kw.response_rate:5.1f}% response rate")
```

### TypeScript Examples

#### Track a Job Application

```typescript
import { TursoClient } from './src/cli/db/client';
import { ApplicationStatus } from './src/cli/db/types';

async function trackApplication() {
  const client = new TursoClient();

  try {
    const app = await client.createApplication({
      company: 'Google',
      position: 'Senior Software Engineer',
      applied_date: '2025-10-21',
      job_url: 'https://careers.google.com/jobs/123',
      location: 'Mountain View, CA',
      salary_range: '$180k - $250k',
      source: 'LinkedIn',
      keywords_targeted: JSON.stringify(['TypeScript', 'React', 'Node.js']),
      status: ApplicationStatus.APPLIED,
      cover_letter_used: true,
    });

    console.log(`Application created with ID: ${app.id}`);
    return app;
  } finally {
    await client.close();
  }
}
```

#### Add Interview

```typescript
import { InterviewType } from './src/cli/db/types';

async function addInterview(applicationId: number) {
  const client = new TursoClient();

  try {
    const interview = await client.createInterview({
      application_id: applicationId,
      interview_date: '2025-10-28',
      interview_time: '14:00',
      interview_type: InterviewType.TECHNICAL,
      round_number: 1,
      interviewer_name: 'Jane Smith',
      interviewer_title: 'Engineering Manager',
      duration_minutes: 60,
      meeting_link: 'https://meet.google.com/abc-defg-hij',
      topics_covered: 'System design, algorithms, culture fit',
      personal_notes: 'Went well, asked about scale and distributed systems',
    });

    console.log(`Interview scheduled: ${interview.interview_date}`);
  } finally {
    await client.close();
  }
}
```

#### View Dashboard

```typescript
async function viewDashboard() {
  const client = new TursoClient();

  try {
    // Pipeline summary
    console.log('\n=== Pipeline Summary ===');
    const pipeline = await client.getPipelineSummary();
    pipeline.forEach(item => {
      console.log(`${item.status.padEnd(15)} ${item.count.toString().padStart(3)} (${item.percentage.toFixed(1).padStart(5)}%)`);
    });

    // Active applications
    console.log('\n=== Active Applications ===');
    const active = await client.getActiveApplications(5);
    active.forEach(app => {
      console.log(`${app.company.padEnd(20)} ${app.position.padEnd(30)} (${app.interview_count} interviews)`);
    });

    // Top keywords
    console.log('\n=== Top Keywords ===');
    const keywords = await client.getTopKeywords(10);
    keywords.forEach(kw => {
      console.log(`${kw.keyword.padEnd(20)} ${kw.response_rate.toFixed(1).padStart(5)}% response rate`);
    });
  } finally {
    await client.close();
  }
}
```

## Useful Queries

### Get Applications Needing Follow-up

```python
async def get_followups():
    async with TursoClient() as client:
        from datetime import date
        today = str(date.today())

        result = await client.execute(
            "SELECT * FROM applications WHERE next_followup_date <= ? AND status NOT IN ('rejected', 'withdrawn', 'accepted')",
            [today]
        )
        # Parse results...
```

### Get Interview Success Rate

```python
async def interview_success_rate():
    async with TursoClient() as client:
        result = await client.execute("""
            SELECT
                COUNT(DISTINCT CASE WHEN status IN ('offer', 'accepted') THEN id END) * 100.0 / COUNT(DISTINCT id) as success_rate
            FROM applications
            WHERE id IN (SELECT DISTINCT application_id FROM interviews)
        """)
        # Parse results...
```

### Get Average Time to Offer

```python
async def avg_time_to_offer():
    async with TursoClient() as client:
        result = await client.execute("""
            SELECT
                AVG(julianday(
                    (SELECT stage_date FROM application_stages WHERE application_id = a.id AND status = 'offer' LIMIT 1)
                ) - julianday(applied_date)) as avg_days
            FROM applications a
            WHERE status IN ('offer', 'accepted')
        """)
        # Parse results...
```

## CLI Integration Ideas

### Example CLI Commands

```bash
# Add application
resume-tracker apply \
  --company "Google" \
  --position "Senior Engineer" \
  --url "https://..." \
  --keywords "Python,Kubernetes,AWS"

# List applications
resume-tracker list \
  --status interviewing \
  --limit 10

# Add interview
resume-tracker interview add \
  --app-id 123 \
  --date 2025-10-28 \
  --type technical \
  --interviewer "Jane Smith"

# Update status
resume-tracker status \
  --app-id 123 \
  --status offer

# View dashboard
resume-tracker dashboard

# Show metrics
resume-tracker metrics \
  --from 2025-10-01 \
  --to 2025-10-31
```

## Troubleshooting

### Connection Issues

```python
# Test connection
async def test_connection():
    try:
        async with TursoClient() as client:
            result = await client.execute("SELECT 1")
            print("Connection successful!")
    except Exception as e:
        print(f"Connection failed: {e}")
```

### Validation Errors

```python
# Handle validation errors
from pydantic import ValidationError

try:
    app = ApplicationCreate(
        company="Test",
        position="Engineer",
        applied_date="invalid-date"  # Wrong format!
    )
except ValidationError as e:
    print(f"Validation error: {e}")
    # Fix: Use YYYY-MM-DD format
```

### Query Debugging

```python
# Enable query logging
async def debug_query():
    async with TursoClient() as client:
        # Use execute for raw queries
        result = await client.execute(
            "EXPLAIN QUERY PLAN SELECT * FROM applications WHERE status = ?",
            ["applied"]
        )
        print(result)
```

## Best Practices

1. **Always use context managers** (`async with`) for automatic cleanup
2. **Validate dates** before passing to database (YYYY-MM-DD)
3. **Use enums** instead of string literals for status/type fields
4. **Limit queries** to prevent loading too much data
5. **Batch operations** when inserting multiple records
6. **Update metrics regularly** for accurate dashboard data
7. **Track keywords** on every application for optimization insights
8. **Use views** for complex queries instead of raw SQL

## Next Steps

1. **Build CLI**: Create command-line interface using client
2. **Add Dashboard**: Web dashboard with charts and graphs
3. **Email Integration**: Auto-track applications from email
4. **Calendar Sync**: Sync interviews to calendar
5. **Analytics**: Build reports and insights
6. **Automation**: Auto-follow-up reminders
7. **Export**: Export data to CSV/PDF for reports

## Resources

- **README**: Full documentation in `/src/python/db/README.md`
- **Schema Design**: Detailed design doc in `/src/python/db/SCHEMA_DESIGN.md`
- **Turso Docs**: https://docs.turso.tech/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **Zod Docs**: https://zod.dev/
