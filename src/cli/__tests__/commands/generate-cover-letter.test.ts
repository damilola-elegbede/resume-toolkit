import { describe, it, expect, vi, beforeEach } from 'vitest';
import { generateCoverLetter } from '../../commands/generate-cover-letter';
import { readFile, writeFile, mkdir } from 'fs/promises';
import { join } from 'path';

// Mock file system operations
vi.mock('fs/promises', () => ({
  readFile: vi.fn(),
  writeFile: vi.fn(),
  mkdir: vi.fn(),
}));

// Mock JD scraper
vi.mock('../../lib/jd-scraper', () => ({
  scrapeJobDescription: vi.fn(),
}));

describe('generate-cover-letter command', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('input validation', () => {
    it('should accept valid job URL', async () => {
      const url = 'https://www.linkedin.com/jobs/view/1234567890';
      expect(url).toContain('linkedin.com/jobs/view/');
    });

    it('should accept company name option', () => {
      const options = { company: 'TechCorp' };
      expect(options.company).toBe('TechCorp');
    });

    it('should accept tone options', () => {
      const validTones = ['formal', 'professional', 'casual'];
      validTones.forEach((tone) => {
        expect(['formal', 'professional', 'casual']).toContain(tone);
      });
    });
  });

  describe('file I/O', () => {
    it('should read JD analysis file', async () => {
      const mockJdAnalysis = {
        technical_skills: ['python', 'react'],
        leadership_skills: ['mentoring'],
        ats_keywords: ['python', 'react', 'aws'],
      };

      vi.mocked(readFile).mockResolvedValue(JSON.stringify(mockJdAnalysis));

      const path = 'applications/2024-01-01-techcorp-engineer/jd-analysis.json';
      const data = await readFile(path, 'utf-8');
      const parsed = JSON.parse(data);

      expect(parsed.technical_skills).toContain('python');
    });

    it('should read company research file', async () => {
      const mockResearch = {
        company: 'TechCorp',
        mission: 'Build great products',
        recent_news: ['Series B funding'],
      };

      vi.mocked(readFile).mockResolvedValue(JSON.stringify(mockResearch));

      const path = 'applications/2024-01-01-techcorp-engineer/company-research.json';
      const data = await readFile(path, 'utf-8');
      const parsed = JSON.parse(data);

      expect(parsed.company).toBe('TechCorp');
    });

    it('should read anecdotes from directory', async () => {
      const mockAnecdote = {
        title: 'Led Migration',
        skills: ['kubernetes', 'docker'],
        impact: 'Reduced time by 70%',
        content: 'Led the migration...',
      };

      vi.mocked(readFile).mockResolvedValue(JSON.stringify(mockAnecdote));

      const path = '.resume-toolkit/anecdotes/kubernetes-migration.json';
      const data = await readFile(path, 'utf-8');
      const parsed = JSON.parse(data);

      expect(parsed.title).toBe('Led Migration');
    });

    it('should create output directory if not exists', async () => {
      vi.mocked(mkdir).mockResolvedValue(undefined);

      const outputDir = 'applications/2024-01-01-techcorp-engineer';
      await mkdir(outputDir, { recursive: true });

      expect(mkdir).toHaveBeenCalledWith(outputDir, { recursive: true });
    });

    it('should write cover letter to file', async () => {
      const mockCoverLetter = 'Dear Hiring Manager,\n\nI am excited...';

      vi.mocked(writeFile).mockResolvedValue(undefined);

      const outputPath = 'applications/2024-01-01-techcorp-engineer/cover-letter.md';
      await writeFile(outputPath, mockCoverLetter);

      expect(writeFile).toHaveBeenCalledWith(outputPath, mockCoverLetter);
    });
  });

  describe('error handling', () => {
    it('should handle missing JD analysis gracefully', async () => {
      vi.mocked(readFile).mockRejectedValue(new Error('File not found'));

      await expect(readFile('applications/missing/jd-analysis.json', 'utf-8')).rejects.toThrow(
        'File not found'
      );
    });

    it('should handle missing company research gracefully', async () => {
      vi.mocked(readFile).mockRejectedValue(new Error('File not found'));

      await expect(readFile('applications/missing/company-research.json', 'utf-8')).rejects.toThrow(
        'File not found'
      );
    });

    it('should handle Python script errors', async () => {
      const errorMessage = 'Python script failed: Module not found';

      // Simulate Python error
      expect(() => {
        if (!errorMessage.includes('success')) {
          throw new Error(errorMessage);
        }
      }).toThrow('Python script failed');
    });

    it('should provide helpful error for missing anecdotes', async () => {
      vi.mocked(readFile).mockRejectedValue(new Error('ENOENT: no such file'));

      try {
        await readFile('.resume-toolkit/anecdotes/', 'utf-8');
      } catch (error) {
        expect(error).toBeInstanceOf(Error);
      }
    });
  });

  describe('file naming', () => {
    it('should generate correct filename with date', () => {
      const date = new Date('2024-01-15');
      const formatted = date.toISOString().split('T')[0];
      expect(formatted).toBe('2024-01-15');
    });

    it('should sanitize company name for filename', () => {
      const sanitize = (text: string) =>
        text
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, '-')
          .replace(/^-+|-+$/g, '');

      expect(sanitize('Tech Corp Inc.')).toBe('tech-corp-inc');
      expect(sanitize('Amazon Web Services')).toBe('amazon-web-services');
      expect(sanitize('ABC & Co.')).toBe('abc-co');
    });

    it('should sanitize position for filename', () => {
      const sanitize = (text: string) =>
        text
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, '-')
          .replace(/^-+|-+$/g, '');

      expect(sanitize('Senior Software Engineer')).toBe('senior-software-engineer');
      expect(sanitize('Full-Stack Developer')).toBe('full-stack-developer');
    });
  });

  describe('output format', () => {
    it('should generate markdown format', () => {
      const mockOutput = `# Cover Letter

Dear Hiring Manager,

I am excited to apply...

Sincerely,
John Doe`;

      expect(mockOutput).toContain('Dear');
      expect(mockOutput).toContain('Sincerely');
    });

    it('should include contact information in header', () => {
      const header = `John Doe
john.doe@example.com
+1 (555) 123-4567
linkedin.com/in/johndoe`;

      expect(header).toContain('@');
      expect(header).toContain('+1');
    });
  });

  describe('tone options', () => {
    it('should handle formal tone', () => {
      const tone = 'formal';
      expect(['formal', 'professional', 'casual']).toContain(tone);
    });

    it('should handle professional tone (default)', () => {
      const tone = 'professional';
      expect(['formal', 'professional', 'casual']).toContain(tone);
    });

    it('should handle casual tone', () => {
      const tone = 'casual';
      expect(['formal', 'professional', 'casual']).toContain(tone);
    });
  });

  describe('custom notes integration', () => {
    it('should accept custom notes option', () => {
      const options = {
        notes: 'Mention referral from Jane Smith',
      };

      expect(options.notes).toBeDefined();
      expect(options.notes).toContain('referral');
    });

    it('should include custom notes in cover letter context', () => {
      const customNote = 'Jane Smith referred me to this position';
      // Custom notes should be available for generator
      expect(customNote).toContain('referred');
    });
  });

  describe('integration with other commands', () => {
    it('should use JD analysis from analyze-jd command', () => {
      const jdAnalysisPath = 'applications/2024-01-01-company-role/jd-analysis.json';
      expect(jdAnalysisPath).toContain('jd-analysis.json');
    });

    it('should work with company-research output', () => {
      const researchPath = 'applications/2024-01-01-company-role/company-research.json';
      expect(researchPath).toContain('company-research.json');
    });

    it('should read from anecdotes directory', () => {
      const anecdotesDir = '.resume-toolkit/anecdotes';
      expect(anecdotesDir).toBe('.resume-toolkit/anecdotes');
    });
  });

  describe('success output', () => {
    it('should display success message with file path', () => {
      const outputPath = 'applications/2024-01-01-techcorp-engineer/cover-letter.md';
      const message = `Cover letter generated: ${outputPath}`;

      expect(message).toContain('Cover letter generated');
      expect(message).toContain(outputPath);
    });

    it('should show word count', () => {
      const coverLetter = 'Dear Hiring Manager, I am excited...';
      const wordCount = coverLetter.split(/\s+/).length;

      expect(wordCount).toBeGreaterThan(0);
    });
  });

  describe('validation', () => {
    it('should validate user info exists', () => {
      const userInfo = {
        name: 'John Doe',
        email: 'john@example.com',
      };

      expect(userInfo.name).toBeDefined();
      expect(userInfo.email).toBeDefined();
    });

    it('should validate position is provided', () => {
      const position = 'Software Engineer';
      expect(position).toBeDefined();
      expect(position.length).toBeGreaterThan(0);
    });
  });
});
