-- Migration: 001_initial_schema
-- Description: Initial database schema for job application tracking system
-- Created: 2025-10-21
-- Author: Database Admin Agent

-- This migration creates all tables, indexes, triggers, and views
-- for the job application tracking system

-- Execute the complete schema
-- Note: In production, you would typically run this via:
-- turso db shell <database-name> < 001_initial_schema.sql

-- ============================================================================
-- TABLES
-- ============================================================================

-- Applications table
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    position TEXT NOT NULL,
    job_url TEXT,
    job_description TEXT,
    location TEXT,
    salary_range TEXT,
    employment_type TEXT DEFAULT 'Full-time',
    applied_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'applied',
    source TEXT,
    resume_version TEXT,
    cover_letter_used INTEGER DEFAULT 0,
    keywords_targeted TEXT,
    last_contact_date TEXT,
    next_followup_date TEXT,
    notes TEXT,
    resume_path TEXT,
    cover_letter_path TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK (status IN ('applied', 'screening', 'interviewing', 'offer', 'rejected', 'accepted', 'withdrawn')),
    CHECK (employment_type IN ('Full-time', 'Part-time', 'Contract', 'Internship', 'Freelance'))
);

-- Interviews table
CREATE TABLE IF NOT EXISTS interviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    interview_date TEXT NOT NULL,
    interview_time TEXT,
    duration_minutes INTEGER,
    interview_type TEXT NOT NULL,
    round_number INTEGER DEFAULT 1,
    interviewer_name TEXT,
    interviewer_title TEXT,
    interviewer_email TEXT,
    panel_size INTEGER DEFAULT 1,
    questions_asked TEXT,
    topics_covered TEXT,
    technical_assessment TEXT,
    result TEXT,
    feedback_received TEXT,
    personal_notes TEXT,
    areas_to_improve TEXT,
    location TEXT,
    meeting_link TEXT,
    timezone TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
    CHECK (interview_type IN ('phone', 'video', 'onsite', 'technical', 'behavioral', 'panel', 'hr', 'case_study', 'presentation')),
    CHECK (result IS NULL OR result IN ('passed', 'failed', 'pending', 'cancelled'))
);

-- Application stages table
CREATE TABLE IF NOT EXISTS application_stages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    stage_date TEXT NOT NULL DEFAULT (date('now')),
    notes TEXT,
    changed_by TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
    CHECK (status IN ('applied', 'screening', 'interviewing', 'offer', 'rejected', 'accepted', 'withdrawn'))
);

-- Metrics table
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date TEXT NOT NULL UNIQUE,
    total_applications INTEGER DEFAULT 0,
    applications_sent_today INTEGER DEFAULT 0,
    total_responses INTEGER DEFAULT 0,
    response_rate REAL DEFAULT 0.0,
    total_interviews INTEGER DEFAULT 0,
    interview_rate REAL DEFAULT 0.0,
    total_offers INTEGER DEFAULT 0,
    offer_rate REAL DEFAULT 0.0,
    total_rejections INTEGER DEFAULT 0,
    avg_response_time_days REAL DEFAULT 0.0,
    avg_time_to_interview_days REAL DEFAULT 0.0,
    avg_time_to_offer_days REAL DEFAULT 0.0,
    active_applications INTEGER DEFAULT 0,
    pending_followups INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Keyword performance table
CREATE TABLE IF NOT EXISTS keyword_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL UNIQUE,
    total_uses INTEGER DEFAULT 0,
    response_count INTEGER DEFAULT 0,
    response_rate REAL DEFAULT 0.0,
    interview_count INTEGER DEFAULT 0,
    interview_rate REAL DEFAULT 0.0,
    offer_count INTEGER DEFAULT 0,
    offer_rate REAL DEFAULT 0.0,
    category TEXT,
    last_used_date TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK (category IS NULL OR category IN ('technical_skill', 'soft_skill', 'certification', 'tool', 'framework', 'domain', 'language', 'methodology'))
);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_applied_date ON applications(applied_date DESC);
CREATE INDEX IF NOT EXISTS idx_applications_company ON applications(company);
CREATE INDEX IF NOT EXISTS idx_applications_next_followup ON applications(next_followup_date) WHERE next_followup_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_applications_status_date ON applications(status, applied_date DESC);

CREATE INDEX IF NOT EXISTS idx_interviews_application_id ON interviews(application_id);
CREATE INDEX IF NOT EXISTS idx_interviews_date ON interviews(interview_date DESC);
CREATE INDEX IF NOT EXISTS idx_interviews_type ON interviews(interview_type);
CREATE INDEX IF NOT EXISTS idx_interviews_result ON interviews(result) WHERE result IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_stages_application_id ON application_stages(application_id);
CREATE INDEX IF NOT EXISTS idx_stages_date ON application_stages(stage_date DESC);
CREATE INDEX IF NOT EXISTS idx_stages_status ON application_stages(status);

CREATE INDEX IF NOT EXISTS idx_metrics_date ON metrics(metric_date DESC);

CREATE INDEX IF NOT EXISTS idx_keywords_response_rate ON keyword_performance(response_rate DESC);
CREATE INDEX IF NOT EXISTS idx_keywords_category ON keyword_performance(category) WHERE category IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_keywords_last_used ON keyword_performance(last_used_date DESC);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE TRIGGER IF NOT EXISTS update_applications_timestamp
AFTER UPDATE ON applications
FOR EACH ROW
BEGIN
    UPDATE applications SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_interviews_timestamp
AFTER UPDATE ON interviews
FOR EACH ROW
BEGIN
    UPDATE interviews SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_metrics_timestamp
AFTER UPDATE ON metrics
FOR EACH ROW
BEGIN
    UPDATE metrics SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_keyword_performance_timestamp
AFTER UPDATE ON keyword_performance
FOR EACH ROW
BEGIN
    UPDATE keyword_performance SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS track_application_status_change
AFTER UPDATE OF status ON applications
FOR EACH ROW
WHEN NEW.status != OLD.status
BEGIN
    INSERT INTO application_stages (application_id, status, stage_date, notes, changed_by)
    VALUES (NEW.id, NEW.status, date('now'), 'Status changed from ' || OLD.status || ' to ' || NEW.status, 'system');
END;

CREATE TRIGGER IF NOT EXISTS update_last_contact_on_interview
AFTER INSERT ON interviews
FOR EACH ROW
BEGIN
    UPDATE applications
    SET last_contact_date = NEW.interview_date
    WHERE id = NEW.application_id
    AND (last_contact_date IS NULL OR NEW.interview_date > last_contact_date);
END;

-- ============================================================================
-- VIEWS
-- ============================================================================

CREATE VIEW IF NOT EXISTS v_active_applications AS
SELECT
    a.*,
    (SELECT COUNT(*) FROM interviews WHERE application_id = a.id) as interview_count,
    (SELECT MAX(interview_date) FROM interviews WHERE application_id = a.id) as latest_interview_date,
    (SELECT interview_type FROM interviews WHERE application_id = a.id ORDER BY interview_date DESC LIMIT 1) as latest_interview_type
FROM applications a
WHERE a.status NOT IN ('rejected', 'withdrawn', 'accepted');

CREATE VIEW IF NOT EXISTS v_pipeline_summary AS
SELECT
    status,
    COUNT(*) as count,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM applications WHERE status NOT IN ('rejected', 'withdrawn', 'accepted')) as percentage
FROM applications
WHERE status NOT IN ('rejected', 'withdrawn', 'accepted')
GROUP BY status;

CREATE VIEW IF NOT EXISTS v_interview_performance AS
SELECT
    a.company,
    COUNT(DISTINCT a.id) as total_applications,
    COUNT(DISTINCT i.id) as total_interviews,
    CAST(COUNT(DISTINCT i.id) AS REAL) / COUNT(DISTINCT a.id) as interviews_per_application,
    AVG(i.round_number) as avg_rounds
FROM applications a
LEFT JOIN interviews i ON a.id = i.application_id
GROUP BY a.company
HAVING total_applications > 0
ORDER BY total_interviews DESC;

CREATE VIEW IF NOT EXISTS v_top_keywords AS
SELECT
    keyword,
    category,
    total_uses,
    response_rate,
    interview_rate,
    offer_rate
FROM keyword_performance
WHERE total_uses >= 3
ORDER BY response_rate DESC, total_uses DESC;

-- ============================================================================
-- SEED DATA (Optional - for testing)
-- ============================================================================

-- Initial metrics entry for today
INSERT OR IGNORE INTO metrics (metric_date) VALUES (date('now'));
