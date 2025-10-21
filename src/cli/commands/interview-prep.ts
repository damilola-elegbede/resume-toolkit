/**
 * Interview Prep Command
 *
 * Generates comprehensive interview preparation materials based on JD analysis,
 * company research, and resume anecdotes
 */

import { spawn } from 'child_process';
import { writeFile, mkdir, readFile, readdir } from 'fs/promises';
import { join } from 'path';

import chalk from 'chalk';
import { Command } from 'commander';
import ora from 'ora';

import { scrapeJobDescription } from '../lib/jd-scraper';

interface InterviewPrepResult {
  interview_prep: string;
  technical_count: number;
  behavioral_count: number;
  questions_to_ask_count: number;
}

/**
 * Call Python interview prep generator
 */
async function callPythonInterviewPrepGenerator(
  companyResearchPath: string,
  jdAnalysisPath: string,
  anecdotesDir: string,
  position: string
): Promise<InterviewPrepResult> {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python3', [
      '-c',
      `
import sys
import json
from pathlib import Path
sys.path.insert(0, 'src/python')

from interview_prep_generator.generator import generate_interview_prep
import yaml

# Load inputs
company_research_path = Path(sys.argv[1])
jd_analysis_path = Path(sys.argv[2])
anecdotes_dir = Path(sys.argv[3])
position = sys.argv[4]

# Load company research
with open(company_research_path) as f:
    company_research = json.load(f)

# Load JD analysis
with open(jd_analysis_path) as f:
    jd_analysis = json.load(f)

# Load anecdotes from directory
anecdotes = []
if anecdotes_dir.exists():
    for anecdote_file in anecdotes_dir.glob("*.md"):
        try:
            content = anecdote_file.read_text(encoding='utf-8')

            # Parse frontmatter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2].strip()

                    anecdote = {
                        "title": frontmatter.get("title", ""),
                        "skills": frontmatter.get("skills", []),
                        "impact": frontmatter.get("impact", ""),
                        "content": body,
                    }
                    anecdotes.append(anecdote)
        except Exception as e:
            print(f"Warning: Could not parse {anecdote_file}: {e}", file=sys.stderr)

# Generate interview prep
interview_prep = generate_interview_prep(
    company_research=company_research,
    jd_analysis=jd_analysis,
    anecdotes=anecdotes,
    position=position,
)

# Count questions
technical_count = interview_prep.count("## Likely Technical Questions") or interview_prep.count("## Technical Questions")
behavioral_count = interview_prep.count("## Behavioral Questions")
questions_to_ask_count = len([line for line in interview_prep.split("\\n") if line.strip().startswith("-") and "?" in line])

# Return result
result = {
    "interview_prep": interview_prep,
    "technical_count": len([line for line in interview_prep.split("###") if "Technical" in interview_prep[max(0, interview_prep.find(line)-200):interview_prep.find(line)+200]]),
    "behavioral_count": len([line for line in interview_prep.split("###") if "Behavioral" in interview_prep[max(0, interview_prep.find(line)-200):interview_prep.find(line)+200]]),
    "questions_to_ask_count": questions_to_ask_count,
}
print(json.dumps(result))
`,
      companyResearchPath,
      jdAnalysisPath,
      anecdotesDir,
      position,
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
        reject(new Error(`Python interview prep generator failed: ${errorOutput}`));
        return;
      }

      try {
        // Parse JSON from last line of output
        const lines = output.trim().split('\n');
        const jsonLine = lines[lines.length - 1];
        const result = JSON.parse(jsonLine || '{}');
        resolve(result);
      } catch (error) {
        reject(new Error(`Failed to parse generator result: ${error}`));
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
 * Generate interview prep for specific job
 */
export async function generateInterviewPrep(
  jdUrl: string,
  options: {
    company?: string | undefined;
    anecdotes?: string | undefined;
  } = {}
): Promise<void> {
  const spinner = ora('Generating interview prep...').start();

  try {
    // Step 1: Fetch and analyze JD
    spinner.text = 'Fetching and analyzing job description...';
    const jdData = await scrapeJobDescription(jdUrl);

    const date = formatDate(new Date());
    const company = sanitizeForFilename(options.company || jdData.company);
    const role = sanitizeForFilename(jdData.position);

    const applicationDir = join(process.cwd(), 'applications', `${date}-${company}-${role}`);

    await mkdir(applicationDir, { recursive: true });

    // Step 2: Check for required files
    spinner.text = 'Loading required files...';

    const anecdotesDir = options.anecdotes || join(process.cwd(), '.resume-toolkit', 'anecdotes');
    const jdAnalysisPath = join(applicationDir, 'jd-analysis.json');
    const companyResearchPath = join(applicationDir, 'company-research.json');

    // Check if JD analysis exists
    try {
      await readFile(jdAnalysisPath, 'utf-8');
    } catch {
      // Generate JD analysis if it doesn't exist
      spinner.text = 'Analyzing job description...';

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

    // Check if company research exists
    let companyResearchExists = false;
    try {
      await readFile(companyResearchPath, 'utf-8');
      companyResearchExists = true;
    } catch {
      // Create basic company research from JD data
      const basicResearch = {
        company: jdData.company,
        mission: '',
        values: [],
        recent_news: [],
        culture: '',
        tech_stack: [],
      };
      await writeFile(companyResearchPath, JSON.stringify(basicResearch, null, 2));
    }

    // Check if anecdotes exist
    let anecdoteCount = 0;
    try {
      const files = await readdir(anecdotesDir);
      anecdoteCount = files.filter((f) => f.endsWith('.md')).length;
    } catch {
      // Anecdotes directory doesn't exist
      spinner.warn('No anecdotes found');
      console.log(
        chalk.yellow(
          '\nWarning: No anecdotes directory found. Interview prep will have generic answer templates.\n' +
            `Create anecdotes at: ${anecdotesDir}\n`
        )
      );
    }

    spinner.succeed('Files loaded');

    // Step 3: Generate interview prep
    spinner.start('Generating interview preparation materials...');

    const result = await callPythonInterviewPrepGenerator(
      companyResearchPath,
      jdAnalysisPath,
      anecdotesDir,
      jdData.position
    );

    const outputPath = join(applicationDir, 'interview-prep.md');
    await writeFile(outputPath, result.interview_prep);

    spinner.succeed('Interview prep generated!');

    // Step 4: Display results
    console.log('');
    console.log(chalk.green.bold('Interview Prep Generated Successfully!'));
    console.log('');
    console.log(chalk.blue('Details:'));
    console.log(`  ${chalk.gray('Company:')} ${jdData.company}`);
    console.log(`  ${chalk.gray('Position:')} ${jdData.position}`);
    console.log(`  ${chalk.gray('Technical Questions:')} ${result.technical_count || 'Multiple'}`);
    console.log(
      `  ${chalk.gray('Behavioral Questions:')} ${result.behavioral_count || 'Multiple'}`
    );
    console.log(`  ${chalk.gray('Questions to Ask:')} ${result.questions_to_ask_count || '15+'}`);
    if (anecdoteCount > 0) {
      console.log(`  ${chalk.gray('Anecdotes Used:')} ${anecdoteCount}`);
    }
    console.log('');
    console.log(chalk.green('Saved to:') + ` ${chalk.cyan(outputPath)}`);
    console.log('');

    // Provide tips
    if (!companyResearchExists || anecdoteCount === 0) {
      console.log(chalk.yellow('Tips for Better Preparation:'));
      if (!companyResearchExists) {
        console.log(
          chalk.yellow(
            `  • Add company research to ${companyResearchPath.replace(process.cwd(), '.')}`
          )
        );
        console.log(chalk.yellow('    Include: mission, values, recent news, culture, tech stack'));
      }
      if (anecdoteCount === 0) {
        console.log(
          chalk.yellow(`  • Create anecdotes in ${anecdotesDir.replace(process.cwd(), '.')}`)
        );
        console.log(chalk.yellow('    Use STAR format with specific metrics and achievements'));
      }
      console.log('');
    }

    console.log(chalk.cyan('Next Steps:'));
    console.log(chalk.cyan('  1. Review and customize the generated questions and answers'));
    console.log(chalk.cyan('  2. Practice your STAR answers out loud (2-3 minutes each)'));
    console.log(chalk.cyan('  3. Research the interviewers on LinkedIn if names are provided'));
    console.log(chalk.cyan('  4. Prepare 3-5 thoughtful questions tailored to each interviewer'));
    console.log('');
  } catch (error) {
    spinner.fail('Failed to generate interview prep');

    if (error instanceof Error) {
      console.error(chalk.red('Error:'), error.message);

      if (error.message.includes('not found')) {
        console.error(
          chalk.yellow(
            '\nTip: Ensure required files exist.\n' +
              'Run `resume-toolkit analyze-jd <url>` first to analyze the job description.'
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
 * Create interview-prep command
 */
export const interviewPrepCommand = new Command('interview-prep')
  .description('Generate comprehensive interview preparation materials')
  .argument('<url>', 'Job description URL (LinkedIn, Greenhouse, Lever, Indeed, Workday)')
  .option('-c, --company <name>', 'Company name (if different from JD)')
  .option('-a, --anecdotes <path>', 'Path to anecdotes directory')
  .action(
    async (
      url: string,
      options: {
        company?: string;
        anecdotes?: string;
      }
    ) => {
      try {
        await generateInterviewPrep(url, options);
      } catch (error) {
        process.exit(1);
      }
    }
  );
