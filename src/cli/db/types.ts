/**
 * TypeScript types and Zod schemas for job application tracking system.
 * Provides type-safe data validation for Turso database operations.
 */

import { z } from 'zod';

// ============================================================================
// ENUMS AND CONSTANTS
// ============================================================================

export const ApplicationStatus = {
  APPLIED: 'applied',
  SCREENING: 'screening',
  INTERVIEWING: 'interviewing',
  OFFER: 'offer',
  REJECTED: 'rejected',
  ACCEPTED: 'accepted',
  WITHDRAWN: 'withdrawn',
} as const;

export type ApplicationStatus = (typeof ApplicationStatus)[keyof typeof ApplicationStatus];

export const EmploymentType = {
  FULL_TIME: 'Full-time',
  PART_TIME: 'Part-time',
  CONTRACT: 'Contract',
  INTERNSHIP: 'Internship',
  FREELANCE: 'Freelance',
} as const;

export type EmploymentType = (typeof EmploymentType)[keyof typeof EmploymentType];

export const InterviewType = {
  PHONE: 'phone',
  VIDEO: 'video',
  ONSITE: 'onsite',
  TECHNICAL: 'technical',
  BEHAVIORAL: 'behavioral',
  PANEL: 'panel',
  HR: 'hr',
  CASE_STUDY: 'case_study',
  PRESENTATION: 'presentation',
} as const;

export type InterviewType = (typeof InterviewType)[keyof typeof InterviewType];

export const InterviewResult = {
  PASSED: 'passed',
  FAILED: 'failed',
  PENDING: 'pending',
  CANCELLED: 'cancelled',
} as const;

export type InterviewResult = (typeof InterviewResult)[keyof typeof InterviewResult];

export const KeywordCategory = {
  TECHNICAL_SKILL: 'technical_skill',
  SOFT_SKILL: 'soft_skill',
  CERTIFICATION: 'certification',
  TOOL: 'tool',
  FRAMEWORK: 'framework',
  DOMAIN: 'domain',
  LANGUAGE: 'language',
  METHODOLOGY: 'methodology',
} as const;

export type KeywordCategory = (typeof KeywordCategory)[keyof typeof KeywordCategory];

// ============================================================================
// ZOD SCHEMAS - APPLICATIONS
// ============================================================================

export const ApplicationBaseSchema = z.object({
  company: z.string().min(1).max(255),
  position: z.string().min(1).max(255),
  job_url: z.string().url().optional().nullable(),
  job_description: z.string().optional().nullable(),
  location: z.string().optional().nullable(),
  salary_range: z.string().optional().nullable(),
  employment_type: z
    .enum([
      EmploymentType.FULL_TIME,
      EmploymentType.PART_TIME,
      EmploymentType.CONTRACT,
      EmploymentType.INTERNSHIP,
      EmploymentType.FREELANCE,
    ])
    .default(EmploymentType.FULL_TIME),
  applied_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be in YYYY-MM-DD format'),
  status: z
    .enum([
      ApplicationStatus.APPLIED,
      ApplicationStatus.SCREENING,
      ApplicationStatus.INTERVIEWING,
      ApplicationStatus.OFFER,
      ApplicationStatus.REJECTED,
      ApplicationStatus.ACCEPTED,
      ApplicationStatus.WITHDRAWN,
    ])
    .default(ApplicationStatus.APPLIED),
  source: z.string().optional().nullable(),
  resume_version: z.string().optional().nullable(),
  cover_letter_used: z.boolean().default(false),
  keywords_targeted: z.string().optional().nullable(), // JSON array string
  last_contact_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/)
    .optional()
    .nullable(),
  next_followup_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/)
    .optional()
    .nullable(),
  notes: z.string().optional().nullable(),
  resume_path: z.string().optional().nullable(),
  cover_letter_path: z.string().optional().nullable(),
});

export const ApplicationSchema = ApplicationBaseSchema.extend({
  id: z.number().int().positive(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const ApplicationCreateSchema = ApplicationBaseSchema;

export const ApplicationUpdateSchema = ApplicationBaseSchema.partial();

export type ApplicationBase = z.infer<typeof ApplicationBaseSchema>;
export type Application = z.infer<typeof ApplicationSchema>;
export type ApplicationCreate = z.infer<typeof ApplicationCreateSchema>;
export type ApplicationUpdate = z.infer<typeof ApplicationUpdateSchema>;

// ============================================================================
// ZOD SCHEMAS - INTERVIEWS
// ============================================================================

export const InterviewBaseSchema = z.object({
  application_id: z.number().int().positive(),
  interview_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be in YYYY-MM-DD format'),
  interview_time: z
    .string()
    .regex(/^\d{2}:\d{2}$/)
    .optional()
    .nullable(),
  duration_minutes: z.number().int().nonnegative().optional().nullable(),
  interview_type: z.enum([
    InterviewType.PHONE,
    InterviewType.VIDEO,
    InterviewType.ONSITE,
    InterviewType.TECHNICAL,
    InterviewType.BEHAVIORAL,
    InterviewType.PANEL,
    InterviewType.HR,
    InterviewType.CASE_STUDY,
    InterviewType.PRESENTATION,
  ]),
  round_number: z.number().int().positive().default(1),
  interviewer_name: z.string().optional().nullable(),
  interviewer_title: z.string().optional().nullable(),
  interviewer_email: z.string().email().optional().nullable(),
  panel_size: z.number().int().positive().default(1),
  questions_asked: z.string().optional().nullable(),
  topics_covered: z.string().optional().nullable(),
  technical_assessment: z.string().optional().nullable(),
  result: z
    .enum([
      InterviewResult.PASSED,
      InterviewResult.FAILED,
      InterviewResult.PENDING,
      InterviewResult.CANCELLED,
    ])
    .optional()
    .nullable(),
  feedback_received: z.string().optional().nullable(),
  personal_notes: z.string().optional().nullable(),
  areas_to_improve: z.string().optional().nullable(),
  location: z.string().optional().nullable(),
  meeting_link: z.string().url().optional().nullable(),
  timezone: z.string().optional().nullable(),
});

export const InterviewSchema = InterviewBaseSchema.extend({
  id: z.number().int().positive(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const InterviewCreateSchema = InterviewBaseSchema;

export const InterviewUpdateSchema = InterviewBaseSchema.partial().omit({ application_id: true });

export type InterviewBase = z.infer<typeof InterviewBaseSchema>;
export type Interview = z.infer<typeof InterviewSchema>;
export type InterviewCreate = z.infer<typeof InterviewCreateSchema>;
export type InterviewUpdate = z.infer<typeof InterviewUpdateSchema>;

// ============================================================================
// ZOD SCHEMAS - APPLICATION STAGES
// ============================================================================

export const ApplicationStageBaseSchema = z.object({
  application_id: z.number().int().positive(),
  status: z.enum([
    ApplicationStatus.APPLIED,
    ApplicationStatus.SCREENING,
    ApplicationStatus.INTERVIEWING,
    ApplicationStatus.OFFER,
    ApplicationStatus.REJECTED,
    ApplicationStatus.ACCEPTED,
    ApplicationStatus.WITHDRAWN,
  ]),
  stage_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  notes: z.string().optional().nullable(),
  changed_by: z.string().default('manual'),
});

export const ApplicationStageSchema = ApplicationStageBaseSchema.extend({
  id: z.number().int().positive(),
  created_at: z.string(),
});

export const ApplicationStageCreateSchema = ApplicationStageBaseSchema;

export type ApplicationStageBase = z.infer<typeof ApplicationStageBaseSchema>;
export type ApplicationStage = z.infer<typeof ApplicationStageSchema>;
export type ApplicationStageCreate = z.infer<typeof ApplicationStageCreateSchema>;

// ============================================================================
// ZOD SCHEMAS - METRICS
// ============================================================================

export const MetricsBaseSchema = z.object({
  metric_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  total_applications: z.number().int().nonnegative().default(0),
  applications_sent_today: z.number().int().nonnegative().default(0),
  total_responses: z.number().int().nonnegative().default(0),
  response_rate: z.number().min(0).max(100).default(0),
  total_interviews: z.number().int().nonnegative().default(0),
  interview_rate: z.number().min(0).max(100).default(0),
  total_offers: z.number().int().nonnegative().default(0),
  offer_rate: z.number().min(0).max(100).default(0),
  total_rejections: z.number().int().nonnegative().default(0),
  avg_response_time_days: z.number().nonnegative().default(0),
  avg_time_to_interview_days: z.number().nonnegative().default(0),
  avg_time_to_offer_days: z.number().nonnegative().default(0),
  active_applications: z.number().int().nonnegative().default(0),
  pending_followups: z.number().int().nonnegative().default(0),
});

export const MetricsSchema = MetricsBaseSchema.extend({
  id: z.number().int().positive(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const MetricsCreateSchema = MetricsBaseSchema;

export const MetricsUpdateSchema = MetricsBaseSchema.partial().omit({ metric_date: true });

export type MetricsBase = z.infer<typeof MetricsBaseSchema>;
export type Metrics = z.infer<typeof MetricsSchema>;
export type MetricsCreate = z.infer<typeof MetricsCreateSchema>;
export type MetricsUpdate = z.infer<typeof MetricsUpdateSchema>;

// ============================================================================
// ZOD SCHEMAS - KEYWORD PERFORMANCE
// ============================================================================

export const KeywordPerformanceBaseSchema = z.object({
  keyword: z.string().min(1),
  total_uses: z.number().int().nonnegative().default(0),
  response_count: z.number().int().nonnegative().default(0),
  response_rate: z.number().min(0).max(100).default(0),
  interview_count: z.number().int().nonnegative().default(0),
  interview_rate: z.number().min(0).max(100).default(0),
  offer_count: z.number().int().nonnegative().default(0),
  offer_rate: z.number().min(0).max(100).default(0),
  category: z
    .enum([
      KeywordCategory.TECHNICAL_SKILL,
      KeywordCategory.SOFT_SKILL,
      KeywordCategory.CERTIFICATION,
      KeywordCategory.TOOL,
      KeywordCategory.FRAMEWORK,
      KeywordCategory.DOMAIN,
      KeywordCategory.LANGUAGE,
      KeywordCategory.METHODOLOGY,
    ])
    .optional()
    .nullable(),
  last_used_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/)
    .optional()
    .nullable(),
});

export const KeywordPerformanceSchema = KeywordPerformanceBaseSchema.extend({
  id: z.number().int().positive(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const KeywordPerformanceCreateSchema = KeywordPerformanceBaseSchema;

export const KeywordPerformanceUpdateSchema = KeywordPerformanceBaseSchema.partial().omit({
  keyword: true,
});

export type KeywordPerformanceBase = z.infer<typeof KeywordPerformanceBaseSchema>;
export type KeywordPerformance = z.infer<typeof KeywordPerformanceSchema>;
export type KeywordPerformanceCreate = z.infer<typeof KeywordPerformanceCreateSchema>;
export type KeywordPerformanceUpdate = z.infer<typeof KeywordPerformanceUpdateSchema>;

// ============================================================================
// VIEW TYPES
// ============================================================================

export const ActiveApplicationSchema = ApplicationSchema.extend({
  interview_count: z.number().int().nonnegative(),
  latest_interview_date: z.string().nullable(),
  latest_interview_type: z.string().nullable(),
});

export const PipelineSummarySchema = z.object({
  status: z.enum([
    ApplicationStatus.APPLIED,
    ApplicationStatus.SCREENING,
    ApplicationStatus.INTERVIEWING,
    ApplicationStatus.OFFER,
    ApplicationStatus.REJECTED,
    ApplicationStatus.ACCEPTED,
    ApplicationStatus.WITHDRAWN,
  ]),
  count: z.number().int().nonnegative(),
  percentage: z.number().min(0).max(100),
});

export const InterviewPerformanceSchema = z.object({
  company: z.string(),
  total_applications: z.number().int().nonnegative(),
  total_interviews: z.number().int().nonnegative(),
  interviews_per_application: z.number().nonnegative(),
  avg_rounds: z.number().nonnegative().nullable(),
});

export const TopKeywordSchema = z.object({
  keyword: z.string(),
  category: z
    .enum([
      KeywordCategory.TECHNICAL_SKILL,
      KeywordCategory.SOFT_SKILL,
      KeywordCategory.CERTIFICATION,
      KeywordCategory.TOOL,
      KeywordCategory.FRAMEWORK,
      KeywordCategory.DOMAIN,
      KeywordCategory.LANGUAGE,
      KeywordCategory.METHODOLOGY,
    ])
    .nullable(),
  total_uses: z.number().int().nonnegative(),
  response_rate: z.number().min(0).max(100),
  interview_rate: z.number().min(0).max(100),
  offer_rate: z.number().min(0).max(100),
});

export type ActiveApplication = z.infer<typeof ActiveApplicationSchema>;
export type PipelineSummary = z.infer<typeof PipelineSummarySchema>;
export type InterviewPerformance = z.infer<typeof InterviewPerformanceSchema>;
export type TopKeyword = z.infer<typeof TopKeywordSchema>;

// ============================================================================
// UTILITY TYPES
// ============================================================================

export interface QueryFilters {
  status?: ApplicationStatus;
  company?: string;
  limit?: number;
  offset?: number;
  orderBy?: string;
}

export interface DateRange {
  startDate?: string;
  endDate?: string;
}

export interface PaginationParams {
  limit?: number;
  offset?: number;
}
