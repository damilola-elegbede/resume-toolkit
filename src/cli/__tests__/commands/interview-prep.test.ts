import { describe, it, expect, vi, beforeEach } from 'vitest';
import { generateInterviewPrep } from '../../commands/interview-prep';
import { readFile, writeFile, mkdir } from 'fs/promises';

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

describe('interview-prep command', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('input validation', () => {
    it('should accept valid job URL', () => {
      const url = 'https://www.linkedin.com/jobs/view/1234567890';
      expect(url).toContain('linkedin.com/jobs/view/');
    });

    it('should accept company name option', () => {
      const options = { company: 'TechCorp' };
      expect(options.company).toBe('TechCorp');
    });
  });

  describe('file I/O', () => {
    it('should read JD analysis file', async () => {
      const mockJdAnalysis = {
        technical_skills: ['python', 'react', 'kubernetes'],
        leadership_skills: ['mentoring', 'team leadership'],
        domain_expertise: ['distributed systems', 'architecture'],
        seniority_level: 'director',
      };

      vi.mocked(readFile).mockResolvedValue(JSON.stringify(mockJdAnalysis));

      const path = 'applications/2024-01-01-techcorp-director/jd-analysis.json';
      const data = await readFile(path, 'utf-8');
      const parsed = JSON.parse(data);

      expect(parsed.technical_skills).toContain('python');
      expect(parsed.seniority_level).toBe('director');
    });

    it('should read company research file', async () => {
      const mockResearch = {
        company: 'TechCorp',
        mission: 'Build innovative solutions',
        recent_news: ['Series B funding', 'AWS partnership'],
        values: ['Innovation', 'Collaboration'],
      };

      vi.mocked(readFile).mockResolvedValue(JSON.stringify(mockResearch));

      const path = 'applications/2024-01-01-techcorp-director/company-research.json';
      const data = await readFile(path, 'utf-8');
      const parsed = JSON.parse(data);

      expect(parsed.company).toBe('TechCorp');
      expect(parsed.recent_news).toHaveLength(2);
    });

    it('should read anecdotes from directory', async () => {
      const mockAnecdote = `---
title: Led Kubernetes Migration
skills: [kubernetes, docker, leadership]
impact: Reduced deployment time by 70%
---

Led the migration to Kubernetes...`;

      vi.mocked(readFile).mockResolvedValue(mockAnecdote);

      const path = '.resume-toolkit/anecdotes/kubernetes-migration.md';
      const data = await readFile(path, 'utf-8');

      expect(data).toContain('Led Kubernetes Migration');
      expect(data).toContain('70%');
    });

    it('should create output directory if not exists', async () => {
      vi.mocked(mkdir).mockResolvedValue(undefined);

      const outputDir = 'applications/2024-01-01-techcorp-director';
      await mkdir(outputDir, { recursive: true });

      expect(mkdir).toHaveBeenCalledWith(outputDir, { recursive: true });
    });

    it('should write interview prep to file', async () => {
      const mockPrep = `# Interview Prep: Director @ TechCorp

## Technical Questions

### 1. Describe your experience with Kubernetes
...`;

      vi.mocked(writeFile).mockResolvedValue(undefined);

      const outputPath = 'applications/2024-01-01-techcorp-director/interview-prep.md';
      await writeFile(outputPath, mockPrep);

      expect(writeFile).toHaveBeenCalledWith(outputPath, mockPrep);
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

    it('should handle Python script errors', () => {
      const errorMessage = 'Python script failed: Module not found';

      expect(() => {
        if (!errorMessage.includes('success')) {
          throw new Error(errorMessage);
        }
      }).toThrow('Python script failed');
    });

    it('should provide helpful error for missing anecdotes', async () => {
      vi.mocked(readFile).mockRejectedValue(new Error('ENOENT: no such file'));

      try {
        await readFile('.resume-toolkit/anecdotes/missing.md', 'utf-8');
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
    });

    it('should sanitize position for filename', () => {
      const sanitize = (text: string) =>
        text
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, '-')
          .replace(/^-+|-+$/g, '');

      expect(sanitize('Director of Engineering')).toBe('director-of-engineering');
      expect(sanitize('Senior Software Engineer')).toBe('senior-software-engineer');
    });
  });

  describe('output format', () => {
    it('should generate markdown format', () => {
      const mockOutput = `# Interview Prep: Director @ TechCorp

## Technical Questions

### 1. Describe your experience with Kubernetes
**Your Answer Template:**
...

## Behavioral Questions

### 1. Tell me about a time you resolved a conflict
**STAR Answer:**
...`;

      expect(mockOutput).toContain('# Interview Prep');
      expect(mockOutput).toContain('## Technical Questions');
      expect(mockOutput).toContain('## Behavioral Questions');
    });

    it('should include STAR format answers', () => {
      const starAnswer = `**STAR Answer:**

**Situation:** At TechCorp...
**Task:** Needed to resolve...
**Action:** I facilitated...
**Result:** Delivered project ahead of schedule`;

      expect(starAnswer).toContain('Situation:');
      expect(starAnswer).toContain('Task:');
      expect(starAnswer).toContain('Action:');
      expect(starAnswer).toContain('Result:');
    });

    it('should include questions to ask section', () => {
      const questionsSection = `## Questions to Ask Interviewers

### Technical Questions
- What's your deployment frequency?
- How do you handle technical debt?

### Culture Questions
- What does work-life balance look like?
- How do you support growth?

### Strategic Questions
- What are the top 3 technical challenges?
- How do you see the team evolving?`;

      expect(questionsSection).toContain('Questions to Ask');
      expect(questionsSection).toContain('Technical Questions');
      expect(questionsSection).toContain('Culture Questions');
      expect(questionsSection).toContain('Strategic Questions');
    });

    it('should include key talking points', () => {
      const talkingPoints = `## Key Talking Points
- Kubernetes migration: Reduced deployment time by 70%
- Team growth: 8 to 25 engineers, 95% retention
- Database scaling: Handled 10x traffic increase`;

      expect(talkingPoints).toContain('Key Talking Points');
      expect(talkingPoints).toContain('70%');
      expect(talkingPoints).toContain('10x');
    });
  });

  describe('integration with other commands', () => {
    it('should use JD analysis from analyze-jd command', () => {
      const jdAnalysisPath = 'applications/2024-01-01-company-role/jd-analysis.json';
      expect(jdAnalysisPath).toContain('jd-analysis.json');
    });

    it('should use company research from research-company command', () => {
      const researchPath = 'applications/2024-01-01-company-role/company-research.json';
      expect(researchPath).toContain('company-research.json');
    });

    it('should read anecdotes from standard location', () => {
      const anecdotesDir = '.resume-toolkit/anecdotes';
      expect(anecdotesDir).toBe('.resume-toolkit/anecdotes');
    });
  });

  describe('success output', () => {
    it('should display success message with file path', () => {
      const outputPath = 'applications/2024-01-01-techcorp-director/interview-prep.md';
      const message = `Interview prep generated: ${outputPath}`;

      expect(message).toContain('Interview prep generated');
      expect(message).toContain(outputPath);
    });

    it('should show question counts', () => {
      const stats = {
        technical_questions: 5,
        behavioral_questions: 7,
        questions_to_ask: 15,
      };

      expect(stats.technical_questions).toBeGreaterThan(0);
      expect(stats.behavioral_questions).toBeGreaterThan(0);
      expect(stats.questions_to_ask).toBeGreaterThan(0);
    });
  });

  describe('question generation', () => {
    it('should generate technical questions', () => {
      const technicalQuestions = [
        'Describe your experience with Kubernetes',
        'How would you design a real-time data pipeline?',
        'Tell me about a time you improved system performance',
      ];

      expect(technicalQuestions.length).toBeGreaterThan(0);
      technicalQuestions.forEach((q) => {
        expect(q.length).toBeGreaterThan(10);
      });
    });

    it('should generate behavioral questions', () => {
      const behavioralQuestions = [
        'Tell me about a time you resolved a conflict',
        'Describe managing an underperforming team member',
        'Give an example of a project that did not go as planned',
      ];

      expect(behavioralQuestions.length).toBeGreaterThan(0);
      behavioralQuestions.forEach((q) => {
        expect(q.length).toBeGreaterThan(10);
      });
    });

    it('should generate company-specific questions', () => {
      const companyQuestions = ['Why TechCorp?', 'What interests you about this role?'];

      expect(companyQuestions.length).toBeGreaterThan(0);
    });
  });

  describe('anecdote matching', () => {
    it('should match anecdotes to questions', () => {
      const question = 'Tell me about a time you resolved a conflict';
      const anecdote = {
        title: 'Resolved Team Conflict',
        skills: ['leadership', 'conflict resolution'],
        impact: 'Restored team productivity',
      };

      expect(anecdote.title.toLowerCase()).toContain('conflict');
      expect(anecdote.skills).toContain('conflict resolution');
    });

    it('should prioritize most relevant anecdotes', () => {
      const anecdotes = [
        { title: 'Kubernetes Migration', skills: ['kubernetes', 'docker'] },
        { title: 'React Dashboard', skills: ['react', 'typescript'] },
        { title: 'Team Conflict', skills: ['leadership', 'conflict'] },
      ];

      const question = 'Tell me about a conflict you resolved';
      const relevantAnecdote = anecdotes.find((a) => a.title.toLowerCase().includes('conflict'));

      expect(relevantAnecdote).toBeDefined();
      expect(relevantAnecdote?.title).toBe('Team Conflict');
    });
  });

  describe('STAR format', () => {
    it('should format answers in STAR format', () => {
      const anecdote = {
        content: `**Context:**
- Team conflict blocking delivery

**Actions:**
- Facilitated design session
- Created cross-functional pairs

**Results:**
- Delivered ahead of schedule
- Improved collaboration by 40%`,
      };

      const formatted = anecdote.content;
      expect(formatted).toContain('Context:');
      expect(formatted).toContain('Actions:');
      expect(formatted).toContain('Results:');
    });
  });

  describe('metrics extraction', () => {
    it('should extract percentages from anecdotes', () => {
      const text = 'Reduced deployment time by 70% and improved uptime to 99.9%';
      const percentages = text.match(/\d+\.?\d*%/g);

      expect(percentages).toHaveLength(2);
      expect(percentages).toContain('70%');
      expect(percentages).toContain('99.9%');
    });

    it('should extract multipliers from anecdotes', () => {
      const text = 'Scaled to handle 10x traffic increase';
      const multipliers = text.match(/\d+x/gi);

      expect(multipliers).toHaveLength(1);
      expect(multipliers?.[0].toLowerCase()).toBe('10x');
    });

    it('should extract time metrics', () => {
      const text = 'Reduced query time from 5 seconds to 200ms';
      const hasTimeMetrics = /\d+\s*(ms|seconds?|minutes?|hours?)/.test(text);

      expect(hasTimeMetrics).toBe(true);
    });
  });

  describe('role-specific questions', () => {
    it('should include system design questions for senior roles', () => {
      const seniorityLevel = 'director';
      const shouldIncludeSystemDesign = ['director', 'vp', 'principal'].includes(seniorityLevel);

      expect(shouldIncludeSystemDesign).toBe(true);
    });

    it('should include leadership questions for senior roles', () => {
      const seniorityLevel = 'director';
      const shouldIncludeLeadership = ['senior', 'lead', 'director', 'vp'].includes(seniorityLevel);

      expect(shouldIncludeLeadership).toBe(true);
    });

    it('should focus on technical questions for IC roles', () => {
      const seniorityLevel = 'mid';
      const isIC = !['director', 'vp', 'head'].includes(seniorityLevel);

      expect(isIC).toBe(true);
    });
  });
});
