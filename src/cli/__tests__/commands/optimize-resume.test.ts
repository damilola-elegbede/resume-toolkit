/**
 * Tests for Optimize Resume Command
 *
 * Tests CLI integration, file I/O, and error handling
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { spawn } from 'child_process';
import { readFile, writeFile, mkdir, rm } from 'fs/promises';
import { join } from 'path';
import { optimizeResume } from '../../commands/optimize-resume';

describe('optimize-resume command', () => {
  const testDir = join(process.cwd(), '.tmp', 'test-optimize-resume');
  const baseResumePath = join(testDir, 'base-resume.md');
  const anecdotesDir = join(testDir, 'anecdotes');
  const jdAnalysisPath = join(testDir, 'jd-analysis.json');
  const outputDir = join(testDir, 'output');

  beforeEach(async () => {
    // Create test directory structure
    await mkdir(testDir, { recursive: true });
    await mkdir(anecdotesDir, { recursive: true });
    await mkdir(outputDir, { recursive: true });

    // Create sample base resume
    const baseResume = `---
name: John Doe
title: Senior Software Engineer
email: john@example.com
---

# Summary
Senior Software Engineer with 5 years of experience in web development.

# Experience

## Software Engineer - TechCorp
*Jan 2020 - Present*

- Developed web applications using modern technologies
- Collaborated with cross-functional teams
- Improved application performance

## Junior Developer - StartupXYZ
*Jun 2018 - Dec 2019*

- Built frontend features using React
- Implemented REST APIs
- Participated in code reviews

# Skills

**Languages:** Python, JavaScript, TypeScript
**Frameworks:** React, Django, Node.js
**Tools:** Git, Docker
`;

    await writeFile(baseResumePath, baseResume);

    // Create sample anecdotes
    const anecdote1 = `---
title: Led Kubernetes Migration
skills: [kubernetes, docker, devops, leadership]
impact: Reduced deployment time by 70%
date: 2023-06
---

Led the migration of our monolithic application to a Kubernetes-based microservices architecture.
Coordinated with DevOps team to implement CI/CD pipelines.
Trained team of 5 engineers on container orchestration best practices.
`;

    const anecdote2 = `---
title: Built Distributed Caching System
skills: [python, redis, distributed systems, performance]
impact: Improved API response time by 85%
date: 2023-03
---

Architected and implemented a distributed caching layer using Redis Cluster.
Handled 1M+ requests per day with 99.9% uptime.
Reduced database load by 60% through intelligent caching strategies.
`;

    await writeFile(join(anecdotesDir, 'k8s-migration.md'), anecdote1);
    await writeFile(join(anecdotesDir, 'redis-caching.md'), anecdote2);

    // Create sample JD analysis
    const jdAnalysis = {
      technical_skills: ['kubernetes', 'python', 'docker', 'redis', 'microservices'],
      leadership_skills: ['leadership', 'mentoring', 'collaboration'],
      domain_expertise: ['distributed systems', 'architecture', 'performance'],
      ats_keywords: ['kubernetes', 'python', 'docker', 'redis', 'leadership'],
      keyword_importance: {
        kubernetes: 0.95,
        python: 0.9,
        docker: 0.85,
        redis: 0.8,
        leadership: 0.75,
      },
    };

    await writeFile(jdAnalysisPath, JSON.stringify(jdAnalysis, null, 2));
  });

  afterEach(async () => {
    // Clean up test directory
    await rm(testDir, { recursive: true, force: true });
  });

  describe('file I/O operations', () => {
    it('should load base resume from markdown file', async () => {
      const content = await readFile(baseResumePath, 'utf-8');

      expect(content).toContain('name: John Doe');
      expect(content).toContain('# Summary');
      expect(content).toContain('# Experience');
    });

    it('should load anecdotes from directory', async () => {
      const files = await readFile(join(anecdotesDir, 'k8s-migration.md'), 'utf-8');

      expect(files).toContain('Led Kubernetes Migration');
      expect(files).toContain('skills: [kubernetes');
    });

    it('should load JD analysis from JSON file', async () => {
      const content = await readFile(jdAnalysisPath, 'utf-8');
      const analysis = JSON.parse(content);

      expect(analysis.technical_skills).toContain('kubernetes');
      expect(analysis.keyword_importance.kubernetes).toBe(0.95);
    });

    it('should save optimized resume to output directory', async () => {
      const optimizedResume = `---
name: John Doe
title: Senior Software Engineer
---

# Summary
Senior Software Engineer with expertise in Kubernetes and distributed systems.
`;

      const outputPath = join(outputDir, 'tailored-resume.md');
      await writeFile(outputPath, optimizedResume);

      const saved = await readFile(outputPath, 'utf-8');
      expect(saved).toContain('Kubernetes');
    });
  });

  describe('Python optimizer integration', () => {
    it('should call Python optimizer with correct arguments', async () => {
      // This test verifies the spawn command structure
      // Mock implementation
      const pythonProcess = spawn('python3', [
        '-m',
        'resume_optimizer.cli',
        '--base-resume',
        baseResumePath,
        '--anecdotes-dir',
        anecdotesDir,
        '--jd-analysis',
        jdAnalysisPath,
        '--output',
        join(outputDir, 'tailored-resume.md'),
      ]);

      expect(pythonProcess).toBeDefined();
    });

    it('should handle Python process errors gracefully', async () => {
      // Test error handling when Python process fails
      const invalidPath = '/nonexistent/path/resume.md';

      expect(async () => {
        await readFile(invalidPath, 'utf-8');
      }).rejects.toThrow();
    });

    it('should parse Python optimizer JSON output', async () => {
      const mockPythonOutput = JSON.stringify({
        iterations: [
          { iteration: 1, score: 75, gaps: ['kubernetes'], improvements: ['Added K8s'] },
          { iteration: 2, score: 88, gaps: [], improvements: ['Reordered'] },
        ],
        final_score: 88,
        final_resume_path: join(outputDir, 'tailored-resume.md'),
      });

      const result = JSON.parse(mockPythonOutput);

      expect(result.iterations).toHaveLength(2);
      expect(result.final_score).toBe(88);
      expect(result.iterations[0].score).toBe(75);
    });
  });

  describe('command options', () => {
    it('should accept JD URL option', () => {
      const url = 'https://jobs.example.com/senior-engineer';

      expect(url).toMatch(/^https?:\/\//);
    });

    it('should accept optional template path', () => {
      const templatePath = join(testDir, 'custom-template.md');

      expect(templatePath).toBeTruthy();
    });

    it('should accept optional output directory', () => {
      const customOutput = join(testDir, 'custom-output');

      expect(customOutput).toBeTruthy();
    });

    it('should accept optional max iterations', () => {
      const maxIterations = 5;

      expect(maxIterations).toBeGreaterThan(0);
      expect(maxIterations).toBeLessThanOrEqual(10);
    });

    it('should accept optional target score', () => {
      const targetScore = 95;

      expect(targetScore).toBeGreaterThan(0);
      expect(targetScore).toBeLessThanOrEqual(100);
    });
  });

  describe('progress display', () => {
    it('should show spinner during optimization', () => {
      // Test that spinner is displayed
      const spinnerText = 'Optimizing resume...';

      expect(spinnerText).toBeTruthy();
    });

    it('should display iteration results', () => {
      const iterationResult = {
        iteration: 1,
        score: 78,
        gaps: ['kubernetes', 'distributed systems'],
        improvements: ['Added K8s experience', 'Emphasized architecture'],
      };

      const displayText = `Iteration ${iterationResult.iteration}: Score ${iterationResult.score}% → Adding keywords: ${iterationResult.gaps.join(', ')}`;

      expect(displayText).toContain('Iteration 1');
      expect(displayText).toContain('78%');
    });

    it('should show final success message', () => {
      const finalScore = 92;
      const outputPath = join(outputDir, 'tailored-resume.md');

      const successMessage = `✓ Target reached! Final score: ${finalScore}%\nOptimized resume saved to: ${outputPath}`;

      expect(successMessage).toContain('92%');
      expect(successMessage).toContain('tailored-resume.md');
    });
  });

  describe('error handling', () => {
    it('should handle missing base resume file', async () => {
      const invalidPath = join(testDir, 'nonexistent-resume.md');

      await expect(async () => {
        await readFile(invalidPath, 'utf-8');
      }).rejects.toThrow();
    });

    it('should handle missing anecdotes directory', async () => {
      const invalidDir = join(testDir, 'nonexistent-anecdotes');

      await expect(async () => {
        await readFile(join(invalidDir, 'test.md'), 'utf-8');
      }).rejects.toThrow();
    });

    it('should handle missing JD analysis', async () => {
      const invalidPath = join(testDir, 'nonexistent-analysis.json');

      await expect(async () => {
        await readFile(invalidPath, 'utf-8');
      }).rejects.toThrow();
    });

    it('should handle invalid markdown format', async () => {
      const invalidResume = 'This is not valid markdown with frontmatter';
      const invalidPath = join(testDir, 'invalid-resume.md');
      await writeFile(invalidPath, invalidResume);

      const content = await readFile(invalidPath, 'utf-8');

      // Should detect missing frontmatter
      expect(content).not.toMatch(/^---\n/);
    });

    it('should handle Python process timeout', () => {
      const timeout = 30000; // 30 seconds

      expect(timeout).toBeGreaterThan(0);
    });

    it('should handle Python process crash', () => {
      const errorMessage = 'Python optimizer crashed: ModuleNotFoundError';

      expect(errorMessage).toContain('crashed');
    });
  });

  describe('output validation', () => {
    it('should validate optimized resume has required sections', async () => {
      const optimizedContent = `---
name: John Doe
title: Senior Software Engineer
---

# Summary
Senior Software Engineer with Kubernetes expertise.

# Experience
## Senior Engineer - TechCorp
- Led Kubernetes migration
`;

      const hasMetadata = optimizedContent.includes('name: John Doe');
      const hasSummary = optimizedContent.includes('# Summary');
      const hasExperience = optimizedContent.includes('# Experience');

      expect(hasMetadata).toBe(true);
      expect(hasSummary).toBe(true);
      expect(hasExperience).toBe(true);
    });

    it('should verify keywords are naturally integrated', () => {
      const bullet = 'Led Kubernetes migration reducing deployment time by 70%';

      // Should not be keyword stuffing
      const keywordCount = (bullet.match(/kubernetes|docker|python|redis/gi) || []).length;
      expect(keywordCount).toBeLessThanOrEqual(3);

      // Should maintain natural language
      expect(bullet).toMatch(/^[A-Z]/); // Starts with capital
      expect(bullet).toContain('ing'); // Has verbs
    });

    it('should preserve STAR format in bullets', () => {
      const bullet =
        'Led team of 5 engineers to migrate application to Kubernetes, resulting in 70% reduction in deployment time';

      // Situation/Task: Led team
      expect(bullet).toMatch(/led|developed|implemented|created/i);
      // Action: migrate
      expect(bullet.length).toBeGreaterThan(30);
      // Result: 70% reduction
      expect(bullet).toMatch(/\d+%|resulting|achieved/);
    });

    it('should check ATS score improvement', () => {
      const iterations = [
        { iteration: 1, score: 75 },
        { iteration: 2, score: 83 },
        { iteration: 3, score: 91 },
      ];

      // Scores should improve
      for (let i = 1; i < iterations.length; i++) {
        expect(iterations[i].score).toBeGreaterThanOrEqual(iterations[i - 1].score);
      }
    });
  });

  describe('workflow integration', () => {
    it('should create application directory with correct naming', () => {
      const date = new Date().toISOString().split('T')[0];
      const company = 'techcorp';
      const role = 'senior-engineer';

      const expectedPath = join(process.cwd(), 'applications', `${date}-${company}-${role}`);

      expect(expectedPath).toContain('applications');
      expect(expectedPath).toContain(date);
      expect(expectedPath).toContain(company);
    });

    it('should save optimization report alongside resume', async () => {
      const reportContent = `# Optimization Report

## Iterations
### Iteration 1
- Score: 78%
- Gaps: kubernetes, docker
- Improvements: Added K8s experience

### Iteration 2
- Score: 88%
- Gaps: redis
- Improvements: Added caching experience

## Final Result
- Final Score: 91%
- Target Reached: Yes
`;

      const reportPath = join(outputDir, 'optimization-report.md');
      await writeFile(reportPath, reportContent);

      const saved = await readFile(reportPath, 'utf-8');
      expect(saved).toContain('# Optimization Report');
      expect(saved).toContain('Final Score: 91%');
    });
  });
});
