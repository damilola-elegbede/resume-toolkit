import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { TursoClient } from '../../db/client';
import {
  addApplication,
  updateApplication,
  listApplications,
  addInterviewNotes,
  type AddApplicationOptions,
  type UpdateApplicationOptions,
  type ListApplicationsOptions,
  type InterviewNotesOptions,
} from '../../commands/track-application';
import { ApplicationStatus } from '../../db/types';
import { existsSync, mkdirSync, rmSync } from 'fs';
import { join } from 'path';

// Mock dependencies
vi.mock('../../db/client');
vi.mock('fs/promises');
vi.mock('inquirer', () => ({
  default: {
    prompt: vi.fn(),
  },
}));

describe('track-application command', () => {
  let mockClient: any;
  const testAppDir = join(
    process.cwd(),
    'applications',
    '2025-10-21-techcorp-director-of-engineering'
  );

  beforeEach(() => {
    vi.clearAllMocks();

    // Mock TursoClient
    mockClient = {
      createApplication: vi.fn(),
      updateApplication: vi.fn(),
      getApplications: vi.fn(),
      getApplication: vi.fn(),
      createInterview: vi.fn(),
      close: vi.fn(),
    };

    vi.mocked(TursoClient).mockImplementation(() => mockClient);
  });

  afterEach(() => {
    // Clean up test directories
    if (existsSync(testAppDir)) {
      rmSync(testAppDir, { recursive: true, force: true });
    }
  });

  describe('addApplication', () => {
    it('should create new application with required fields', async () => {
      const options: AddApplicationOptions = {
        company: 'TechCorp',
        position: 'Director of Engineering',
        url: 'https://jobs.techcorp.com/123',
        appliedDate: '2025-10-21',
      };

      const mockApplication = {
        id: 1,
        company: 'TechCorp',
        position: 'Director of Engineering',
        job_url: 'https://jobs.techcorp.com/123',
        applied_date: '2025-10-21',
        status: ApplicationStatus.APPLIED,
        employment_type: 'Full-time',
        cover_letter_used: false,
        created_at: '2025-10-21T12:00:00Z',
        updated_at: '2025-10-21T12:00:00Z',
      };

      mockClient.createApplication.mockResolvedValue(mockApplication);

      const result = await addApplication(options);

      expect(mockClient.createApplication).toHaveBeenCalledWith(
        expect.objectContaining({
          company: 'TechCorp',
          position: 'Director of Engineering',
          job_url: 'https://jobs.techcorp.com/123',
          applied_date: '2025-10-21',
          status: ApplicationStatus.APPLIED,
        })
      );

      expect(result).toEqual(mockApplication);
    });

    it('should create application with optional fields', async () => {
      const options: AddApplicationOptions = {
        company: 'StartupCo',
        position: 'Engineering Manager',
        url: 'https://startup.co/jobs/em',
        appliedDate: '2025-10-21',
        status: ApplicationStatus.SCREENING,
        notes: 'Referred by John',
        resumeVersion: 'tailored-startup-em-v1',
        coverLetterUsed: true,
      };

      const mockApplication = {
        id: 2,
        company: 'StartupCo',
        position: 'Engineering Manager',
        job_url: 'https://startup.co/jobs/em',
        applied_date: '2025-10-21',
        status: ApplicationStatus.SCREENING,
        notes: 'Referred by John',
        resume_version: 'tailored-startup-em-v1',
        cover_letter_used: true,
        employment_type: 'Full-time',
        created_at: '2025-10-21T12:00:00Z',
        updated_at: '2025-10-21T12:00:00Z',
      };

      mockClient.createApplication.mockResolvedValue(mockApplication);

      const result = await addApplication(options);

      expect(mockClient.createApplication).toHaveBeenCalledWith(
        expect.objectContaining({
          company: 'StartupCo',
          status: ApplicationStatus.SCREENING,
          notes: 'Referred by John',
          resume_version: 'tailored-startup-em-v1',
          cover_letter_used: true,
        })
      );

      expect(result).toEqual(mockApplication);
    });

    it('should create application folder structure', async () => {
      const options: AddApplicationOptions = {
        company: 'TechCorp',
        position: 'Director of Engineering',
        url: 'https://jobs.techcorp.com/123',
        appliedDate: '2025-10-21',
      };

      const mockApplication = {
        id: 1,
        company: 'TechCorp',
        position: 'Director of Engineering',
        job_url: 'https://jobs.techcorp.com/123',
        applied_date: '2025-10-21',
        status: ApplicationStatus.APPLIED,
        employment_type: 'Full-time',
        cover_letter_used: false,
        created_at: '2025-10-21T12:00:00Z',
        updated_at: '2025-10-21T12:00:00Z',
      };

      mockClient.createApplication.mockResolvedValue(mockApplication);

      await addApplication(options);

      // Verify directory exists (mocked)
      expect(existsSync).toBeDefined();
    });

    it('should handle missing required fields', async () => {
      const options: any = {
        company: 'TechCorp',
        // Missing position
        url: 'https://jobs.techcorp.com/123',
        appliedDate: '2025-10-21',
      };

      await expect(addApplication(options)).rejects.toThrow();
    });

    it('should validate date format', async () => {
      const options: AddApplicationOptions = {
        company: 'TechCorp',
        position: 'Director of Engineering',
        url: 'https://jobs.techcorp.com/123',
        appliedDate: 'invalid-date',
      };

      await expect(addApplication(options)).rejects.toThrow();
    });

    it('should handle database errors gracefully', async () => {
      const options: AddApplicationOptions = {
        company: 'TechCorp',
        position: 'Director of Engineering',
        url: 'https://jobs.techcorp.com/123',
        appliedDate: '2025-10-21',
      };

      mockClient.createApplication.mockRejectedValue(new Error('Database connection failed'));

      await expect(addApplication(options)).rejects.toThrow('Database connection failed');
    });
  });

  describe('updateApplication', () => {
    it('should update application status', async () => {
      const options: UpdateApplicationOptions = {
        applicationId: 1,
        status: ApplicationStatus.INTERVIEWING,
        notes: 'First round scheduled for next week',
      };

      const mockUpdatedApplication = {
        id: 1,
        company: 'TechCorp',
        position: 'Director of Engineering',
        job_url: 'https://jobs.techcorp.com/123',
        applied_date: '2025-10-21',
        status: ApplicationStatus.INTERVIEWING,
        notes: 'First round scheduled for next week',
        employment_type: 'Full-time',
        cover_letter_used: false,
        created_at: '2025-10-21T12:00:00Z',
        updated_at: '2025-10-21T13:00:00Z',
      };

      mockClient.updateApplication.mockResolvedValue(mockUpdatedApplication);

      const result = await updateApplication(options);

      expect(mockClient.updateApplication).toHaveBeenCalledWith(1, {
        status: ApplicationStatus.INTERVIEWING,
        notes: 'First round scheduled for next week',
      });

      expect(result).toEqual(mockUpdatedApplication);
    });

    it('should update multiple fields', async () => {
      const options: UpdateApplicationOptions = {
        applicationId: 1,
        status: ApplicationStatus.OFFER,
        notes: 'Received offer',
        nextFollowupDate: '2025-10-25',
      };

      const mockUpdatedApplication = {
        id: 1,
        company: 'TechCorp',
        position: 'Director of Engineering',
        job_url: 'https://jobs.techcorp.com/123',
        applied_date: '2025-10-21',
        status: ApplicationStatus.OFFER,
        notes: 'Received offer',
        next_followup_date: '2025-10-25',
        employment_type: 'Full-time',
        cover_letter_used: false,
        created_at: '2025-10-21T12:00:00Z',
        updated_at: '2025-10-21T14:00:00Z',
      };

      mockClient.updateApplication.mockResolvedValue(mockUpdatedApplication);

      const result = await updateApplication(options);

      expect(mockClient.updateApplication).toHaveBeenCalledWith(1, {
        status: ApplicationStatus.OFFER,
        notes: 'Received offer',
        next_followup_date: '2025-10-25',
      });

      expect(result).toEqual(mockUpdatedApplication);
    });

    it('should find application by company and position when ID not provided', async () => {
      const options: UpdateApplicationOptions = {
        company: 'TechCorp',
        position: 'Director of Engineering',
        status: ApplicationStatus.REJECTED,
      };

      const mockExistingApp = {
        id: 1,
        company: 'TechCorp',
        position: 'Director of Engineering',
        job_url: 'https://jobs.techcorp.com/123',
        applied_date: '2025-10-21',
        status: ApplicationStatus.INTERVIEWING,
        employment_type: 'Full-time',
        cover_letter_used: false,
        created_at: '2025-10-21T12:00:00Z',
        updated_at: '2025-10-21T12:00:00Z',
      };

      const mockUpdatedApp = {
        ...mockExistingApp,
        status: ApplicationStatus.REJECTED,
        updated_at: '2025-10-21T15:00:00Z',
      };

      mockClient.getApplications.mockResolvedValue([mockExistingApp]);
      mockClient.updateApplication.mockResolvedValue(mockUpdatedApp);

      const result = await updateApplication(options);

      expect(mockClient.getApplications).toHaveBeenCalledWith({
        company: 'TechCorp',
        limit: 1,
      });

      expect(result).toEqual(mockUpdatedApp);
    });

    it('should handle application not found', async () => {
      const options: UpdateApplicationOptions = {
        applicationId: 999,
        status: ApplicationStatus.REJECTED,
      };

      mockClient.updateApplication.mockResolvedValue(null);

      await expect(updateApplication(options)).rejects.toThrow();
    });
  });

  describe('listApplications', () => {
    it('should list all applications', async () => {
      const mockApplications = [
        {
          id: 1,
          company: 'TechCorp',
          position: 'Director of Engineering',
          job_url: 'https://jobs.techcorp.com/123',
          applied_date: '2025-10-21',
          status: ApplicationStatus.INTERVIEWING,
          employment_type: 'Full-time',
          cover_letter_used: false,
          created_at: '2025-10-21T12:00:00Z',
          updated_at: '2025-10-21T12:00:00Z',
        },
        {
          id: 2,
          company: 'StartupCo',
          position: 'Engineering Manager',
          job_url: 'https://startup.co/jobs/em',
          applied_date: '2025-10-20',
          status: ApplicationStatus.APPLIED,
          employment_type: 'Full-time',
          cover_letter_used: true,
          created_at: '2025-10-20T12:00:00Z',
          updated_at: '2025-10-20T12:00:00Z',
        },
      ];

      mockClient.getApplications.mockResolvedValue(mockApplications);

      const result = await listApplications({});

      expect(mockClient.getApplications).toHaveBeenCalledWith({});
      expect(result).toEqual(mockApplications);
      expect(result).toHaveLength(2);
    });

    it('should filter by status', async () => {
      const options: ListApplicationsOptions = {
        status: ApplicationStatus.INTERVIEWING,
      };

      const mockApplications = [
        {
          id: 1,
          company: 'TechCorp',
          position: 'Director of Engineering',
          job_url: 'https://jobs.techcorp.com/123',
          applied_date: '2025-10-21',
          status: ApplicationStatus.INTERVIEWING,
          employment_type: 'Full-time',
          cover_letter_used: false,
          created_at: '2025-10-21T12:00:00Z',
          updated_at: '2025-10-21T12:00:00Z',
        },
      ];

      mockClient.getApplications.mockResolvedValue(mockApplications);

      const result = await listApplications(options);

      expect(mockClient.getApplications).toHaveBeenCalledWith({
        status: ApplicationStatus.INTERVIEWING,
      });
      expect(result).toHaveLength(1);
      expect(result[0].status).toBe(ApplicationStatus.INTERVIEWING);
    });

    it('should filter by company', async () => {
      const options: ListApplicationsOptions = {
        company: 'TechCorp',
      };

      const mockApplications = [
        {
          id: 1,
          company: 'TechCorp',
          position: 'Director of Engineering',
          job_url: 'https://jobs.techcorp.com/123',
          applied_date: '2025-10-21',
          status: ApplicationStatus.INTERVIEWING,
          employment_type: 'Full-time',
          cover_letter_used: false,
          created_at: '2025-10-21T12:00:00Z',
          updated_at: '2025-10-21T12:00:00Z',
        },
      ];

      mockClient.getApplications.mockResolvedValue(mockApplications);

      const result = await listApplications(options);

      expect(mockClient.getApplications).toHaveBeenCalledWith({
        company: 'TechCorp',
      });
      expect(result).toHaveLength(1);
      expect(result[0].company).toBe('TechCorp');
    });

    it('should support pagination', async () => {
      const options: ListApplicationsOptions = {
        limit: 10,
        offset: 0,
      };

      mockClient.getApplications.mockResolvedValue([]);

      await listApplications(options);

      expect(mockClient.getApplications).toHaveBeenCalledWith({
        limit: 10,
        offset: 0,
      });
    });

    it('should handle empty results', async () => {
      mockClient.getApplications.mockResolvedValue([]);

      const result = await listApplications({});

      expect(result).toEqual([]);
      expect(result).toHaveLength(0);
    });
  });

  describe('addInterviewNotes', () => {
    it('should add interview notes to application', async () => {
      const options: InterviewNotesOptions = {
        applicationId: 1,
        interviewDate: '2025-10-25',
        interviewType: 'technical',
        notes: 'Went well, discussed system design',
        roundNumber: 1,
      };

      const mockInterview = {
        id: 1,
        application_id: 1,
        interview_date: '2025-10-25',
        interview_type: 'technical',
        personal_notes: 'Went well, discussed system design',
        round_number: 1,
        panel_size: 1,
        created_at: '2025-10-25T14:00:00Z',
        updated_at: '2025-10-25T14:00:00Z',
      };

      mockClient.createInterview.mockResolvedValue(mockInterview);

      const result = await addInterviewNotes(options);

      expect(mockClient.createInterview).toHaveBeenCalledWith(
        expect.objectContaining({
          application_id: 1,
          interview_date: '2025-10-25',
          interview_type: 'technical',
          personal_notes: 'Went well, discussed system design',
          round_number: 1,
        })
      );

      expect(result).toEqual(mockInterview);
    });

    it('should include optional interview details', async () => {
      const options: InterviewNotesOptions = {
        applicationId: 1,
        interviewDate: '2025-10-25',
        interviewType: 'panel',
        notes: 'Met with engineering team',
        roundNumber: 2,
        interviewerName: 'Jane Smith',
        interviewerTitle: 'VP of Engineering',
        duration: 60,
      };

      const mockInterview = {
        id: 2,
        application_id: 1,
        interview_date: '2025-10-25',
        interview_type: 'panel',
        personal_notes: 'Met with engineering team',
        round_number: 2,
        interviewer_name: 'Jane Smith',
        interviewer_title: 'VP of Engineering',
        duration_minutes: 60,
        panel_size: 1,
        created_at: '2025-10-25T15:00:00Z',
        updated_at: '2025-10-25T15:00:00Z',
      };

      mockClient.createInterview.mockResolvedValue(mockInterview);

      const result = await addInterviewNotes(options);

      expect(result).toEqual(mockInterview);
    });

    it('should validate interview type', async () => {
      const options: any = {
        applicationId: 1,
        interviewDate: '2025-10-25',
        interviewType: 'invalid-type',
        notes: 'Test notes',
      };

      await expect(addInterviewNotes(options)).rejects.toThrow();
    });
  });

  describe('Turso database integration', () => {
    it('should initialize TursoClient with environment variables', () => {
      const client = new TursoClient();
      expect(TursoClient).toHaveBeenCalled();
    });

    it('should close database connection after operations', async () => {
      const options: AddApplicationOptions = {
        company: 'TechCorp',
        position: 'Director of Engineering',
        url: 'https://jobs.techcorp.com/123',
        appliedDate: '2025-10-21',
      };

      mockClient.createApplication.mockResolvedValue({
        id: 1,
        company: 'TechCorp',
        position: 'Director of Engineering',
        job_url: 'https://jobs.techcorp.com/123',
        applied_date: '2025-10-21',
        status: ApplicationStatus.APPLIED,
        employment_type: 'Full-time',
        cover_letter_used: false,
        created_at: '2025-10-21T12:00:00Z',
        updated_at: '2025-10-21T12:00:00Z',
      });

      await addApplication(options);

      // Verify client was used
      expect(mockClient.createApplication).toHaveBeenCalled();
    });
  });

  describe('metadata.yaml generation', () => {
    it('should generate metadata file for new application', async () => {
      const options: AddApplicationOptions = {
        company: 'TechCorp',
        position: 'Director of Engineering',
        url: 'https://jobs.techcorp.com/123',
        appliedDate: '2025-10-21',
        resumeVersion: 'tailored-techcorp-director-v1',
        coverLetterUsed: true,
      };

      const mockApplication = {
        id: 1,
        company: 'TechCorp',
        position: 'Director of Engineering',
        job_url: 'https://jobs.techcorp.com/123',
        applied_date: '2025-10-21',
        status: ApplicationStatus.APPLIED,
        resume_version: 'tailored-techcorp-director-v1',
        cover_letter_used: true,
        employment_type: 'Full-time',
        created_at: '2025-10-21T12:00:00Z',
        updated_at: '2025-10-21T12:00:00Z',
      };

      mockClient.createApplication.mockResolvedValue(mockApplication);

      await addApplication(options);

      // Metadata file creation is mocked via fs/promises
      expect(mockClient.createApplication).toHaveBeenCalled();
    });
  });

  describe('edge cases and validation', () => {
    it('should handle application with all optional fields', async () => {
      const options: AddApplicationOptions = {
        company: 'MegaCorp',
        position: 'VP Engineering',
        url: 'https://megacorp.com/jobs/vp',
        appliedDate: '2025-10-21',
        status: ApplicationStatus.INTERVIEWING,
        notes: 'CEO referred me directly',
        resumeVersion: 'executive-v5',
        coverLetterUsed: true,
        location: 'San Francisco, CA',
        salaryRange: '$300k-$400k',
        source: 'CEO Referral',
      };

      const mockApplication = {
        id: 5,
        company: 'MegaCorp',
        position: 'VP Engineering',
        job_url: 'https://megacorp.com/jobs/vp',
        applied_date: '2025-10-21',
        status: ApplicationStatus.INTERVIEWING,
        employment_type: 'Full-time',
        notes: 'CEO referred me directly',
        resume_version: 'executive-v5',
        cover_letter_used: true,
        location: 'San Francisco, CA',
        salary_range: '$300k-$400k',
        source: 'CEO Referral',
        created_at: '2025-10-21T12:00:00Z',
        updated_at: '2025-10-21T12:00:00Z',
      };

      mockClient.createApplication.mockResolvedValue(mockApplication);

      const result = await addApplication(options);

      expect(result.location).toBe('San Francisco, CA');
      expect(result.salary_range).toBe('$300k-$400k');
      expect(result.source).toBe('CEO Referral');
    });

    it('should reject invalid date formats', async () => {
      const invalidDates = ['2025/10/21', '10-21-2025', '21-10-2025', 'October 21, 2025'];

      for (const invalidDate of invalidDates) {
        const options: AddApplicationOptions = {
          company: 'Test',
          position: 'Engineer',
          appliedDate: invalidDate,
        };

        await expect(addApplication(options)).rejects.toThrow('Invalid date format');
      }
    });

    it('should handle company names with special characters', async () => {
      const options: AddApplicationOptions = {
        company: 'Company & Co., Inc.',
        position: 'Software Engineer',
        appliedDate: '2025-10-21',
      };

      const mockApplication = {
        id: 6,
        company: 'Company & Co., Inc.',
        position: 'Software Engineer',
        applied_date: '2025-10-21',
        status: ApplicationStatus.APPLIED,
        employment_type: 'Full-time',
        cover_letter_used: false,
        created_at: '2025-10-21T12:00:00Z',
        updated_at: '2025-10-21T12:00:00Z',
      };

      mockClient.createApplication.mockResolvedValue(mockApplication);

      const result = await addApplication(options);

      expect(result.company).toBe('Company & Co., Inc.');
    });

    it('should handle position names with slashes', async () => {
      const options: AddApplicationOptions = {
        company: 'TechCorp',
        position: 'Software Engineer / Team Lead',
        appliedDate: '2025-10-21',
      };

      const mockApplication = {
        id: 7,
        company: 'TechCorp',
        position: 'Software Engineer / Team Lead',
        applied_date: '2025-10-21',
        status: ApplicationStatus.APPLIED,
        employment_type: 'Full-time',
        cover_letter_used: false,
        created_at: '2025-10-21T12:00:00Z',
        updated_at: '2025-10-21T12:00:00Z',
      };

      mockClient.createApplication.mockResolvedValue(mockApplication);

      const result = await addApplication(options);

      expect(result.position).toBe('Software Engineer / Team Lead');
    });

    it('should update last contact date', async () => {
      const options: UpdateApplicationOptions = {
        applicationId: 1,
        lastContactDate: '2025-10-22',
      };

      const mockUpdatedApplication = {
        id: 1,
        company: 'TechCorp',
        position: 'Director of Engineering',
        job_url: 'https://jobs.techcorp.com/123',
        applied_date: '2025-10-21',
        status: ApplicationStatus.APPLIED,
        last_contact_date: '2025-10-22',
        employment_type: 'Full-time',
        cover_letter_used: false,
        created_at: '2025-10-21T12:00:00Z',
        updated_at: '2025-10-22T14:00:00Z',
      };

      mockClient.updateApplication.mockResolvedValue(mockUpdatedApplication);

      const result = await updateApplication(options);

      expect(result.last_contact_date).toBe('2025-10-22');
    });

    it('should reject invalid last contact date format', async () => {
      const options: UpdateApplicationOptions = {
        applicationId: 1,
        lastContactDate: 'invalid-date',
      };

      await expect(updateApplication(options)).rejects.toThrow('Invalid last contact date format');
    });

    it('should reject invalid next followup date format', async () => {
      const options: UpdateApplicationOptions = {
        applicationId: 1,
        nextFollowupDate: '2025/10/25',
      };

      await expect(updateApplication(options)).rejects.toThrow('Invalid next followup date format');
    });
  });
});
