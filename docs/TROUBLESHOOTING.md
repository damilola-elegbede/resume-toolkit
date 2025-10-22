# Troubleshooting Guide

Comprehensive guide for resolving common issues with Resume Toolkit.

## Table of Contents

- [Installation Problems](#installation-problems)
- [Turso Database Connection](#turso-database-connection)
- [PDF Parsing Errors](#pdf-parsing-errors)
- [Web Scraping Failures](#web-scraping-failures)
- [Command Execution Issues](#command-execution-issues)
- [Database Issues](#database-issues)
- [Performance Issues](#performance-issues)
- [Getting Help](#getting-help)

## Installation Problems

### npm install fails with peer dependency errors

```bash
# Error
npm ERR! Could not resolve dependency:
npm ERR! peer react@"^18.0.0" from react-dom@18.2.0

# Solution 1: Use --legacy-peer-deps
npm install --legacy-peer-deps

# Solution 2: Update package.json to match peer dependencies
npm install react@^18.0.0 react-dom@^18.0.0
```

### Python dependencies fail to install

```bash
# Error
ERROR: Failed building wheel for some-package

# Solution: Install build tools
# macOS:
brew install python@3.11
xcode-select --install

# Ubuntu:
sudo apt-get update
sudo apt-get install python3-dev build-essential

# Then retry:
pip install -e ".[dev]"
```

## Turso Database Connection

### Cannot connect to Turso database

```bash
# Error
Error: Failed to connect to database
LibsqlError: SQLITE_AUTH: not authorized

# Solution: Verify environment variables
echo $TURSO_DATABASE_URL
echo $TURSO_AUTH_TOKEN

# If empty, reconfigure:
turso db show resume-toolkit --url
turso db tokens create resume-toolkit

# Update .env file
cat > .env << EOF
TURSO_DATABASE_URL=libsql://your-db.turso.io
TURSO_AUTH_TOKEN=your-token-here
EOF
```

### Database schema not initialized

```bash
# Error
Error: table "resumes" does not exist

# Solution: Push schema
npm run db:push

# Or manually initialize:
turso db shell resume-toolkit < schema.sql
```

### Database connection timeout

```bash
# Error
Error: Connection timeout after 5000ms

# Solution 1: Check network connectivity
curl https://your-db.turso.io

# Solution 2: Increase timeout
# In database config:
{
  "connectionTimeout": 10000
}

# Solution 3: Use local development database
export NODE_ENV=development
npm run db:push
```

## PDF Parsing Errors

### PDF parsing fails with encoding errors

```bash
# Error
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x89

# Solution: Install additional dependencies
pip install pdfplumber chardet

# Or try alternative parser:
npm run cli parse-resume --parser pypdf2 resume.pdf
```

### Corrupted or scanned PDF

```bash
# Error
Error: No text extracted from PDF

# Solution 1: Check if PDF is scanned image
# Use OCR parser:
pip install pytesseract
npm run cli parse-resume --ocr resume.pdf

# Solution 2: Convert to text first
# macOS:
pdftotext resume.pdf resume.txt
npm run cli parse-resume resume.txt

# Solution 3: Re-export PDF from source document
```

### PDF parsing extracts garbled text

```bash
# Symptom: Text appears as random characters

# Solution: Try different extraction method
# In Python code:
from pdfminer.high_level import extract_text
text = extract_text('resume.pdf', codec='utf-8')

# Or use pdfplumber with layout:
import pdfplumber
with pdfplumber.open('resume.pdf') as pdf:
    text = pdf.pages[0].extract_text(layout=True)
```

## Web Scraping Failures

### Company research returns no data

```bash
# Error
Error: Failed to fetch company data: 403 Forbidden

# Solution 1: Website blocking automated requests
# Add user agent:
headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; ResumeToolkit/1.0)'
}

# Solution 2: Rate limiting
# Add delay between requests:
import time
time.sleep(2)  # 2 second delay

# Solution 3: Use API instead of scraping
# Check if company has public API
```

### Job description URL returns 404

```bash
# Error
Error: Job posting not found (404)

# Solution 1: Job may have been removed
# Use cached version or saved text file instead

# Solution 2: URL requires authentication
# Download HTML manually and parse from file:
npm run cli analyze-jd --file job-posting.html

# Solution 3: Use Internet Archive
https://web.archive.org/save/[original-url]
```

### Cloudflare or bot protection

```bash
# Error
Error: Cloudflare security check detected

# Solution: Not recommended to bypass
# Instead, save page manually:
# 1. Open URL in browser
# 2. Save page as HTML
# 3. Parse from file:
npm run cli research-company --file company-page.html
```

## Command Execution Issues

### Command not found

```bash
# Error
bash: resume-toolkit: command not found

# Solution: Use npm script instead
npm run cli <command>

# Or install globally:
npm install -g .
resume-toolkit <command>
```

### Permission denied

```bash
# Error
EACCES: permission denied, open '/Users/...'

# Solution 1: Fix file permissions
chmod +x dist/index.js

# Solution 2: Run with proper permissions
sudo npm run cli <command>  # Not recommended

# Solution 3: Fix ownership
sudo chown -R $USER:$USER .resume-toolkit/
```

### Python process fails silently

```bash
# Error: Command succeeds but no output

# Solution: Check Python logs
# Enable debug mode:
export DEBUG=true
npm run cli <command>

# Check Python error output:
python python/main.py <args> 2>&1 | tee error.log

# Verify Python environment:
which python
python --version
```

## Database Issues

### Duplicate key error

```bash
# Error
UNIQUE constraint failed: resumes.id

# Solution 1: Check for existing record
npm run cli parse-resume --force resume.pdf

# Solution 2: Use update instead of insert
# Or delete old record:
turso db shell resume-toolkit "DELETE FROM resumes WHERE id='...'"
```

### Database locked

```bash
# Error
Error: database is locked

# Solution 1: Close other connections
# Check for running processes:
ps aux | grep turso

# Solution 2: Use Turso cloud instead of local
export NODE_ENV=production

# Solution 3: Increase timeout
# In database config:
{
  "busyTimeout": 5000
}
```

## Performance Issues

### Commands running very slowly

```bash
# Symptom: Commands take >30 seconds

# Solution 1: Check network connectivity
ping turso.io

# Solution 2: Use local database for development
export NODE_ENV=development

# Solution 3: Enable caching
# In config.json:
{
  "cache": {
    "enabled": true,
    "ttl": 3600
  }
}

# Solution 4: Profile performance
npm run cli <command> --profile
```

### High memory usage

```bash
# Symptom: Process killed by OS

# Solution 1: Process smaller files
# Split large resume into sections

# Solution 2: Increase Node memory limit
export NODE_OPTIONS="--max-old-space-size=4096"
npm run cli <command>

# Solution 3: Use streaming for large files
# Enable in config:
{
  "streaming": true
}
```

## Getting Help

### Debug Mode

Enable verbose logging to see detailed error information:

```bash
# Enable verbose logging
export DEBUG=resume-toolkit:*
npm run cli <command>

# Save logs to file
npm run cli <command> 2>&1 | tee debug.log
```

### Check System Status

Verify installation and dependencies:

```bash
# Verify installation
npm run cli doctor

# Expected output:
✓ Node.js version: 18.17.0
✓ Python version: 3.11.5
✓ Database connection: OK
✓ Required dependencies: OK
⚠ Optional dependencies: 1 missing (pytesseract)
```

### Report Issues

Generate diagnostic report for bug reports:

```bash
# Generate diagnostic report
npm run cli diagnose > diagnostic-report.txt

# Submit issue with:
# 1. Diagnostic report
# 2. Error messages
# 3. Steps to reproduce
# 4. Expected vs actual behavior
```

## Common Error Messages

| Error Message | Likely Cause | Quick Fix |
|--------------|--------------|-----------|
| `SQLITE_AUTH: not authorized` | Invalid Turso credentials | Regenerate auth token |
| `table "resumes" does not exist` | Schema not initialized | Run `npm run db:push` |
| `UnicodeDecodeError` | PDF encoding issue | Install pdfplumber |
| `Command not found` | Not installed globally | Use `npm run cli` |
| `Permission denied` | File permissions | Run `chmod +x dist/index.js` |
| `Connection timeout` | Network/firewall issue | Check network connectivity |
| `Database locked` | Multiple connections | Close other processes |
| `Process killed` | Out of memory | Increase Node memory limit |

## Additional Resources

- See [CLAUDE.md](../CLAUDE.md) for general usage
- See [CONTRIBUTING.md](../CONTRIBUTING.md) for development setup
- File issues on GitHub for additional help
