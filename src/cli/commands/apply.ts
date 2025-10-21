/**
 * Apply Command - Master Orchestrator
 *
 * End-to-end job application workflow orchestration
 */

import { spawn } from 'child_process';
import { existsSync } from 'fs';
import { writeFile, mkdir, readFile, unlink } from 'fs/promises';
import { join } from 'path';

import chalk from 'chalk';
import { Command } from 'commander';
import ora, { Ora } from 'ora';

export interface ApplyOptions {
  template?: string;
  withPrep?: boolean;
  resume?: boolean;
  dryRun?: boolean;
}

interface StageResult {
  completed: boolean;
  error?: string;
  data?: any;
  duration?: number;
  iterations?: number;
  finalScore?: number;
  fallback?: string;
}

export interface WorkflowResult {
  success: boolean;
  stages: {
    analysis?: StageResult;
    research?: StageResult;
    optimization?: StageResult;
    coverLetter?: StageResult;
    scoring?: StageResult;
    pdf?: StageResult;
    tracking?: StageResult;
    interviewPrep?: StageResult;
    summary?: StageResult;
  };
  files: string[];
  metrics?: {
    totalTime: number;
    stageTimings: Record<string, number>;
    atsScore?: number;
  };
  warnings?: string[];
  errors?: string[];
  summary?: string;
  dryRun?: boolean;
  plan?: string[];
}

interface ProgressData {
  url: string;
  completedStages: string[];
  data: any;
  timestamp: string;
}

// Temporary simplified interfaces for commands that need to be implemented
interface InterviewQuestion {
  question: string;
  category: string;
  suggestedAnswer: string;
}

interface InterviewPrepData {
  questions: InterviewQuestion[];
  keyTopics: string[];
  companySpecific: string[];
}

/**
 * Simplified versions of command functions for testing
 * These will be replaced with actual implementations
 */
export async function analyzeJobDescription(url: string): Promise<any> {
  // This is a simplified mock - replace with actual implementation
  return {
    jdData: {
      url,
      company: 'TechCorp Inc',
      position: 'Director of Engineering',
      description: 'Lead our engineering team...',
      requirements: ['10+ years', 'Team leadership', 'System design'],
      benefits: ['Remote', 'Equity', 'Health'],
      scrapedAt: new Date().toISOString(),
    },
    analysis: {
      technical_skills: ['React', 'TypeScript', 'Node.js', 'AWS'],
      leadership_skills: ['Team management', 'Strategic planning'],
      domain_expertise: ['SaaS', 'Enterprise software'],
      required_skills: ['Leadership', 'Architecture'],
      nice_to_have_skills: ['Kubernetes', 'ML'],
      ats_keywords: ['engineering', 'leadership', 'scalability', 'team', 'technical'],
      keyword_importance: { engineering: 0.95, leadership: 0.9 },
      keyword_frequency: { engineering: 5, leadership: 4 },
    },
  };
}

export async function researchCompany(company: string): Promise<any> {
  // Simplified mock
  return {
    company,
    website: 'https://techcorp.com',
    industry: 'Software',
    size: '500-1000',
    founded: 2015,
    headquarters: 'San Francisco, CA',
    culture: {
      values: ['Innovation', 'Collaboration'],
      mission: 'Transform enterprise software',
      workEnvironment: 'Remote-first',
      glassdoorRating: 4.2,
    },
    recentNews: [
      {
        title: 'TechCorp Announces AWS Partnership',
        date: '2025-10-01',
        summary: 'Strategic cloud partnership',
        url: 'https://news.com/techcorp-aws',
      },
    ],
    products: ['CloudSync', 'DataFlow'],
    competitors: ['CompetitorA', 'CompetitorB'],
    financials: {
      revenue: '$100M',
      funding: 'Series C',
      investors: ['VC Firm A', 'VC Firm B'],
    },
  };
}

export async function optimizeResume(_options: any): Promise<any> {
  // Simplified mock
  return {
    original: 'original resume content',
    optimized: 'optimized resume content with keywords',
    score: 92,
    improvements: ['Added keywords', 'Improved formatting'],
    iterations: 2,
  };
}

export async function generateCoverLetter(_options: any): Promise<any> {
  // Simplified mock
  return {
    content: 'Dear Hiring Manager...',
    wordCount: 387,
    keywordsUsed: 12,
    personalizationScore: 9,
  };
}

export async function scoreATS(_options: any): Promise<any> {
  // Simplified mock
  return {
    overall: 92,
    categories: {
      keywords: 95,
      formatting: 90,
      content: 91,
      readability: 89,
    },
    recommendations: ['Consider adding "regulatory compliance"'],
  };
}

export async function trackApplication(options: any): Promise<any> {
  // Simplified mock
  return {
    id: 'app-2025-10-21-001',
    company: options.company,
    position: options.position,
    status: 'ready_to_apply',
    dateCreated: new Date().toISOString(),
    followUpDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
  };
}

export async function prepareInterviewQuestions(_options: any): Promise<InterviewPrepData> {
  // Simplified mock
  return {
    questions: [
      {
        question: 'Tell me about a time you led a technical transformation',
        category: 'Leadership',
        suggestedAnswer: 'STAR format answer...',
      },
    ],
    keyTopics: ['Technical leadership', 'System design', 'Team building'],
    companySpecific: ['AWS partnership impact', 'Remote team management'],
  };
}

/**
 * Format date for filename
 */
function formatDate(date: Date): string {
  return date.toISOString().split('T')[0] ?? 'unknown-date'; // YYYY-MM-DD
}

/**
 * Sanitize text for filename
 */
function sanitizeForFilename(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Remove diacritics
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .substring(0, 50); // Limit length
}

/**
 * Validate URL format
 */
function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Generate PDF from markdown
 */
async function generatePDF(
  markdownPath: string,
  outputPath: string
): Promise<{ success: boolean; error?: string }> {
  return new Promise((resolve) => {
    const pandoc = spawn('pandoc', [
      markdownPath,
      '-o',
      outputPath,
      '--pdf-engine=xelatex',
      '-V',
      'geometry:margin=1in',
      '-V',
      'fontsize=11pt',
      '-V',
      'linkcolor=blue',
    ]);

    let errorOutput = '';

    pandoc.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    pandoc.on('close', (code) => {
      if (code === 0) {
        resolve({ success: true });
      } else {
        resolve({ success: false, error: errorOutput || 'PDF generation failed' });
      }
    });

    pandoc.on('error', () => {
      resolve({ success: false, error: 'Pandoc not installed or not in PATH' });
    });
  });
}

/**
 * Save progress to file
 */
async function saveProgress(data: ProgressData): Promise<void> {
  const progressPath = join(process.cwd(), '.tmp', 'apply-progress.json');
  await mkdir(join(process.cwd(), '.tmp'), { recursive: true });
  await writeFile(progressPath, JSON.stringify(data, null, 2), 'utf-8');
}

/**
 * Load progress from file
 */
async function loadProgress(): Promise<ProgressData | null> {
  const progressPath = join(process.cwd(), '.tmp', 'apply-progress.json');

  if (!existsSync(progressPath)) {
    return null;
  }

  try {
    const content = await readFile(progressPath, 'utf-8');
    return JSON.parse(content);
  } catch {
    return null;
  }
}

/**
 * Clean up progress file
 */
async function cleanupProgress(): Promise<void> {
  const progressPath = join(process.cwd(), '.tmp', 'apply-progress.json');

  try {
    if (existsSync(progressPath)) {
      await unlink(progressPath);
    }
  } catch {
    // Ignore cleanup errors
  }
}

/**
 * Format workflow summary
 */
function formatSummary(result: WorkflowResult, options: ApplyOptions): string {
  const lines: string[] = [];

  lines.push(chalk.green('━'.repeat(50)));
  lines.push(
    chalk.green.bold('✅ Application package complete!') +
      (result.metrics
        ? chalk.gray(` (${Math.round(result.metrics.totalTime / 1000)} seconds)`)
        : '')
  );
  lines.push('');

  lines.push(chalk.bold('📁 Generated Files:'));
  result.files.forEach((file) => {
    lines.push(`  • ${file}`);
  });
  lines.push('');

  if (result.metrics?.atsScore) {
    lines.push(chalk.bold('📊 Metrics:'));
    lines.push(`  • ATS Score: ${chalk.green(result.metrics.atsScore + '%')}`);
    lines.push(`  • Time to create: ${Math.round(result.metrics.totalTime / 1000)} seconds`);
    lines.push(`  • Files generated: ${result.files.length}`);
    lines.push('');
  }

  lines.push(chalk.bold('🎯 Next Steps:'));
  lines.push('  1. Review the generated resume and cover letter');
  lines.push('  2. Submit application via the job posting URL');
  lines.push(
    '  3. Follow up date: ' +
      chalk.cyan(new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toLocaleDateString())
  );

  if (options.withPrep) {
    lines.push('  4. Prepare for interview using interview-prep.md');
  }
  lines.push('');

  if (result.warnings && result.warnings.length > 0) {
    lines.push(chalk.yellow.bold('⚠️  Warnings:'));
    result.warnings.forEach((warning) => {
      lines.push(chalk.yellow(`  • ${warning}`));
    });
    lines.push('');
  }

  if (result.metrics?.atsScore && result.metrics.atsScore < 95) {
    lines.push(
      chalk.cyan('💡 Pro Tip:') +
        ' Your ATS score is ' +
        (result.metrics.atsScore >= 90 ? 'excellent' : 'good') +
        ` (${result.metrics.atsScore}%). Consider adding more keywords for a potential boost.`
    );
  }

  return lines.join('\n');
}

/**
 * Main workflow orchestrator
 */
export async function applyWorkflow(
  url: string,
  options: ApplyOptions = {}
): Promise<WorkflowResult> {
  const startTime = Date.now();
  const result: WorkflowResult = {
    success: false,
    stages: {},
    files: [],
    warnings: [],
    errors: [],
    metrics: {
      totalTime: 0,
      stageTimings: {},
    },
  };

  // Handle dry-run mode
  if (options.dryRun) {
    result.dryRun = true;
    result.plan = [
      'Stage 1: Analyze job description',
      'Stage 2: Research company',
      'Stage 3: Optimize resume for ATS',
      'Stage 4: Generate cover letter',
      'Stage 5: Calculate ATS score',
      'Stage 6: Generate PDF resume',
      'Stage 7: Track application',
      options.withPrep ? 'Stage 8: Prepare interview questions' : null,
      'Stage 9: Generate summary',
    ].filter(Boolean) as string[];
    result.success = true;
    return result;
  }

  let spinner: Ora | null = null;
  let progressData: ProgressData | null = null;
  let applicationDir: string = '';

  try {
    // Load progress if resuming
    if (options.resume) {
      progressData = await loadProgress();
      if (progressData) {
        if (progressData.url !== url) {
          throw new Error('Resume data is for a different job URL');
        }
        console.log(chalk.cyan('📂 Resuming from previous progress...'));
      } else {
        result.warnings?.push('Could not read progress file, starting fresh');
      }
    }

    // Initialize progress data
    if (!progressData) {
      progressData = {
        url,
        completedStages: [],
        data: {},
        timestamp: new Date().toISOString(),
      };
    }

    console.log(chalk.bold.cyan('\n🚀 Starting application workflow\n'));

    // Stage 1: Analyze JD (Critical - abort on failure)
    if (!progressData.completedStages.includes('analysis')) {
      const stageStart = Date.now();
      spinner = ora('Analyzing job description...').start();

      try {
        const { jdData, analysis } = await analyzeJobDescription(url);

        progressData.data['jdData'] = jdData;
        progressData.data['analysis'] = analysis;
        progressData.completedStages.push('analysis');

        await saveProgress(progressData);

        result.stages.analysis = {
          completed: true,
          data: { jdData, analysis },
          duration: Date.now() - stageStart,
        };

        spinner.succeed(
          `Analyzed job: ${chalk.cyan(jdData.position)} at ${chalk.cyan(jdData.company)}`
        );
        console.log(chalk.gray(`  • Keywords identified: ${analysis.ats_keywords.length}`));

        if (result.metrics) {
          result.metrics.stageTimings['analysis'] = Date.now() - stageStart;
        }
      } catch (error) {
        spinner.fail('Failed to analyze job description');
        throw error; // Critical failure
      }
    } else {
      console.log(chalk.gray('✓ Job analysis already completed'));
      result.stages.analysis = { completed: true, data: progressData.data };
    }

    const { jdData, analysis } = progressData.data as { jdData: any; analysis: any };

    // Create application directory
    const date = formatDate(new Date());
    const company = sanitizeForFilename(jdData.company);
    const role = sanitizeForFilename(jdData.position);
    applicationDir = join(process.cwd(), 'applications', `${date}-${company}-${role}`);
    await mkdir(applicationDir, { recursive: true });

    // Save job description
    const jdPath = join(applicationDir, 'job-description.md');
    await writeFile(jdPath, `# Job Description\n\n${jdData.description}`, 'utf-8');
    result.files.push(jdPath);

    // Save JD analysis
    const analysisPath = join(applicationDir, 'jd-analysis.md');
    const analysisContent = `# Job Analysis\n\n**Company:** ${jdData.company}\n**Position:** ${jdData.position}\n\n## Keywords\n${analysis.ats_keywords.slice(0, 20).join(', ')}`;
    await writeFile(analysisPath, analysisContent, 'utf-8');
    result.files.push(analysisPath);

    // Stage 2: Research Company (Non-critical - continue on failure)
    if (!progressData.completedStages.includes('research')) {
      const stageStart = Date.now();
      spinner = ora('Researching company...').start();

      try {
        const companyResearch = await researchCompany(jdData.company);

        progressData.data['companyResearch'] = companyResearch;
        progressData.completedStages.push('research');

        await saveProgress(progressData);

        result.stages.research = {
          completed: true,
          data: companyResearch,
          duration: Date.now() - stageStart,
        };

        spinner.succeed('Company research completed');

        if (companyResearch.recentNews?.length > 0) {
          console.log(chalk.gray(`  • Recent news: ${companyResearch.recentNews[0].title}`));
        }
        if (companyResearch.culture?.glassdoorRating) {
          console.log(
            chalk.gray(`  • Glassdoor rating: ${companyResearch.culture.glassdoorRating}/5`)
          );
        }

        // Save research
        const researchPath = join(applicationDir, 'company-research.md');
        await writeFile(researchPath, JSON.stringify(companyResearch, null, 2), 'utf-8');
        result.files.push(researchPath);

        if (result.metrics) {
          result.metrics.stageTimings['research'] = Date.now() - stageStart;
        }
      } catch (error) {
        spinner.warn('Company research partially failed');
        result.stages.research = {
          completed: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        };
        result.warnings?.push('Company research incomplete - continuing with available data');
      }
    } else {
      console.log(chalk.gray('✓ Company research already completed'));
      result.stages.research = { completed: true, data: progressData.data['companyResearch'] };
    }

    // Stage 3: Optimize Resume (Critical for quality)
    if (!progressData.completedStages.includes('optimization')) {
      const stageStart = Date.now();
      spinner = ora('Optimizing resume...').start();

      let attempts = 0;
      let optimized = null;

      while (attempts < 3) {
        attempts++;

        try {
          optimized = await optimizeResume({
            template: options.template,
            keywords: analysis.ats_keywords,
            requirements: jdData.requirements,
          });

          spinner.text = `Optimization iteration ${attempts}: ${optimized.score}%`;

          if (optimized.score >= 90) {
            break;
          }
        } catch (error) {
          if (attempts === 3) {
            throw error;
          }
        }
      }

      if (optimized) {
        progressData.data['optimizedResume'] = optimized;
        progressData.completedStages.push('optimization');

        await saveProgress(progressData);

        result.stages.optimization = {
          completed: true,
          data: optimized,
          iterations: attempts,
          finalScore: optimized.score,
          duration: Date.now() - stageStart,
        };

        spinner.succeed(
          `Resume optimized: ${chalk.green(optimized.score + '%')} (${attempts} iteration${attempts > 1 ? 's' : ''})`
        );

        // Save optimized resume
        const resumePath = join(applicationDir, 'tailored-resume.md');
        await writeFile(resumePath, optimized.optimized, 'utf-8');
        result.files.push(resumePath);

        if (result.metrics) {
          result.metrics.stageTimings['optimization'] = Date.now() - stageStart;
          result.metrics.atsScore = optimized.score;
        }
      } else {
        throw new Error('Failed to optimize resume');
      }
    } else {
      console.log(chalk.gray('✓ Resume optimization already completed'));
      const optimizedResume = progressData.data['optimizedResume'];
      result.stages.optimization = {
        completed: true,
        data: optimizedResume,
        finalScore: optimizedResume?.score,
      };
    }

    // Stage 4: Generate Cover Letter
    if (!progressData.completedStages.includes('coverLetter')) {
      const stageStart = Date.now();
      spinner = ora('Generating cover letter...').start();

      try {
        const coverLetter = await generateCoverLetter({
          company: jdData.company,
          position: jdData.position,
          companyResearch: progressData.data['companyResearch'],
          requirements: jdData.requirements,
        });

        progressData.data['coverLetter'] = coverLetter;
        progressData.completedStages.push('coverLetter');

        await saveProgress(progressData);

        result.stages.coverLetter = {
          completed: true,
          data: coverLetter,
          duration: Date.now() - stageStart,
        };

        spinner.succeed('Cover letter generated');
        console.log(chalk.gray(`  • Length: ${coverLetter.wordCount} words ✓`));
        console.log(chalk.gray(`  • Keywords integrated: ${coverLetter.keywordsUsed} ✓`));

        // Save cover letter
        const coverPath = join(applicationDir, 'cover-letter.md');
        await writeFile(coverPath, coverLetter.content, 'utf-8');
        result.files.push(coverPath);

        if (result.metrics) {
          result.metrics.stageTimings['coverLetter'] = Date.now() - stageStart;
        }
      } catch (error) {
        spinner.warn('Cover letter generation failed');
        result.stages.coverLetter = {
          completed: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        };
        result.warnings?.push('Cover letter generation failed - manual creation required');
      }
    } else {
      console.log(chalk.gray('✓ Cover letter already generated'));
      result.stages.coverLetter = { completed: true, data: progressData.data['coverLetter'] };
    }

    // Stage 5: Calculate ATS Score
    if (!progressData.completedStages.includes('scoring')) {
      const stageStart = Date.now();
      spinner = ora('Calculating final ATS score...').start();

      try {
        const optimizedResume = progressData.data['optimizedResume'];
        const atsScore = await scoreATS({
          resume: optimizedResume?.optimized,
          jobDescription: jdData.description,
        });

        progressData.data['atsScore'] = atsScore;
        progressData.completedStages.push('scoring');

        await saveProgress(progressData);

        result.stages.scoring = {
          completed: true,
          data: atsScore,
          duration: Date.now() - stageStart,
        };

        const scoreColor =
          atsScore.overall >= 90 ? chalk.green : atsScore.overall >= 80 ? chalk.yellow : chalk.red;

        spinner.succeed(`ATS Score: ${scoreColor(atsScore.overall + '%')}`);
        console.log(chalk.gray(`  • Keyword match: ${atsScore.categories.keywords}%`));
        console.log(chalk.gray(`  • Formatting: ${atsScore.categories.formatting}%`));

        // Save score report
        const scorePath = join(applicationDir, 'ats-score-report.md');
        const scoreContent = `# ATS Score Report\n\n**Overall Score:** ${atsScore.overall}%\n\n## Categories\n- Keywords: ${atsScore.categories.keywords}%\n- Formatting: ${atsScore.categories.formatting}%\n- Content: ${atsScore.categories.content}%\n- Readability: ${atsScore.categories.readability}%`;
        await writeFile(scorePath, scoreContent, 'utf-8');
        result.files.push(scorePath);

        if (result.metrics) {
          result.metrics.stageTimings['scoring'] = Date.now() - stageStart;
          result.metrics.atsScore = atsScore.overall;
        }
      } catch (error) {
        spinner.warn('ATS scoring failed');
        result.stages.scoring = {
          completed: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        };
      }
    } else {
      console.log(chalk.gray('✓ ATS scoring already completed'));
      result.stages.scoring = { completed: true, data: progressData.data['atsScore'] };
    }

    // Stage 6: Generate PDF
    if (!progressData.completedStages.includes('pdf')) {
      const stageStart = Date.now();
      spinner = ora('Generating PDF resume...').start();

      const resumePath = join(applicationDir, 'tailored-resume.md');
      const pdfPath = join(applicationDir, 'resume.pdf');

      const pdfResult = await generatePDF(resumePath, pdfPath);

      if (pdfResult.success) {
        progressData.completedStages.push('pdf');
        await saveProgress(progressData);

        result.stages.pdf = {
          completed: true,
          duration: Date.now() - stageStart,
        };

        spinner.succeed('PDF resume generated');
        result.files.push(pdfPath);

        if (result.metrics) {
          result.metrics.stageTimings['pdf'] = Date.now() - stageStart;
        }
      } else {
        spinner.warn('PDF generation failed - saved as markdown');
        const errorMsg = (pdfResult as { error?: string }).error;
        if (errorMsg) {
          result.stages.pdf = {
            completed: false,
            error: errorMsg,
            fallback: 'markdown',
          };
        } else {
          result.stages.pdf = {
            completed: false,
            fallback: 'markdown',
          };
        }
        result.warnings?.push('PDF generation failed, saved as markdown');
      }
    } else {
      console.log(chalk.gray('✓ PDF already generated'));
      result.stages.pdf = { completed: true };
    }

    // Stage 7: Track Application
    if (!progressData.completedStages.includes('tracking')) {
      const stageStart = Date.now();
      spinner = ora('Creating application tracking entry...').start();

      try {
        const trackingEntry = await trackApplication({
          company: jdData.company,
          position: jdData.position,
          url: url,
          status: 'ready_to_apply',
        });

        progressData.data['trackingEntry'] = trackingEntry;
        progressData.completedStages.push('tracking');

        await saveProgress(progressData);

        result.stages.tracking = {
          completed: true,
          data: trackingEntry,
          duration: Date.now() - stageStart,
        };

        spinner.succeed(`Tracking entry created: ${chalk.cyan(trackingEntry.id)}`);

        if (result.metrics) {
          result.metrics.stageTimings['tracking'] = Date.now() - stageStart;
        }
      } catch (error) {
        spinner.warn('Application tracking failed');
        result.stages.tracking = {
          completed: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        };
      }
    } else {
      console.log(chalk.gray('✓ Application tracking already set up'));
      result.stages.tracking = { completed: true, data: progressData.data['trackingEntry'] };
    }

    // Stage 8: Interview Prep (Optional)
    if (options.withPrep && !progressData.completedStages.includes('interviewPrep')) {
      const stageStart = Date.now();
      spinner = ora('Preparing interview questions...').start();

      try {
        const interviewPrep = await prepareInterviewQuestions({
          company: jdData.company,
          position: jdData.position,
          jobDescription: jdData.description,
          companyResearch: progressData.data['companyResearch'],
        });

        progressData.data['interviewPrep'] = interviewPrep;
        progressData.completedStages.push('interviewPrep');

        await saveProgress(progressData);

        result.stages.interviewPrep = {
          completed: true,
          data: interviewPrep,
          duration: Date.now() - stageStart,
        };

        spinner.succeed(`Interview prep created: ${interviewPrep.questions.length} questions`);

        // Save interview prep
        const prepPath = join(applicationDir, 'interview-prep.md');
        const prepContent = `# Interview Preparation\n\n## Questions\n\n${interviewPrep.questions.map((q) => `### ${q.question}\n\n**Category:** ${q.category}\n\n**Suggested Answer:**\n${q.suggestedAnswer}\n`).join('\n')}`;
        await writeFile(prepPath, prepContent, 'utf-8');
        result.files.push(prepPath);

        if (result.metrics) {
          result.metrics.stageTimings['interviewPrep'] = Date.now() - stageStart;
        }
      } catch (error) {
        spinner.warn('Interview prep failed');
        result.stages.interviewPrep = {
          completed: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        };
      }
    }

    // Stage 9: Generate Metadata
    const metadataPath = join(applicationDir, 'metadata.yaml');
    const metadata = `# Application Metadata
generated: ${new Date().toISOString()}
company: ${jdData.company}
position: ${jdData.position}
url: ${url}
ats_score: ${result.metrics?.atsScore || 'N/A'}
status: ready_to_apply
follow_up: ${new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()}
files:
${result.files.map((f) => `  - ${f.replace(applicationDir + '/', '')}`).join('\n')}
`;
    await writeFile(metadataPath, metadata, 'utf-8');
    result.files.push(metadataPath);

    // Clean up progress file on success
    await cleanupProgress();

    // Stage 9: Summary
    result.stages.summary = { completed: true };
    result.success = true;

    if (result.metrics) {
      result.metrics.totalTime = Date.now() - startTime;
    }

    result.summary = formatSummary(result, options);

    // Display summary
    console.log('\n' + result.summary);
  } catch (error) {
    if (spinner) {
      spinner.fail('Workflow failed');
    }

    result.success = false;
    result.errors?.push(error instanceof Error ? error.message : 'Unknown error');

    console.error(chalk.red('\n❌ Application workflow failed:'), error);

    throw error;
  }

  return result;
}

/**
 * Create apply command
 */
export const applyCommand = new Command('apply')
  .description('Complete job application workflow - analyze, optimize, and prepare all materials')
  .argument('<url>', 'Job description URL')
  .option(
    '-t, --template <template>',
    'Resume template to use (executive, director, manager, senior, mid)'
  )
  .option('--with-prep', 'Include interview preparation materials')
  .option('--resume', 'Resume from previous incomplete workflow')
  .option('--dry-run', 'Show what would be done without executing')
  .action(async (url: string, options: ApplyOptions) => {
    try {
      // Validate URL
      if (!isValidUrl(url)) {
        console.error(chalk.red('Error: Invalid URL provided'));
        process.exit(1);
      }

      await applyWorkflow(url, options);
    } catch (error) {
      console.error(chalk.red('Fatal error:'), error);
      process.exit(1);
    }
  });
