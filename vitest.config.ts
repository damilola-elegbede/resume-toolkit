import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    exclude: ['node_modules', 'dist', '.idea', '.git', '.cache'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: [
        'src/**/*.{test,spec}.{ts,tsx}',
        'src/**/__tests__/**',
        'src/**/types/**',
        'src/**/interfaces/**',
        'dist/**',
      ],
      all: true,
      // Coverage Restoration Plan:
      // - Current: 40% (baseline as of Jan 2025)
      // - Target: 80%+ to match CLAUDE.md standards
      // - Milestones: 50% (Q1 2025), 65% (Q2 2025), 80% (Q3 2025)
      // - Priority: Critical paths first (parsing, optimization, scoring)
      // - Tracking: Monitor per-command coverage in CI reports
      // Global coverage thresholds (overall project coverage)
      lines: 40,
      functions: 40,
      branches: 40,
      statements: 40,
      // Per-file enforcement disabled for now - will be enabled incrementally
      // as test coverage improves across all commands
      thresholds: {
        lines: 40,
        functions: 40,
        branches: 40,
        statements: 40,
        perFile: false,
      },
    },
    testTimeout: 10000,
    hookTimeout: 10000,
    teardownTimeout: 10000,
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: false,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@cli': path.resolve(__dirname, './src/cli'),
      '@python': path.resolve(__dirname, './src/python'),
    },
  },
});
