---
name: merge-pr
description: Run pre-flight integration checks, evaluate system dependency risks, merge the PR, and perform cleanup
argument-hint: <pr-number>
---

# Merge PR Gate

**Input**: $ARGUMENTS

## Your Mission

Run safety checks on a pull request before merging:
1. Verify CI status and branch freshness.
2. Analyze the changed files and map downstream dependencies/services that rely on them.
3. Audit for breaking database changes, API schema changes, or missing environment variables.
4. Present a pre-flight risk report and wait for user approval.
5. Merge the PR, clean up branches, and transition the associated Jira issue to Done.

**Core Philosophy**: The merge command is a safety gate. Never merge blindly. Always understand the blast radius of changes.

**Golden Rule**: If CI is failing or there is unresolved env drift, warn the user and do not merge automatically.

---

## Phase 1: PRE-FLIGHT SYSTEM CHECKS

### 1.1 Verify PR and CI Status

```bash
# Get PR status, target branch, and source branch details
gh pr view {NUMBER} --json number,title,headRefName,baseRefName,state,mergeable

# Check remote CI status (GitHub Actions, etc.)
gh pr checks {NUMBER}
```

- **If PR is already merged or closed**: Stop and inform user.
- **If CI checks are failing**: Warn user of build/test failures on the branch.
- **If there are merge conflicts**: Stop and instruct user to resolve conflicts first.

### 1.2 Check Branch Drift

Check if the PR branch is up-to-date with its target branch (e.g., `main`):
```bash
git fetch origin
# Compare commits between origin/{baseRefName} and the PR branch
git log origin/{baseRefName}..origin/{headRefName} --oneline
```
If the base branch has moved significantly ahead of the PR branch, note this in the risk assessment.

---

## Phase 2: BLAST RADIUS & IMPACT ANALYSIS

### 2.1 Identify Changed Files

```bash
# Get the names of all files changed in the PR
gh pr diff {NUMBER} --name-only
```

### 2.2 Trace Downstream Dependencies (Impact Mapping)

Scan the codebase to locate files/services that import or depend on the modified files:
* For each modified file, search for import statements referencing it (e.g., `import ... from 'path/to/modified'`).
* Group the affected files by service, module, or system layer (e.g., Frontend Hooks, Backend Controllers, Shared Utils).

### 2.3 Check Environment Variable Drift

Detect if new environment variables have been introduced:
* Diff `.env.example` between the PR branch and the base branch:
```bash
gh pr diff {NUMBER} -- .env.example
```
* If any environment variables were added, highlight them as required configuration steps for deployment.

### 2.4 Audit for Breaking Changes

Analyze the diff to detect potential regressions or breaking changes:
* **Database Schema Changes**: Check for migrations or SQL script changes. Look for column drops, table renames, or restrictive constraints.
* **API Route & Controller Changes**: Check for route renames, parameter deletions, or format shifts in request/response bodies.
* **Component/Prop Signature Changes**: Check if exported function signatures or React component props were changed without updating all callers.

---

## Phase 3: PRE-FLIGHT INTEGRATION REPORT

Generate a comprehensive risk brief and present it to the user. Do not proceed to merge until this report is generated.

### Output Report Template:

```markdown
# Pre-Flight Merge Assessment: PR #{NUMBER}

## 📊 Status Summary
- **PR Title**: {title}
- **Source Branch**: `{headRefName}` ➔ `{baseRefName}`
- **CI Status**: {PASSING / FAILING / PENDING}
- **Conflicts**: {None / Conflict Present}

## 🔍 Blast Radius (Files & Dependencies)
| Modified File | Downstream Consumers / Dependent Files | Impact Risk Level |
|---|---|---|
| `path/to/file.ts` | `src/components/Card.tsx`, `src/pages/Home.tsx` | Medium |
| `src/services/api.ts`| `src/hooks/useFetch.ts` | High (Shared Service) |

## ⚠️ Risk Evaluation
* **Database Migrations**: {None / Yes (non-destructive) / Warning (destructive action detected)}
* **API Schema Changes**: {None / Backward-Compatible / Breaking Change Detected}
* **Environment Variable Drift**: {None / New variables added: [list]}
* **Branch Freshness**: {Up-to-date with main / X commits behind main}

## 🚀 Deployment Action Items
- [ ] Add env vars to production dashboard: `{VAR_NAME}`
- [ ] Run database migrations during deployment.
```

> **⚠️ WARNING**: If risk factors (Failing CI, destrutive DB changes, breaking APIs) are high, flag them clearly in a blockquote.

---

## Phase 4: EXECUTE MERGE (With User Consent)

1. Prompt the user for explicit approval to merge:
   * **"Do you want to proceed with squash-merging this PR and deleting the remote branch?"**
2. If approved, execute the merge:
```bash
# Squash merge the PR and delete the source branch
gh pr merge {NUMBER} --squash --delete-branch
```

---

## Phase 5: LOCAL CLEANUP & SYNC

After a successful merge, clean up the local git state:
```bash
# Switch to base branch (e.g. main)
git checkout {baseRefName}

# Pull latest merged changes
git pull origin {baseRefName}

# Delete the local feature branch if it exists
git branch -d {headRefName}
```

---

## Phase 6: JIRA TICKET TRANSITION

If a Jira issue was associated with the branch (either in the PR title, git branch name, or `.agents/plans` metadata):

1. **Resolve Cloud ID**:
   Call `mcp__atlassian__getAccessibleAtlassianResources` to get the `cloudId`.
2. **Transition the Ticket to Done**:
   * Call `mcp__atlassian__getTransitionsForJiraIssue` to discover transitions.
   * Call `mcp__atlassian__transitionJiraIssue` to move the status of the key (e.g. `RH-5`) to "Done" or "Closed".
3. **Add Comment**:
   * Comment on the issue notifying that the PR was merged and the feature is completed.

---

## Phase 7: MERGE COMPLETE SUMMARY

Provide a summary of the merge operation in chat:

```markdown
## PR Merged Successfully 🎉

- **PR**: #{NUMBER}
- **Branch**: `{headRefName}` merged into `{baseRefName}`
- **Jira Status**: `{ISSUE_KEY}` transitioned to **Done**
- **Local Git State**: Synced with `origin/{baseRefName}`, local branch `{headRefName}` cleaned up.

### 📋 Post-Merge Action Items
1. [ ] Deploy code to staging/production environment.
2. [ ] {Any specific DB migration or env var setup noted in Phase 3}.
```
