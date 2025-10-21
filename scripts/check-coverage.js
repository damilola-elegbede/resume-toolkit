#!/usr/bin/env node

/**
 * Coverage Quality Gate Checker
 * Enforces 85% minimum coverage for all command files
 */

const fs = require('fs');
const path = require('path');

const COVERAGE_THRESHOLD = 85;
const COVERAGE_FILE = path.join(__dirname, '../coverage/coverage-summary.json');

function checkCoverage() {
  console.log('\n🔍 Running Coverage Quality Gate Check...\n');

  if (!fs.existsSync(COVERAGE_FILE)) {
    console.error('❌ Coverage report not found!');
    console.error('   Run: npm run test:coverage');
    process.exit(1);
  }

  const coverage = JSON.parse(fs.readFileSync(COVERAGE_FILE, 'utf8'));

  // Filter for command files only
  const commandFiles = Object.entries(coverage)
    .filter(([file]) => file.includes('src/cli/commands/') && file.endsWith('.ts'))
    .filter(([file]) => !file.includes('.test.') && !file.includes('.spec.'));

  if (commandFiles.length === 0) {
    console.error('❌ No command files found in coverage report!');
    process.exit(1);
  }

  console.log(`📦 Checking coverage for ${commandFiles.length} command files...\n`);

  let totalLines = 0, coveredLines = 0;
  let totalBranches = 0, coveredBranches = 0;
  let totalFunctions = 0, coveredFunctions = 0;
  let totalStatements = 0, coveredStatements = 0;

  const failures = [];

  commandFiles.forEach(([file, metrics]) => {
    const fileName = path.basename(file);

    totalLines += metrics.lines.total;
    coveredLines += metrics.lines.covered;
    totalBranches += metrics.branches.total;
    coveredBranches += metrics.branches.covered;
    totalFunctions += metrics.functions.total;
    coveredFunctions += metrics.functions.covered;
    totalStatements += metrics.statements.total;
    coveredStatements += metrics.statements.covered;

    // Check if this file meets threshold
    const lineCoverage = metrics.lines.pct;
    const branchCoverage = metrics.branches.pct;
    const functionCoverage = metrics.functions.pct;
    const statementCoverage = metrics.statements.pct;

    if (lineCoverage < COVERAGE_THRESHOLD ||
        branchCoverage < COVERAGE_THRESHOLD ||
        functionCoverage < COVERAGE_THRESHOLD ||
        statementCoverage < COVERAGE_THRESHOLD) {
      failures.push({
        file: fileName,
        lines: lineCoverage,
        branches: branchCoverage,
        functions: functionCoverage,
        statements: statementCoverage
      });
    }
  });

  // Calculate overall coverage
  const overallLineCoverage = (coveredLines / totalLines * 100).toFixed(2);
  const overallBranchCoverage = (coveredBranches / totalBranches * 100).toFixed(2);
  const overallFunctionCoverage = (coveredFunctions / totalFunctions * 100).toFixed(2);
  const overallStatementCoverage = (coveredStatements / totalStatements * 100).toFixed(2);

  console.log('📊 Overall Command Coverage:');
  console.log(`   Lines:      ${overallLineCoverage}% (${coveredLines}/${totalLines})`);
  console.log(`   Branches:   ${overallBranchCoverage}% (${coveredBranches}/${totalBranches})`);
  console.log(`   Functions:  ${overallFunctionCoverage}% (${coveredFunctions}/${totalFunctions})`);
  console.log(`   Statements: ${overallStatementCoverage}% (${coveredStatements}/${totalStatements})`);
  console.log();

  if (failures.length > 0) {
    console.error(`❌ QUALITY GATE FAILED! ${failures.length} command(s) below ${COVERAGE_THRESHOLD}% threshold:\n`);

    failures.forEach(({ file, lines, branches, functions, statements }) => {
      console.error(`   ${file}:`);
      console.error(`     Lines:      ${lines.toFixed(2)}%`);
      console.error(`     Branches:   ${branches.toFixed(2)}%`);
      console.error(`     Functions:  ${functions.toFixed(2)}%`);
      console.error(`     Statements: ${statements.toFixed(2)}%`);
      console.error();
    });

    console.error(`💡 Fix: Add more tests to increase coverage above ${COVERAGE_THRESHOLD}%`);
    console.error(`   Run: npm run test:watch`);
    console.error();
    process.exit(1);
  }

  // Check overall coverage
  if (overallLineCoverage < COVERAGE_THRESHOLD ||
      overallBranchCoverage < COVERAGE_THRESHOLD ||
      overallFunctionCoverage < COVERAGE_THRESHOLD ||
      overallStatementCoverage < COVERAGE_THRESHOLD) {
    console.error(`❌ QUALITY GATE FAILED! Overall command coverage below ${COVERAGE_THRESHOLD}%`);
    console.error(`   Add more tests to meet the threshold.`);
    console.error();
    process.exit(1);
  }

  console.log(`✅ QUALITY GATE PASSED! All commands have ${COVERAGE_THRESHOLD}%+ coverage.`);
  console.log();
  process.exit(0);
}

checkCoverage();
