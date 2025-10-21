/**
 * Research Company Command
 *
 * Comprehensive company research including web scraping, news aggregation,
 * and intelligent analysis
 */

import { spawn } from 'child_process';
import { writeFile, mkdir } from 'fs/promises';
import { join } from 'path';

import chalk from 'chalk';
import { Command } from 'commander';
import ora from 'ora';

import {
  scrapeCompanyWebsite,
  fetchCompanyNews,
  extractCompanyData,
  rateLimitDelay,
  type CompanyData,
  type NewsArticle,
} from '../lib/company-researcher';

interface AnalysisResult {
  overview: {
    name: string;
    industry: string;
    size: string;
    founded: string;
    location: string;
  };
  mission_values: string;
  recent_news: NewsArticle[];
  green_flags: string[];
  red_flags: string[];
  talking_points: string[];
  interview_insights: {
    culture: string;
    expectations: string;
    questions_to_ask: string[];
  };
}

type ResearchDepth = 'quick' | 'standard' | 'deep';

/**
 * Normalize company input to URL
 */
function normalizeCompanyInput(input: string): string {
  if (!input || input.trim().length === 0) {
    throw new Error('Company name or domain is required');
  }

  // If it's already a URL, return it
  if (input.startsWith('http://') || input.startsWith('https://')) {
    return input;
  }

  // If it looks like a domain (has a dot), add https://
  if (input.includes('.')) {
    return `https://${input}`;
  }

  // Otherwise, try to construct a likely URL
  const domain = input
    .toLowerCase()
    .replace(/\s+/g, '')
    .replace(/[^a-z0-9]/g, '');
  return `https://${domain}.com`;
}

/**
 * Call Python analyzer
 */
async function callPythonAnalyzer(companyData: Record<string, unknown>): Promise<AnalysisResult> {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python3', [
      '-c',
      `
import sys
import json
sys.path.insert(0, 'src/python')
from company_analyzer.analyzer import analyze_company_data

data = json.loads(sys.stdin.read())
result = analyze_company_data(data)
print(json.dumps(result))
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
        reject(new Error(`Python analyzer failed: ${errorOutput}`));
        return;
      }

      try {
        const result = JSON.parse(output);
        resolve(result);
      } catch (error) {
        reject(new Error(`Failed to parse analysis result: ${error}`));
      }
    });

    // Send data to Python process
    pythonProcess.stdin.write(JSON.stringify(companyData));
    pythonProcess.stdin.end();
  });
}

/**
 * Format date for filename
 */
function formatDate(date: Date): string {
  const isoString = date.toISOString();
  return isoString.split('T')[0] || 'unknown-date'; // YYYY-MM-DD
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
 * Generate markdown report
 */
function generateMarkdownReport(companyData: CompanyData, analysis: AnalysisResult): string {
  const {
    overview,
    mission_values,
    recent_news,
    green_flags,
    red_flags,
    talking_points,
    interview_insights,
  } = analysis;

  const report = `# Company Research: ${overview.name || companyData.name}

**Generated:** ${new Date().toLocaleString() || 'N/A'}
**URL:** ${companyData.url}

---

## Overview

- **Industry:** ${overview.industry || 'Not specified'}
- **Size:** ${overview.size || 'Not specified'}
- **Founded:** ${overview.founded || 'Not specified'}
- **Headquarters:** ${overview.location || 'Not specified'}

---

## Mission & Values

${mission_values || companyData.description || 'Information not available from public sources'}

---

## Recent News (Last 6 months)

${
  recent_news && recent_news.length > 0
    ? recent_news
        .map(
          (article, idx) =>
            `${idx + 1}. **${article.title}**\n   - Source: ${article.source}\n   - Date: ${article.publishedAt}\n   - [Read more](${article.url})`
        )
        .join('\n\n')
    : '_No recent news articles found_'
}

---

## Green Flags ✓

${green_flags && green_flags.length > 0 ? green_flags.map((flag) => `- ${flag}`).join('\n') : '_No specific green flags identified_'}

---

## Red Flags ⚠

${red_flags && red_flags.length > 0 ? red_flags.map((flag) => `- ${flag}`).join('\n') : '_No significant red flags identified_'}

---

## Culture & Work Environment

${interview_insights?.culture || 'Culture information not available from public sources'}

**What to Expect:**
${interview_insights?.expectations || 'Expectations not specified'}

---

## Talk Track Ideas

${
  talking_points && talking_points.length > 0
    ? talking_points.map((point, idx) => `${idx + 1}. ${point}`).join('\n\n')
    : '_Generate your own talking points based on the information above_'
}

---

## Questions to Ask in Interviews

${
  interview_insights?.questions_to_ask && interview_insights.questions_to_ask.length > 0
    ? interview_insights.questions_to_ask.map((q, idx) => `${idx + 1}. ${q}`).join('\n')
    : '1. What does success look like in this role?\n2. How does the team approach collaboration?\n3. What are the biggest challenges ahead?'
}

---

## Next Steps

- [ ] Review company's product/service in detail
- [ ] Check Glassdoor reviews for employee perspectives
- [ ] Research key executives and interviewers on LinkedIn
- [ ] Prepare specific examples from your experience that align with company values
- [ ] Identify 2-3 projects or initiatives you're excited about

---

_Generated by Resume Toolkit - ${new Date().toISOString()}_
`;

  return report;
}

/**
 * Research company
 */
export async function researchCompany(
  companyInput: string,
  depth: ResearchDepth = 'standard',
  role?: string
): Promise<void> {
  const spinner = ora('Researching company...').start();

  try {
    // Normalize input to URL
    spinner.text = 'Processing company information...';
    const companyUrl = normalizeCompanyInput(companyInput);

    // Determine research depth settings
    const newsLimit = depth === 'quick' ? 3 : depth === 'standard' ? 5 : 10;

    // Step 1: Scrape company website
    spinner.text = 'Scraping company website...';
    const websiteData = await scrapeCompanyWebsite(companyUrl);
    await rateLimitDelay(3); // Respectful rate limiting

    // Step 2: Extract company data
    spinner.text = 'Extracting company information...';
    const companyData = extractCompanyData(websiteData.content, companyUrl);
    spinner.succeed(`Found company: ${chalk.cyan(companyData.name || 'Unknown')}`);

    // Step 3: Fetch company news
    spinner.start('Fetching recent news...');
    const news = await fetchCompanyNews(companyData.name || companyInput, newsLimit);
    spinner.succeed(`Found ${news.length} recent news articles`);
    await rateLimitDelay(2);

    // Step 4: Analyze with Python
    spinner.start('Analyzing company data...');
    const analysisInput = {
      ...companyData,
      website_content: websiteData.content,
      news,
    };
    const analysis = await callPythonAnalyzer(analysisInput);
    spinner.succeed('Analysis complete');

    // Step 5: Generate report
    spinner.start('Generating research report...');
    const report = generateMarkdownReport(companyData, analysis);

    // Step 6: Save to file
    const date = formatDate(new Date());
    const companySlug = sanitizeForFilename(companyData.name || companyInput);
    const roleSlug = role ? sanitizeForFilename(role) : 'general';
    const outputDir = join(process.cwd(), 'applications', `${date}-${companySlug}-${roleSlug}`);
    const outputPath = join(outputDir, 'company-research.md');

    await mkdir(outputDir, { recursive: true });
    await writeFile(outputPath, report, 'utf-8');

    spinner.succeed(`Research report saved to ${chalk.green(outputPath)}`);

    // Display summary
    console.log('\n' + chalk.bold('Research Summary:'));
    console.log(`${chalk.blue('Company:')} ${companyData.name || 'Unknown'}`);
    console.log(`${chalk.blue('Industry:')} ${analysis.overview.industry || 'Not specified'}`);
    console.log(`${chalk.blue('Recent News:')} ${news.length} articles`);
    console.log(`${chalk.blue('Green Flags:')} ${analysis.green_flags.length}`);
    console.log(`${chalk.blue('Red Flags:')} ${analysis.red_flags.length}`);
    console.log(`${chalk.blue('Talking Points:')} ${analysis.talking_points.length} generated`);

    if (analysis.green_flags.length > 0) {
      console.log(`\n${chalk.green('Top Green Flag:')}`);
      console.log(`  ${analysis.green_flags[0]}`);
    }

    if (analysis.red_flags.length > 0) {
      console.log(`\n${chalk.yellow('⚠ Red Flag to Note:')}`);
      console.log(`  ${analysis.red_flags[0]}`);
    }

    console.log(`\n${chalk.green('✓')} Full research report: ${outputPath}\n`);
  } catch (error) {
    spinner.fail('Failed to research company');

    if (error instanceof Error) {
      console.error(chalk.red('Error:'), error.message);

      // Provide helpful error messages
      if (error.message.includes('403')) {
        console.error(
          chalk.yellow(
            '\nTip: Some websites block automated access. Try using a different company domain or manual research.'
          )
        );
      } else if (error.message.includes('404')) {
        console.error(
          chalk.yellow('\nTip: The website may not exist. Check the company name or domain.')
        );
      } else if (error.message.includes('Python')) {
        console.error(
          chalk.yellow(
            '\nTip: Ensure Python dependencies are installed: pip install -r requirements.txt'
          )
        );
      }
    }

    throw error;
  }
}

/**
 * Create research-company command
 */
export const researchCompanyCommand = new Command('research-company')
  .description('Research company for interview preparation')
  .argument('<company>', 'Company name or domain (e.g., "google.com" or "Google")')
  .option('-d, --depth <level>', 'Research depth: quick, standard, or deep', 'standard')
  .option('-r, --role <role>', "Role you're applying for (for folder organization)")
  .action(async (company: string, options: { depth?: string; role?: string }) => {
    try {
      const depth = (options.depth || 'standard') as ResearchDepth;
      if (!['quick', 'standard', 'deep'].includes(depth)) {
        console.error(chalk.red('Error: Depth must be one of: quick, standard, deep'));
        process.exit(1);
      }

      await researchCompany(company, depth, options.role);
    } catch (error) {
      process.exit(1);
    }
  });
