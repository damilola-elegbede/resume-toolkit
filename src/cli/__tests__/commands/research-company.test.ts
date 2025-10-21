/**
 * Research Company Command Tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { researchCompany } from '../../commands/research-company';
import * as companyResearcher from '../../lib/company-researcher';
import { spawn } from 'child_process';
import { mkdir, writeFile } from 'fs/promises';

// Mock dependencies
vi.mock('child_process');
vi.mock('fs/promises');
vi.mock('../../lib/company-researcher');

describe('Research Company Command', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Mock mkdir and writeFile
    (mkdir as ReturnType<typeof vi.fn>).mockResolvedValue(undefined);
    (writeFile as ReturnType<typeof vi.fn>).mockResolvedValue(undefined);
  });

  it('should research company by domain', async () => {
    const mockWebsiteData = {
      url: 'https://example.com',
      content: '<html>Company website</html>',
      scrapedAt: new Date().toISOString(),
    };

    const mockNews = [
      {
        title: 'Company News',
        url: 'https://news.com/article',
        publishedAt: '2025-10-20',
        source: 'TechCrunch',
      },
    ];

    vi.spyOn(companyResearcher, 'scrapeCompanyWebsite').mockResolvedValue(mockWebsiteData);
    vi.spyOn(companyResearcher, 'fetchCompanyNews').mockResolvedValue(mockNews);
    vi.spyOn(companyResearcher, 'extractCompanyData').mockReturnValue({
      name: 'Example Corp',
      description: 'Tech company',
      industry: 'Technology',
      size: '100-500',
      founded: '2015',
      location: 'SF',
      url: 'https://example.com',
    });

    // Mock Python analyzer
    const mockPythonProcess = {
      stdout: {
        on: vi.fn((event, handler) => {
          if (event === 'data') {
            handler(
              JSON.stringify({
                overview: { name: 'Example Corp' },
                green_flags: ['Recent funding'],
                red_flags: [],
                talking_points: ['Point 1', 'Point 2'],
                interview_insights: { culture: 'Innovative' },
              })
            );
          }
        }),
      },
      stderr: { on: vi.fn() },
      stdin: { write: vi.fn(), end: vi.fn() },
      on: vi.fn((event, handler) => {
        if (event === 'close') {
          handler(0);
        }
      }),
    };

    (spawn as ReturnType<typeof vi.fn>).mockReturnValue(mockPythonProcess);

    await researchCompany('example.com');

    expect(companyResearcher.scrapeCompanyWebsite).toHaveBeenCalled();
    expect(companyResearcher.fetchCompanyNews).toHaveBeenCalled();
    expect(writeFile).toHaveBeenCalled();
  });

  it('should research company by name', async () => {
    const mockWebsiteData = {
      url: 'https://techcorp.com',
      content: '<html>Company website</html>',
      scrapedAt: new Date().toISOString(),
    };

    vi.spyOn(companyResearcher, 'scrapeCompanyWebsite').mockResolvedValue(mockWebsiteData);
    vi.spyOn(companyResearcher, 'fetchCompanyNews').mockResolvedValue([]);
    vi.spyOn(companyResearcher, 'extractCompanyData').mockReturnValue({
      name: 'TechCorp',
      description: 'Tech company',
      industry: 'Technology',
      size: '',
      founded: '',
      location: '',
      url: 'https://techcorp.com',
    });

    const mockPythonProcess = {
      stdout: {
        on: vi.fn((event, handler) => {
          if (event === 'data') {
            handler(
              JSON.stringify({
                overview: {},
                green_flags: [],
                red_flags: [],
                talking_points: [],
                interview_insights: {},
              })
            );
          }
        }),
      },
      stderr: { on: vi.fn() },
      stdin: { write: vi.fn(), end: vi.fn() },
      on: vi.fn((event, handler) => {
        if (event === 'close') {
          handler(0);
        }
      }),
    };

    (spawn as ReturnType<typeof vi.fn>).mockReturnValue(mockPythonProcess);

    await researchCompany('TechCorp');

    expect(companyResearcher.scrapeCompanyWebsite).toHaveBeenCalled();
  });

  it('should handle depth flag - quick', async () => {
    vi.spyOn(companyResearcher, 'scrapeCompanyWebsite').mockResolvedValue({
      url: 'https://example.com',
      content: '<html>Content</html>',
      scrapedAt: new Date().toISOString(),
    });
    vi.spyOn(companyResearcher, 'fetchCompanyNews').mockResolvedValue([]);
    vi.spyOn(companyResearcher, 'extractCompanyData').mockReturnValue({
      name: 'Company',
      description: '',
      industry: '',
      size: '',
      founded: '',
      location: '',
      url: 'https://example.com',
    });

    const mockPythonProcess = {
      stdout: {
        on: vi.fn((event, handler) => {
          if (event === 'data') {
            handler(
              JSON.stringify({
                overview: {},
                green_flags: [],
                red_flags: [],
                talking_points: [],
                interview_insights: {},
              })
            );
          }
        }),
      },
      stderr: { on: vi.fn() },
      stdin: { write: vi.fn(), end: vi.fn() },
      on: vi.fn((event, handler) => {
        if (event === 'close') {
          handler(0);
        }
      }),
    };

    (spawn as ReturnType<typeof vi.fn>).mockReturnValue(mockPythonProcess);

    await researchCompany('example.com', 'quick');

    // Quick mode should fetch fewer news articles
    expect(companyResearcher.fetchCompanyNews).toHaveBeenCalledWith(expect.any(String), 3);
  });

  it('should handle depth flag - standard', async () => {
    vi.spyOn(companyResearcher, 'scrapeCompanyWebsite').mockResolvedValue({
      url: 'https://example.com',
      content: '<html>Content</html>',
      scrapedAt: new Date().toISOString(),
    });
    vi.spyOn(companyResearcher, 'fetchCompanyNews').mockResolvedValue([]);
    vi.spyOn(companyResearcher, 'extractCompanyData').mockReturnValue({
      name: 'Company',
      description: '',
      industry: '',
      size: '',
      founded: '',
      location: '',
      url: 'https://example.com',
    });

    const mockPythonProcess = {
      stdout: {
        on: vi.fn((event, handler) => {
          if (event === 'data') {
            handler(
              JSON.stringify({
                overview: {},
                green_flags: [],
                red_flags: [],
                talking_points: [],
                interview_insights: {},
              })
            );
          }
        }),
      },
      stderr: { on: vi.fn() },
      stdin: { write: vi.fn(), end: vi.fn() },
      on: vi.fn((event, handler) => {
        if (event === 'close') {
          handler(0);
        }
      }),
    };

    (spawn as ReturnType<typeof vi.fn>).mockReturnValue(mockPythonProcess);

    await researchCompany('example.com', 'standard');

    expect(companyResearcher.fetchCompanyNews).toHaveBeenCalledWith(expect.any(String), 5);
  });

  it('should handle depth flag - deep', async () => {
    vi.spyOn(companyResearcher, 'scrapeCompanyWebsite').mockResolvedValue({
      url: 'https://example.com',
      content: '<html>Content</html>',
      scrapedAt: new Date().toISOString(),
    });
    vi.spyOn(companyResearcher, 'fetchCompanyNews').mockResolvedValue([]);
    vi.spyOn(companyResearcher, 'extractCompanyData').mockReturnValue({
      name: 'Company',
      description: '',
      industry: '',
      size: '',
      founded: '',
      location: '',
      url: 'https://example.com',
    });

    const mockPythonProcess = {
      stdout: {
        on: vi.fn((event, handler) => {
          if (event === 'data') {
            handler(
              JSON.stringify({
                overview: {},
                green_flags: [],
                red_flags: [],
                talking_points: [],
                interview_insights: {},
              })
            );
          }
        }),
      },
      stderr: { on: vi.fn() },
      stdin: { write: vi.fn(), end: vi.fn() },
      on: vi.fn((event, handler) => {
        if (event === 'close') {
          handler(0);
        }
      }),
    };

    (spawn as ReturnType<typeof vi.fn>).mockReturnValue(mockPythonProcess);

    await researchCompany('example.com', 'deep');

    expect(companyResearcher.fetchCompanyNews).toHaveBeenCalledWith(expect.any(String), 10);
  });

  it('should save to correct directory', async () => {
    vi.spyOn(companyResearcher, 'scrapeCompanyWebsite').mockResolvedValue({
      url: 'https://example.com',
      content: '<html>Content</html>',
      scrapedAt: new Date().toISOString(),
    });
    vi.spyOn(companyResearcher, 'fetchCompanyNews').mockResolvedValue([]);
    vi.spyOn(companyResearcher, 'extractCompanyData').mockReturnValue({
      name: 'TechCorp',
      description: '',
      industry: '',
      size: '',
      founded: '',
      location: '',
      url: 'https://example.com',
    });

    const mockPythonProcess = {
      stdout: {
        on: vi.fn((event, handler) => {
          if (event === 'data') {
            handler(
              JSON.stringify({
                overview: {},
                green_flags: [],
                red_flags: [],
                talking_points: [],
                interview_insights: {},
              })
            );
          }
        }),
      },
      stderr: { on: vi.fn() },
      stdin: { write: vi.fn(), end: vi.fn() },
      on: vi.fn((event, handler) => {
        if (event === 'close') {
          handler(0);
        }
      }),
    };

    (spawn as ReturnType<typeof vi.fn>).mockReturnValue(mockPythonProcess);

    await researchCompany('example.com', 'standard', 'Software Engineer');

    expect(mkdir).toHaveBeenCalledWith(
      expect.stringContaining('techcorp-software-engineer'),
      expect.any(Object)
    );
    expect(writeFile).toHaveBeenCalledWith(
      expect.stringContaining('company-research.md'),
      expect.any(String),
      'utf-8'
    );
  });

  it('should handle scraping errors gracefully', async () => {
    vi.spyOn(companyResearcher, 'scrapeCompanyWebsite').mockRejectedValue(
      new Error('Failed to scrape')
    );

    await expect(researchCompany('example.com')).rejects.toThrow();
  });

  it('should handle Python analyzer errors', async () => {
    vi.spyOn(companyResearcher, 'scrapeCompanyWebsite').mockResolvedValue({
      url: 'https://example.com',
      content: '<html>Content</html>',
      scrapedAt: new Date().toISOString(),
    });
    vi.spyOn(companyResearcher, 'fetchCompanyNews').mockResolvedValue([]);
    vi.spyOn(companyResearcher, 'extractCompanyData').mockReturnValue({
      name: 'Company',
      description: '',
      industry: '',
      size: '',
      founded: '',
      location: '',
      url: 'https://example.com',
    });

    const mockPythonProcess = {
      stdout: { on: vi.fn() },
      stderr: {
        on: vi.fn((event, handler) => {
          if (event === 'data') {
            handler('Python error');
          }
        }),
      },
      stdin: { write: vi.fn(), end: vi.fn() },
      on: vi.fn((event, handler) => {
        if (event === 'close') {
          handler(1); // Error exit code
        }
      }),
    };

    (spawn as ReturnType<typeof vi.fn>).mockReturnValue(mockPythonProcess);

    await expect(researchCompany('example.com')).rejects.toThrow('Python analyzer failed');
  });

  it('should handle empty company name', async () => {
    await expect(researchCompany('')).rejects.toThrow();
  });
});
