/**
 * Parse Resume Command - Convert PDF resume to structured markdown
 *
 * Usage: resume-toolkit parse-resume <pdf-file>
 *
 * Converts a PDF resume into structured markdown format with YAML frontmatter.
 * Extracts contact information, experience, education, skills, etc.
 */

import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { resolve } from 'path';

import chalk from 'chalk';
import { Command } from 'commander';
import ora from 'ora';

interface ParseOptions {
  output?: string;
  verbose?: boolean;
}

export const parseResumeCommand = new Command('parse-resume')
  .description('Convert PDF resume to structured markdown template')
  .argument('<pdf-file>', 'Path to PDF resume file')
  .option(
    '-o, --output <path>',
    'Output markdown file path (default: .resume-toolkit/base-resume.md)'
  )
  .option('-v, --verbose', 'Show verbose output')
  .action(async (pdfFile: string, options: ParseOptions) => {
    const spinner = ora('Parsing resume PDF...').start();

    try {
      // Resolve paths
      const pdfPath = resolve(pdfFile);
      const outputPath = options.output
        ? resolve(options.output)
        : resolve(process.cwd(), '.resume-toolkit', 'base-resume.md');

      // Validate PDF file exists
      if (!existsSync(pdfPath)) {
        spinner.fail(chalk.red(`PDF file not found: ${pdfFile}`));
        process.exit(1);
      }

      // Get project root and Python script path
      const projectRoot = resolve(__dirname, '../../..');
      const pythonScript = resolve(projectRoot, 'src/python/pdf_parser/cli.py');

      if (options.verbose) {
        spinner.info(`PDF file: ${pdfPath}`);
        spinner.info(`Output file: ${outputPath}`);
        spinner.info(`Python script: ${pythonScript}`);
      }

      // Check if Python script exists
      if (!existsSync(pythonScript)) {
        spinner.fail(
          chalk.red('PDF parser script not found. Please ensure Python dependencies are installed.')
        );
        process.exit(1);
      }

      // Build Python command
      // Use venv if it exists, otherwise use system Python
      const venvPython = resolve(projectRoot, 'venv/bin/python');
      const pythonCmd = existsSync(venvPython) ? venvPython : 'python3';

      const command = `${pythonCmd} "${pythonScript}" "${pdfPath}" "${outputPath}"`;

      if (options.verbose) {
        spinner.info(`Running: ${command}`);
      }

      // Execute Python parser
      try {
        const output = execSync(command, {
          encoding: 'utf-8',
          cwd: projectRoot,
          env: {
            ...process.env,
            PYTHONPATH: resolve(projectRoot, 'src/python'),
          },
        });

        if (options.verbose && output) {
          spinner.info(output.trim());
        }

        spinner.succeed(chalk.green(`Resume parsed successfully: ${outputPath}`));

        // Show next steps
        console.log('\n' + chalk.blue('Next steps:'));
        console.log(chalk.gray('  1. Review the generated markdown file'));
        console.log(chalk.gray('  2. Edit and customize as needed'));
        console.log(chalk.gray('  3. Use as base template for tailored resumes'));
      } catch (error: any) {
        const errorMessage = error.stderr?.toString() || error.message;
        spinner.fail(chalk.red('Failed to parse PDF'));
        console.error(chalk.red('\nError details:'));
        console.error(chalk.gray(errorMessage));

        if (errorMessage.includes('pdfplumber')) {
          console.error(chalk.yellow('\nHint: Make sure pdfplumber is installed:'));
          console.error(chalk.gray('  pip install -r requirements.txt'));
        }

        process.exit(1);
      }
    } catch (error: any) {
      spinner.fail(chalk.red('An error occurred'));
      console.error(chalk.red(error.message));
      if (options.verbose) {
        console.error(error);
      }
      process.exit(1);
    }
  });
