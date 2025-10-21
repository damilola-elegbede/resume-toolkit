#!/usr/bin/env node

/**
 * Resume Toolkit CLI - Main Entry Point
 *
 * Production-quality CLI for managing job application workflows
 */

import { Command } from 'commander';

import { analyzeJdCommand } from './commands/analyze-jd.js';
import { applicationDashboardCommand } from './commands/application-dashboard.js';
import { applyCommand } from './commands/apply.js';
import { generateCoverLetterCommand } from './commands/generate-cover-letter.js';
import { interviewPrepCommand } from './commands/interview-prep.js';
import { optimizeResumeCommand } from './commands/optimize-resume.js';
import { parseResumeCommand } from './commands/parse-resume.js';
import { researchCompanyCommand } from './commands/research-company.js';
import { scoreAtsCommand } from './commands/score-ats.js';
import { trackApplicationCommand } from './commands/track-application.js';

const program = new Command();

program
  .name('resume-toolkit')
  .description('Complete Job Application Workflow System')
  .version('0.1.0');

// Add commands
program.addCommand(applyCommand); // Master orchestrator - list first
program.addCommand(analyzeJdCommand);
program.addCommand(parseResumeCommand);
program.addCommand(scoreAtsCommand);
program.addCommand(optimizeResumeCommand);
program.addCommand(generateCoverLetterCommand);
program.addCommand(researchCompanyCommand);
program.addCommand(trackApplicationCommand);
program.addCommand(applicationDashboardCommand);
program.addCommand(interviewPrepCommand);

// Future commands:
// program.addCommand(jobsCommand);
// program.addCommand(resumeCommand);

program.parse();
