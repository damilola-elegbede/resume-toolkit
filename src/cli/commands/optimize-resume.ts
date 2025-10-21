/**
 * Optimize Resume Command
 *
 * Tailors a base resume to a specific job description through iterative optimization
 */

import { spawn } from 'child_process';
import { writeFile, mkdir, readFile } from 'fs/promises';
import { join } from 'path';

import chalk from 'chalk';
import { Command } from 'commander';
import ora from 'ora';

import { scrapeJobDescription } from '../lib/jd-scraper';

interface OptimizationResult {
  iterations: Array<{
    iteration: number;
    score: number;
    gaps: string[];
    improvements: string[];
  }>;
  final_score: number;
  final_resume_path: string;
}

/**
 * Call Python resume optimizer
 */
async function callPythonOptimizer(
  baseResumePath: string,
  anecdotesDir: string,
  jdAnalysisPath: string,
  outputPath: string,
  targetScore: number = 90,
  maxIterations: number = 3
): Promise<OptimizationResult> {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python3', [
      '-c',
      `
import sys
import json
from pathlib import Path
sys.path.insert(0, 'src/python')

from resume_optimizer.optimizer import (
    parse_resume_markdown,
    load_anecdotes,
    optimize_resume_iteratively,
    generate_resume_markdown,
    save_optimization_report
)

# Load inputs
base_resume_path = Path(sys.argv[1])
anecdotes_dir = Path(sys.argv[2])
jd_analysis_path = Path(sys.argv[3])
output_path = Path(sys.argv[4])
target_score = float(sys.argv[5])
max_iterations = int(sys.argv[6])

# Parse base resume
base_resume = parse_resume_markdown(base_resume_path)

# Load anecdotes
anecdotes = load_anecdotes(anecdotes_dir)

# Load JD analysis
with open(jd_analysis_path) as f:
    jd_analysis = json.load(f)

# Optimize iteratively
result = optimize_resume_iteratively(
    base_resume,
    jd_analysis,
    target_score=target_score,
    max_iterations=max_iterations
)

# Save optimized resume
optimized_markdown = generate_resume_markdown(result['final_resume'])
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(optimized_markdown, encoding='utf-8')

# Save optimization report
report_path = output_path.parent / 'optimization-report.md'
save_optimization_report(result, report_path)

# Return result
result['final_resume_path'] = str(output_path)
print(json.dumps(result))
`,
      baseResumePath,
      anecdotesDir,
      jdAnalysisPath,
      outputPath,
      targetScore.toString(),
      maxIterations.toString(),
    ]);

    let output = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python optimizer failed: ${errorOutput}`));
        return;
      }

      try {
        // Parse JSON from last line of output
        const lines = output.trim().split('\n');
        const jsonLine = lines[lines.length - 1];
        const result = JSON.parse(jsonLine || '{}');
        resolve(result);
      } catch (error) {
        reject(new Error(`Failed to parse optimizer result: ${error}`));
      }
    });
  });
}

/**
 * Format date for filename
 */
function formatDate(date: Date): string {
  return date.toISOString().split('T')[0] || 'unknown-date';
}

/**
 * Sanitize text for filename
 */
function sanitizeForFilename(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

/**
 * Display iteration progress
 */
function displayIterationProgress(iteration: number, score: number, gaps: string[]): string {
  const scoreColor = score >= 90 ? chalk.green : score >= 80 ? chalk.yellow : chalk.red;

  let message = `${chalk.bold(`Iteration ${iteration}:`)} Score ${scoreColor(`${score.toFixed(1)}%`)}`;

  if (gaps.length > 0) {
    message += ` → Adding keywords: ${chalk.cyan(gaps.slice(0, 3).join(', '))}`;
  }

  return message;
}

/**
 * Optimize resume for specific job description
 */
export async function optimizeResume(
  jdUrl: string,
  options: {
    baseResume?: string | undefined;
    anecdotes?: string | undefined;
    output?: string | undefined;
    targetScore?: number | undefined;
    maxIterations?: number | undefined;
  } = {}
): Promise<void> {
  const spinner = ora('Optimizing resume...').start();

  try {
    // Step 1: Analyze JD if not already done
    spinner.text = 'Fetching and analyzing job description...';
    const jdData = await scrapeJobDescription(jdUrl);

    const date = formatDate(new Date());
    const company = sanitizeForFilename(jdData.company);
    const role = sanitizeForFilename(jdData.position);

    const applicationDir = join(process.cwd(), 'applications', `${date}-${company}-${role}`);

    await mkdir(applicationDir, { recursive: true });

    // Save JD analysis
    const jdAnalysisPath = join(applicationDir, 'jd-analysis.json');

    // Check if analysis already exists
    let jdAnalysisExists = false;
    try {
      await readFile(jdAnalysisPath, 'utf-8');
      jdAnalysisExists = true;
    } catch {
      // File doesn't exist, need to analyze
    }

    if (!jdAnalysisExists) {
      spinner.text = 'Analyzing job description...';

      // Call Python analyzer (simplified - in real implementation would reuse analyze-jd)
      const analysisProcess = spawn('python3', [
        '-c',
        `
import sys
import json
sys.path.insert(0, 'src/python')
from jd_analyzer.analyzer import analyze_job_description

description = sys.stdin.read()
result = analyze_job_description(description)
print(json.dumps(result))
`,
      ]);

      let analysisOutput = '';

      analysisProcess.stdout.on('data', (data) => {
        analysisOutput += data.toString();
      });

      await new Promise<void>((resolve, reject) => {
        analysisProcess.on('close', (code) => {
          if (code !== 0) {
            reject(new Error('JD analysis failed'));
          } else {
            resolve();
          }
        });

        analysisProcess.stdin.write(jdData.description);
        analysisProcess.stdin.end();
      });

      const analysis = JSON.parse(analysisOutput);
      await writeFile(jdAnalysisPath, JSON.stringify(analysis, null, 2));
    }

    spinner.succeed('Job description analyzed');

    // Step 2: Load base resume and anecdotes
    spinner.start('Loading base resume and anecdotes...');

    const baseResumePath =
      options.baseResume || join(process.cwd(), '.resume-toolkit', 'base-resume.md');
    const anecdotesDir = options.anecdotes || join(process.cwd(), '.resume-toolkit', 'anecdotes');

    // Verify files exist
    try {
      await readFile(baseResumePath, 'utf-8');
    } catch {
      spinner.fail('Base resume not found');
      console.error(
        chalk.red(
          `\nBase resume not found at: ${baseResumePath}\n` +
            `Please create a base resume or specify path with --base-resume option`
        )
      );
      process.exit(1);
    }

    spinner.succeed('Resources loaded');

    // Step 3: Run iterative optimization
    spinner.start('Optimizing resume (this may take a minute)...');

    const outputPath = options.output || join(applicationDir, 'tailored-resume.md');

    const targetScore = options.targetScore || 90;
    const maxIterations = options.maxIterations || 3;

    const result = await callPythonOptimizer(
      baseResumePath,
      anecdotesDir,
      jdAnalysisPath,
      outputPath,
      targetScore,
      maxIterations
    );

    spinner.stop();

    // Step 4: Display iteration results
    console.log('\n' + chalk.bold.underline('Optimization Progress:') + '\n');

    for (const iteration of result.iterations) {
      console.log(displayIterationProgress(iteration.iteration, iteration.score, iteration.gaps));
    }

    // Step 5: Display final result
    console.log('');

    if (result.final_score >= targetScore) {
      console.log(
        chalk.green.bold('✓ Target reached!') +
          ` Final score: ${chalk.bold(`${result.final_score.toFixed(1)}%`)}`
      );
    } else {
      console.log(
        chalk.yellow.bold('○ Maximum iterations reached.') +
          ` Final score: ${chalk.bold(`${result.final_score.toFixed(1)}%`)}`
      );
    }

    console.log('');
    console.log(chalk.green('Optimized resume saved to:') + ` ${chalk.cyan(outputPath)}`);
    console.log(
      chalk.green('Optimization report:') +
        ` ${chalk.cyan(join(applicationDir, 'optimization-report.md'))}`
    );

    // Step 6: Display summary
    console.log('\n' + chalk.bold('Summary:'));
    console.log(
      `${chalk.blue('Company:')} ${jdData.company} | ${chalk.blue('Role:')} ${jdData.position}`
    );
    console.log(`${chalk.blue('Iterations:')} ${result.iterations.length}`);
    console.log(`${chalk.blue('Final Score:')} ${result.final_score.toFixed(1)}%`);

    if (result.iterations.length > 0) {
      const firstScore = result.iterations[0]?.score || 0;
      const improvement = result.final_score - firstScore;
      if (improvement > 0) {
        console.log(
          `${chalk.blue('Improvement:')} +${improvement.toFixed(1)}% ${chalk.green('↑')}`
        );
      }
    }

    console.log('');
  } catch (error) {
    spinner.fail('Failed to optimize resume');

    if (error instanceof Error) {
      console.error(chalk.red('Error:'), error.message);

      // Provide helpful error messages
      if (error.message.includes('not found')) {
        console.error(
          chalk.yellow(
            '\nTip: Ensure your base resume and anecdotes directory exist.\n' +
              'Run `resume-toolkit init` to set up the directory structure.'
          )
        );
      } else if (error.message.includes('Python')) {
        console.error(
          chalk.yellow(
            '\nTip: Ensure Python dependencies are installed.\n' + 'Run: pip install -e .'
          )
        );
      }
    }

    throw error;
  }
}

/**
 * Create optimize-resume command
 */
export const optimizeResumeCommand = new Command('optimize-resume')
  .description('Optimize resume for specific job description through iterative refinement')
  .argument('<url>', 'Job description URL (LinkedIn, Greenhouse, Lever, Indeed, Workday)')
  .option('-b, --base-resume <path>', 'Path to base resume markdown file')
  .option('-a, --anecdotes <path>', 'Path to anecdotes directory')
  .option('-o, --output <path>', 'Output path for optimized resume')
  .option('-t, --target-score <score>', 'Target ATS score (default: 90)', '90')
  .option('-i, --max-iterations <count>', 'Maximum optimization iterations (default: 3)', '3')
  .action(
    async (
      url: string,
      options: {
        baseResume?: string;
        anecdotes?: string;
        output?: string;
        targetScore?: string;
        maxIterations?: string;
      }
    ) => {
      try {
        await optimizeResume(url, {
          baseResume: options.baseResume || undefined,
          anecdotes: options.anecdotes || undefined,
          output: options.output || undefined,
          targetScore: options.targetScore ? parseFloat(options.targetScore) : 90,
          maxIterations: options.maxIterations ? parseInt(options.maxIterations, 10) : 3,
        });
      } catch (error) {
        process.exit(1);
      }
    }
  );
