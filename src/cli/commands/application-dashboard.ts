/**
 * Application Dashboard Command
 *
 * Generates analytics dashboards showing application pipeline metrics,
 * success rates, and keyword performance
 */

import { writeFile } from 'fs/promises';
import { resolve } from 'path';

import chalk from 'chalk';
import { Command } from 'commander';
import ora from 'ora';

import { TursoClient } from '../db/client';
import type { Application, ApplicationStage, KeywordPerformance } from '../db/types';

interface DashboardData {
  applications: Application[];
  stages: ApplicationStage[];
  keywords: KeywordPerformance[];
}

interface PipelineData {
  total: number;
  applied: number;
  screening: number;
  interviewing: number;
  offer: number;
  rejected: number;
}

interface SuccessRates {
  responseRate: number;
  interviewRate: number;
  offerRate: number;
}

interface TimeMetrics {
  avgResponseTimeDays: number;
  avgTimeToInterviewDays: number;
  avgTimeToOfferDays: number;
}

/**
 * Parse date filter string into SQL conditions
 */
export function parseDateFilter(filter?: string): {
  startDate: string | null;
  endDate: string | null;
} {
  if (!filter) {
    return { startDate: null, endDate: null };
  }

  const today = new Date();

  // Handle "last N months"
  if (filter.includes('last') && filter.includes('month')) {
    const match = filter.match(/(\d+)/);
    if (match && match[1]) {
      const n = parseInt(match[1]);
      const startDate = new Date(today);
      startDate.setMonth(today.getMonth() - n);
      const startDateStr = startDate.toISOString().split('T')[0];
      const endDateStr = today.toISOString().split('T')[0];
      return {
        startDate: startDateStr || null,
        endDate: endDateStr || null,
      };
    }
  }

  // Handle "last N days"
  if (filter.includes('last') && filter.includes('day')) {
    const match = filter.match(/(\d+)/);
    if (match && match[1]) {
      const n = parseInt(match[1]);
      const startDate = new Date(today);
      startDate.setDate(today.getDate() - n);
      const startDateStr = startDate.toISOString().split('T')[0];
      const endDateStr = today.toISOString().split('T')[0];
      return {
        startDate: startDateStr || null,
        endDate: endDateStr || null,
      };
    }
  }

  // Handle "this year"
  if (filter.includes('this year')) {
    const startDate = new Date(today.getFullYear(), 0, 1);
    const startDateStr = startDate.toISOString().split('T')[0];
    const endDateStr = today.toISOString().split('T')[0];
    return {
      startDate: startDateStr || null,
      endDate: endDateStr || null,
    };
  }

  // Handle custom range "YYYY-MM-DD:YYYY-MM-DD"
  if (filter.includes(':')) {
    const [start, end] = filter.split(':');
    return { startDate: start || null, endDate: end || null };
  }

  return { startDate: null, endDate: null };
}

/**
 * Fetch dashboard data from Turso
 */
async function fetchDashboardData(dateFilter?: string): Promise<DashboardData> {
  const client = new TursoClient();

  try {
    // Parse date filter
    const { startDate, endDate } = parseDateFilter(dateFilter);

    // Build SQL conditions
    const dateCondition =
      startDate && endDate ? `WHERE applied_date BETWEEN '${startDate}' AND '${endDate}'` : '';

    // Query applications
    const appsResult = await client.execute(
      `SELECT * FROM applications ${dateCondition} ORDER BY applied_date DESC`
    );
    const applications = appsResult.rows as unknown as Application[];

    // Get application IDs for filtering stages
    const appIds = applications.map((app) => app.id).join(',');
    const stagesCondition = appIds ? `WHERE application_id IN (${appIds})` : 'WHERE 1=0';

    // Query stages
    const stagesResult = await client.execute(
      `SELECT * FROM application_stages ${stagesCondition} ORDER BY stage_date ASC`
    );
    const stages = stagesResult.rows as unknown as ApplicationStage[];

    // Query keyword performance
    const keywordsResult = await client.execute(
      'SELECT * FROM keyword_performance ORDER BY response_rate DESC'
    );
    const keywords = keywordsResult.rows as unknown as KeywordPerformance[];

    await client.close();

    return { applications, stages, keywords };
  } catch (error) {
    await client.close();
    throw error;
  }
}

/**
 * Aggregate pipeline data
 */
export function aggregatePipelineData(applications: any[]): PipelineData {
  const total = applications.length;
  const counts = applications.reduce(
    (acc, app) => {
      const status = app.status || 'applied';
      if (status in acc) {
        acc[status]++;
      }
      return acc;
    },
    {
      applied: 0,
      screening: 0,
      interviewing: 0,
      offer: 0,
      rejected: 0,
    }
  );

  return {
    total,
    ...counts,
  };
}

/**
 * Calculate success rates
 */
export function calculateSuccessRates(applications: any[]): SuccessRates {
  if (applications.length === 0) {
    return { responseRate: 0, interviewRate: 0, offerRate: 0 };
  }

  const total = applications.length;

  const responded = applications.filter((app) => app.status !== 'applied').length;
  const interviewed = applications.filter((app) =>
    ['interviewing', 'offer', 'accepted'].includes(app.status)
  ).length;
  const offered = applications.filter((app) => ['offer', 'accepted'].includes(app.status)).length;

  return {
    responseRate: (responded / total) * 100,
    interviewRate: (interviewed / total) * 100,
    offerRate: (offered / total) * 100,
  };
}

/**
 * Calculate time metrics from stages
 */
export function calculateTimeMetrics(stages: any[]): TimeMetrics {
  if (stages.length === 0) {
    return { avgResponseTimeDays: 0, avgTimeToInterviewDays: 0, avgTimeToOfferDays: 0 };
  }

  // Group stages by application
  const stagesByApp: Map<number, any[]> = new Map();
  for (const stage of stages) {
    const appId = stage.application_id;
    if (!stagesByApp.has(appId)) {
      stagesByApp.set(appId, []);
    }
    stagesByApp.get(appId)!.push(stage);
  }

  const responseTimes: number[] = [];
  const interviewTimes: number[] = [];
  const offerTimes: number[] = [];

  stagesByApp.forEach((appStages) => {
    const sorted = appStages.sort((a, b) => a.stage_date.localeCompare(b.stage_date));

    const appliedStage = sorted.find((s) => s.status === 'applied');
    const screeningStage = sorted.find((s) => s.status === 'screening');
    const interviewStage = sorted.find((s) => s.status === 'interviewing');
    const offerStage = sorted.find((s) => s.status === 'offer');

    if (appliedStage && screeningStage) {
      const days = daysBetween(appliedStage.stage_date, screeningStage.stage_date);
      responseTimes.push(days);
    }

    if (appliedStage && interviewStage) {
      const days = daysBetween(appliedStage.stage_date, interviewStage.stage_date);
      interviewTimes.push(days);
    }

    if (appliedStage && offerStage) {
      const days = daysBetween(appliedStage.stage_date, offerStage.stage_date);
      offerTimes.push(days);
    }
  });

  const avg = (arr: number[]) => (arr.length > 0 ? arr.reduce((a, b) => a + b, 0) / arr.length : 0);

  return {
    avgResponseTimeDays: avg(responseTimes),
    avgTimeToInterviewDays: avg(interviewTimes),
    avgTimeToOfferDays: avg(offerTimes),
  };
}

/**
 * Calculate days between two ISO date strings
 */
function daysBetween(date1: string, date2: string): number {
  const d1 = new Date(date1);
  const d2 = new Date(date2);
  return Math.abs((d2.getTime() - d1.getTime()) / (1000 * 60 * 60 * 24));
}

/**
 * Rank keywords by response rate
 */
export function rankKeywords(keywords: any[]): any[] {
  return [...keywords].sort((a, b) => b.response_rate - a.response_rate);
}

/**
 * Generate recommendations based on data
 */
export function generateRecommendations(data: any): string[] {
  const recommendations: string[] = [];

  // Keyword recommendations
  if (data.keywords && data.keywords.length > 0) {
    const topKeywords = data.keywords.slice(0, 3);
    for (const kw of topKeywords) {
      if (kw.response_rate >= 70) {
        recommendations.push(
          `Emphasize "${kw.keyword}" in future applications - ${kw.response_rate.toFixed(0)}% response rate`
        );
      }
    }
  }

  // Conversion recommendations
  if (data.metrics) {
    const { responseRate, interviewRate } = data.metrics;

    if (responseRate < 50) {
      recommendations.push('Response rate below average - review resume keywords and formatting');
    } else if (interviewRate > 25) {
      recommendations.push(
        'Your interview conversion is strong - focus on getting more interviews'
      );
    }

    if (interviewRate < 15 && responseRate > 50) {
      recommendations.push(
        'Strong response rate but low interview rate - improve screening call performance'
      );
    }
  }

  // Timing recommendations
  if (data.timeMetrics && data.timeMetrics.avgResponseTimeDays > 0) {
    const followupDays = Math.ceil(data.timeMetrics.avgResponseTimeDays + 2);
    recommendations.push(`Consider following up after ${followupDays} days if no response`);
  }

  return recommendations;
}

/**
 * Format dashboard output
 */
export function formatDashboardOutput(data: any, format: string): string {
  if (format === 'json') {
    return JSON.stringify(data, null, 2);
  }

  // Terminal or markdown format
  const lines: string[] = [];

  // Title
  lines.push(chalk.bold('Application Pipeline Dashboard'));
  lines.push(chalk.bold('='.repeat(60)));
  lines.push('');

  // Pipeline funnel
  if (data.funnel) {
    const { total, applied, screening, interviewing, offer, rejected } = data.funnel;
    const maxWidth = 40;

    lines.push(chalk.bold('Pipeline:'));
    lines.push(`Total Applications: ${total}`);

    const makeBar = (count: number, label: string) => {
      const pct = total > 0 ? (count / total) * 100 : 0;
      const barWidth = Math.round((count / total) * maxWidth);
      const bar = '█'.repeat(Math.max(barWidth, 0));
      return `  ${label.padEnd(15)} ${bar} ${count} (${pct.toFixed(0)}%)`;
    };

    lines.push(makeBar(applied, 'Applied'));
    lines.push(makeBar(screening, 'Screening'));
    lines.push(makeBar(interviewing, 'Interview'));
    lines.push(makeBar(offer, 'Offer'));
    lines.push(makeBar(rejected, 'Rejected'));
    lines.push('');
  }

  // Success metrics
  if (data.metrics) {
    const { responseRate, interviewRate, offerRate } = data.metrics;
    lines.push(chalk.bold('Success Metrics:'));
    lines.push(`  Response Rate:  ${responseRate.toFixed(0)}%`);
    lines.push(`  Interview Rate: ${interviewRate.toFixed(0)}%`);
    lines.push(`  Offer Rate:     ${offerRate.toFixed(0)}%`);
    lines.push('');
  }

  // Time metrics
  if (data.timeMetrics && data.timeMetrics.avgResponseTimeDays > 0) {
    const { avgResponseTimeDays, avgTimeToInterviewDays, avgTimeToOfferDays } = data.timeMetrics;
    lines.push(chalk.bold('Time Analysis:'));
    lines.push(`  Avg time to response:  ${avgResponseTimeDays.toFixed(1)} days`);
    if (avgTimeToInterviewDays > 0) {
      lines.push(`  Avg time to interview: ${avgTimeToInterviewDays.toFixed(1)} days`);
    }
    if (avgTimeToOfferDays > 0) {
      lines.push(`  Avg time to offer:     ${avgTimeToOfferDays.toFixed(1)} days`);
    }
    lines.push('');
  }

  // Top keywords
  if (data.keywords && data.keywords.length > 0) {
    lines.push(chalk.bold('Top Keywords (by response rate):'));
    data.keywords.slice(0, 5).forEach((kw: any, i: number) => {
      const usage = `(${kw.response_count}/${kw.total_uses})`;
      lines.push(`  ${i + 1}. ${kw.keyword} - ${kw.response_rate.toFixed(0)}% ${usage}`);
    });
    lines.push('');
  }

  // Recommendations
  if (data.recommendations && data.recommendations.length > 0) {
    lines.push(chalk.bold('Recommendations:'));
    data.recommendations.forEach((rec: string) => {
      lines.push(`  → ${rec}`);
    });
    lines.push('');
  }

  return lines.join('\n');
}

/**
 * Generate dashboard
 */
export async function generateDashboard(options: {
  filter?: string;
  export?: string;
  verbose?: boolean;
}): Promise<void> {
  const spinner = ora('Fetching application data...').start();

  try {
    // Fetch data from Turso
    const { applications, stages, keywords } = await fetchDashboardData(options.filter);

    if (applications.length === 0) {
      spinner.warn('No applications found. Start tracking applications to see analytics.');
      return;
    }

    spinner.succeed(`Loaded ${applications.length} applications`);

    // Calculate metrics
    const funnel = aggregatePipelineData(applications);
    const metrics = calculateSuccessRates(applications);
    const timeMetrics = calculateTimeMetrics(stages);
    const rankedKeywords = rankKeywords(keywords);

    const dashboardData = {
      funnel,
      metrics,
      timeMetrics,
      keywords: rankedKeywords,
      recommendations: generateRecommendations({
        funnel,
        metrics,
        timeMetrics,
        keywords: rankedKeywords,
      }),
    };

    // Format output
    const outputFormat = options.export?.endsWith('.json') ? 'json' : 'terminal';
    const output = formatDashboardOutput(dashboardData, outputFormat);

    // Display or export
    if (options.export) {
      spinner.start('Saving dashboard...');
      await writeFile(resolve(options.export), output, 'utf-8');
      spinner.succeed(`Dashboard saved to ${chalk.green(options.export)}`);
    } else {
      console.log('\n' + output);
    }
  } catch (error) {
    spinner.fail('Failed to generate dashboard');
    throw error;
  }
}

/**
 * Create application-dashboard command
 */
export const applicationDashboardCommand = new Command('application-dashboard')
  .description('Generate analytics dashboard for job applications')
  .option(
    '--filter <period>',
    'Filter by date (e.g., "last 3 months", "last 30 days", "this year")'
  )
  .option('--export <path>', 'Export dashboard to file (markdown or JSON)')
  .option('-v, --verbose', 'Show detailed breakdown')
  .action(async (options) => {
    try {
      await generateDashboard(options);
    } catch (error) {
      if (error instanceof Error) {
        console.error(chalk.red('Error:'), error.message);
      }
      process.exit(1);
    }
  });
