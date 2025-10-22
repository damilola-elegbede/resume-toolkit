/**
 * Job Description Scraper
 *
 * Scrapes job descriptions from various job boards using Playwright.
 * Supports: LinkedIn, Greenhouse, Lever, Indeed, Workday
 */

import { chromium, type Browser, type Page } from 'playwright';

export interface JobDescriptionData {
  url: string;
  company: string;
  position: string;
  description: string;
  requirements: string[];
  benefits: string[];
  scrapedAt: string;
}

interface JobBoardConfig {
  name: string;
  selectors: {
    company: string[];
    position: string[];
    description: string[];
    requirements: string[];
    benefits: string[];
  };
}

const JOB_BOARDS: Record<string, JobBoardConfig> = {
  linkedin: {
    name: 'LinkedIn',
    selectors: {
      company: ['.topcard__org-name-link', '.job-details-jobs-unified-top-card__company-name'],
      position: ['.topcard__title', '.job-details-jobs-unified-top-card__job-title'],
      description: ['.show-more-less-html__markup', '.description__text'],
      requirements: ['.show-more-less-html__markup', '.description__text'],
      benefits: ['.show-more-less-html__markup', '.description__text'],
    },
  },
  greenhouse: {
    name: 'Greenhouse',
    selectors: {
      company: ['.company-name', '#header .company-name'],
      position: ['.app-title', '#header h1'],
      description: ['#content', '.content'],
      requirements: ['#content', '.content'],
      benefits: ['#content', '.content'],
    },
  },
  lever: {
    name: 'Lever',
    selectors: {
      company: ['.main-header-text h4', '.company-name'],
      position: ['.posting-headline h2', '.posting-headline'],
      description: ['.content .section-wrapper', '.posting-description'],
      requirements: ['.content .section-wrapper', '.posting-requirements'],
      benefits: ['.content .section-wrapper', '.posting-benefits'],
    },
  },
  indeed: {
    name: 'Indeed',
    selectors: {
      company: ['[data-company-name]', '.jobsearch-InlineCompanyRating'],
      position: ['.jobsearch-JobInfoHeader-title', 'h1'],
      description: ['#jobDescriptionText', '.jobsearch-jobDescriptionText'],
      requirements: ['#jobDescriptionText', '.jobsearch-jobDescriptionText'],
      benefits: ['#jobDescriptionText', '.jobsearch-jobDescriptionText'],
    },
  },
  workday: {
    name: 'Workday',
    selectors: {
      company: ['[data-automation-id="company"]', '.company-name'],
      position: ['[data-automation-id="job-title"]', 'h1'],
      description: ['[data-automation-id="jobPostingDescription"]', '.job-description'],
      requirements: ['[data-automation-id="jobPostingDescription"]', '.job-description'],
      benefits: ['[data-automation-id="jobPostingDescription"]', '.job-description'],
    },
  },
};

/**
 * Identify job board from URL
 */
function identifyJobBoard(url: string): string | null {
  if (url.includes('linkedin.com/jobs/view/')) {return 'linkedin';}
  if (url.includes('boards.greenhouse.io/')) {return 'greenhouse';}
  if (url.includes('jobs.lever.co/')) {return 'lever';}
  if (url.includes('indeed.com/viewjob')) {return 'indeed';}
  if (url.includes('.myworkdayjobs.com/')) {return 'workday';}
  return null;
}

/**
 * Extract text from page using multiple selectors
 */
async function extractText(page: Page, selectors: string[]): Promise<string> {
  for (const selector of selectors) {
    try {
      const element = await page.$(selector);
      if (element) {
        const text = await element.textContent();
        if (text && text.trim()) {
          return text.trim();
        }
      }
    } catch (_error) {
      // Try next selector
      continue;
    }
  }
  return '';
}

/**
 * Parse requirements from description text
 */
function parseRequirements(text: string): string[] {
  const requirements: string[] = [];

  // Look for requirements section
  const requirementsMatch =
    text.match(/(?:Requirements?|Qualifications?|You Have|What We're Looking For)[:\n]+([\s\S]*?)(?=\n\n[A-Z]|Benefits|Responsibilities|$)/i);

  if (requirementsMatch && requirementsMatch[1]) {
    const reqText = requirementsMatch[1];

    // Extract bullet points or numbered items
    const bullets = reqText.match(/[•\-*\d+.]\s*(.+)/g);
    if (bullets) {
      requirements.push(...bullets.map((b) => b.replace(/^[•\-*\d+.]\s*/, '').trim()));
    } else {
      // Split by newlines if no bullets
      const lines = reqText
        .split('\n')
        .map((l) => l.trim())
        .filter((l) => l.length > 0);
      requirements.push(...lines);
    }
  }

  // If no requirements section found, extract common skill patterns
  if (requirements.length === 0) {
    const skillPatterns = [
      /(?:\d+\+?\s*)?years?\s+(?:of\s+)?experience\s+(?:with|in)\s+([^\n.,]+)/gi,
      /(?:experience|proficiency|expertise)\s+(?:with|in)\s+([^\n.,]+)/gi,
      /strong\s+(?:knowledge|understanding)\s+of\s+([^\n.,]+)/gi,
    ];

    skillPatterns.forEach((pattern) => {
      const matches = text.matchAll(pattern);
      for (const match of matches) {
        if (match[1] && match[1].trim()) {
          requirements.push(match[1].trim());
        }
      }
    });
  }

  return requirements.filter((r) => r.length > 0 && r.length < 200); // Filter out empty or too long
}

/**
 * Parse benefits from description text
 */
function parseBenefits(text: string): string[] {
  const benefits: string[] = [];

  // Look for benefits section
  const benefitsMatch = text.match(
    /(?:Benefits|What We Offer|Perks|Compensation)[:\n]+([\s\S]*?)(?=\n\n[A-Z]|Requirements|Responsibilities|$)/i,
  );

  if (benefitsMatch && benefitsMatch[1]) {
    const benText = benefitsMatch[1];

    // Extract bullet points or numbered items
    const bullets = benText.match(/[•\-*\d+.]\s*(.+)/g);
    if (bullets) {
      benefits.push(...bullets.map((b) => b.replace(/^[•\-*\d+.]\s*/, '').trim()));
    } else {
      // Split by newlines if no bullets
      const lines = benText
        .split('\n')
        .map((l) => l.trim())
        .filter((l) => l.length > 0);
      benefits.push(...lines);
    }
  }

  return benefits.filter((b) => b.length > 0 && b.length < 200);
}

/**
 * Scrape job description from URL
 */
export async function scrapeJobDescription(url: string): Promise<JobDescriptionData> {
  // Validate URL
  if (!url || typeof url !== 'string') {
    throw new Error('Invalid URL provided');
  }

  try {
    new URL(url);
  } catch {
    throw new Error('Invalid URL format');
  }

  // Identify job board
  const boardType = identifyJobBoard(url);
  if (!boardType) {
    throw new Error(
      'Unsupported job board. Supported: LinkedIn, Greenhouse, Lever, Indeed, Workday',
    );
  }

  const config = JOB_BOARDS[boardType];
  let browser: Browser | null = null;

  try {
    // Launch browser
    browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    const page = await browser.newPage();

    // Set realistic user agent to avoid detection
    await page.setExtraHTTPHeaders({
      'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.9',
    });

    // Navigate to page
    const response = await page.goto(url, {
      waitUntil: 'networkidle',
      timeout: 30000,
    });

    if (!response) {
      throw new Error('Failed to load page');
    }

    // Check for errors
    const status = response.status();
    if (status === 403) {
      throw new Error('403 Forbidden - Cloudflare protection or access denied');
    }
    if (status === 404) {
      throw new Error('404 Not Found - Job posting may have been removed');
    }
    if (status >= 400) {
      throw new Error(`HTTP ${status} - Failed to fetch job description`);
    }

    // Wait for content to load
    await page.waitForTimeout(2000);

    // Extract data
    if (!config) {
      throw new Error('Job board configuration not found');
    }
    const selectors = config.selectors;
    const company = await extractText(page, selectors.company);
    const position = await extractText(page, selectors.position);
    const description = await extractText(page, selectors.description);

    if (!description) {
      throw new Error('Could not extract job description from page');
    }

    // Parse requirements and benefits
    const requirements = parseRequirements(description);
    const benefits = parseBenefits(description);

    await browser.close();

    return {
      url,
      company: company || 'Unknown Company',
      position: position || 'Unknown Position',
      description,
      requirements,
      benefits,
      scrapedAt: new Date().toISOString(),
    };
  } catch (error) {
    if (browser) {
      await browser.close();
    }

    if (error instanceof Error) {
      // Re-throw known errors
      if (error.message.includes('Timeout')) {
        throw new Error('Timeout exceeded - Page took too long to load');
      }
      throw error;
    }

    throw new Error('Failed to scrape job description');
  }
}
