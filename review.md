---
name: review
description: Code review - reviews PRs, files, folders, or any code scope
argument-hint: <pr-number|file|folder|scope> [--gate=high|medium|critical] [--plan=path] [--report=path]
---

# Code Review

**Input**: $ARGUMENTS

## Your Mission

Perform a thorough code review:
1. **Understand** what you're reviewing and its purpose
2. **Check** the code against project patterns
3. **Verify Compliance** — compare the implemented changes against the intended plan and implementation report (if available) to ensure intent is met and deviations are justified
4. **Run** validation (type-check, lint, tests)
5. **Identify** issues by severity
6. **Gate** — determine if the PR passes the severity threshold
7. **Report** findings with branch metadata so `/fix-review` can consume the output

**Golden Rule**: Be constructive and actionable. Every issue should have a clear recommendation.

---

## Phase 1: DETERMINE SCOPE & ARTIFACTS

### Parse Input

| Input Type | Example | Action |
|------------|---------|--------|
| PR number | `123`, `#123` | Fetch PR diff with `gh pr diff 123` |
| PR URL | `github.com/.../pull/123` | Extract number, fetch PR diff |
| File path | `src/api/flags.ts` | Review single file |
| Folder path | `server/src/` | Review all files in folder |
| Blank | (none) | Review unstaged git changes |

### Parse Flags

| Flag | Default | Effect |
|------|---------|--------|
| `--gate=critical` | — | Only block on Critical issues |
| `--gate=high` | ✅ default | Block on Critical + High issues |
| `--gate=medium` | — | Block on Critical + High + Medium issues |
| `--plan=<path>` | (auto-detect) | Compare against a specific implementation plan |
| `--report=<path>` | (auto-detect) | Compare against a specific implementation report |

### Get Review Target

**For PR:**
```bash
gh pr view {NUMBER} --json number,title,author,headRefName,baseRefName,files
gh pr diff {NUMBER}
```

**For file/folder:**
```bash
# List files to review
find {path} -name "*.ts" -o -name "*.tsx" | grep -v node_modules
```

**For blank (unstaged changes):**
```bash
git diff --name-only
git diff
```

### Capture Branch Metadata

**Always capture this information** — it's required for `/fix-review` to work:

```bash
# For PRs
gh pr view {NUMBER} --json headRefName,baseRefName --jq '.headRefName + " -> " + .baseRefName'

# For non-PR reviews
git branch --show-current
```

Record:
- **PR Branch** (head): the branch with the changes
- **Base Branch**: what it's merging into (usually `main`)
- **PR Number**: if applicable

### Resolve Plan and Report Artifacts

If `--plan` or `--report` are not explicitly specified:
1. Identify the feature name from the branch name (e.g. `feature/add-auth` ➔ `add-auth`) or the PR title.
2. Search `.agents/plans/` and `.agents/plans/completed/` for `{feature-name}.plan.md`.
3. Search `.agents/reports/` for `{feature-name}-report.md`.
4. If found, load both files to read the intent and outcomes.

---

## Phase 2: CONTEXT & INTENT MATCHING

### Read Project Rules

- Understand the patterns in the codebase

### Understand Intent

- For PRs: Read title and description
- For files: Understand the file's purpose in the codebase
- For changes: What was modified and why?

### Parse Plan and Report (Intent Verification)

If plan or report files are available:
1. **Extract Plan Scope**:
   - What were the **Acceptance Criteria**?
   - What files were designated to be **CREATED** or **UPDATED**?
   - What tests were planned?
2. **Extract Report Outcomes**:
   - What deviations did the implementation report record?
3. **Compare Diff to Plan**:
   - Did the implementation create/update files that were *not* in the plan? Are these changes justified?
   - Were any files/tasks in the plan omitted?
   - Does the test coverage in the diff align with the planned test specifications?

---

## Phase 3: REVIEW

### Review Each File

For each file in scope, check:

| Category | Check |
|----------|-------|
| **Compliance & Intent** | Does the code align with the plan design? Are all Acceptance Criteria satisfied? If deviations occurred, are they documented and correct? |
| **Correctness** | Does the code work as intended? |
| **Type Safety** | Are types explicit, no implicit `any`? |
| **Patterns** | Does it follow existing codebase patterns? |
| **Error Handling** | Are errors handled appropriately? |
| **Tests** | Are there tests for this code? |
| **Security** | No hardcoded secrets, proper input validation? |
| **Performance** | No obvious N+1 queries, unnecessary re-renders, memory leaks? |

### Categorize Issues

| Severity | Criteria | Blocks Merge? |
|----------|----------|---------------|
| **Critical** | Security issues, data loss, crashes | Always |
| **High** | Type violations, missing error handling, logic errors | At `--gate=high` (default) and above |
| **Medium** | Pattern inconsistencies, missing edge cases | At `--gate=medium` only |
| **Low** | Style suggestions, minor improvements | Never |

**For each issue, provide:**
- **File and line reference** (e.g. `src/api.ts:45-52`)
- **What's wrong** — specific, not vague
- **How to fix** — actionable recommendation
- **Severity** — one of the four levels above

---

## Phase 4: VALIDATE

Run automated checks:

```bash
# Type check
pnpm run build

# Lint
pnpm run lint

# Tests
pnpm test
```

---

## Phase 5: GATE DECISION

### Apply Severity Gate

Count issues by severity and compare against the gate threshold:

| Gate Level | Blocks on | Passes with |
|------------|-----------|-------------|
| `critical` | Critical only | High + Medium + Low |
| `high` (default) | Critical + High | Medium + Low |
| `medium` | Critical + High + Medium | Low only |

### Determine Recommendation

| Condition | Recommendation |
|-----------|----------------|
| No blocking issues AND validation passes | **APPROVE** |
| Has blocking issues OR validation fails | **NEEDS WORK** |

---

## Phase 6: REPORT

### Create Report

**Output path**: `.agents/reviews/{scope-name}-review.md`

```bash
mkdir -p .agents/reviews
```

```markdown
# Code Review: {SCOPE}

## Metadata

| Field | Value |
|-------|-------|
| **Scope** | {PR #N / file path / folder path / unstaged changes} |
| **PR Number** | {N or "N/A"} |
| **Branch** | {head branch name, e.g. "feature/add-auth"} |
| **Base** | {base branch name, e.g. "main"} |
| **Author** | {PR author or "N/A"} |
| **Date** | {current date} |
| **Gate** | {critical / high / medium} |
| **Recommendation** | {APPROVE / NEEDS WORK} |

## Summary

{2-3 sentences: What was reviewed and overall assessment}

## Issues Found

### Critical
{List with file:line references and fix recommendations, or "None"}

### High Priority
{List with file:line references and fix recommendations, or "None"}

### Medium Priority
{List with file:line references and fix recommendations, or "None"}

### Suggestions
{List with file:line references and fix recommendations, or "None"}

## Issue Count

| Severity | Count | Blocks Merge? |
|----------|-------|---------------|
| Critical | {N} | {Yes/No based on gate} |
| High | {N} | {Yes/No based on gate} |
| Medium | {N} | {Yes/No based on gate} |
| Suggestions | {N} | No |

## Validation Results

| Check | Status |
|-------|--------|
| Type Check | {PASS/FAIL} |
| Lint | {PASS/FAIL} |
| Tests | {PASS/FAIL} |

## What's Good

{Acknowledge positive aspects — good patterns, clean code, thorough tests}

## Recommendation

{What needs to happen next — specific action items or "Ready to merge"}

## Audit Trail

| Artifact | Path |
|----------|------|
| Plan | `.agents/plans/{name}.plan.md` (if found) |
| Implementation Report | `.agents/reports/{name}-report.md` (if found) |
| This Review | `.agents/reviews/{scope-name}-review.md` |
```

### Post to GitHub (if PR)

```bash
gh pr review {NUMBER} --comment --body-file .agents/reviews/pr-{NUMBER}-review.md
```

---

## Phase 7: OUTPUT

```markdown
## Review Complete

**Scope**: {what was reviewed}
**Branch**: {branch name}
**Gate**: {severity threshold}
**Recommendation**: {APPROVE / NEEDS WORK}

### Issues Found

| Severity | Count | Blocks? |
|----------|-------|---------|
| Critical | {N} | {Yes/No} |
| High | {N} | {Yes/No} |
| Medium | {N} | {Yes/No} |
| Suggestions | {N} | No |

### Validation

| Check | Result |
|-------|--------|
| Type Check | {PASS/FAIL} |
| Lint | {PASS/FAIL} |
| Tests | {PASS/FAIL} |

### Report

`.agents/reviews/{scope-name}-review.md`

### Next Steps

{If NEEDS WORK: "Run `/fix-review .agents/reviews/{scope-name}-review.md` to apply fixes automatically."}
{If APPROVE: "Ready to merge. Run `gh pr merge {NUMBER}`."}
```