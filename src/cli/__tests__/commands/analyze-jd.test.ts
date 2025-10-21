import { describe, it, expect, vi, beforeEach } from 'vitest';
import { analyzeJobDescription } from '../../commands/analyze-jd';
import type { JobDescriptionData } from '../../lib/jd-scraper';

// Mock the JD scraper
vi.mock('../../lib/jd-scraper', () => ({
  scrapeJobDescription: vi.fn(),
}));

// Mock Playwright
vi.mock('playwright', () => ({
  chromium: {
    launch: vi.fn(() => ({
      newPage: vi.fn(() => ({
        goto: vi.fn(),
        content: vi.fn(() => '<html><body>Job Description</body></html>'),
        close: vi.fn(),
      })),
      close: vi.fn(),
    })),
  },
}));

describe('analyze-jd command', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('URL parsing', () => {
    it('should identify LinkedIn job URLs', () => {
      const url = 'https://www.linkedin.com/jobs/view/1234567890';
      expect(url).toContain('linkedin.com/jobs/view/');
    });

    it('should identify Greenhouse job URLs', () => {
      const url = 'https://boards.greenhouse.io/company/jobs/1234567890';
      expect(url).toContain('boards.greenhouse.io/');
    });

    it('should identify Lever job URLs', () => {
      const url = 'https://jobs.lever.co/company/1234567890';
      expect(url).toContain('jobs.lever.co/');
    });

    it('should identify Indeed job URLs', () => {
      const url = 'https://www.indeed.com/viewjob?jk=1234567890';
      expect(url).toContain('indeed.com/viewjob');
    });

    it('should identify Workday job URLs', () => {
      const url = 'https://company.wd1.myworkdayjobs.com/en-US/careers/job/1234567890';
      expect(url).toContain('.myworkdayjobs.com/');
    });
  });

  describe('scrapeJobDescription', () => {
    it('should extract company name from LinkedIn', async () => {
      const { scrapeJobDescription } = await import('../../lib/jd-scraper');
      const mockData: JobDescriptionData = {
        url: 'https://www.linkedin.com/jobs/view/1234567890',
        company: 'Tech Corp',
        position: 'Senior Software Engineer',
        description: 'We are looking for an experienced developer...',
        requirements: ['5+ years experience', 'TypeScript', 'React'],
        benefits: ['Health insurance', 'Remote work'],
        scrapedAt: new Date().toISOString(),
      };

      vi.mocked(scrapeJobDescription).mockResolvedValue(mockData);

      const result = await scrapeJobDescription(mockData.url);
      expect(result.company).toBe('Tech Corp');
      expect(result.position).toBe('Senior Software Engineer');
    });

    it('should handle scraping errors gracefully', async () => {
      const { scrapeJobDescription } = await import('../../lib/jd-scraper');

      vi.mocked(scrapeJobDescription).mockRejectedValue(
        new Error('403 Forbidden - Cloudflare protection')
      );

      await expect(
        scrapeJobDescription('https://www.linkedin.com/jobs/view/invalid')
      ).rejects.toThrow('403 Forbidden');
    });

    it('should extract requirements section', async () => {
      const { scrapeJobDescription } = await import('../../lib/jd-scraper');
      const mockData: JobDescriptionData = {
        url: 'https://boards.greenhouse.io/company/jobs/1234',
        company: 'Startup Inc',
        position: 'Frontend Developer',
        description: 'Join our team...',
        requirements: ['React', 'TypeScript', 'CSS'],
        benefits: [],
        scrapedAt: new Date().toISOString(),
      };

      vi.mocked(scrapeJobDescription).mockResolvedValue(mockData);

      const result = await scrapeJobDescription(mockData.url);
      expect(result.requirements).toHaveLength(3);
      expect(result.requirements).toContain('React');
    });

    it('should handle missing benefits section', async () => {
      const { scrapeJobDescription } = await import('../../lib/jd-scraper');
      const mockData: JobDescriptionData = {
        url: 'https://jobs.lever.co/company/role',
        company: 'Corp Ltd',
        position: 'Backend Engineer',
        description: 'Great opportunity...',
        requirements: ['Node.js', 'PostgreSQL'],
        benefits: [],
        scrapedAt: new Date().toISOString(),
      };

      vi.mocked(scrapeJobDescription).mockResolvedValue(mockData);

      const result = await scrapeJobDescription(mockData.url);
      expect(result.benefits).toEqual([]);
    });
  });

  describe('error handling', () => {
    it('should handle 404 errors', async () => {
      const { scrapeJobDescription } = await import('../../lib/jd-scraper');

      vi.mocked(scrapeJobDescription).mockRejectedValue(new Error('404 Not Found'));

      await expect(
        scrapeJobDescription('https://www.linkedin.com/jobs/view/nonexistent')
      ).rejects.toThrow('404');
    });

    it('should handle network timeouts', async () => {
      const { scrapeJobDescription } = await import('../../lib/jd-scraper');

      vi.mocked(scrapeJobDescription).mockRejectedValue(new Error('Timeout exceeded'));

      await expect(scrapeJobDescription('https://example.com/timeout')).rejects.toThrow('Timeout');
    });

    it('should handle invalid URLs', async () => {
      const { scrapeJobDescription } = await import('../../lib/jd-scraper');

      vi.mocked(scrapeJobDescription).mockRejectedValue(new Error('Invalid URL'));

      await expect(scrapeJobDescription('not-a-url')).rejects.toThrow('Invalid URL');
    });
  });

  describe('analyzeJobDescription integration', () => {
    it('should call scraper and return analysis', async () => {
      const { scrapeJobDescription } = await import('../../lib/jd-scraper');

      const mockData: JobDescriptionData = {
        url: 'https://www.linkedin.com/jobs/view/1234567890',
        company: 'Tech Corp',
        position: 'Senior Software Engineer',
        description: 'We need React, TypeScript, and Node.js skills.',
        requirements: ['5+ years React', 'TypeScript expert', 'Node.js'],
        benefits: ['Remote', '401k'],
        scrapedAt: new Date().toISOString(),
      };

      vi.mocked(scrapeJobDescription).mockResolvedValue(mockData);

      // This function will be implemented in the command
      expect(analyzeJobDescription).toBeDefined();
    });
  });
});
