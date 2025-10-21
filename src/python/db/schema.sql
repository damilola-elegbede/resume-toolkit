-- Job Application Tracking System Schema for Turso (libSQL)
-- Designed for optimal query performance and data integrity

-- ============================================================================
-- APPLICATIONS TABLE
-- Core table tracking all job applications
-- ============================================================================
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    position TEXT NOT NULL,
    job_url TEXT,
    job_description TEXT,
    location TEXT,
    salary_range TEXT,
    employment_type TEXT DEFAULT 'Full-time', -- Full-time, Part-time, Contract, etc.

    -- Application metadata
    applied_date TEXT NOT NULL, -- ISO 8601 format: YYYY-MM-DD
    status TEXT NOT NULL DEFAULT 'applied', -- applied, screening, interviewing, offer, rejected, accepted, withdrawn
    source TEXT, -- LinkedIn, Indeed, Company Website, Referral, etc.

    -- Resume customization tracking
    resume_version TEXT, -- Version or hash of resume used
    cover_letter_used INTEGER DEFAULT 0, -- Boolean: 0 or 1
    keywords_targeted TEXT, -- JSON array of keywords targeted for this application

    -- Follow-up tracking
    last_contact_date TEXT, -- Last interaction date
    next_followup_date TEXT, -- Scheduled follow-up date

    -- Notes and attachments
    notes TEXT,
    resume_path TEXT, -- Path to stored resume PDF
    cover_letter_path TEXT, -- Path to stored cover letter

    -- Metadata
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),

    -- Constraints
    CHECK (status IN ('applied', 'screening', 'interviewing', 'offer', 'rejected', 'accepted', 'withdrawn')),
    CHECK (employment_type IN ('Full-time', 'Part-time', 'Contract', 'Internship', 'Freelance'))
);

-- ============================================================================
-- INTERVIEWS TABLE
-- Track all interview rounds and interactions
-- ============================================================================
CREATE TABLE IF NOT EXISTS interviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,

    -- Interview details
    interview_date TEXT NOT NULL, -- ISO 8601 format: YYYY-MM-DD
    interview_time TEXT, -- HH:MM format
    duration_minutes INTEGER,

    -- Interview type and stage
    interview_type TEXT NOT NULL, -- phone, video, onsite, technical, behavioral, panel, etc.
    round_number INTEGER DEFAULT 1,

    -- Participants
    interviewer_name TEXT,
    interviewer_title TEXT,
    interviewer_email TEXT,
    panel_size INTEGER DEFAULT 1,

    -- Interview content
    questions_asked TEXT, -- JSON array or newline-separated
    topics_covered TEXT, -- JSON array or comma-separated
    technical_assessment TEXT, -- Description of technical tasks/questions

    -- Outcome and feedback
    result TEXT, -- passed, failed, pending, cancelled
    feedback_received TEXT,
    personal_notes TEXT,
    areas_to_improve TEXT,

    -- Logistics
    location TEXT, -- Office address or video link
    meeting_link TEXT,
    timezone TEXT,

    -- Metadata
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),

    -- Constraints
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
    CHECK (interview_type IN ('phone', 'video', 'onsite', 'technical', 'behavioral', 'panel', 'hr', 'case_study', 'presentation')),
    CHECK (result IS NULL OR result IN ('passed', 'failed', 'pending', 'cancelled'))
);

-- ============================================================================
-- APPLICATION_STAGES TABLE
-- Track complete status history for each application (audit trail)
-- ============================================================================
CREATE TABLE IF NOT EXISTS application_stages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,

    -- Stage information
    status TEXT NOT NULL,
    stage_date TEXT NOT NULL DEFAULT (date('now')), -- ISO 8601 format: YYYY-MM-DD

    -- Additional context
    notes TEXT,
    changed_by TEXT, -- System or manual tracking

    -- Metadata
    created_at TEXT NOT NULL DEFAULT (datetime('now')),

    -- Constraints
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
    CHECK (status IN ('applied', 'screening', 'interviewing', 'offer', 'rejected', 'accepted', 'withdrawn'))
);

-- ============================================================================
-- METRICS TABLE
-- Aggregate metrics for dashboard and analytics
-- ============================================================================
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date TEXT NOT NULL UNIQUE, -- ISO 8601 format: YYYY-MM-DD

    -- Application metrics
    total_applications INTEGER DEFAULT 0,
    applications_sent_today INTEGER DEFAULT 0,

    -- Response metrics
    total_responses INTEGER DEFAULT 0,
    response_rate REAL DEFAULT 0.0, -- Percentage: responses/applications

    -- Interview metrics
    total_interviews INTEGER DEFAULT 0,
    interview_rate REAL DEFAULT 0.0, -- Percentage: interviews/applications

    -- Outcome metrics
    total_offers INTEGER DEFAULT 0,
    offer_rate REAL DEFAULT 0.0, -- Percentage: offers/applications
    total_rejections INTEGER DEFAULT 0,

    -- Time-based metrics
    avg_response_time_days REAL DEFAULT 0.0,
    avg_time_to_interview_days REAL DEFAULT 0.0,
    avg_time_to_offer_days REAL DEFAULT 0.0,

    -- Status distribution
    active_applications INTEGER DEFAULT 0,
    pending_followups INTEGER DEFAULT 0,

    -- Metadata
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================================
-- KEYWORD_PERFORMANCE TABLE
-- Track effectiveness of resume keywords and skills
-- ============================================================================
CREATE TABLE IF NOT EXISTS keyword_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL UNIQUE,

    -- Usage metrics
    total_uses INTEGER DEFAULT 0, -- Number of applications using this keyword

    -- Response metrics
    response_count INTEGER DEFAULT 0, -- Applications with responses (any stage beyond applied)
    response_rate REAL DEFAULT 0.0, -- Percentage: response_count/total_uses

    -- Interview metrics
    interview_count INTEGER DEFAULT 0, -- Applications that reached interview stage
    interview_rate REAL DEFAULT 0.0, -- Percentage: interview_count/total_uses

    -- Offer metrics
    offer_count INTEGER DEFAULT 0, -- Applications that received offers
    offer_rate REAL DEFAULT 0.0, -- Percentage: offer_count/total_uses

    -- Category classification
    category TEXT, -- technical_skill, soft_skill, certification, tool, framework, domain, etc.

    -- Metadata
    last_used_date TEXT, -- ISO 8601 format: YYYY-MM-DD
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),

    -- Constraints
    CHECK (category IS NULL OR category IN ('technical_skill', 'soft_skill', 'certification', 'tool', 'framework', 'domain', 'language', 'methodology'))
);

-- ============================================================================
-- INDEXES
-- Optimized for common query patterns
-- ============================================================================

-- Applications indexes
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_applied_date ON applications(applied_date DESC);
CREATE INDEX IF NOT EXISTS idx_applications_company ON applications(company);
CREATE INDEX IF NOT EXISTS idx_applications_next_followup ON applications(next_followup_date) WHERE next_followup_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_applications_status_date ON applications(status, applied_date DESC);

-- Interviews indexes
CREATE INDEX IF NOT EXISTS idx_interviews_application_id ON interviews(application_id);
CREATE INDEX IF NOT EXISTS idx_interviews_date ON interviews(interview_date DESC);
CREATE INDEX IF NOT EXISTS idx_interviews_type ON interviews(interview_type);
CREATE INDEX IF NOT EXISTS idx_interviews_result ON interviews(result) WHERE result IS NOT NULL;

-- Application stages indexes
CREATE INDEX IF NOT EXISTS idx_stages_application_id ON application_stages(application_id);
CREATE INDEX IF NOT EXISTS idx_stages_date ON application_stages(stage_date DESC);
CREATE INDEX IF NOT EXISTS idx_stages_status ON application_stages(status);

-- Metrics indexes
CREATE INDEX IF NOT EXISTS idx_metrics_date ON metrics(metric_date DESC);

-- Keyword performance indexes
CREATE INDEX IF NOT EXISTS idx_keywords_response_rate ON keyword_performance(response_rate DESC);
CREATE INDEX IF NOT EXISTS idx_keywords_category ON keyword_performance(category) WHERE category IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_keywords_last_used ON keyword_performance(last_used_date DESC);

-- ============================================================================
-- TRIGGERS
-- Automatic timestamp updates and audit trail
-- ============================================================================

-- Update applications.updated_at on changes
CREATE TRIGGER IF NOT EXISTS update_applications_timestamp
AFTER UPDATE ON applications
FOR EACH ROW
BEGIN
    UPDATE applications SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- Update interviews.updated_at on changes
CREATE TRIGGER IF NOT EXISTS update_interviews_timestamp
AFTER UPDATE ON interviews
FOR EACH ROW
BEGIN
    UPDATE interviews SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- Update metrics.updated_at on changes
CREATE TRIGGER IF NOT EXISTS update_metrics_timestamp
AFTER UPDATE ON metrics
FOR EACH ROW
BEGIN
    UPDATE metrics SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- Update keyword_performance.updated_at on changes
CREATE TRIGGER IF NOT EXISTS update_keyword_performance_timestamp
AFTER UPDATE ON keyword_performance
FOR EACH ROW
BEGIN
    UPDATE keyword_performance SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- Automatically create stage entry when application status changes
CREATE TRIGGER IF NOT EXISTS track_application_status_change
AFTER UPDATE OF status ON applications
FOR EACH ROW
WHEN NEW.status != OLD.status
BEGIN
    INSERT INTO application_stages (application_id, status, stage_date, notes, changed_by)
    VALUES (NEW.id, NEW.status, date('now'), 'Status changed from ' || OLD.status || ' to ' || NEW.status, 'system');
END;

-- Update last_contact_date when interview is added/updated
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
-- Commonly used queries for convenience
-- ============================================================================

-- Active applications with latest interview
CREATE VIEW IF NOT EXISTS v_active_applications AS
SELECT
    a.*,
    (SELECT COUNT(*) FROM interviews WHERE application_id = a.id) as interview_count,
    (SELECT MAX(interview_date) FROM interviews WHERE application_id = a.id) as latest_interview_date,
    (SELECT interview_type FROM interviews WHERE application_id = a.id ORDER BY interview_date DESC LIMIT 1) as latest_interview_type
FROM applications a
WHERE a.status NOT IN ('rejected', 'withdrawn', 'accepted');

-- Application pipeline summary
CREATE VIEW IF NOT EXISTS v_pipeline_summary AS
SELECT
    status,
    COUNT(*) as count,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM applications WHERE status NOT IN ('rejected', 'withdrawn', 'accepted')) as percentage
FROM applications
WHERE status NOT IN ('rejected', 'withdrawn', 'accepted')
GROUP BY status;

-- Interview performance by company
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

-- Top performing keywords
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
