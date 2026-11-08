# Agent Workspace Slash Commands

This repository contains the templates and instruction specifications for custom coding agent workflows. These workflows are categorized into three main tracks: **Fresh Projects**, **Story Implementation**, and **Live Projects & Reviews**.

---

## Workspace Workflows

### 1. Fresh Project Initialization Workflow
Use this workflow when bootstraping a new project from scratch.
```
[Fresh Window] ──(Discuss Requirements)──> /create-prd ──(Same Window)──> /create-stories ──> /create-rules
```

### 2. Feature & Story Implementation Loop
Use this loop to implement defined features/stories in isolation.
```
[Fresh Window] ──> /prime ──(Discuss Feature)──> /plan-feature ──> [Clear Context / Fresh Window] ──> /implement ──> /postmortem ──> /commit
```

### 3. Review & Feedback Loop
Use this loop to quality-gate changes, review PRs, automatically fix issues, and safely merge.
```
[Fresh Window on main] ──> /review <PR> ──> [Clear Context] ──> /fix-review <Review File> ──> [Clear Context] ──> /merge-pr <PR>
```

---

## Command Reference Catalog

### 1. `create-prd`
* **What it does**: Synthesizes the discussion context into a formal Product Requirements Document (PRD) specifying user requirements, architecture, and scope.
* **Arguments**: None (or optional topic).
* **Context Style**: 🧠 **Primed Context** (should be run after a back-and-forth discussion of requirements so the agent has all context loaded in its history).
* **Possible Scenarios**: When starting a brand new project and transitioning from brainstorm/chat mode to documentation.

### 2. `create-stories`
* **What it does**: Reads the generated PRD and breaks it down into small, distinct, actionable user stories (Jira style) to form the backlog.
* **Arguments**: `<path/to/prd.md>`
* **Context Style**: 🧠 **Primed Context** (run in the same session or right after the PRD is finalized).
* **Possible Scenarios**: To create the feature checklist right after writing the PRD.

### 3. `create-rules`
* **What it does**: Analyzes the project layout and conventions to write a custom ruleset (`CLAUDE.md` or system guidelines) to ensure the agent adheres to coding standards.
* **Arguments**: Optional directory path.
* **Context Style**: 🧠 **Primed Context** (run against the bootstrapped project directory).
* **Possible Scenarios**: During project setup or whenever adding a major system dependency that introduces new style rules.

### 4. `prime`
* **What it does**: Performs workspace exploration by listing tracked files, directory maps, reading documentation, and checking git status to load the workspace context.
* **Arguments**: None.
* **Context Style**: 🧼 **Fresh Context** (run immediately upon opening a new agent session).
* **Possible Scenarios**: 
  * Starting a new session to work on a feature.
  * Loading state before discussing a plan.
  * Checking out main before executing a review.

### 5. `plan-feature`
* **What it does**: Researches matching patterns in the codebase and creates a structured implementation plan (`.agents/plans/{kebab-name}.plan.md`) without writing any actual project code.
* **Arguments**: `<feature description | path/to/prd.md>`
* **Context Style**: 🧠 **Primed Context** (run after discussing implementation ideas with the agent and agreeing on the direction).
* **Possible Scenarios**: When you are ready to detail *how* a feature/story should be built, mapping out the precise file modifications and validation commands.

### 6. `implement`
* **What it does**: Reads the plan, switches to or creates a feature branch, and executes each plan step sequentially. Validates build/test stages after *every* single step.
* **Arguments**: `<path/to/plan.md>`
* **Context Style**: 🧼 **Fresh Context** (clear the chat window before running this command so the agent doesn't get confused by planning discussion).
* **Possible Scenarios**: Executing the plan end-to-end after a planning phase.

### 7. `postmortem`
* **What it does**: Creates a postmortem decision log (`.agents/decisions/{feature}.md`) capturing architecture decisions, errors, and workarounds.
* **Arguments**: `[feature-name]`
* **Context Style**: 🧠 **Primed Context** (run in the implementation session immediately after `/implement` completes).
* **Possible Scenarios**: Documenting lesson learned and decisions right after finishing the code implementation.

### 8. `commit`
* **What it does**: Verifies the final unstaged/dirty status, stages changes, and makes a structured git commit with atomic prefixes (e.g., `feat:`, `fix:`).
* **Arguments**: None.
* **Context Style**: 🧠 **Primed Context** (run at the end of the implementation session).
* **Possible Scenarios**: Staging and committing changes to prepare for pulling and opening a PR.

### 9. `review`
* **What it does**: Checks out the target, parses files/PRs, runs automated checks (build, lint, test), gates quality via severity thresholds, and outputs a report.
* **Arguments**: `<pr-number|file|folder|scope> [--gate=high|medium|critical]`
* **Context Style**: 🧼 **Fresh Context** (run on a clean window on your base branch, e.g. `main`).
* **Possible Scenarios**: When a PR is submitted and you need an agent to check types, tests, code patterns, and security risks.

### 10. `fix-review`
* **What it does**: Reads a review report, checkouts the PR branch, automatically runs a repair loop fixing Critical -> High -> Medium issues, and pushes the fixes.
* **Arguments**: `<path/to/review.md | PR number> [--all]`
* **Context Style**: 🧼 **Fresh Context** (run in a clean agent session to focus entirely on fixing).
* **Possible Scenarios**: After a review report signals `NEEDS WORK` and you want to auto-remediate the feedback.

### 11. `merge-pr`
* **What it does**: Runs integration safety checks, maps downstream file dependencies, audits API breaking changes and database migration safety, presents a risk evaluation report, merges the PR, cleans up local/remote branch states, and transitions the associated Jira ticket to Done.
* **Arguments**: `<pr-number>`
* **Context Style**: 🧼 **Fresh Context** (run in a clean session before merging to avoid context pollution).
* **Possible Scenarios**: When you are satisfied with a PR's status, review fixes have passed, and you want to safely squash-merge and clean up branches.


### 12. `excalidraw-diagram`
* **What it does**: Generates `.excalidraw` diagrams that argue visually (not just label boxes) for workflows, architectures, and protocols — maps each concept to a matching visual pattern (fan-out, convergence, timeline, cycle), includes evidence artifacts (real code snippets, data formats, API names), renders the result to PNG headlessly, and runs a render-view-fix loop until the layout is clean. Light and dark modes are supported via `references/color-palette.md` / `color-palette-dark.md`.
* **Arguments**: `<concept|workflow|architecture to diagram>` (usually discussed in session first).
* **Context Style**: 🧠 **Primed Context** (run after discussing the system you want visualized so the diagram reflects the real design, not generic boxes).
* **Possible Scenarios**: 
  * Visualizing a system architecture for a README or docs.
  * Explaining a protocol or pipeline (e.g., TLS handshake, event loop, RAG) as a teaching diagram.
  * Before/after or side-by-side visuals for a design decision.
* **Setup**: One-time `npm i -g agent-browser && agent-browser install` (headless Chromium via CDP). The render script is stdlib-only Python — no pip/uv packages.
