# Interview Prep Command

Generate comprehensive interview preparation materials based on job description analysis, company research, and your resume anecdotes. Get ready to ace your interview with tailored questions, STAR-format answers, and strategic questions to ask.

## Usage

```bash
resume-toolkit interview-prep <job-url> [options]
```

## Arguments

- `<job-url>` - Job description URL (LinkedIn, Greenhouse, Lever, Indeed, Workday)

## Options

- `-c, --company <name>` - Company name (if different from JD)
- `-a, --anecdotes <path>` - Path to anecdotes directory (default: `.resume-toolkit/anecdotes`)

## Examples

### Basic Usage

```bash
resume-toolkit interview-prep https://www.linkedin.com/jobs/view/1234567890
```

### With Custom Company Name

```bash
resume-toolkit interview-prep https://jobs.lever.co/company/role --company "TechCorp Inc"
```

### With Custom Anecdotes Path

```bash
resume-toolkit interview-prep https://www.linkedin.com/jobs/view/123 \
  --anecdotes ~/my-career/achievements
```

## Prerequisites

### 1. Job Description Analysis

The command will automatically analyze the JD if not already done, but you can run it separately:

```bash
resume-toolkit analyze-jd <url>
```

### 2. Company Research (Optional but Recommended)

After running the command once, enhance `applications/YYYY-MM-DD-company-role/company-research.json`:

```json
{
  "company": "TechCorp",
  "mission": "To build innovative cloud solutions that scale globally",
  "values": ["Innovation", "Collaboration", "Customer Focus"],
  "recent_news": [
    "Announced $50M Series B funding",
    "Launched new AWS partnership program",
    "Expanded engineering team to 200+ engineers"
  ],
  "culture": "Fast-paced startup with strong engineering culture and work-life balance",
  "tech_stack": ["Python", "React", "AWS", "Kubernetes", "PostgreSQL"]
}
```

Then regenerate for more personalized preparation materials.

### 3. Anecdotes Directory

Create `.resume-toolkit/anecdotes/` with markdown files containing your achievements:

Example: `.resume-toolkit/anecdotes/kubernetes-migration.md`

```markdown
---
title: Led Kubernetes Migration
skills: [kubernetes, docker, devops, leadership, aws]
impact: Reduced deployment time by 70%
date: 2023-06
company: TechCorp
---

Led the migration of our monolithic application to a Kubernetes-based microservices architecture.

**Context:**
- Legacy monolithic application with 2-hour deployment cycles
- Team of 5 engineers unfamiliar with container orchestration
- Growing performance issues affecting 1M+ users

**Actions:**
- Designed microservices architecture with 12 independent services
- Implemented Kubernetes cluster on AWS EKS with auto-scaling
- Trained team on Docker containerization and Kubernetes best practices
- Created comprehensive documentation and runbooks

**Results:**
- Reduced deployment time from 2 hours to 20 minutes (70% improvement)
- Improved system uptime from 99.5% to 99.9%
- Enabled independent service scaling, reducing infrastructure costs by 30%
- Team became self-sufficient in K8s operations within 3 months
```

Example: `.resume-toolkit/anecdotes/team-conflict-resolution.md`

```markdown
---
title: Resolved Cross-Team Conflict
skills: [leadership, conflict resolution, communication, stakeholder management]
impact: Delivered project 1 week ahead of revised timeline
date: 2023-03
company: TechCorp
---

Resolved a major conflict between frontend and backend teams blocking project delivery.

**Situation:**
- Frontend and backend teams had conflicting API design approaches
- Project was 2 weeks behind schedule due to constant redesigns
- Team morale declining, finger-pointing escalating

**Task:**
- Needed to mediate the conflict and get the critical project back on track
- Had to restore trust between teams for future collaboration

**Action:**
- Facilitated joint design session with both teams
- Established clear API contract using OpenAPI specification
- Created documentation standards both teams agreed to
- Formed cross-functional pairs for remaining work
- Set up daily syncs to catch issues early

**Result:**
- Delivered project 1 week ahead of revised timeline
- Improved team collaboration scores by 40% in next survey
- Established lasting cross-team communication practices
- API design process became template for other projects
```

## Output

The command generates a comprehensive interview prep document:

**File:** `applications/YYYY-MM-DD-company-role/interview-prep.md`

### Example Output

```
Interview Prep Generated Successfully!

Details:
  Company: TechCorp
  Position: Director of Engineering
  Technical Questions: 6
  Behavioral Questions: 7
  Questions to Ask: 15+
  Anecdotes Used: 5

Saved to: applications/2024-10-21-techcorp-director-of-engineering/interview-prep.md

Next Steps:
  1. Review and customize the generated questions and answers
  2. Practice your STAR answers out loud (2-3 minutes each)
  3. Research the interviewers on LinkedIn if names are provided
  4. Prepare 3-5 thoughtful questions tailored to each interviewer
```

## Interview Prep Structure

The generated document includes:

### 1. Technical Questions

Questions based on JD requirements with answer templates from your experience:

```markdown
## Likely Technical Questions

### 1. Describe your experience with Kubernetes

**Your Answer Template (STAR):**

**Situation:** At TechCorp, we had a monolithic application serving 1M+ users with
2-hour deployment cycles causing frequent production issues.

**Task:** Lead migration to Kubernetes-based microservices architecture.

**Action:** Designed microservices architecture with 12 independent services,
implemented K8s cluster on AWS EKS with auto-scaling, trained team of 5 engineers
on containerization best practices.

**Result:** Reduced deployment time from 2 hours to 20 minutes (70% improvement),
improved uptime from 99.5% to 99.9%, reduced infrastructure costs by 30%.

### 2. How would you design a real-time data pipeline?

**Your Answer Template:**
[Approach: requirements gathering, architecture decisions, technology choices,
scalability considerations, and trade-offs based on your analytics platform experience]
```

### 2. Behavioral Questions

STAR-format answers matched from your anecdotes:

```markdown
## Behavioral Questions

### 1. Tell me about a time you resolved a conflict

**STAR Answer:**

**Situation:** Frontend and backend teams had conflicting API design approaches,
project 2 weeks behind schedule.

**Task:** Mediate conflict and get critical project back on track.

**Action:** Facilitated joint design session, established clear API contract,
created cross-functional pairs, set up daily syncs.

**Result:** Delivered 1 week ahead of revised timeline, improved collaboration
scores by 40%, established lasting communication practices.

### 2. Describe managing an underperforming team member

**STAR Answer:**
[Matched from your performance management anecdote]
```

### 3. Company-Specific Questions

Tailored to the specific company:

```markdown
## Company-Specific Questions

### 1. Why TechCorp?

**Your Answer:**
"I'm excited about TechCorp's recent $50M Series B funding and AWS partnership
program. Having followed your growth from Series A to B, I'm impressed by your
focus on distributed systems and cloud solutions. Your mission to build innovative
solutions that scale globally aligns perfectly with my experience scaling systems
to handle 10x traffic increases. The values around Innovation and Collaboration
resonate with my leadership approach of fostering strong engineering cultures."
```

### 4. Questions to Ask Interviewers

Categorized by type:

```markdown
## Questions to Ask Interviewers

### Technical Questions

- What's your current deployment frequency and what are the main blockers?
- How does the team handle on-call and incident management?
- What's the balance between new features and technical debt?
- Can you walk me through a recent technical challenge the team faced?
- How do you approach testing and quality assurance?

### Culture Questions

- What does work-life balance look like for this role?
- How does the team collaborate - what does a typical day look like?
- What are the biggest opportunities for professional growth?
- How do you support continuous learning and development?
- How are decisions made between engineering and product?

### Strategic Questions

- What are the top 3 technical challenges for this role in the next year?
- How do you see the engineering organization evolving?
- What does success look like in the first 90 days?
- How will the recent Series B funding impact engineering priorities?
```

### 5. Key Talking Points

Your strongest achievements relevant to the role:

```markdown
## Key Talking Points

- Kubernetes migration: Reduced deployment time by 70%
- Team growth: Scaled from 8 to 25 engineers, 95% retention
- Database scaling: Handled 10x traffic increase, 99.99% uptime
- Cross-team collaboration: Improved collaboration scores by 40%
- Technical leadership: Led 5 major architecture initiatives
```

## Role-Specific Preparation

The generator adapts to role seniority:

### Individual Contributor Roles

- **Focus:** Technical depth, problem-solving, collaboration
- **Questions:** Coding challenges, technical design, teamwork
- **Less emphasis:** People management, organizational strategy

### Senior IC / Staff Engineer

- **Focus:** Technical leadership, architecture, mentoring
- **Questions:** System design, technical influence, cross-team projects
- **Moderate emphasis:** Technical mentoring, technical strategy

### Engineering Manager / Director

- **Focus:** People leadership, team building, delivery
- **Questions:** Conflict resolution, performance management, team growth
- **High emphasis:** Leadership scenarios, organizational impact

### VP / Executive

- **Focus:** Strategic vision, organizational design, business impact
- **Questions:** Strategic decisions, organizational transformation, stakeholder management
- **Very high emphasis:** Business alignment, executive presence

## Tips for Effective Preparation

### 1. Customize Your Answers

The generated answers are templates - personalize them:

- Add specific metrics and numbers
- Include relevant technical details
- Adjust tone to match company culture
- Make sure stories feel authentic

### 2. Practice STAR Answers Out Loud

- Each answer should be 2-3 minutes when spoken
- Practice pacing and natural delivery
- Don't memorize word-for-word - know the key points
- Record yourself to catch filler words ("um", "like")

### 3. Prepare for Follow-ups

Interviewers will dig deeper:

- Know technical details of your projects
- Be ready to discuss trade-offs and alternatives
- Prepare for "What would you do differently?" questions
- Have metrics and impact numbers ready

### 4. Research Interviewers

If you know who will interview you:

- Check their LinkedIn profiles
- Read their blog posts or talks
- Tailor questions to their expertise
- Find common connections or interests

### 5. Use the "Rule of Three"

For each question, prepare:

- **Primary answer:** Your best, most relevant example
- **Backup answer:** Alternative example if they ask for another
- **Follow-up details:** Technical specifics, metrics, learnings

### 6. Prepare Questions for Different Interviewer Types

**For Hiring Manager:**

- Team dynamics and culture
- Success metrics for the role
- Biggest challenges ahead

**For Peer Engineers:**

- Day-to-day work and collaboration
- Technical challenges and tech debt
- Development practices and tools

**For Skip-Level (Director/VP):**

- Team vision and strategy
- Organizational priorities
- Growth opportunities

**For HR/Recruiter:**

- Interview process timeline
- Team structure and growth
- Compensation and benefits

## Common Pitfalls to Avoid

### 1. Generic Answers

**Bad:** "I have experience with Kubernetes."

**Good:** "At TechCorp, I led our migration to Kubernetes, reducing deployment
time by 70% and improving uptime to 99.9%. Let me walk you through the approach..."

### 2. Rambling Stories

Keep STAR answers focused:

- **Situation:** 1-2 sentences
- **Task:** 1 sentence
- **Action:** 2-3 sentences (most detail here)
- **Result:** 1-2 sentences with metrics

### 3. Negative Language

Frame challenges positively:

**Bad:** "The team was terrible at communication."

**Good:** "We had opportunities to improve cross-team communication, so I..."

### 4. Taking All Credit

Use "I" for your actions, "we" for team results:

**Good:** "I designed the architecture and mentored the team. We achieved
99.9% uptime and reduced costs by 30%."

### 5. No Questions Prepared

Always have questions ready - "No questions" signals:

- Lack of interest
- Poor preparation
- Lack of curiosity

## Interview Day Checklist

**Before the Interview:**

- [ ] Review company research and recent news
- [ ] Practice 3-5 key STAR stories out loud
- [ ] Prepare 5-7 questions for each interviewer
- [ ] Review JD and match your experience to requirements
- [ ] Check equipment (video, audio) if remote
- [ ] Have resume and notes accessible

**During the Interview:**

- [ ] Listen carefully to the full question
- [ ] Take a moment to think before answering
- [ ] Use STAR format for behavioral questions
- [ ] Include specific metrics and impact
- [ ] Ask clarifying questions when needed
- [ ] Take notes on interviewer responses
- [ ] End with 2-3 thoughtful questions

**After the Interview:**

- [ ] Send thank-you email within 24 hours
- [ ] Reference specific discussion points
- [ ] Reiterate your interest and fit
- [ ] Note any follow-up items mentioned

## Workflow Integration

### Recommended Preparation Workflow

1. **Analyze JD** - `resume-toolkit analyze-jd <url>`
2. **Research Company** - `resume-toolkit research-company <url>` (if available)
3. **Generate Interview Prep** - `resume-toolkit interview-prep <url>`
4. **Review and Customize** - Personalize answers and add details
5. **Practice Answers** - Rehearse out loud, time yourself
6. **Prepare Questions** - Tailor to specific interviewers
7. **Mock Interview** - Practice with a friend or mentor
8. **Final Review** - Day before, review key points

### Continuous Improvement

After each interview:

1. Update anecdotes with new experiences
2. Add questions you were asked
3. Refine answers that didn't land well
4. Note what worked well to repeat

## Best Practices

1. **Keep answers concise** - 2-3 minutes maximum
2. **Lead with impact** - Start with the result, then explain how
3. **Use specific numbers** - "Reduced by 70%" not "significantly reduced"
4. **Show your thinking** - Explain trade-offs and decision-making
5. **Be authentic** - Don't exaggerate or fabricate stories
6. **Stay positive** - Frame challenges as opportunities
7. **Ask great questions** - Shows genuine interest and preparation
8. **Practice regularly** - Update and rehearse your stories

## See Also

- `analyze-jd` - Analyze job descriptions to identify key requirements
- `research-company` - Research company for personalized preparation (if available)
- `generate-cover-letter` - Generate personalized cover letter
- `optimize-resume` - Tailor resume to job description
