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
      // Global coverage thresholds (overall project coverage)
      // Set to current coverage level - will increase as tests are added
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
