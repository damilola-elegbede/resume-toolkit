"""
Turso database client for job application tracking system.
Provides type-safe database operations using libsql_client and Pydantic models.
"""

import os
from typing import Any, TypeVar

try:
    import libsql_client
except ImportError:
    raise ImportError(
        "libsql_client is not installed. Install it with: pip install libsql-client"
    )

from .models import (
    ActiveApplication,
    Application,
    ApplicationCreate,
    ApplicationStage,
    ApplicationUpdate,
    Interview,
    InterviewCreate,
    InterviewPerformance,
    InterviewUpdate,
    KeywordPerformance,
    KeywordPerformanceCreate,
    Metrics,
    MetricsCreate,
    PipelineSummary,
    TopKeyword,
)

T = TypeVar('T')


class TursoClient:
    """
    Type-safe Turso database client for job application tracking.

    Usage:
        client = TursoClient()
        await client.connect()

        # Create an application
        app = await client.create_application(
            ApplicationCreate(
                company="Tech Corp",
                position="Senior Engineer",
                applied_date="2025-10-21"
            )
        )

        # Query applications
        apps = await client.get_applications(status="applied", limit=10)

        await client.close()

    Or use as async context manager:
        async with TursoClient() as client:
            apps = await client.get_applications()
    """

    def __init__(
        self,
        database_url: str | None = None,
        auth_token: str | None = None
    ):
        """
        Initialize Turso client.

        Args:
            database_url: Turso database URL (defaults to TURSO_DATABASE_URL env var)
            auth_token: Turso auth token (defaults to TURSO_AUTH_TOKEN env var)
        """
        self.database_url = database_url or os.getenv("TURSO_DATABASE_URL")
        self.auth_token = auth_token or os.getenv("TURSO_AUTH_TOKEN")

        if not self.database_url:
            raise ValueError(
                "Database URL not provided. Set TURSO_DATABASE_URL environment variable "
                "or pass database_url parameter."
            )

        if not self.auth_token:
            raise ValueError(
                "Auth token not provided. Set TURSO_AUTH_TOKEN environment variable "
                "or pass auth_token parameter."
            )

        self.client = None

    async def connect(self) -> None:
        """Establish connection to Turso database"""
        self.client = libsql_client.create_client(
            url=self.database_url,
            auth_token=self.auth_token
        )

    async def close(self) -> None:
        """Close database connection"""
        if self.client:
            await self.client.close()
            self.client = None

    async def __aenter__(self) -> "TursoClient":
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit"""
        await self.close()

    def _ensure_connected(self) -> Any:
        """Ensure client is connected and return it."""
        if not self.client:
            raise RuntimeError("Database client not connected. Call connect() first.")
        return self.client

    def _row_to_dict(self, row: Any) -> dict[str, Any]:
        """Convert database row to dictionary"""
        if hasattr(row, '_asdict'):
            return row._asdict()
        return dict(row)

    def _parse_model(self, row: Any, model: type[T]) -> T:
        """Parse database row into Pydantic model"""
        if row is None:
            return None
        data = self._row_to_dict(row)
        return model(**data)

    def _parse_models(self, rows: list[Any], model: type[T]) -> list[T]:
        """Parse multiple database rows into Pydantic models"""
        return [self._parse_model(row, model) for row in rows]

    # ========================================================================
    # APPLICATION OPERATIONS
    # ========================================================================

    async def create_application(self, app: ApplicationCreate) -> Application:
        """
        Create a new job application.

        Args:
            app: Application data

        Returns:
            Created application with ID and timestamps
        """
        query = """
            INSERT INTO applications (
                company, position, job_url, job_description, location,
                salary_range, employment_type, applied_date, status, source,
                resume_version, cover_letter_used, keywords_targeted,
                last_contact_date, next_followup_date, notes,
                resume_path, cover_letter_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING *
        """

        result = await self._ensure_connected().execute(query, [
            app.company, app.position, app.job_url, app.job_description,
            app.location, app.salary_range, app.employment_type.value,
            app.applied_date, app.status.value, app.source,
            app.resume_version, int(app.cover_letter_used), app.keywords_targeted,
            app.last_contact_date, app.next_followup_date, app.notes,
            app.resume_path, app.cover_letter_path
        ])

        return self._parse_model(result.rows[0], Application)

    async def get_application(self, application_id: int) -> Application | None:
        """Get application by ID"""
        query = "SELECT * FROM applications WHERE id = ?"
        result = await self._ensure_connected().execute(query, [application_id])

        if not result.rows:
            return None

        return self._parse_model(result.rows[0], Application)

    async def get_applications(
        self,
        status: str | None = None,
        company: str | None = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "applied_date DESC"
    ) -> list[Application]:
        """
        Get applications with optional filters.

        Args:
            status: Filter by application status
            company: Filter by company name (case-insensitive partial match)
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: SQL ORDER BY clause

        Returns:
            List of applications
        """
        conditions = []
        params = []

        if status:
            conditions.append("status = ?")
            params.append(status)

        if company:
            conditions.append("company LIKE ?")
            params.append(f"%{company}%")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT * FROM applications
            {where_clause}
            ORDER BY {order_by}
            LIMIT ? OFFSET ?
        """

        params.extend([limit, offset])
        result = await self._ensure_connected().execute(query, params)

        return self._parse_models(result.rows, Application)

    async def update_application(
        self,
        application_id: int,
        update: ApplicationUpdate
    ) -> Application | None:
        """
        Update an application.

        Args:
            application_id: ID of application to update
            update: Fields to update

        Returns:
            Updated application or None if not found
        """
        # Build dynamic update query
        update_data = update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_application(application_id)

        set_clauses = []
        params = []

        for key, value in update_data.items():
            set_clauses.append(f"{key} = ?")
            # Handle enum values
            if hasattr(value, 'value'):
                params.append(value.value)
            elif isinstance(value, bool):
                params.append(int(value))
            else:
                params.append(value)

        params.append(application_id)

        query = f"""
            UPDATE applications
            SET {', '.join(set_clauses)}
            WHERE id = ?
            RETURNING *
        """

        result = await self._ensure_connected().execute(query, params)

        if not result.rows:
            return None

        return self._parse_model(result.rows[0], Application)

    async def delete_application(self, application_id: int) -> bool:
        """
        Delete an application (and cascade to interviews/stages).

        Args:
            application_id: ID of application to delete

        Returns:
            True if deleted, False if not found
        """
        query = "DELETE FROM applications WHERE id = ?"
        result = await self._ensure_connected().execute(query, [application_id])
        return result.rows_affected > 0

    # ========================================================================
    # INTERVIEW OPERATIONS
    # ========================================================================

    async def create_interview(self, interview: InterviewCreate) -> Interview:
        """Create a new interview"""
        query = """
            INSERT INTO interviews (
                application_id, interview_date, interview_time, duration_minutes,
                interview_type, round_number, interviewer_name, interviewer_title,
                interviewer_email, panel_size, questions_asked, topics_covered,
                technical_assessment, result, feedback_received, personal_notes,
                areas_to_improve, location, meeting_link, timezone
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING *
        """

        result = await self._ensure_connected().execute(query, [
            interview.application_id, interview.interview_date, interview.interview_time,
            interview.duration_minutes, interview.interview_type.value, interview.round_number,
            interview.interviewer_name, interview.interviewer_title, interview.interviewer_email,
            interview.panel_size, interview.questions_asked, interview.topics_covered,
            interview.technical_assessment,
            interview.result.value if interview.result else None,
            interview.feedback_received, interview.personal_notes, interview.areas_to_improve,
            interview.location, interview.meeting_link, interview.timezone
        ])

        return self._parse_model(result.rows[0], Interview)

    async def get_interviews(
        self,
        application_id: int | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Interview]:
        """Get interviews with optional application filter"""
        if application_id:
            query = """
                SELECT * FROM interviews
                WHERE application_id = ?
                ORDER BY interview_date DESC
                LIMIT ? OFFSET ?
            """
            params = [application_id, limit, offset]
        else:
            query = """
                SELECT * FROM interviews
                ORDER BY interview_date DESC
                LIMIT ? OFFSET ?
            """
            params = [limit, offset]

        result = await self._ensure_connected().execute(query, params)
        return self._parse_models(result.rows, Interview)

    async def update_interview(
        self,
        interview_id: int,
        update: InterviewUpdate
    ) -> Interview | None:
        """Update an interview"""
        update_data = update.model_dump(exclude_unset=True)
        if not update_data:
            query = "SELECT * FROM interviews WHERE id = ?"
            result = await self._ensure_connected().execute(query, [interview_id])
            return self._parse_model(result.rows[0], Interview) if result.rows else None

        set_clauses = []
        params = []

        for key, value in update_data.items():
            set_clauses.append(f"{key} = ?")
            if hasattr(value, 'value'):
                params.append(value.value)
            else:
                params.append(value)

        params.append(interview_id)

        query = f"""
            UPDATE interviews
            SET {', '.join(set_clauses)}
            WHERE id = ?
            RETURNING *
        """

        result = await self._ensure_connected().execute(query, params)
        return self._parse_model(result.rows[0], Interview) if result.rows else None

    # ========================================================================
    # APPLICATION STAGE OPERATIONS
    # ========================================================================

    async def get_application_stages(
        self,
        application_id: int
    ) -> list[ApplicationStage]:
        """Get stage history for an application"""
        query = """
            SELECT * FROM application_stages
            WHERE application_id = ?
            ORDER BY stage_date DESC, created_at DESC
        """

        result = await self._ensure_connected().execute(query, [application_id])
        return self._parse_models(result.rows, ApplicationStage)

    # ========================================================================
    # METRICS OPERATIONS
    # ========================================================================

    async def get_metrics(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 30
    ) -> list[Metrics]:
        """
        Get metrics for date range.

        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            limit: Maximum number of results

        Returns:
            List of metrics ordered by date descending
        """
        conditions = []
        params = []

        if start_date:
            conditions.append("metric_date >= ?")
            params.append(start_date)

        if end_date:
            conditions.append("metric_date <= ?")
            params.append(end_date)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT * FROM metrics
            {where_clause}
            ORDER BY metric_date DESC
            LIMIT ?
        """

        params.append(limit)
        result = await self._ensure_connected().execute(query, params)

        return self._parse_models(result.rows, Metrics)

    async def upsert_metrics(self, metrics: MetricsCreate) -> Metrics:
        """Create or update metrics for a date"""
        query = """
            INSERT INTO metrics (
                metric_date, total_applications, applications_sent_today,
                total_responses, response_rate, total_interviews, interview_rate,
                total_offers, offer_rate, total_rejections,
                avg_response_time_days, avg_time_to_interview_days,
                avg_time_to_offer_days, active_applications, pending_followups
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(metric_date) DO UPDATE SET
                total_applications = excluded.total_applications,
                applications_sent_today = excluded.applications_sent_today,
                total_responses = excluded.total_responses,
                response_rate = excluded.response_rate,
                total_interviews = excluded.total_interviews,
                interview_rate = excluded.interview_rate,
                total_offers = excluded.total_offers,
                offer_rate = excluded.offer_rate,
                total_rejections = excluded.total_rejections,
                avg_response_time_days = excluded.avg_response_time_days,
                avg_time_to_interview_days = excluded.avg_time_to_interview_days,
                avg_time_to_offer_days = excluded.avg_time_to_offer_days,
                active_applications = excluded.active_applications,
                pending_followups = excluded.pending_followups
            RETURNING *
        """

        result = await self._ensure_connected().execute(query, [
            metrics.metric_date, metrics.total_applications, metrics.applications_sent_today,
            metrics.total_responses, metrics.response_rate, metrics.total_interviews,
            metrics.interview_rate, metrics.total_offers, metrics.offer_rate,
            metrics.total_rejections, metrics.avg_response_time_days,
            metrics.avg_time_to_interview_days, metrics.avg_time_to_offer_days,
            metrics.active_applications, metrics.pending_followups
        ])

        return self._parse_model(result.rows[0], Metrics)

    # ========================================================================
    # KEYWORD PERFORMANCE OPERATIONS
    # ========================================================================

    async def upsert_keyword_performance(
        self,
        keyword_perf: KeywordPerformanceCreate
    ) -> KeywordPerformance:
        """Create or update keyword performance"""
        query = """
            INSERT INTO keyword_performance (
                keyword, total_uses, response_count, response_rate,
                interview_count, interview_rate, offer_count, offer_rate,
                category, last_used_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(keyword) DO UPDATE SET
                total_uses = excluded.total_uses,
                response_count = excluded.response_count,
                response_rate = excluded.response_rate,
                interview_count = excluded.interview_count,
                interview_rate = excluded.interview_rate,
                offer_count = excluded.offer_count,
                offer_rate = excluded.offer_rate,
                category = excluded.category,
                last_used_date = excluded.last_used_date
            RETURNING *
        """

        result = await self._ensure_connected().execute(query, [
            keyword_perf.keyword, keyword_perf.total_uses, keyword_perf.response_count,
            keyword_perf.response_rate, keyword_perf.interview_count,
            keyword_perf.interview_rate, keyword_perf.offer_count, keyword_perf.offer_rate,
            keyword_perf.category.value if keyword_perf.category else None,
            keyword_perf.last_used_date
        ])

        return self._parse_model(result.rows[0], KeywordPerformance)

    async def get_top_keywords(self, limit: int = 20) -> list[TopKeyword]:
        """Get top performing keywords"""
        query = "SELECT * FROM v_top_keywords LIMIT ?"
        result = await self._ensure_connected().execute(query, [limit])
        return self._parse_models(result.rows, TopKeyword)

    # ========================================================================
    # VIEW QUERIES
    # ========================================================================

    async def get_active_applications(self, limit: int = 100) -> list[ActiveApplication]:
        """Get active applications with interview counts"""
        query = "SELECT * FROM v_active_applications LIMIT ?"
        result = await self._ensure_connected().execute(query, [limit])
        return self._parse_models(result.rows, ActiveApplication)

    async def get_pipeline_summary(self) -> list[PipelineSummary]:
        """Get application pipeline summary"""
        query = "SELECT * FROM v_pipeline_summary"
        result = await self._ensure_connected().execute(query)
        return self._parse_models(result.rows, PipelineSummary)

    async def get_interview_performance(self) -> list[InterviewPerformance]:
        """Get interview performance by company"""
        query = "SELECT * FROM v_interview_performance"
        result = await self._ensure_connected().execute(query)
        return self._parse_models(result.rows, InterviewPerformance)

    # ========================================================================
    # RAW QUERY EXECUTION
    # ========================================================================

    async def execute(self, query: str, params: list[Any] | None = None) -> Any:
        """
        Execute raw SQL query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Raw query result
        """
        return await self._ensure_connected().execute(query, params or [])
