/**
 * Company Researcher
 *
 * Scrapes company websites and aggregates news for comprehensive company research
 */

import axios from 'axios';
import * as cheerio from 'cheerio';
import { chromium, type Browser } from 'playwright';

export interface CompanyData {
  name: string;
  description: string;
  industry: string;
  size: string;
  founded: string;
  location: string;
  url: string;
}

export interface NewsArticle {
  title: string;
  url: string;
  publishedAt: string;
  source: string;
  snippet?: string;
}

export interface WebsiteData {
  url: string;
  content: string;
  scrapedAt: string;
}

/**
 * Scrape company website
 */
export async function scrapeCompanyWebsite(url: string): Promise<WebsiteData> {
  // Validate URL
  if (!url || typeof url !== 'string' || url.trim().length === 0) {
    throw new Error('Invalid URL provided');
  }

  try {
    new URL(url);
  } catch {
    throw new Error('Invalid URL format');
  }

  let browser: Browser | null = null;

  try {
    // Launch browser with stealth settings
    browser = await chromium.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-blink-features=AutomationControlled',
      ],
    });

    const page = await browser.newPage();

    // Set realistic user agent and headers
    await page.setExtraHTTPHeaders({
      'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.9',
      'Accept-Encoding': 'gzip, deflate, br',
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
      throw new Error('403 Forbidden - Access denied or anti-bot protection');
    }
    if (status === 404) {
      throw new Error('404 Not Found - Page does not exist');
    }
    if (status >= 400) {
      throw new Error(`HTTP ${status} - Failed to fetch page`);
    }

    // Wait for DOM to be fully loaded
    await page.waitForLoadState('domcontentloaded');
    // Extract page content
    const content = await page.content();

    await browser.close();

    return {
      url,
      content,
      scrapedAt: new Date().toISOString(),
    };
  } catch (error) {
    if (browser) {
      await browser.close();
    }

    if (error instanceof Error) {
      if (error.message.includes('Timeout')) {
        throw new Error('Timeout exceeded - Page took too long to load');
      }
      throw error;
    }

    throw new Error('Failed to scrape website');
  }
}

/**
 * Fetch company news from web search
 * Uses web scraping as a fallback to news APIs
 */
export async function fetchCompanyNews(
  companyName: string,
  limit: number = 5
): Promise<NewsArticle[]> {
  if (!companyName || companyName.trim().length === 0) {
    return [];
  }

  // Bound limit parameter to reasonable range (1-20)
  limit = Math.max(1, Math.min(limit, 20));


  try {
    // Use Google News RSS as a simple alternative to paid APIs
    const searchQuery = encodeURIComponent(`${companyName} news`);
    const rssUrl = `https://news.google.com/rss/search?q=${searchQuery}&hl=en-US&gl=US&ceid=US:en`;

    const response = await axios.get(rssUrl, {
      headers: {
        'User-Agent':
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      },
      timeout: 10000,
    });

    const $ = cheerio.load(response.data, { xmlMode: true });
    const articles: NewsArticle[] = [];

    $('item')
      .slice(0, limit)
      .each((_, element) => {
        const title = $(element).find('title').text();
        const link = $(element).find('link').text();
        const pubDate = $(element).find('pubDate').text();
        const source = $(element).find('source').text() || 'Google News';

        if (title && link) {
          articles.push({
            title,
            url: link,
            publishedAt: pubDate ? new Date(pubDate).toISOString().split('T')[0] || pubDate : '',
            source,
          });
        }
      });

    return articles;
  } catch (error) {
    // Graceful degradation - return empty array on error
    console.error('Failed to fetch news:', error);
    return [];
  }
}

/**
 * Extract company data from HTML content
 */
export function extractCompanyData(html: string, url: string): CompanyData {
  const $ = cheerio.load(html);

  // Extract company name
  let name = '';
  const ogTitle = $('meta[property="og:title"]').attr('content');
  const title = $('title').text();

  if (ogTitle) {
    name = ogTitle.split('-')[0]?.trim() || ogTitle.split('|')[0]?.trim() || ogTitle;
  } else if (title) {
    name = title.split('-')[0]?.trim() || title.split('|')[0]?.trim() || title;
  }

  // Extract description
  const description =
    $('meta[name="description"]').attr('content') ||
    $('meta[property="og:description"]').attr('content') ||
    '';

  // Extract industry from content
  let industry = '';
  const bodyText = $('body').text().toLowerCase();
  const industryKeywords = [
    'technology',
    'saas',
    'software',
    'finance',
    'healthcare',
    'e-commerce',
    'retail',
    'education',
    'manufacturing',
    'consulting',
  ];

  for (const keyword of industryKeywords) {
    if (bodyText.includes(keyword)) {
      industry = keyword.charAt(0).toUpperCase() + keyword.slice(1);
      break;
    }
  }

  // Extract company size
  let size = '';
  const sizeMatch = bodyText.match(/(\d+[+-]?\d*)\s*(?:employees|team members|people)/i);
  if (sizeMatch) {
    size = sizeMatch[1] + ' employees';
  }

  // Extract founded year
  let founded = '';
  const foundedMatch = bodyText.match(/founded\s+(?:in\s+)?(\d{4})/i);
  if (foundedMatch) {
    founded = foundedMatch[1] || '';
  }

  // Extract location/headquarters
  let location = '';
  const locationMatch = bodyText.match(
    /(?:headquarters?|based|located)[\s:]+([A-Z][a-zA-Z\s,]+(?:CA|NY|TX|MA|WA|IL|CO|GA|FL|OR))/i
  );
  if (locationMatch) {
    location = locationMatch[1]?.trim() || '';
  }

  return {
    name,
    description,
    industry,
    size,
    founded,
    location,
    url,
  };
}

/**
 * Rate limiting helper
 */
export async function rateLimitDelay(seconds: number = 3): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, seconds * 1000));
}
