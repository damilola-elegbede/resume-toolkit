# Job Application Tracking Database

Comprehensive database schema and client libraries for tracking job applications, interviews, and performance metrics using Turso (distributed SQLite/libSQL).

## Table of Contents

- [Overview](#overview)
- [Schema Design](#schema-design)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Python Client Usage](#python-client-usage)
- [TypeScript Client Usage](#typescript-client-usage)
- [Database Schema](#database-schema)
- [Design Decisions](#design-decisions)
- [Performance Optimizations](#performance-optimizations)
- [Migration Guide](#migration-guide)

## Overview

This database system provides a complete solution for tracking job applications throughout the entire application lifecycle, from initial submission through interviews to final outcomes. It includes:

- **Applications**: Core job application tracking
- **Interviews**: Detailed interview round tracking
- **Application Stages**: Complete audit trail of status changes
- **Metrics**: Aggregated performance analytics
- **Keyword Performance**: Resume keyword effectiveness tracking

## Schema Design

### Tables

#### 1. `applications`
Central table tracking all job applications with:
- Company and position information
- Application dates and status tracking
- Resume customization metadata
- Follow-up scheduling
- Document references

**Key Features:**
- Status workflow: applied → screening → interviewing → offer/rejected/withdrawn
- Automatic status change tracking via triggers
- Support for multiple employment types

#### 2. `interviews`
Detailed interview round tracking including:
- Interview scheduling (date, time, timezone)
- Interview type classification (phone, video, technical, etc.)
- Interviewer information
- Questions and assessment details
- Results and feedback

**Key Features:**
- Multi-round interview support
- Panel interview tracking
- Automatic last_contact_date updates

#### 3. `application_stages`
Complete audit trail of all status changes:
- Historical status tracking
- Change timestamps
- Notes for each transition
- System vs. manual change tracking

**Key Features:**
- Automatically populated via triggers
- Complete change history
- Useful for timeline visualizations

#### 4. `metrics`
Daily aggregated metrics for dashboard analytics:
- Application volume tracking
- Response and interview rates
- Time-to-event metrics (response, interview, offer)
- Active pipeline tracking

**Key Features:**
- Daily rollup calculations
- Percentage-based metrics
- Time-series analytics ready

#### 5. `keyword_performance`
Resume keyword effectiveness tracking:
- Usage counts across applications
- Response, interview, and offer rates per keyword
- Category classification
- Historical performance

**Key Features:**
- Keyword optimization insights
- Category-based analysis
- ROI tracking for resume customization

### Views

Pre-built views for common queries:

- **`v_active_applications`**: Active applications with interview counts
- **`v_pipeline_summary`**: Current pipeline status distribution
- **`v_interview_performance`**: Interview conversion rates by company
- **`v_top_keywords`**: Highest performing keywords

### Indexes

Optimized indexes for common query patterns:
- Status and date filtering
- Company searches
- Interview lookups
- Follow-up scheduling
- Keyword analysis

### Triggers

Automatic data maintenance:
- Timestamp updates on all tables
- Status change audit trail
- Last contact date synchronization

## Installation

### Python Setup

```bash
# Install required packages
pip install libsql-client pydantic

# Set environment variables
export TURSO_DATABASE_URL="libsql://your-database.turso.io"
export TURSO_AUTH_TOKEN="your-auth-token"
```

### TypeScript Setup

```bash
# Install required packages
npm install @libsql/client zod

# Set environment variables (or use .env file)
export TURSO_DATABASE_URL="libsql://your-database.turso.io"
export TURSO_AUTH_TOKEN="your-auth-token"
```

### Database Initialization

```bash
# Apply schema using Turso CLI
turso db shell your-database < src/python/db/migrations/001_initial_schema.sql

# Or using the schema file directly
turso db shell your-database < src/python/db/schema.sql
```

## Quick Start

### Python Example

```python
import asyncio
from datetime import date
from src.python.db.client import TursoClient
from src.python.db.models import ApplicationCreate, ApplicationStatus

async def main():
    # Initialize client
    async with TursoClient() as client:
        # Create an application
        app = await client.create_application(
            ApplicationCreate(
                company="Tech Corp",
                position="Senior Software Engineer",
                applied_date=str(date.today()),
                job_url="https://example.com/job/123",
                location="San Francisco, CA",
                salary_range="$150k - $200k",
                keywords_targeted='["Python", "AWS", "Kubernetes"]',
                status=ApplicationStatus.APPLIED
            )
        )
        print(f"Created application: {app.id}")

        # Get active applications
        active = await client.get_active_applications(limit=10)
        for app in active:
            print(f"{app.company} - {app.position}: {app.interview_count} interviews")

        # Update application status
        updated = await client.update_application(
            app.id,
            ApplicationUpdate(status=ApplicationStatus.SCREENING)
        )
        print(f"Updated status to: {updated.status}")

        # Get pipeline summary
        summary = await client.get_pipeline_summary()
        for item in summary:
            print(f"{item.status}: {item.count} ({item.percentage:.1f}%)")

asyncio.run(main())
```

### TypeScript Example

```typescript
import { TursoClient } from './src/cli/db/client';
import { ApplicationStatus, EmploymentType } from './src/cli/db/types';

async function main() {
  const client = new TursoClient();

  try {
    // Create an application
    const app = await client.createApplication({
      company: 'Tech Corp',
      position: 'Senior Software Engineer',
      applied_date: new Date().toISOString().split('T')[0],
      job_url: 'https://example.com/job/123',
      location: 'San Francisco, CA',
      salary_range: '$150k - $200k',
      employment_type: EmploymentType.FULL_TIME,
      keywords_targeted: JSON.stringify(['TypeScript', 'React', 'Node.js']),
      status: ApplicationStatus.APPLIED,
      cover_letter_used: true,
    });

    console.log(`Created application: ${app.id}`);

    // Get active applications
    const active = await client.getActiveApplications(10);
    active.forEach(app => {
      console.log(`${app.company} - ${app.position}: ${app.interview_count} interviews`);
    });

    // Update application
    const updated = await client.updateApplication(app.id, {
      status: ApplicationStatus.SCREENING,
    });
    console.log(`Updated status to: ${updated?.status}`);

    // Get pipeline summary
    const summary = await client.getPipelineSummary();
    summary.forEach(item => {
      console.log(`${item.status}: ${item.count} (${item.percentage.toFixed(1)}%)`);
    });
  } finally {
    await client.close();
  }
}

main();
```

## Python Client Usage

### Creating Records

```python
from src.python.db.client import TursoClient
from src.python.db.models import (
    ApplicationCreate, InterviewCreate, InterviewType
)

async with TursoClient() as client:
    # Create application
    app = await client.create_application(
        ApplicationCreate(
            company="Google",
            position="Senior Backend Engineer",
            applied_date="2025-10-21",
            source="LinkedIn"
        )
    )

    # Create interview
    interview = await client.create_interview(
        InterviewCreate(
            application_id=app.id,
            interview_date="2025-10-28",
            interview_time="14:00",
            interview_type=InterviewType.TECHNICAL,
            interviewer_name="John Doe",
            meeting_link="https://meet.google.com/xyz"
        )
    )
```

### Querying Records

```python
# Get applications with filters
apps = await client.get_applications(
    status="interviewing",
    company="Google",
    limit=50,
    order_by="applied_date DESC"
)

# Get specific application
app = await client.get_application(application_id=123)

# Get interviews for application
interviews = await client.get_interviews(application_id=app.id)

# Get application history
stages = await client.get_application_stages(application_id=app.id)
```

### Updating Records

```python
from src.python.db.models import ApplicationUpdate, ApplicationStatus

# Update application
updated = await client.update_application(
    application_id=123,
    update=ApplicationUpdate(
        status=ApplicationStatus.OFFER,
        notes="Received verbal offer, awaiting written confirmation"
    )
)
```

### Analytics Queries

```python
# Get metrics
metrics = await client.get_metrics(
    start_date="2025-10-01",
    end_date="2025-10-31",
    limit=31
)

# Get top keywords
keywords = await client.get_top_keywords(limit=20)
for kw in keywords:
    print(f"{kw.keyword}: {kw.response_rate}% response rate")

# Get interview performance
perf = await client.get_interview_performance()
for company in perf:
    print(f"{company.company}: {company.interviews_per_application:.2f} interviews/app")
```

## TypeScript Client Usage

### Creating Records

```typescript
import { TursoClient } from './src/cli/db/client';
import { InterviewType } from './src/cli/db/types';

const client = new TursoClient();

// Create application
const app = await client.createApplication({
  company: 'Google',
  position: 'Senior Backend Engineer',
  applied_date: '2025-10-21',
  source: 'LinkedIn',
});

// Create interview
const interview = await client.createInterview({
  application_id: app.id,
  interview_date: '2025-10-28',
  interview_time: '14:00',
  interview_type: InterviewType.TECHNICAL,
  interviewer_name: 'John Doe',
  meeting_link: 'https://meet.google.com/xyz',
});
```

### Querying Records

```typescript
// Get applications with filters
const apps = await client.getApplications({
  status: 'interviewing',
  company: 'Google',
  limit: 50,
  orderBy: 'applied_date DESC',
});

// Get specific application
const app = await client.getApplication(123);

// Get interviews
const interviews = await client.getInterviews(app?.id);

// Get application history
const stages = await client.getApplicationStages(app?.id ?? 0);
```

### Analytics Queries

```typescript
// Get metrics
const metrics = await client.getMetrics({
  startDate: '2025-10-01',
  endDate: '2025-10-31',
  limit: 31,
});

// Get top keywords
const keywords = await client.getTopKeywords(20);
keywords.forEach(kw => {
  console.log(`${kw.keyword}: ${kw.response_rate}% response rate`);
});

// Get interview performance
const perf = await client.getInterviewPerformance();
perf.forEach(company => {
  console.log(`${company.company}: ${company.interviews_per_application.toFixed(2)} interviews/app`);
});
```

## Database Schema

### ERD (Entity Relationship Diagram)

```
┌─────────────────┐       ┌─────────────────┐
│  applications   │──────<│   interviews    │
│                 │       │                 │
│ PK: id          │       │ PK: id          │
│    company      │       │ FK: application │
│    position     │       │    interview_   │
│    status       │       │    date         │
│    applied_date │       │    type         │
└────────┬────────┘       └─────────────────┘
         │
         │
         v
┌─────────────────┐
│ application_    │
│    stages       │
│                 │
│ PK: id          │
│ FK: application │
│    status       │
│    stage_date   │
└─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│    metrics      │       │   keyword_      │
│                 │       │   performance   │
│ PK: id          │       │                 │
│ UQ: metric_date │       │ PK: id          │
│    total_apps   │       │ UQ: keyword     │
│    response_    │       │    response_    │
│    rate         │       │    rate         │
└─────────────────┘       └─────────────────┘
```

### Status Workflow

```
applied ──────> screening ──────> interviewing ──────> offer
   │               │                   │                  │
   │               │                   │                  v
   │               │                   │              accepted
   │               │                   │
   v               v                   v
rejected       rejected             rejected
   │               │                   │
   v               v                   v
withdrawn      withdrawn           withdrawn
```

## Design Decisions

### 1. **SQLite/libSQL Choice**
- **Rationale**: Turso provides distributed SQLite with edge replication
- **Benefits**: Simple schema, ACID compliance, great performance
- **Trade-offs**: Limited concurrent writes (acceptable for this use case)

### 2. **Text-based Dates (ISO 8601)**
- **Rationale**: SQLite date functions work well with ISO 8601 strings
- **Format**: YYYY-MM-DD for consistency
- **Benefits**: Timezone-agnostic, sortable, human-readable

### 3. **Status Enum via CHECK Constraints**
- **Rationale**: Enforce valid status values at database level
- **Benefits**: Data integrity, no invalid states
- **Alternative**: Could use lookup tables, but overkill for this use case

### 4. **JSON Strings for Arrays**
- **Rationale**: SQLite JSON functions support querying
- **Use cases**: keywords_targeted, questions_asked, topics_covered
- **Benefits**: Flexible storage, queryable via JSON functions

### 5. **Audit Trail via Triggers**
- **Rationale**: Automatic status history without application logic
- **Benefits**: Never miss a state transition, complete timeline
- **Implementation**: application_stages table populated automatically

### 6. **Computed Metrics Table**
- **Rationale**: Pre-calculate expensive aggregations
- **Benefits**: Fast dashboard queries, historical trends
- **Update Strategy**: Daily batch job or real-time updates

### 7. **Denormalized Views**
- **Rationale**: Common queries pre-optimized
- **Benefits**: Cleaner application code, consistent results
- **Examples**: v_active_applications, v_pipeline_summary

### 8. **Partial Indexes**
- **Rationale**: Index only relevant rows (WHERE clause)
- **Benefits**: Smaller indexes, faster writes
- **Example**: `idx_applications_next_followup` only indexes non-null dates

## Performance Optimizations

### Indexing Strategy

1. **Covering Indexes**: Most queries use indexed columns
2. **Composite Indexes**: Common filter combinations (status + date)
3. **Partial Indexes**: Only index relevant rows
4. **Filtered Indexes**: Skip NULL values where appropriate

### Query Patterns

1. **Limit All Queries**: Default limits prevent runaway queries
2. **Pagination Support**: Offset/limit for large result sets
3. **View Materialization**: Pre-compute complex aggregations
4. **Selective Columns**: Only SELECT needed columns

### Write Optimization

1. **Bulk Inserts**: Use transactions for multiple inserts
2. **Batch Updates**: Update metrics in batches
3. **Trigger Efficiency**: Minimal logic in triggers
4. **Index Maintenance**: Triggers don't create excessive index updates

### Expected Performance

- **Simple Queries**: < 10ms (indexed lookups)
- **Aggregations**: < 50ms (with indexes)
- **Complex Reports**: < 200ms (using views)
- **Writes**: < 5ms (with triggers)

## Migration Guide

### Creating Migrations

```bash
# Create new migration file
touch src/python/db/migrations/002_add_salary_tracking.sql
```

```sql
-- Migration: 002_add_salary_tracking
-- Description: Add salary negotiation tracking
-- Created: 2025-10-22

ALTER TABLE applications ADD COLUMN salary_offered TEXT;
ALTER TABLE applications ADD COLUMN salary_negotiated TEXT;

CREATE INDEX idx_applications_salary ON applications(salary_offered)
  WHERE salary_offered IS NOT NULL;
```

### Applying Migrations

```bash
# Using Turso CLI
turso db shell your-database < src/python/db/migrations/002_add_salary_tracking.sql

# Verify migration
turso db shell your-database "SELECT sql FROM sqlite_master WHERE name='applications'"
```

### Rollback Strategy

Create corresponding rollback files:

```sql
-- Rollback: 002_add_salary_tracking
-- Reverts: 002_add_salary_tracking.sql

DROP INDEX IF EXISTS idx_applications_salary;

-- Note: SQLite doesn't support DROP COLUMN directly
-- Options:
-- 1. Leave columns (recommended for SQLite)
-- 2. Create new table without columns and migrate data
-- 3. Use ALTER TABLE RENAME in newer SQLite versions
```

## Environment Variables

Required environment variables:

```bash
# Turso Database Configuration
TURSO_DATABASE_URL=libsql://your-database-name.turso.io
TURSO_AUTH_TOKEN=eyJhbGc...your-token-here

# Optional: Connection Configuration
TURSO_SYNC_URL=       # For embedded replicas
TURSO_SYNC_INTERVAL=  # Sync interval in seconds
```

## Best Practices

### 1. Use Type-Safe Models
Always use Pydantic (Python) or Zod (TypeScript) schemas for validation.

### 2. Handle Dates Consistently
Use ISO 8601 format (YYYY-MM-DD) for all dates.

### 3. Leverage Views
Use pre-built views for complex queries instead of recreating logic.

### 4. Batch Operations
Group related operations in transactions for consistency.

### 5. Monitor Metrics
Regularly update the metrics table for dashboard analytics.

### 6. Track Keywords
Update keyword_performance after each application for insights.

### 7. Use Filters
Always specify filters and limits to prevent expensive queries.

### 8. Close Connections
Always close database connections (use context managers).

## Troubleshooting

### Common Issues

**Issue**: "Database URL not provided"
```bash
# Solution: Set environment variable
export TURSO_DATABASE_URL="libsql://your-database.turso.io"
```

**Issue**: "Auth token not provided"
```bash
# Solution: Set auth token
export TURSO_AUTH_TOKEN="your-token"
```

**Issue**: "Validation error on date field"
```python
# Solution: Use ISO 8601 format
applied_date="2025-10-21"  # Correct
applied_date="10/21/2025"  # Wrong
```

**Issue**: "Foreign key constraint failed"
```python
# Solution: Ensure parent record exists
app = await client.get_application(application_id)
if app:
    interview = await client.create_interview(...)
```

## Support and Contributing

For issues or questions:
1. Check the troubleshooting section above
2. Review the schema documentation
3. Examine the client code examples
4. Check Turso documentation: https://docs.turso.tech/

## License

This database schema and client libraries are part of the resume-toolkit project.
