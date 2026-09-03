---
name: fix-review
description: Apply fixes from a code review report with validation loops
argument-hint: <path/to/review.md | PR number>
---

# Fix Review

**Input**: $ARGUMENTS

## Your Mission

Read a code review report, checkout the PR branch, apply all required fixes in priority order, validate after each change, and push the result.

**Core Philosophy**: Review fixes are surgical — small, targeted patches. Move fast but validate constantly.

**Golden Rule**: Fix Critical and High issues first. Never push with unresolved Critical issues.

---

## Phase 1: LOAD REVIEW

### Locate Review File

| Input | Action |
|-------|--------|
| File path (e.g. `.agents/reviews/pr-5-review.md`) | Read directly |
| PR number (e.g. `5`, `#5`) | Look for `.agents/reviews/pr-5-review.md` |
| Blank | Find the most recently modified file in `.agents/reviews/` |

**If review not found:**
```
Error: No review found at $ARGUMENTS
Run a review first: /review <PR number>
```

### Extract Review Data

From the review file, extract:

- **PR Number / Scope** — what was reviewed
- **Branch** — from the `Branch` metadata field
- **Recommendation** — APPROVE or NEEDS WORK
- **Issues** — grouped by severity (Critical, High, Medium, Suggestions)
- **Validation Results** — which checks passed/failed

**If recommendation is APPROVE and no Critical/High issues:**
```
✅ Review is clean — no fixes needed.
```
Stop here.

---

## Phase 2: PREPARE

### Severity Gate

Determine which issues to fix based on severity:

| Severity | Action |
|----------|--------|
| **Critical** | MUST fix — blocks merge |
| **High** | MUST fix — blocks merge |
| **Medium** | FIX if straightforward, SKIP if risky or ambiguous |
| **Suggestions** | SKIP unless user explicitly requested |

If `$ARGUMENTS` includes `--all`, fix everything including suggestions.

### Checkout PR Branch

```bash
# Get current branch
git branch --show-current

# Checkout the PR branch (from review metadata)
git checkout {branch-name}

# Make sure it's up to date
git pull origin {branch-name}
```

| State | Action |
|-------|--------|
| Already on PR branch | Continue |
| On different branch, clean | Checkout PR branch |
| On different branch, dirty | STOP: "Stash or commit changes first" |

---

## Phase 3: FIX

**Process each issue in priority order: Critical → High → Medium → Suggestions**

### For Each Issue:

#### 3.1 Understand the Issue

- Read the file(s) mentioned in the review issue
- Read adjacent/related files for context
- Understand what the reviewer flagged and why

#### 3.2 Apply the Fix

- Make the minimal change that resolves the issue
- Follow existing codebase patterns (don't introduce new patterns during a fix)
- If the fix touches tests, update them too

#### 3.3 Validate Immediately

**After EVERY fix:**

```bash
# Build / type check
pnpm run build  # or the project's equivalent

# Lint
pnpm run lint

# Tests
pnpm test
```

**If validation fails:**
1. Read the error
2. Fix the regression
3. Re-run validation
4. Only proceed when passing

#### 3.4 Track Progress

```
Issue 1 (Critical): Missing input validation in api.ts  ✅ FIXED
Issue 2 (High):     Unhandled promise rejection          ✅ FIXED
Issue 3 (Medium):   Inconsistent naming                  ⏭️ SKIPPED (ambiguous scope)
Issue 4 (Suggestion): Consider memoization               ⏭️ SKIPPED (suggestion)
```

**If a fix is too risky or ambiguous**, skip it and document why. Don't introduce new bugs fixing review comments.

---

## Phase 4: VALIDATE

### Run Full Validation Suite

```bash
# Type check
pnpm run build

# Lint
pnpm run lint

# Tests
pnpm test
```

**All must pass with zero errors.**

### Regression Check

- Re-read each fixed file to confirm the changes are clean
- Verify no unintended side effects on adjacent code
- If the review mentioned specific test scenarios, verify they pass

---

## Phase 5: COMMIT & PUSH

### Commit the Fixes

```bash
git add -A
git commit -m "fix: address review feedback

Resolves:
- {Issue 1 summary}
- {Issue 2 summary}
{...}

Review: .agents/reviews/{review-file}"
```

### Push

```bash
git push origin {branch-name}
```

---

## Phase 6: REPORT

### Create Fix Report

**Output path**: `.agents/reports/{scope-name}-review-fixes.md`

```bash
mkdir -p .agents/reports
```

```markdown
# Review Fix Report

**Review**: `{path-to-review-file}`
**Branch**: `{branch-name}`
**Status**: {COMPLETE / PARTIAL}

## Original Review Summary

- **Recommendation**: {APPROVE / NEEDS WORK}
- **Total Issues**: {N}
- **Critical**: {N} | **High**: {N} | **Medium**: {N} | **Suggestions**: {N}

## Fixes Applied

| # | Severity | Issue | File | Status | Notes |
|---|----------|-------|------|--------|-------|
| 1 | Critical | {description} | `path/file` | ✅ FIXED | |
| 2 | High | {description} | `path/file` | ✅ FIXED | |
| 3 | Medium | {description} | `path/file` | ⏭️ SKIPPED | {reason} |

## Validation Results

| Check | Result |
|-------|--------|
| Type check | ✅ |
| Lint | ✅ |
| Tests | ✅ ({N} passed) |

## Remaining Issues

{List any skipped issues with rationale, or "All issues resolved."}

## Files Changed

| File | Lines Changed |
|------|---------------|
| `path/file` | +{N}/-{M} |
```

### Link the Artifacts

The fix report should reference:
- The original plan: `.agents/plans/{name}.plan.md`
- The implementation report: `.agents/reports/{name}-report.md`
- The review: `.agents/reviews/{scope}-review.md`

This creates a full audit trail: **plan → implement → review → fix**

---

## Phase 7: OUTPUT

```markdown
## Review Fixes Applied

**Review**: `{review-file}`
**Branch**: `{branch-name}`
**Status**: ✅ Complete

### Issues Resolved

| Severity | Fixed | Skipped |
|----------|-------|---------|
| Critical | {N} | {N} |
| High | {N} | {N} |
| Medium | {N} | {N} |
| Suggestions | {N} | {N} |

### Validation

| Check | Result |
|-------|--------|
| Type check | ✅ |
| Lint | ✅ |
| Tests | ✅ |

### Remaining

{List skipped issues or "All issues resolved."}

### Artifacts

- Fix report: `.agents/reports/{name}-review-fixes.md`
- Original review: `.agents/reviews/{scope}-review.md`

### Next Steps

1. Re-review if needed: `/review {PR}`
2. Merge when approved
```

---

## Handling Failures

| Failure | Action |
|---------|--------|
| Review file not found | Stop and tell user to run `/review` first |
| Branch checkout fails | Stop and tell user to resolve git state |
| Fix introduces regression | Revert the fix, skip that issue, document why |
| Validation fails after all fixes | Debug, fix the failure, re-validate |
| Too many issues to fix safely | Fix Critical/High only, skip rest, note in report |
