"""
Pydantic models for job application tracking system.
Provides type-safe data validation and serialization for Turso database operations.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ============================================================================
# ENUMS
# ============================================================================


class ApplicationStatus(str, Enum):
    """Valid application status values"""

    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    WITHDRAWN = "withdrawn"


class EmploymentType(str, Enum):
    """Valid employment type values"""

    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    INTERNSHIP = "Internship"
    FREELANCE = "Freelance"


class InterviewType(str, Enum):
    """Valid interview type values"""

    PHONE = "phone"
    VIDEO = "video"
    ONSITE = "onsite"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    PANEL = "panel"
    HR = "hr"
    CASE_STUDY = "case_study"
    PRESENTATION = "presentation"


class InterviewResult(str, Enum):
    """Valid interview result values"""

    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"
    CANCELLED = "cancelled"


class KeywordCategory(str, Enum):
    """Valid keyword category values"""

    TECHNICAL_SKILL = "technical_skill"
    SOFT_SKILL = "soft_skill"
    CERTIFICATION = "certification"
    TOOL = "tool"
    FRAMEWORK = "framework"
    DOMAIN = "domain"
    LANGUAGE = "language"
    METHODOLOGY = "methodology"


# ============================================================================
# BASE MODELS
# ============================================================================


class ApplicationBase(BaseModel):
    """Base model for application data (used for creation)"""

    company: str = Field(..., min_length=1, max_length=255)
    position: str = Field(..., min_length=1, max_length=255)
    job_url: str | None = None
    job_description: str | None = None
    location: str | None = None
    salary_range: str | None = None
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    applied_date: str = Field(..., description="ISO 8601 date format: YYYY-MM-DD")
    status: ApplicationStatus = ApplicationStatus.APPLIED
    source: str | None = None
    resume_version: str | None = None
    cover_letter_used: bool = False
    keywords_targeted: str | None = Field(None, description="JSON array of keywords")
    last_contact_date: str | None = None
    next_followup_date: str | None = None
    notes: str | None = None
    resume_path: str | None = None
    cover_letter_path: str | None = None

    @field_validator("applied_date", "last_contact_date", "next_followup_date")
    @classmethod
    def validate_date_format(cls, v: str | None) -> str | None:
        """Validate ISO 8601 date format"""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError(f"Date must be in ISO 8601 format (YYYY-MM-DD): {v}")


class Application(ApplicationBase):
    """Complete application model (includes database fields)"""

    id: int
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class ApplicationCreate(ApplicationBase):
    """Model for creating new applications"""


class ApplicationUpdate(BaseModel):
    """Model for updating applications (all fields optional)"""

    company: str | None = None
    position: str | None = None
    job_url: str | None = None
    job_description: str | None = None
    location: str | None = None
    salary_range: str | None = None
    employment_type: EmploymentType | None = None
    applied_date: str | None = None
    status: ApplicationStatus | None = None
    source: str | None = None
    resume_version: str | None = None
    cover_letter_used: bool | None = None
    keywords_targeted: str | None = None
    last_contact_date: str | None = None
    next_followup_date: str | None = None
    notes: str | None = None
    resume_path: str | None = None
    cover_letter_path: str | None = None


# ============================================================================
# INTERVIEW MODELS
# ============================================================================


class InterviewBase(BaseModel):
    """Base model for interview data"""

    application_id: int
    interview_date: str = Field(..., description="ISO 8601 date format: YYYY-MM-DD")
    interview_time: str | None = Field(None, description="Time in HH:MM format")
    duration_minutes: int | None = Field(None, ge=0)
    interview_type: InterviewType
    round_number: int = Field(1, ge=1)
    interviewer_name: str | None = None
    interviewer_title: str | None = None
    interviewer_email: str | None = None
    panel_size: int = Field(1, ge=1)
    questions_asked: str | None = Field(None, description="JSON array or newline-separated")
    topics_covered: str | None = Field(None, description="JSON array or comma-separated")
    technical_assessment: str | None = None
    result: InterviewResult | None = None
    feedback_received: str | None = None
    personal_notes: str | None = None
    areas_to_improve: str | None = None
    location: str | None = None
    meeting_link: str | None = None
    timezone: str | None = None

    @field_validator("interview_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate ISO 8601 date format"""
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError(f"Date must be in ISO 8601 format (YYYY-MM-DD): {v}")


class Interview(InterviewBase):
    """Complete interview model (includes database fields)"""

    id: int
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class InterviewCreate(InterviewBase):
    """Model for creating new interviews"""


class InterviewUpdate(BaseModel):
    """Model for updating interviews (all fields optional)"""

    interview_date: str | None = None
    interview_time: str | None = None
    duration_minutes: int | None = None
    interview_type: InterviewType | None = None
    round_number: int | None = None
    interviewer_name: str | None = None
    interviewer_title: str | None = None
    interviewer_email: str | None = None
    panel_size: int | None = None
    questions_asked: str | None = None
    topics_covered: str | None = None
    technical_assessment: str | None = None
    result: InterviewResult | None = None
    feedback_received: str | None = None
    personal_notes: str | None = None
    areas_to_improve: str | None = None
    location: str | None = None
    meeting_link: str | None = None
    timezone: str | None = None


# ============================================================================
# APPLICATION STAGE MODELS
# ============================================================================


class ApplicationStageBase(BaseModel):
    """Base model for application stage data"""

    application_id: int
    status: ApplicationStatus
    stage_date: str = Field(..., description="ISO 8601 date format: YYYY-MM-DD")
    notes: str | None = None
    changed_by: str | None = "manual"

    @field_validator("stage_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate ISO 8601 date format"""
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError(f"Date must be in ISO 8601 format (YYYY-MM-DD): {v}")


class ApplicationStage(ApplicationStageBase):
    """Complete application stage model (includes database fields)"""

    id: int
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class ApplicationStageCreate(ApplicationStageBase):
    """Model for creating new application stages"""


# ============================================================================
# METRICS MODELS
# ============================================================================


class MetricsBase(BaseModel):
    """Base model for metrics data"""

    metric_date: str = Field(..., description="ISO 8601 date format: YYYY-MM-DD")
    total_applications: int = 0
    applications_sent_today: int = 0
    total_responses: int = 0
    response_rate: float = 0.0
    total_interviews: int = 0
    interview_rate: float = 0.0
    total_offers: int = 0
    offer_rate: float = 0.0
    total_rejections: int = 0
    avg_response_time_days: float = 0.0
    avg_time_to_interview_days: float = 0.0
    avg_time_to_offer_days: float = 0.0
    active_applications: int = 0
    pending_followups: int = 0

    @field_validator("metric_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate ISO 8601 date format"""
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError(f"Date must be in ISO 8601 format (YYYY-MM-DD): {v}")


class Metrics(MetricsBase):
    """Complete metrics model (includes database fields)"""

    id: int
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class MetricsCreate(MetricsBase):
    """Model for creating new metrics"""


class MetricsUpdate(BaseModel):
    """Model for updating metrics (all fields optional)"""

    total_applications: int | None = None
    applications_sent_today: int | None = None
    total_responses: int | None = None
    response_rate: float | None = None
    total_interviews: int | None = None
    interview_rate: float | None = None
    total_offers: int | None = None
    offer_rate: float | None = None
    total_rejections: int | None = None
    avg_response_time_days: float | None = None
    avg_time_to_interview_days: float | None = None
    avg_time_to_offer_days: float | None = None
    active_applications: int | None = None
    pending_followups: int | None = None


# ============================================================================
# KEYWORD PERFORMANCE MODELS
# ============================================================================


class KeywordPerformanceBase(BaseModel):
    """Base model for keyword performance data"""

    keyword: str = Field(..., min_length=1)
    total_uses: int = 0
    response_count: int = 0
    response_rate: float = 0.0
    interview_count: int = 0
    interview_rate: float = 0.0
    offer_count: int = 0
    offer_rate: float = 0.0
    category: KeywordCategory | None = None
    last_used_date: str | None = Field(None, description="ISO 8601 date format: YYYY-MM-DD")

    @field_validator("last_used_date")
    @classmethod
    def validate_date_format(cls, v: str | None) -> str | None:
        """Validate ISO 8601 date format"""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError(f"Date must be in ISO 8601 format (YYYY-MM-DD): {v}")


class KeywordPerformance(KeywordPerformanceBase):
    """Complete keyword performance model (includes database fields)"""

    id: int
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class KeywordPerformanceCreate(KeywordPerformanceBase):
    """Model for creating new keyword performance records"""


class KeywordPerformanceUpdate(BaseModel):
    """Model for updating keyword performance (all fields optional)"""

    total_uses: int | None = None
    response_count: int | None = None
    response_rate: float | None = None
    interview_count: int | None = None
    interview_rate: float | None = None
    offer_count: int | None = None
    offer_rate: float | None = None
    category: KeywordCategory | None = None
    last_used_date: str | None = None


# ============================================================================
# VIEW MODELS (Read-only)
# ============================================================================


class ActiveApplication(Application):
    """Model for v_active_applications view"""

    interview_count: int
    latest_interview_date: str | None
    latest_interview_type: str | None


class PipelineSummary(BaseModel):
    """Model for v_pipeline_summary view"""

    status: ApplicationStatus
    count: int
    percentage: float

    model_config = ConfigDict(from_attributes=True)


class InterviewPerformance(BaseModel):
    """Model for v_interview_performance view"""

    company: str
    total_applications: int
    total_interviews: int
    interviews_per_application: float
    avg_rounds: float | None

    model_config = ConfigDict(from_attributes=True)


class TopKeyword(BaseModel):
    """Model for v_top_keywords view"""

    keyword: str
    category: KeywordCategory | None
    total_uses: int
    response_rate: float
    interview_rate: float
    offer_rate: float

    model_config = ConfigDict(from_attributes=True)
