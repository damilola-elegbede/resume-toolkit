/**
 * ATS Score Command
 *
 * Calculates ATS compatibility scores with detailed feedback
 */

import { spawn } from 'child_process';
import { readFile, writeFile } from 'fs/promises';
import { resolve } from 'path';

import chalk from 'chalk';
import { Command } from 'commander';
import ora from 'ora';

interface ScoreBreakdown {
  keyword_match: number;
  formatting: number;
  skills_alignment: number;
  section_structure: number;
}

interface Recommendation {
  description: string;
  impact: number;
  category: string;
}

interface KeywordMatchDetail {
  score: number;
  matched_required: number;
  matched_nice_to_have: number;
  matched_keywords: string[];
  missing_keywords: string[];
}

interface FormattingDetail {
  score: number;
  has_sections: boolean;
  has_bullet_points: boolean;
  date_format_consistent: boolean;
  has_tables: boolean;
  found_sections: string[];
}

interface SkillsAlignmentDetail {
  score: number;
  technical_match: number;
  leadership_match: number;
  domain_match: number;
}

interface SectionStructureDetail {
  score: number;
  has_contact_info: boolean;
  has_experience: boolean;
  has_education: boolean;
  has_skills: boolean;
  logical_order: boolean;
}

interface ATSScoreResult {
  overall_score: number;
  breakdown: ScoreBreakdown;
  recommendations: Recommendation[];
  keyword_details?: KeywordMatchDetail;
  formatting_details?: FormattingDetail;
  skills_details?: SkillsAlignmentDetail;
  structure_details?: SectionStructureDetail;
}

/**
 * Call Python ATS scorer
 */
async function callATSScorer(resumeText: string, jobDescription: string): Promise<ATSScoreResult> {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python3', [
      '-c',
      `
import sys
import json
sys.path.insert(0, 'src/python')
from ats_scorer.scorer import score_resume

# Read inputs
lines = sys.stdin.readlines()
resume_text = lines[0]
jd_text = '\\n'.join(lines[1:])

# Score resume
result = score_resume(resume_text, jd_text)
print(json.dumps(result.model_dump()))
`,
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
        reject(new Error(`ATS scorer failed: ${errorOutput}`));
        return;
      }

      try {
        const result = JSON.parse(output);
        resolve(result);
      } catch (error) {
        reject(new Error(`Failed to parse scoring result: ${error}`));
      }
    });

    // Send resume and JD to Python process
    pythonProcess.stdin.write(resumeText + '\n');
    pythonProcess.stdin.write(jobDescription);
    pythonProcess.stdin.end();
  });
}

/**
 * Get emoji for score
 */
function getScoreEmoji(score: number): string {
  if (score >= 90) {
    return '✓';
  }
  if (score >= 75) {
    return '⚠';
  }
  return '✗';
}

/**
 * Get color for score
 */
function getScoreColor(score: number): (text: string) => string {
  if (score >= 90) {
    return chalk.green;
  }
  if (score >= 75) {
    return chalk.yellow;
  }
  return chalk.red;
}

/**
 * Format score display
 */
function formatScore(label: string, score: number, indent = 0): string {
  const prefix = '  '.repeat(indent);
  const emoji = getScoreEmoji(score);
  const color = getScoreColor(score);
  return `${prefix}${label}: ${color(`${score.toFixed(0)}% ${emoji}`)}`;
}

/**
 * Generate markdown report
 */
function generateMarkdownReport(resumePath: string, jdPath: string, score: ATSScoreResult): string {
  const { overall_score, breakdown, recommendations } = score;

  let report = `# ATS Compatibility Report

**Resume:** ${resumePath}
**Job Description:** ${jdPath}
**Generated:** ${new Date().toLocaleString()}

---

## Overall Score: ${overall_score.toFixed(1)}%

`;

  // Score breakdown
  report += '## Score Breakdown\n\n';
  report += `- **Keyword Match:** ${breakdown.keyword_match.toFixed(0)}%\n`;
  report += `- **Formatting:** ${breakdown.formatting.toFixed(0)}%\n`;
  report += `- **Skills Alignment:** ${breakdown.skills_alignment.toFixed(0)}%\n`;
  report += `- **Section Structure:** ${breakdown.section_structure.toFixed(0)}%\n\n`;

  // Detailed keyword analysis
  if (score.keyword_details) {
    report += '## Keyword Analysis\n\n';
    report += `- Required skills match: ${score.keyword_details.matched_required.toFixed(0)}%\n`;
    report += `- Nice-to-have match: ${score.keyword_details.matched_nice_to_have.toFixed(0)}%\n`;
    report += `- Matched keywords: ${score.keyword_details.matched_keywords.length}\n`;
    report += `- Missing keywords: ${score.keyword_details.missing_keywords.length}\n\n`;

    if (score.keyword_details.missing_keywords.length > 0) {
      report += '### Missing Important Keywords\n\n';
      score.keyword_details.missing_keywords.slice(0, 10).forEach((kw) => {
        report += `- ${kw}\n`;
      });
      report += '\n';
    }
  }

  // Detailed skills analysis
  if (score.skills_details) {
    report += '## Skills Alignment Details\n\n';
    report += `- Technical skills: ${score.skills_details.technical_match.toFixed(0)}%\n`;
    report += `- Leadership skills: ${score.skills_details.leadership_match.toFixed(0)}%\n`;
    report += `- Domain expertise: ${score.skills_details.domain_match.toFixed(0)}%\n\n`;
  }

  // Recommendations
  if (recommendations.length > 0) {
    const targetScore = Math.min(
      overall_score + recommendations.slice(0, 3).reduce((sum, r) => sum + r.impact, 0),
      100
    );

    report += `## Recommendations to Reach ${targetScore.toFixed(0)}%\n\n`;

    recommendations.forEach((rec, idx) => {
      const categoryEmoji: Record<string, string> = {
        keyword: '🔑',
        formatting: '📝',
        skills: '💡',
        structure: '🏗',
      };

      const emoji = categoryEmoji[rec.category] || '•';

      report += `${idx + 1}. ${emoji} **${rec.category.charAt(0).toUpperCase() + rec.category.slice(1)}** `;
      report += `(+${rec.impact.toFixed(0)}% impact): ${rec.description}\n`;
    });
  }

  report += '\n---\n\n*Generated by Resume Toolkit ATS Scorer*\n';

  return report;
}

/**
 * Display score results
 */
function displayResults(score: ATSScoreResult, verbose: boolean): void {
  const overallColor = getScoreColor(score.overall_score);

  console.log('\n');
  console.log(chalk.bold('═'.repeat(60)));
  console.log(
    chalk.bold(`  ATS Compatibility Score: ${overallColor(score.overall_score.toFixed(1) + '%')}`)
  );
  console.log(chalk.bold('═'.repeat(60)));
  console.log('\n');

  // Breakdown
  console.log(chalk.bold('Score Breakdown:'));
  console.log(formatScore('Keyword Match', score.breakdown.keyword_match, 1));

  if (verbose && score.keyword_details) {
    console.log(formatScore('  ├─ Required skills', score.keyword_details.matched_required, 2));
    console.log(formatScore('  └─ Nice-to-have', score.keyword_details.matched_nice_to_have, 2));
  }

  console.log(formatScore('Formatting', score.breakdown.formatting, 1));

  if (verbose && score.formatting_details) {
    console.log(
      `    ├─ Section headers: ${score.formatting_details.has_sections ? chalk.green('✓') : chalk.red('✗')}`
    );
    console.log(
      `    ├─ Bullet points: ${score.formatting_details.has_bullet_points ? chalk.green('✓') : chalk.red('✗')}`
    );
    console.log(
      `    └─ Date consistency: ${score.formatting_details.date_format_consistent ? chalk.green('✓') : chalk.red('✗')}`
    );
  }

  console.log(formatScore('Skills Alignment', score.breakdown.skills_alignment, 1));

  if (verbose && score.skills_details) {
    console.log(formatScore('  ├─ Technical', score.skills_details.technical_match, 2));
    console.log(formatScore('  ├─ Leadership', score.skills_details.leadership_match, 2));
    console.log(formatScore('  └─ Domain', score.skills_details.domain_match, 2));
  }

  console.log(formatScore('Section Structure', score.breakdown.section_structure, 1));

  // Recommendations
  if (score.recommendations.length > 0) {
    const targetScore = Math.min(
      score.overall_score + score.recommendations.slice(0, 3).reduce((sum, r) => sum + r.impact, 0),
      100
    );

    console.log('\n');
    console.log(
      chalk.bold(`Recommendations to reach ${chalk.cyan(targetScore.toFixed(0) + '%')}:`)
    );

    score.recommendations.slice(0, 5).forEach((rec, idx) => {
      const categoryColor: Record<string, (text: string) => string> = {
        keyword: chalk.blue,
        formatting: chalk.magenta,
        skills: chalk.green,
        structure: chalk.yellow,
      };

      const color = categoryColor[rec.category] || chalk.white;

      console.log(
        `  ${idx + 1}. ${color(rec.category.charAt(0).toUpperCase() + rec.category.slice(1))} ` +
          `(+${rec.impact.toFixed(0)}%): ${rec.description}`
      );
    });
  }

  console.log('\n');
}

/**
 * Score resume against job description
 */
export async function scoreResume(
  resumePath: string,
  jdPath: string,
  options: { output?: string; verbose?: boolean; json?: boolean }
): Promise<void> {
  const spinner = ora('Scoring resume...').start();

  try {
    // Step 1: Read files
    spinner.text = 'Reading files...';
    const resumeText = await readFile(resolve(resumePath), 'utf-8');
    const jdText = await readFile(resolve(jdPath), 'utf-8');

    // Step 2: Score with Python
    spinner.text = 'Analyzing ATS compatibility...';
    const score = await callATSScorer(resumeText, jdText);
    spinner.succeed('ATS analysis complete');

    // Step 3: Output results
    if (options.json) {
      console.log(JSON.stringify(score, null, 2));
      return;
    }

    // Display results
    displayResults(score, options.verbose || false);

    // Save report if requested
    if (options.output) {
      spinner.start('Generating report...');
      const report = generateMarkdownReport(resumePath, jdPath, score);
      await writeFile(resolve(options.output), report, 'utf-8');
      spinner.succeed(`Report saved to ${chalk.green(options.output)}`);
    }
  } catch (error) {
    spinner.fail('Failed to score resume');

    if (error instanceof Error) {
      console.error(chalk.red('Error:'), error.message);
    }

    throw error;
  }
}

/**
 * Create score-ats command
 */
export const scoreAtsCommand = new Command('score-ats')
  .description('Calculate ATS compatibility score for resume against job description')
  .requiredOption('-r, --resume <path>', 'Path to resume file (markdown or text)')
  .requiredOption('-j, --jd <path>', 'Path to job description file')
  .option('-o, --output <path>', 'Path to save report markdown (optional)')
  .option('-v, --verbose', 'Show detailed breakdown')
  .option('--json', 'Output results as JSON')
  .action(async (options) => {
    try {
      await scoreResume(options.resume, options.jd, {
        output: options.output,
        verbose: options.verbose,
        json: options.json,
      });
    } catch (error) {
      process.exit(1);
    }
  });
