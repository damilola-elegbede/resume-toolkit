/**
 * Track Application Command
 *
 * Manages job application pipeline tracking in Turso database
 */

import { mkdir, writeFile } from 'fs/promises';
import { join } from 'path';

import chalk from 'chalk';
import { Command } from 'commander';
import inquirer from 'inquirer';
import yaml from 'js-yaml';
import ora from 'ora';

import { TursoClient } from '../db/client';
import {
  ApplicationStatus,
  ApplicationStatusType,
  ApplicationCreate,
  ApplicationUpdate,
  Application,
  Interview,
  InterviewCreate,
  InterviewType,
  InterviewTypeType,
} from '../db/types';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface AddApplicationOptions {
  company: string;
  position: string;
  url?: string;
  appliedDate: string;
  status?: ApplicationStatusType;
  notes?: string;
  resumeVersion?: string;
  coverLetterUsed?: boolean;
  location?: string;
  salaryRange?: string;
  source?: string;
}

export interface UpdateApplicationOptions {
  applicationId?: number;
  company?: string;
  position?: string;
  status?: ApplicationStatusType;
  notes?: string;
  nextFollowupDate?: string;
  lastContactDate?: string;
}

export interface ListApplicationsOptions {
  status?: ApplicationStatusType;
  company?: string;
  limit?: number;
  offset?: number;
  orderBy?: string;
}

export interface InterviewNotesOptions {
  applicationId: number;
  interviewDate: string;
  interviewType: InterviewTypeType;
  notes: string;
  roundNumber?: number;
  interviewerName?: string;
  interviewerTitle?: string;
  duration?: number;
  result?: string;
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Sanitize company and role names for filename
 */
function sanitizeForFilename(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

/**
 * Validate date format (YYYY-MM-DD)
 */
function validateDateFormat(date: string): boolean {
  const regex = /^\d{4}-\d{2}-\d{2}$/;
  if (!regex.test(date)) {
    return false;
  }
  const parsed = new Date(date);
  return !isNaN(parsed.getTime());
}

/**
 * Generate application folder path
 */
function generateApplicationFolder(appliedDate: string, company: string, position: string): string {
  const sanitizedCompany = sanitizeForFilename(company);
  const sanitizedPosition = sanitizeForFilename(position);
  return join(
    process.cwd(),
    'applications',
    `${appliedDate}-${sanitizedCompany}-${sanitizedPosition}`
  );
}

/**
 * Generate metadata YAML content
 */
function generateMetadata(application: Application): string {
  const metadata = {
    application_id: `app-${application.applied_date}-${String(application.id).padStart(3, '0')}`,
    company: application.company,
    position: application.position,
    job_url: application.job_url || 'N/A',
    applied_date: application.applied_date,
    status: application.status,
    resume_version: application.resume_version || 'N/A',
    cover_letter_used: application.cover_letter_used ? 'yes' : 'no',
    created_at: application.created_at,
    updated_at: application.updated_at,
  };

  return yaml.dump(metadata);
}

// ============================================================================
// CORE FUNCTIONS
// ============================================================================

/**
 * Add new application to tracking system
 */
export async function addApplication(options: AddApplicationOptions): Promise<Application> {
  // Validate required fields
  if (!options.company || !options.position || !options.appliedDate) {
    throw new Error('Missing required fields: company, position, and appliedDate are required');
  }

  // Validate date format
  if (!validateDateFormat(options.appliedDate)) {
    throw new Error('Invalid date format. Use YYYY-MM-DD format');
  }

  const client = new TursoClient();

  try {
    // Prepare application data
    const applicationData: ApplicationCreate = {
      company: options.company,
      position: options.position,
      job_url: options.url || null,
      applied_date: options.appliedDate,
      status: options.status || ApplicationStatus.APPLIED,
      employment_type: 'Full-time', // Default
      cover_letter_used: options.coverLetterUsed || false,
      resume_version: options.resumeVersion || null,
      notes: options.notes || null,
      location: options.location || null,
      salary_range: options.salaryRange || null,
      source: options.source || null,
    };

    // Create application in database
    const application = await client.createApplication(applicationData);

    // Create application folder structure
    const appFolder = generateApplicationFolder(
      options.appliedDate,
      options.company,
      options.position
    );
    await mkdir(appFolder, { recursive: true });

    // Generate and save metadata.yaml
    const metadataContent = generateMetadata(application);
    const metadataPath = join(appFolder, 'metadata.yaml');
    await writeFile(metadataPath, metadataContent, 'utf-8');

    await client.close();
    return application;
  } catch (error) {
    await client.close();
    throw error;
  }
}

/**
 * Update existing application
 */
export async function updateApplication(options: UpdateApplicationOptions): Promise<Application> {
  const client = new TursoClient();

  try {
    let applicationId = options.applicationId;

    // If no ID provided, find by company and position
    if (!applicationId && options.company) {
      const apps = await client.getApplications({
        company: options.company,
        limit: 1,
      });

      if (apps.length === 0) {
        throw new Error(`No application found for company: ${options.company}`);
      }

      if (apps[0]) {
        applicationId = apps[0].id;
      }
    }

    if (!applicationId) {
      throw new Error('Application ID or company name is required');
    }

    // Prepare update data
    const updateData: ApplicationUpdate = {};

    if (options.status) {
      updateData.status = options.status;
    }

    if (options.notes) {
      updateData.notes = options.notes;
    }

    if (options.nextFollowupDate) {
      if (!validateDateFormat(options.nextFollowupDate)) {
        throw new Error('Invalid next followup date format. Use YYYY-MM-DD');
      }
      updateData.next_followup_date = options.nextFollowupDate;
    }

    if (options.lastContactDate) {
      if (!validateDateFormat(options.lastContactDate)) {
        throw new Error('Invalid last contact date format. Use YYYY-MM-DD');
      }
      updateData.last_contact_date = options.lastContactDate;
    }

    // Update application
    const updatedApplication = await client.updateApplication(applicationId, updateData);

    if (!updatedApplication) {
      throw new Error(`Application with ID ${applicationId} not found`);
    }

    await client.close();
    return updatedApplication;
  } catch (error) {
    await client.close();
    throw error;
  }
}

/**
 * List applications with optional filters
 */
export async function listApplications(options: ListApplicationsOptions): Promise<Application[]> {
  const client = new TursoClient();

  try {
    const filters: any = {};

    if (options.status) {
      filters.status = options.status;
    }

    if (options.company) {
      filters.company = options.company;
    }

    if (options.limit) {
      filters.limit = options.limit;
    }

    if (options.offset !== undefined) {
      filters.offset = options.offset;
    }

    if (options.orderBy) {
      filters.orderBy = options.orderBy;
    }

    const applications = await client.getApplications(filters);

    await client.close();
    return applications;
  } catch (error) {
    await client.close();
    throw error;
  }
}

/**
 * Add interview notes to application
 */
export async function addInterviewNotes(options: InterviewNotesOptions): Promise<Interview> {
  // Validate date format
  if (!validateDateFormat(options.interviewDate)) {
    throw new Error('Invalid interview date format. Use YYYY-MM-DD');
  }

  // Validate interview type
  const validTypes = Object.values(InterviewType);
  if (!validTypes.includes(options.interviewType as any)) {
    throw new Error(`Invalid interview type. Valid types: ${validTypes.join(', ')}`);
  }

  const client = new TursoClient();

  try {
    const interviewData: InterviewCreate = {
      application_id: options.applicationId,
      interview_date: options.interviewDate,
      interview_type: options.interviewType,
      personal_notes: options.notes,
      round_number: options.roundNumber || 1,
      interviewer_name: options.interviewerName || null,
      interviewer_title: options.interviewerTitle || null,
      duration_minutes: options.duration || null,
      result: (options.result as any) || null,
      panel_size: 1, // Default
    };

    const interview = await client.createInterview(interviewData);

    await client.close();
    return interview;
  } catch (error) {
    await client.close();
    throw error;
  }
}

// ============================================================================
// INTERACTIVE PROMPTS
// ============================================================================

/**
 * Interactive prompt for adding application
 */
async function promptAddApplication(): Promise<AddApplicationOptions> {
  const questions = [
    {
      type: 'input',
      name: 'company',
      message: 'Company name:',
      validate: (input: string) => input.length > 0 || 'Company name is required',
    },
    {
      type: 'input',
      name: 'position',
      message: 'Position/Role:',
      validate: (input: string) => input.length > 0 || 'Position is required',
    },
    {
      type: 'input',
      name: 'url',
      message: 'Job posting URL (optional):',
      default: '',
    },
    {
      type: 'input',
      name: 'appliedDate',
      message: 'Applied date (YYYY-MM-DD):',
      default: new Date().toISOString().split('T')[0],
      validate: (input: string) =>
        validateDateFormat(input) || 'Invalid date format. Use YYYY-MM-DD',
    },
    {
      type: 'list',
      name: 'status',
      message: 'Current status:',
      choices: Object.values(ApplicationStatus),
      default: ApplicationStatus.APPLIED,
    },
    {
      type: 'input',
      name: 'resumeVersion',
      message: 'Resume version used (optional):',
      default: '',
    },
    {
      type: 'confirm',
      name: 'coverLetterUsed',
      message: 'Cover letter used?',
      default: false,
    },
    {
      type: 'input',
      name: 'notes',
      message: 'Notes (optional):',
      default: '',
    },
  ] as any;

  const answers: any = await inquirer.prompt(questions);

  return {
    company: answers.company,
    position: answers.position,
    url: answers.url || undefined,
    appliedDate: answers.appliedDate,
    status: answers.status,
    resumeVersion: answers.resumeVersion || undefined,
    coverLetterUsed: answers.coverLetterUsed,
    notes: answers.notes || undefined,
  };
}

/**
 * Format application for display
 */
function formatApplicationDisplay(app: Application): string {
  const statusColors: Record<ApplicationStatusType, string> = {
    [ApplicationStatus.APPLIED]: 'blue',
    [ApplicationStatus.SCREENING]: 'cyan',
    [ApplicationStatus.INTERVIEWING]: 'yellow',
    [ApplicationStatus.OFFER]: 'green',
    [ApplicationStatus.REJECTED]: 'red',
    [ApplicationStatus.ACCEPTED]: 'green',
    [ApplicationStatus.WITHDRAWN]: 'gray',
  };

  const colorName = statusColors[app.status] || 'white';

  const statusDisplay = (() => {
    switch (colorName) {
      case 'blue':
        return chalk.blue(app.status);
      case 'cyan':
        return chalk.cyan(app.status);
      case 'yellow':
        return chalk.yellow(app.status);
      case 'green':
        return chalk.green(app.status);
      case 'red':
        return chalk.red(app.status);
      case 'gray':
        return chalk.gray(app.status);
      default:
        return chalk.white(app.status);
    }
  })();

  return `
${chalk.bold(app.company)} - ${chalk.bold(app.position)}
  ${chalk.gray('ID:')} ${app.id}
  ${chalk.gray('Status:')} ${statusDisplay}
  ${chalk.gray('Applied:')} ${app.applied_date}
  ${chalk.gray('URL:')} ${app.job_url || 'N/A'}
  ${app.notes ? `${chalk.gray('Notes:')} ${app.notes}` : ''}
`;
}

// ============================================================================
// COMMAND DEFINITIONS
// ============================================================================

/**
 * Add application subcommand
 */
const addCommand = new Command('add')
  .description('Add new job application to tracking system')
  .option('-c, --company <company>', 'Company name')
  .option('-p, --position <position>', 'Position/role title')
  .option('-u, --url <url>', 'Job posting URL')
  .option(
    '-d, --applied-date <date>',
    'Applied date (YYYY-MM-DD)',
    new Date().toISOString().split('T')[0]
  )
  .option('-s, --status <status>', 'Application status', ApplicationStatus.APPLIED)
  .option('-r, --resume-version <version>', 'Resume version used')
  .option('--cover-letter', 'Cover letter was used', false)
  .option('-n, --notes <notes>', 'Additional notes')
  .action(async (cmdOptions) => {
    const spinner = ora('Adding application...').start();

    try {
      let options: AddApplicationOptions;

      // Interactive mode if no company/position provided
      if (!cmdOptions.company || !cmdOptions.position) {
        spinner.stop();
        console.log(chalk.blue('\nInteractive Application Entry\n'));
        options = await promptAddApplication();
        spinner.start('Adding application...');
      } else {
        // Validate status string at boundary (ISSUE #16)
        if (cmdOptions.status) {
          const validStatuses = Object.values(ApplicationStatus);
          if (!validStatuses.includes(cmdOptions.status)) {
            spinner.fail('Invalid status');
            console.error(chalk.red(`Error: Invalid status. Valid options: ${validStatuses.join(', ')}` ));
            process.exit(1);
          }
        }

        options = {
          company: cmdOptions.company,
          position: cmdOptions.position,
          url: cmdOptions.url,
          appliedDate: cmdOptions.appliedDate,
          status: cmdOptions.status,
          resumeVersion: cmdOptions.resumeVersion,
          coverLetterUsed: cmdOptions.coverLetter,
          notes: cmdOptions.notes,
        };
      }

      const application = await addApplication(options);

      spinner.succeed('Application added successfully!');

      console.log(formatApplicationDisplay(application));

      const folder = generateApplicationFolder(
        application.applied_date,
        application.company,
        application.position
      );
      console.log(chalk.green(`\nApplication folder: ${folder}\n`));
    } catch (error) {
      spinner.fail('Failed to add application');
      if (error instanceof Error) {
        console.error(chalk.red('Error:'), error.message);
      }
      process.exit(1);
    }
  });

/**
 * Update application subcommand
 */
const updateCommand = new Command('update')
  .description('Update existing job application')
  .argument('[id]', 'Application ID')
  .option('-c, --company <company>', 'Company name (if ID not provided)')
  .option('-s, --status <status>', 'New status')
  .option('-n, --notes <notes>', 'Update notes')
  .option('-f, --followup <date>', 'Next followup date (YYYY-MM-DD)')
  .option('-l, --last-contact <date>', 'Last contact date (YYYY-MM-DD)')
  .action(async (id, cmdOptions) => {
    const spinner = ora('Updating application...').start();

    try {
      // Validate status string at boundary (ISSUE #16)
      if (cmdOptions.status) {
        const validStatuses = Object.values(ApplicationStatus);
        if (!validStatuses.includes(cmdOptions.status)) {
          spinner.fail('Invalid status');
          console.error(chalk.red(`Error: Invalid status. Valid options: ${validStatuses.join(', ')}` ));
          process.exit(1);
        }
      }

      const options: UpdateApplicationOptions = {
        ...(id && { applicationId: parseInt(id) }),
        ...(cmdOptions.company && { company: cmdOptions.company }),
        ...(cmdOptions.status && { status: cmdOptions.status }),
        ...(cmdOptions.notes && { notes: cmdOptions.notes }),
        ...(cmdOptions.followup && { nextFollowupDate: cmdOptions.followup }),
        ...(cmdOptions.lastContact && { lastContactDate: cmdOptions.lastContact }),
      };

      const application = await updateApplication(options);

      spinner.succeed('Application updated successfully!');
      console.log(formatApplicationDisplay(application));
    } catch (error) {
      spinner.fail('Failed to update application');
      if (error instanceof Error) {
        console.error(chalk.red('Error:'), error.message);
      }
      process.exit(1);
    }
  });

/**
 * List applications subcommand
 */
const listCommand = new Command('list')
  .description('List all job applications')
  .option('-s, --status <status>', 'Filter by status')
  .option('-c, --company <company>', 'Filter by company')
  .option('-l, --limit <number>', 'Limit results', '100')
  .option('-o, --offset <number>', 'Offset results', '0')
  .action(async (cmdOptions) => {
    const spinner = ora('Loading applications...').start();

    try {
      // Validate status string at boundary (ISSUE #16)
      if (cmdOptions.status) {
        const validStatuses = Object.values(ApplicationStatus);
        if (!validStatuses.includes(cmdOptions.status)) {
          spinner.fail('Invalid status');
          console.error(chalk.red(`Error: Invalid status. Valid options: ${validStatuses.join(', ')}` ));
          process.exit(1);
        }
      }

      const options: ListApplicationsOptions = {
        status: cmdOptions.status,
        company: cmdOptions.company,
        limit: parseInt(cmdOptions.limit),
        offset: parseInt(cmdOptions.offset),
      };

      const applications = await listApplications(options);

      spinner.succeed(`Found ${applications.length} applications`);

      if (applications.length === 0) {
        console.log(chalk.yellow('\nNo applications found.\n'));
        return;
      }

      console.log(chalk.bold(`\n${applications.length} Applications:\n`));
      applications.forEach((app) => {
        console.log(formatApplicationDisplay(app));
      });
    } catch (error) {
      spinner.fail('Failed to list applications');
      if (error instanceof Error) {
        console.error(chalk.red('Error:'), error.message);
      }
      process.exit(1);
    }
  });

/**
 * Add interview notes subcommand
 */
const interviewCommand = new Command('interview')
  .description('Add interview notes to application')
  .argument('<id>', 'Application ID')
  .option(
    '-d, --date <date>',
    'Interview date (YYYY-MM-DD)',
    new Date().toISOString().split('T')[0]
  )
  .option(
    '-t, --type <type>',
    'Interview type (phone, video, onsite, technical, behavioral, panel, hr)',
    'phone'
  )
  .option('-r, --round <number>', 'Round number', '1')
  .option('-n, --notes <notes>', 'Interview notes', '')
  .option('-i, --interviewer <name>', 'Interviewer name')
  .option('--title <title>', 'Interviewer title')
  .option('--duration <minutes>', 'Duration in minutes')
  .action(async (id, cmdOptions) => {
    const spinner = ora('Adding interview notes...').start();

    try {
      // Validate interview type at boundary (ISSUE #16)
      if (cmdOptions.type) {
        const validTypes = Object.values(InterviewType);
        if (!validTypes.includes(cmdOptions.type)) {
          spinner.fail('Invalid interview type');
          console.error(chalk.red(`Error: Invalid interview type. Valid types: ${validTypes.join(', ')}` ));
          process.exit(1);
        }
      }

      const options: InterviewNotesOptions = {
        applicationId: parseInt(id),
        interviewDate: cmdOptions.date,
        interviewType: cmdOptions.type,
        notes: cmdOptions.notes,
        ...(cmdOptions.round && { roundNumber: parseInt(cmdOptions.round) }),
        ...(cmdOptions.interviewer && { interviewerName: cmdOptions.interviewer }),
        ...(cmdOptions.title && { interviewerTitle: cmdOptions.title }),
        ...(cmdOptions.duration && { duration: parseInt(cmdOptions.duration) }),
      };

      const interview = await addInterviewNotes(options);

      spinner.succeed('Interview notes added successfully!');

      console.log(chalk.bold('\nInterview Details:\n'));
      console.log(`${chalk.gray('Application ID:')} ${interview.application_id}`);
      console.log(`${chalk.gray('Date:')} ${interview.interview_date}`);
      console.log(`${chalk.gray('Type:')} ${interview.interview_type}`);
      console.log(`${chalk.gray('Round:')} ${interview.round_number}`);
      if (interview.interviewer_name) {
        console.log(`${chalk.gray('Interviewer:')} ${interview.interviewer_name}`);
      }
      if (interview.personal_notes) {
        console.log(`${chalk.gray('Notes:')} ${interview.personal_notes}`);
      }
      console.log();
    } catch (error) {
      spinner.fail('Failed to add interview notes');
      if (error instanceof Error) {
        console.error(chalk.red('Error:'), error.message);
      }
      process.exit(1);
    }
  });

/**
 * Main track-application command
 */
export const trackApplicationCommand = new Command('track-application')
  .description('Track job applications and manage pipeline')
  .addCommand(addCommand)
  .addCommand(updateCommand)
  .addCommand(listCommand)
  .addCommand(interviewCommand);
