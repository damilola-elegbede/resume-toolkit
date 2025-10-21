/**
 * Generate Cover Letter Command
 *
 * Generates personalized, compelling cover letters based on JD analysis,
 * company research, and resume anecdotes
 */

import { spawn } from 'child_process';
import { writeFile, mkdir, readFile } from 'fs/promises';
import { join } from 'path';

import chalk from 'chalk';
import { Command } from 'commander';
import ora from 'ora';

import { scrapeJobDescription } from '../lib/jd-scraper';

interface CoverLetterResult {
  cover_letter: string;
  word_count: number;
  tone: string;
}

/**
 * Call Python cover letter generator
 */
async function callPythonCoverLetterGenerator(
  userInfoPath: string,
  companyResearchPath: string,
  jdAnalysisPath: string,
  anecdotesDir: string,
  position: string,
  tone: string = 'professional',
  customNotes?: string
): Promise<CoverLetterResult> {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python3', [
      '-c',
      `
import sys
import json
from pathlib import Path
sys.path.insert(0, 'src/python')

from cover_letter_generator.generator import generate_cover_letter
import yaml

# Load inputs
user_info_path = Path(sys.argv[1])
company_research_path = Path(sys.argv[2])
jd_analysis_path = Path(sys.argv[3])
anecdotes_dir = Path(sys.argv[4])
position = sys.argv[5]
tone = sys.argv[6]
custom_notes = sys.argv[7] if len(sys.argv) > 7 and sys.argv[7] != "null" else None

# Load user info
with open(user_info_path) as f:
    user_info = json.load(f)

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

# Generate cover letter
cover_letter = generate_cover_letter(
    user_info=user_info,
    company_research=company_research,
    jd_analysis=jd_analysis,
    anecdotes=anecdotes,
    position=position,
    tone=tone,
    custom_notes=custom_notes,
)

# Calculate word count
word_count = len(cover_letter.split())

# Return result
result = {
    "cover_letter": cover_letter,
    "word_count": word_count,
    "tone": tone,
}
print(json.dumps(result))
`,
      userInfoPath,
      companyResearchPath,
      jdAnalysisPath,
      anecdotesDir,
      position,
      tone,
      customNotes || 'null',
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
        reject(new Error(`Python cover letter generator failed: ${errorOutput}`));
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
 * Generate cover letter for specific job
 */
export async function generateCoverLetter(
  jdUrl: string,
  options: {
    company?: string | undefined;
    tone?: string | undefined;
    notes?: string | undefined;
    userInfo?: string | undefined;
    anecdotes?: string | undefined;
  } = {}
): Promise<void> {
  const spinner = ora('Generating cover letter...').start();

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

    const userInfoPath =
      options.userInfo || join(process.cwd(), '.resume-toolkit', 'user-info.json');
    const anecdotesDir = options.anecdotes || join(process.cwd(), '.resume-toolkit', 'anecdotes');
    const jdAnalysisPath = join(applicationDir, 'jd-analysis.json');
    const companyResearchPath = join(applicationDir, 'company-research.json');

    // Verify user info exists
    try {
      await readFile(userInfoPath, 'utf-8');
    } catch {
      spinner.fail('User info not found');
      console.error(
        chalk.red(
          `\nUser info not found at: ${userInfoPath}\n` +
            `Please create a user-info.json file with your contact information.`
        )
      );
      console.error(
        chalk.yellow('\nExample user-info.json:\n') +
          JSON.stringify(
            {
              name: 'Your Name',
              email: 'your.email@example.com',
              phone: '+1 (555) 123-4567',
              linkedin: 'linkedin.com/in/yourprofile',
            },
            null,
            2
          )
      );
      process.exit(1);
    }

    // Generate JD analysis if it doesn't exist
    if (!jdAnalysisPath) {
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

    // Create basic company research if it doesn't exist
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

    spinner.succeed('Files loaded');

    // Step 3: Generate cover letter
    spinner.start('Generating personalized cover letter...');

    const tone = options.tone || 'professional';
    const result = await callPythonCoverLetterGenerator(
      userInfoPath,
      companyResearchPath,
      jdAnalysisPath,
      anecdotesDir,
      jdData.position,
      tone,
      options.notes
    );

    const outputPath = join(applicationDir, 'cover-letter.md');
    await writeFile(outputPath, result.cover_letter);

    spinner.succeed('Cover letter generated!');

    // Step 4: Display results
    console.log('');
    console.log(chalk.green.bold('Cover Letter Generated Successfully!'));
    console.log('');
    console.log(chalk.blue('Details:'));
    console.log(`  ${chalk.gray('Company:')} ${jdData.company}`);
    console.log(`  ${chalk.gray('Position:')} ${jdData.position}`);
    console.log(`  ${chalk.gray('Tone:')} ${result.tone}`);
    console.log(`  ${chalk.gray('Word Count:')} ${result.word_count}`);
    console.log('');
    console.log(chalk.green('Saved to:') + ` ${chalk.cyan(outputPath)}`);
    console.log('');

    if (!companyResearchExists) {
      console.log(
        chalk.yellow(
          'Tip: Add company research to company-research.json for a more personalized letter.'
        )
      );
    }
  } catch (error) {
    spinner.fail('Failed to generate cover letter');

    if (error instanceof Error) {
      console.error(chalk.red('Error:'), error.message);

      if (error.message.includes('not found')) {
        console.error(
          chalk.yellow(
            '\nTip: Ensure your user-info.json and anecdotes directory exist.\n' +
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
 * Create generate-cover-letter command
 */
export const generateCoverLetterCommand = new Command('generate-cover-letter')
  .description('Generate personalized cover letter for job application')
  .argument('<url>', 'Job description URL (LinkedIn, Greenhouse, Lever, Indeed, Workday)')
  .option('-c, --company <name>', 'Company name (if different from JD)')
  .option('-t, --tone <tone>', 'Writing tone (formal, professional, casual)', 'professional')
  .option('-n, --notes <notes>', 'Custom notes to include (e.g., referral information)')
  .option('-u, --user-info <path>', 'Path to user info JSON file')
  .option('-a, --anecdotes <path>', 'Path to anecdotes directory')
  .action(
    async (
      url: string,
      options: {
        company?: string;
        tone?: string;
        notes?: string;
        userInfo?: string;
        anecdotes?: string;
      }
    ) => {
      try {
        await generateCoverLetter(url, options);
      } catch (error) {
        process.exit(1);
      }
    }
  );
