/**
 * Turso database client for job application tracking system.
 * Provides type-safe database operations using @libsql/client and Zod schemas.
 */

import { createClient, Client, ResultSet } from '@libsql/client';

import {
  Application,
  ApplicationCreate,
  ApplicationUpdate,
  ApplicationSchema,
  Interview,
  InterviewCreate,
  InterviewUpdate,
  InterviewSchema,
  ApplicationStage,
  ApplicationStageSchema,
  Metrics,
  MetricsCreate,
  MetricsSchema,
  KeywordPerformance,
  KeywordPerformanceCreate,
  KeywordPerformanceSchema,
  ActiveApplication,
  ActiveApplicationSchema,
  PipelineSummary,
  PipelineSummarySchema,
  InterviewPerformance,
  InterviewPerformanceSchema,
  TopKeyword,
  TopKeywordSchema,
  QueryFilters,
  DateRange,
} from './types';

/**
 * Configuration for TursoClient
 */
export interface TursoClientConfig {
  databaseUrl?: string;
  authToken?: string;
}

/**
 * Type-safe Turso database client for job application tracking.
 *
 * @example
 * ```typescript
 * const client = new TursoClient({
 *   databaseUrl: process.env.TURSO_DATABASE_URL,
 *   authToken: process.env.TURSO_AUTH_TOKEN,
 * });
 *
 * // Create an application
 * const app = await client.createApplication({
 *   company: "Tech Corp",
 *   position: "Senior Engineer",
 *   applied_date: "2025-10-21",
 * });
 *
 * // Query applications
 * const apps = await client.getApplications({ status: "applied", limit: 10 });
 * ```
 */
export class TursoClient {
  private client: Client;

  constructor(config: TursoClientConfig = {}) {
    const databaseUrl = config.databaseUrl || process.env['TURSO_DATABASE_URL'];
    const authToken = config.authToken || process.env['TURSO_AUTH_TOKEN'];

    if (!databaseUrl) {
      throw new Error(
        'Database URL not provided. Set TURSO_DATABASE_URL environment variable or pass databaseUrl in config.'
      );
    }

    if (!authToken) {
      throw new Error(
        'Auth token not provided. Set TURSO_AUTH_TOKEN environment variable or pass authToken in config.'
      );
    }

    this.client = createClient({
      url: databaseUrl,
      authToken: authToken,
    });
  }

  /**
   * Close the database connection
   */
  async close(): Promise<void> {
    await this.client.close();
  }

  /**
   * Parse a database row into a validated type
   */
  private parseRow<T>(row: Record<string, any>, schema: any): T {
    // Convert boolean fields from integers
    const parsed = { ...row };
    if ('cover_letter_used' in parsed && typeof parsed['cover_letter_used'] === 'number') {
      parsed['cover_letter_used'] = Boolean(parsed['cover_letter_used']);
    }

    return schema.parse(parsed) as T;
  }

  /**
   * Parse multiple database rows
   */
  private parseRows<T>(rows: any[], schema: any): T[] {
    return rows.map((row) => this.parseRow<T>(row, schema));
  }

  /**
   * Convert ResultSet to array of objects
   */
  private resultToRows(result: ResultSet): Record<string, any>[] {
    return result.rows.map((row) => {
      const obj: Record<string, any> = {};
      result.columns.forEach((col, i) => {
        obj[col] = row[i];
      });
      return obj;
    });
  }

  // ========================================================================
  // APPLICATION OPERATIONS
  // ========================================================================

  /**
   * Create a new job application
   */
  async createApplication(app: ApplicationCreate): Promise<Application> {
    const query = `
      INSERT INTO applications (
        company, position, job_url, job_description, location,
        salary_range, employment_type, applied_date, status, source,
        resume_version, cover_letter_used, keywords_targeted,
        last_contact_date, next_followup_date, notes,
        resume_path, cover_letter_path
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      RETURNING *
    `;

    const result = await this.client.execute({
      sql: query,
      args: [
        app.company,
        app.position,
        app.job_url ?? null,
        app.job_description ?? null,
        app.location ?? null,
        app.salary_range ?? null,
        app.employment_type,
        app.applied_date,
        app.status,
        app.source ?? null,
        app.resume_version ?? null,
        app.cover_letter_used ? 1 : 0,
        app.keywords_targeted ?? null,
        app.last_contact_date ?? null,
        app.next_followup_date ?? null,
        app.notes ?? null,
        app.resume_path ?? null,
        app.cover_letter_path ?? null,
      ],
    });

    const rows = this.resultToRows(result);
    const firstRow = rows[0];
    if (!firstRow) {
      throw new Error('Failed to create application');
    }
    return this.parseRow<Application>(firstRow, ApplicationSchema);
  }

  /**
   * Get application by ID
   */
  async getApplication(applicationId: number): Promise<Application | null> {
    const result = await this.client.execute({
      sql: 'SELECT * FROM applications WHERE id = ?',
      args: [applicationId],
    });

    const rows = this.resultToRows(result);
    const firstRow = rows[0];
    if (!firstRow) {
      return null;
    }

    return this.parseRow<Application>(firstRow, ApplicationSchema);
  }

  /**
   * Get applications with optional filters
   */
  async getApplications(filters: QueryFilters = {}): Promise<Application[]> {
    const { status, company, limit = 100, offset = 0, orderBy = 'applied_date DESC' } = filters;

    const conditions: string[] = [];
    const args: any[] = [];

    if (status) {
      conditions.push('status = ?');
      args.push(status);
    }

    if (company) {
      conditions.push('company LIKE ?');
      args.push(`%${company}%`);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    const query = `
      SELECT * FROM applications
      ${whereClause}
      ORDER BY ${orderBy}
      LIMIT ? OFFSET ?
    `;

    args.push(limit, offset);

    const result = await this.client.execute({
      sql: query,
      args,
    });

    const rows = this.resultToRows(result);
    return this.parseRows<Application>(rows, ApplicationSchema);
  }

  /**
   * Update an application
   */
  async updateApplication(
    applicationId: number,
    update: ApplicationUpdate
  ): Promise<Application | null> {
    const updateEntries = Object.entries(update).filter(([_, value]) => value !== undefined);

    if (updateEntries.length === 0) {
      return this.getApplication(applicationId);
    }

    const setClauses = updateEntries.map(([key]) => `${key} = ?`);
    const args: (string | boolean | number | null)[] = updateEntries.map(([key, value]) => {
      if (key === 'cover_letter_used' && typeof value === 'boolean') {
        return value ? 1 : 0;
      }
      return value ?? null;
    });

    args.push(applicationId);

    const query = `
      UPDATE applications
      SET ${setClauses.join(', ')}
      WHERE id = ?
      RETURNING *
    `;

    const result = await this.client.execute({
      sql: query,
      args,
    });

    const rows = this.resultToRows(result);
    const firstRow = rows[0];
    if (!firstRow) {
      return null;
    }

    return this.parseRow<Application>(firstRow, ApplicationSchema);
  }

  /**
   * Delete an application (cascades to interviews and stages)
   */
  async deleteApplication(applicationId: number): Promise<boolean> {
    const result = await this.client.execute({
      sql: 'DELETE FROM applications WHERE id = ?',
      args: [applicationId],
    });

    return result.rowsAffected > 0;
  }

  // ========================================================================
  // INTERVIEW OPERATIONS
  // ========================================================================

  /**
   * Create a new interview
   */
  async createInterview(interview: InterviewCreate): Promise<Interview> {
    const query = `
      INSERT INTO interviews (
        application_id, interview_date, interview_time, duration_minutes,
        interview_type, round_number, interviewer_name, interviewer_title,
        interviewer_email, panel_size, questions_asked, topics_covered,
        technical_assessment, result, feedback_received, personal_notes,
        areas_to_improve, location, meeting_link, timezone
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      RETURNING *
    `;

    const result = await this.client.execute({
      sql: query,
      args: [
        interview.application_id,
        interview.interview_date,
        interview.interview_time ?? null,
        interview.duration_minutes ?? null,
        interview.interview_type,
        interview.round_number,
        interview.interviewer_name ?? null,
        interview.interviewer_title ?? null,
        interview.interviewer_email ?? null,
        interview.panel_size,
        interview.questions_asked ?? null,
        interview.topics_covered ?? null,
        interview.technical_assessment ?? null,
        interview.result ?? null,
        interview.feedback_received ?? null,
        interview.personal_notes ?? null,
        interview.areas_to_improve ?? null,
        interview.location ?? null,
        interview.meeting_link ?? null,
        interview.timezone ?? null,
      ],
    });

    const rows = this.resultToRows(result);
    const firstRow = rows[0];
    if (!firstRow) {
      throw new Error('Failed to create interview');
    }
    return this.parseRow<Interview>(firstRow, InterviewSchema);
  }

  /**
   * Get interviews with optional application filter
   */
  async getInterviews(
    applicationId?: number,
    limit: number = 100,
    offset: number = 0
  ): Promise<Interview[]> {
    let query: string;
    let args: any[];

    if (applicationId) {
      query = `
        SELECT * FROM interviews
        WHERE application_id = ?
        ORDER BY interview_date DESC
        LIMIT ? OFFSET ?
      `;
      args = [applicationId, limit, offset];
    } else {
      query = `
        SELECT * FROM interviews
        ORDER BY interview_date DESC
        LIMIT ? OFFSET ?
      `;
      args = [limit, offset];
    }

    const result = await this.client.execute({ sql: query, args });
    const rows = this.resultToRows(result);
    return this.parseRows<Interview>(rows, InterviewSchema);
  }

  /**
   * Update an interview
   */
  async updateInterview(interviewId: number, update: InterviewUpdate): Promise<Interview | null> {
    const updateEntries = Object.entries(update).filter(([_, value]) => value !== undefined);

    if (updateEntries.length === 0) {
      const result = await this.client.execute({
        sql: 'SELECT * FROM interviews WHERE id = ?',
        args: [interviewId],
      });
      const rows = this.resultToRows(result);
      const firstRow = rows[0];
      return firstRow ? this.parseRow<Interview>(firstRow, InterviewSchema) : null;
    }

    const setClauses = updateEntries.map(([key]) => `${key} = ?`);
    const args = updateEntries.map(([_, value]) => value ?? null);
    args.push(interviewId);

    const query = `
      UPDATE interviews
      SET ${setClauses.join(', ')}
      WHERE id = ?
      RETURNING *
    `;

    const result = await this.client.execute({ sql: query, args });
    const rows = this.resultToRows(result);
    const firstRow = rows[0];
    return firstRow ? this.parseRow<Interview>(firstRow, InterviewSchema) : null;
  }

  // ========================================================================
  // APPLICATION STAGE OPERATIONS
  // ========================================================================

  /**
   * Get stage history for an application
   */
  async getApplicationStages(applicationId: number): Promise<ApplicationStage[]> {
    const result = await this.client.execute({
      sql: `
        SELECT * FROM application_stages
        WHERE application_id = ?
        ORDER BY stage_date DESC, created_at DESC
      `,
      args: [applicationId],
    });

    const rows = this.resultToRows(result);
    return this.parseRows<ApplicationStage>(rows, ApplicationStageSchema);
  }

  // ========================================================================
  // METRICS OPERATIONS
  // ========================================================================

  /**
   * Get metrics for date range
   */
  async getMetrics(filters: DateRange & { limit?: number } = {}): Promise<Metrics[]> {
    const { startDate, endDate, limit = 30 } = filters;

    const conditions: string[] = [];
    const args: any[] = [];

    if (startDate) {
      conditions.push('metric_date >= ?');
      args.push(startDate);
    }

    if (endDate) {
      conditions.push('metric_date <= ?');
      args.push(endDate);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    const query = `
      SELECT * FROM metrics
      ${whereClause}
      ORDER BY metric_date DESC
      LIMIT ?
    `;

    args.push(limit);

    const result = await this.client.execute({ sql: query, args });
    const rows = this.resultToRows(result);
    return this.parseRows<Metrics>(rows, MetricsSchema);
  }

  /**
   * Create or update metrics for a date
   */
  async upsertMetrics(metrics: MetricsCreate): Promise<Metrics> {
    const query = `
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
    `;

    const result = await this.client.execute({
      sql: query,
      args: [
        metrics.metric_date,
        metrics.total_applications,
        metrics.applications_sent_today,
        metrics.total_responses,
        metrics.response_rate,
        metrics.total_interviews,
        metrics.interview_rate,
        metrics.total_offers,
        metrics.offer_rate,
        metrics.total_rejections,
        metrics.avg_response_time_days,
        metrics.avg_time_to_interview_days,
        metrics.avg_time_to_offer_days,
        metrics.active_applications,
        metrics.pending_followups,
      ],
    });

    const rows = this.resultToRows(result);
    const firstRow = rows[0];
    if (!firstRow) {
      throw new Error('Failed to upsert metrics');
    }
    return this.parseRow<Metrics>(firstRow, MetricsSchema);
  }

  // ========================================================================
  // KEYWORD PERFORMANCE OPERATIONS
  // ========================================================================

  /**
   * Create or update keyword performance
   */
  async upsertKeywordPerformance(
    keywordPerf: KeywordPerformanceCreate
  ): Promise<KeywordPerformance> {
    const query = `
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
    `;

    const result = await this.client.execute({
      sql: query,
      args: [
        keywordPerf.keyword,
        keywordPerf.total_uses,
        keywordPerf.response_count,
        keywordPerf.response_rate,
        keywordPerf.interview_count,
        keywordPerf.interview_rate,
        keywordPerf.offer_count,
        keywordPerf.offer_rate,
        keywordPerf.category ?? null,
        keywordPerf.last_used_date ?? null,
      ],
    });

    const rows = this.resultToRows(result);
    const firstRow = rows[0];
    if (!firstRow) {
      throw new Error('Failed to upsert keyword performance');
    }
    return this.parseRow<KeywordPerformance>(firstRow, KeywordPerformanceSchema);
  }

  /**
   * Get top performing keywords
   */
  async getTopKeywords(limit: number = 20): Promise<TopKeyword[]> {
    const result = await this.client.execute({
      sql: 'SELECT * FROM v_top_keywords LIMIT ?',
      args: [limit],
    });

    const rows = this.resultToRows(result);
    return this.parseRows<TopKeyword>(rows, TopKeywordSchema);
  }

  // ========================================================================
  // VIEW QUERIES
  // ========================================================================

  /**
   * Get active applications with interview counts
   */
  async getActiveApplications(limit: number = 100): Promise<ActiveApplication[]> {
    const result = await this.client.execute({
      sql: 'SELECT * FROM v_active_applications LIMIT ?',
      args: [limit],
    });

    const rows = this.resultToRows(result);
    return this.parseRows<ActiveApplication>(rows, ActiveApplicationSchema);
  }

  /**
   * Get application pipeline summary
   */
  async getPipelineSummary(): Promise<PipelineSummary[]> {
    const result = await this.client.execute({
      sql: 'SELECT * FROM v_pipeline_summary',
      args: [],
    });

    const rows = this.resultToRows(result);
    return this.parseRows<PipelineSummary>(rows, PipelineSummarySchema);
  }

  /**
   * Get interview performance by company
   */
  async getInterviewPerformance(): Promise<InterviewPerformance[]> {
    const result = await this.client.execute({
      sql: 'SELECT * FROM v_interview_performance',
      args: [],
    });

    const rows = this.resultToRows(result);
    return this.parseRows<InterviewPerformance>(rows, InterviewPerformanceSchema);
  }

  // ========================================================================
  // RAW QUERY EXECUTION
  // ========================================================================

  /**
   * Execute raw SQL query
   */
  async execute(query: string, args: any[] = []): Promise<ResultSet> {
    return this.client.execute({ sql: query, args });
  }
}
