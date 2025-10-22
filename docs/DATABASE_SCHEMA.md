# Database Schema

Complete database schema documentation for Resume Toolkit.

## Tables Overview

**Core Tables**:

- **resumes**: Parsed resume data and versions
- **jobs**: Job descriptions and requirements
- **applications**: Application tracking and status
- **cover_letters**: Generated cover letters
- **companies**: Company research and intelligence
- **analytics**: Performance metrics and insights

## Schema Definitions

### resumes

Stores parsed resume data with version control.

```sql
CREATE TABLE resumes (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  filename TEXT NOT NULL,
  parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  -- Contact Information
  full_name TEXT,
  email TEXT,
  phone TEXT,
  linkedin_url TEXT,
  github_url TEXT,
  portfolio_url TEXT,
  location TEXT,

  -- Structured Data
  summary TEXT,
  skills JSON,              -- ["JavaScript", "Python", ...]
  experiences JSON,         -- [{ company, title, dates, bullets }, ...]
  education JSON,           -- [{ school, degree, dates }, ...]
  certifications JSON,      -- [{ name, issuer, date }, ...]
  projects JSON,            -- [{ name, description, tech }, ...]

  -- Metadata
  total_experience_years INTEGER,
  file_path TEXT,
  file_hash TEXT,
  is_base_resume BOOLEAN DEFAULT false,

  -- Version Control
  version INTEGER DEFAULT 1,
  parent_resume_id TEXT,

  FOREIGN KEY (parent_resume_id) REFERENCES resumes(id)
);
```

### jobs

Stores job descriptions and analyzed requirements.

```sql
CREATE TABLE jobs (
  id TEXT PRIMARY KEY,
  company_id TEXT,

  -- Job Details
  title TEXT NOT NULL,
  company_name TEXT NOT NULL,
  location TEXT,
  remote_type TEXT,         -- remote, hybrid, onsite
  salary_range TEXT,
  job_url TEXT,

  -- Parsed Content
  description TEXT,
  required_skills JSON,     -- [{ skill, importance }, ...]
  preferred_skills JSON,
  responsibilities JSON,
  qualifications JSON,

  -- Requirements
  min_experience_years INTEGER,
  education_requirement TEXT,

  -- Analysis
  keywords JSON,            -- ATS keywords
  culture_indicators JSON,  -- Detected values/culture

  -- Metadata
  posted_date DATE,
  analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  source TEXT,              -- url, file, manual

  FOREIGN KEY (company_id) REFERENCES companies(id)
);
```

### applications

Tracks job applications with timeline and status.

```sql
CREATE TABLE applications (
  id TEXT PRIMARY KEY,

  -- References
  resume_id TEXT NOT NULL,
  job_id TEXT NOT NULL,
  cover_letter_id TEXT,
  company_id TEXT,

  -- Application Info
  applied_date DATE NOT NULL DEFAULT CURRENT_DATE,
  status TEXT NOT NULL,     -- applied, screening, interview, offer, rejected
  status_updated_at TIMESTAMP,

  -- Tracking
  application_url TEXT,
  confirmation_number TEXT,
  referral_source TEXT,

  -- Timeline
  screening_date DATE,
  interview_dates JSON,     -- [{ date, type, interviewer }, ...]
  offer_date DATE,
  offer_deadline DATE,
  rejection_date DATE,

  -- Follow-up
  last_followup_date DATE,
  next_followup_date DATE,
  followup_count INTEGER DEFAULT 0,

  -- Documents
  resume_file_path TEXT,
  cover_letter_file_path TEXT,

  -- Notes
  notes TEXT,
  interview_feedback JSON,

  -- Metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (resume_id) REFERENCES resumes(id),
  FOREIGN KEY (job_id) REFERENCES jobs(id),
  FOREIGN KEY (cover_letter_id) REFERENCES cover_letters(id),
  FOREIGN KEY (company_id) REFERENCES companies(id)
);
```

### cover_letters

Stores generated cover letters.

```sql
CREATE TABLE cover_letters (
  id TEXT PRIMARY KEY,

  -- References
  resume_id TEXT NOT NULL,
  job_id TEXT NOT NULL,

  -- Content
  content TEXT NOT NULL,
  tone TEXT,                -- professional, enthusiastic, conversational
  word_count INTEGER,

  -- Generation
  template_used TEXT,
  highlights JSON,          -- Key points highlighted
  generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  -- File
  file_path TEXT,
  file_format TEXT,         -- pdf, docx, txt

  FOREIGN KEY (resume_id) REFERENCES resumes(id),
  FOREIGN KEY (job_id) REFERENCES jobs(id)
);
```

### companies

Stores company research and intelligence.

```sql
CREATE TABLE companies (
  id TEXT PRIMARY KEY,

  -- Basic Info
  name TEXT NOT NULL,
  website TEXT,
  industry TEXT,
  size TEXT,                -- 1-50, 51-200, 201-500, etc.
  headquarters TEXT,

  -- Research Data
  tech_stack JSON,          -- [{ technology, category }, ...]
  culture JSON,             -- { values, workStyle, benefits }
  recent_news JSON,         -- [{ title, date, source, url }, ...]
  employee_reviews JSON,    -- { glassdoor, indeed, ... }

  -- Financials
  funding_stage TEXT,       -- seed, series-a, public, etc.
  funding_amount TEXT,

  -- Social
  linkedin_url TEXT,
  twitter_url TEXT,
  github_url TEXT,

  -- Metadata
  researched_at TIMESTAMP,
  data_freshness DATE,      -- When to refresh research

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### analytics

Stores performance metrics and insights.

```sql
CREATE TABLE analytics (
  id TEXT PRIMARY KEY,

  -- Time Range
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,

  -- Metrics
  applications_count INTEGER,
  responses_count INTEGER,
  interviews_count INTEGER,
  offers_count INTEGER,
  rejections_count INTEGER,

  -- Rates
  response_rate REAL,       -- responses / applications
  interview_rate REAL,      -- interviews / applications
  offer_rate REAL,          -- offers / applications

  -- Timing
  avg_response_time_days REAL,
  avg_interview_time_days REAL,

  -- Skills Analysis
  top_skills_requested JSON,    -- [{ skill, count }, ...]
  skill_gaps JSON,              -- Skills in jobs but not in resume

  -- ATS Performance
  avg_ats_score REAL,
  ats_score_trend JSON,         -- [{ date, score }, ...]

  -- Company Insights
  top_companies JSON,           -- [{ company, count }, ...]
  top_industries JSON,

  generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Relationships

```text
users (1) ──< (many) resumes
resumes (1) ──< (many) applications
jobs (1) ──< (many) applications
companies (1) ──< (many) jobs
companies (1) ──< (many) applications
resumes (1) ──< (many) cover_letters
jobs (1) ──< (many) cover_letters
```

## Data Flow

### Application Creation Flow

```text
1. Parse Resume → INSERT into resumes table
2. Analyze Job → INSERT into jobs table
3. Research Company → INSERT/UPDATE companies table
4. Optimize Resume → INSERT new resume (version++) with parent_resume_id
5. Generate Cover Letter → INSERT into cover_letters table
6. Track Application → INSERT into applications table
7. Calculate Analytics → INSERT/UPDATE analytics table
```

## Common Query Patterns

### Get all applications with related data

```sql
SELECT a.*, j.title, c.name as company_name, r.full_name
FROM applications a
JOIN jobs j ON a.job_id = j.id
JOIN companies c ON a.company_id = c.id
JOIN resumes r ON a.resume_id = r.id
WHERE a.status IN ('applied', 'screening', 'interview')
ORDER BY a.applied_date DESC;
```

### Calculate success metrics

```sql
SELECT
  COUNT(*) as total_applications,
  SUM(CASE WHEN status != 'rejected' THEN 1 ELSE 0 END) as active,
  SUM(CASE WHEN status = 'interview' THEN 1 ELSE 0 END) as interviews,
  SUM(CASE WHEN status = 'offer' THEN 1 ELSE 0 END) as offers,
  ROUND(AVG(CASE WHEN status = 'interview' THEN 1.0 ELSE 0.0 END) * 100, 2) as interview_rate
FROM applications
WHERE applied_date >= date('now', '-30 days');
```

### Find skill gaps

```sql
SELECT DISTINCT skill
FROM (
  SELECT json_each.value as skill
  FROM jobs, json_each(required_skills)
  WHERE id IN (SELECT job_id FROM applications WHERE status != 'rejected')
)
WHERE skill NOT IN (
  SELECT json_each.value
  FROM resumes, json_each(skills)
  WHERE is_base_resume = true
);
```

## JSON Field Structures

### skills (resumes table)

```json
["JavaScript", "Python", "React", "AWS", "Docker"]
```

### experiences (resumes table)

```json
[
  {
    "company": "TechCorp",
    "title": "Senior Engineer",
    "startDate": "2020-01",
    "endDate": "present",
    "bullets": [
      "Built scalable systems",
      "Led team of 5 engineers"
    ]
  }
]
```

### required_skills (jobs table)

```json
[
  { "skill": "Python", "importance": "high" },
  { "skill": "React", "importance": "high" },
  { "skill": "Docker", "importance": "medium" }
]
```

### interview_dates (applications table)

```json
[
  {
    "date": "2025-10-25",
    "type": "screening",
    "interviewer": "Sarah Johnson"
  },
  {
    "date": "2025-10-28",
    "type": "technical",
    "interviewer": "Mike Chen"
  }
]
```

### tech_stack (companies table)

```json
[
  { "technology": "React", "category": "frontend" },
  { "technology": "Node.js", "category": "backend" },
  { "technology": "PostgreSQL", "category": "database" }
]
```

## Indexes

For optimal performance, consider adding indexes:

```sql
-- Resume lookups
CREATE INDEX idx_resumes_user ON resumes(user_id);
CREATE INDEX idx_resumes_base ON resumes(is_base_resume);

-- Application queries
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_date ON applications(applied_date);

-- Job lookups
CREATE INDEX idx_jobs_company ON jobs(company_id);

-- Analytics time range queries
CREATE INDEX idx_analytics_period ON analytics(period_start, period_end);
```

## Migration Strategy

When adding new columns or tables:

1. Update schema definition
2. Create migration SQL file
3. Test migration on local database
4. Apply to production Turso database
5. Update TypeScript types to match schema

## See Also

- [CLAUDE.md](../CLAUDE.md) - Project overview
- [DEVELOPMENT.md](./DEVELOPMENT.md) - Development guidelines
