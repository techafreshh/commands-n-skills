---
name: postmortem
description: Generate a postmortem report of decisions, errors, and workarounds from the implementation phase
argument-hint: [feature-name]
---

# Postmortem & Decision Log

**Feature**: $ARGUMENTS (if provided, otherwise auto-detected from context)

## Your Mission

Analyze the implementation work just completed in this session, document all key decisions, errors/roadblocks, workarounds, and outcomes, and save this log to `.agents/decisions/{feature}.md`.

---

## Phase 1: IDENTIFY FEATURE & PLAN

Determine the `{feature}` name to use for the output filename:
1. If `$ARGUMENTS` is provided, use that as the `{feature}` name.
2. Otherwise, look at the active session history for the name of the feature or plan that was implemented (e.g., the plan-name from the implementation report or plan file).
3. If not clear from session history, check the `.agents/reports/` directory for the most recently modified report file, and extract the feature name from the filename: `{plan-name}-report.md` -> `{plan-name}` is the feature.
4. If still not found, check the current git branch name (if a git repository exists).
5. If all automatic detection fails, ask the user for the feature name.

---

## Phase 2: ANALYZE IMPLEMENTATION DETAILS

Review the chat log of this active session and any relevant files to gather information:

1. **Key Decisions & Rationale**:
   - What architectural, design, or layout decisions were made?
   - What files were created or modified, and what design choices drove those changes?
   - Were there any library choices or database schema decisions?

2. **Errors & Roadblocks Encountered**:
   - What went wrong? What errors did you encounter (e.g., linter errors, type check failures, compilation errors, runtime issues, test failures)?
   - List specific error messages or behavior if possible.

3. **Workarounds & Resolutions**:
   - How did you resolve the errors or workarounds?
   - Did you have to change any code logic, update dependencies, or adjust commands?

4. **What Went Right & What Went Wrong**:
   - What parts of the implementation were smooth?
   - What parts were unexpectedly difficult or failed initially?

---

## Phase 3: WRITE DECISION LOG

Create the directory `.agents/decisions/` if it does not exist, and write the postmortem report to `.agents/decisions/{feature}.md`.

### Document Structure for `.agents/decisions/{feature}.md`:

```markdown
# Decision Log & Implementation Postmortem: {feature}

- **Date**: {Current Date}
- **Branch**: {Active git branch, or 'N/A' if not in a git repo}
- **Report Path**: `.agents/reports/{feature}-report.md` (if exists)

## 1. Summary of Implementation
{A concise description of the feature implemented and the primary goals achieved}

## 2. Key Decisions & Rationale
{List the major architectural, design, or logic choices made, along with the reasoning behind them}

## 3. Errors & Roadblocks Encountered
{Detail any errors, compilation failures, lint issues, or testing blockages faced during the process}

## 4. Workarounds & Resolutions
{Explain the solutions, workarounds, or fixes applied to overcome the roadblocks detailed above}

## 5. What Went Right & What Went Wrong
- **What Went Right**: {List points}
- **What Went Wrong**: {List points}

## 6. Lessons Learned & Recommendations
{Key takeaways and future recommendations for maintaining or interacting with this codebase area}
```

---

## Phase 4: OUTPUT SUMMARY

Provide a summary of the postmortem directly in the chat for the user, using the following format:

```markdown
## Postmortem Completed 📝

The decision log and postmortem report has been saved to `.agents/decisions/{feature}.md`.

### Summary of Decisions & Roadblocks

| Area | Key Findings |
|---|---|
| **Key Decisions** | {Short bullet points of top decisions} |
| **Errors Faced** | {Short bullet points of errors encountered} |
| **Workarounds** | {Short bullet points of how errors were resolved} |
| **Outcomes** | {What went right / lessons learned} |
```
