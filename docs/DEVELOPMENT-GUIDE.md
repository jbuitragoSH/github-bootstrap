# Development Guide

## Overview

This document describes the recommended development workflow for GitHub Bootstrap.

It is intended for developers who need to:

- configure the local development environment
- modify existing capabilities
- implement new synchronization features
- run automated verification
- validate behavior against GitHub
- prepare changes for commit

GitHub Bootstrap is developed incrementally using small vertical slices.

The general development cycle is:

```text
Define a small capability
        ↓
Implement end-to-end
        ↓
Run focused tests
        ↓
Run make verify
        ↓
Validate with dry-run
        ↓
Perform controlled E2E validation when required
        ↓
Commit
```

The project favors working software, explicit designs, and incremental evolution over speculative abstractions.

---

## Development Principles

Development should follow several practical principles.

### Small Vertical Slices

New functionality should be implemented as a complete, small capability.

For a new managed GitHub resource, a typical slice may include:

```text
Specification
      ↓
Parser
      ↓
State Discovery
      ↓
Planner
      ↓
Executor
      ↓
GitHub API
      ↓
Tests
      ↓
E2E Validation
```

Avoid implementing several unrelated resources simultaneously.

A capability should ideally reach a usable state before beginning the next one.

---

### Keep Changes Focused

A development change should have a clear purpose.

Good examples include:

```text
Add milestone creation
Add Issue discovery
Add iteration field creation
Detect label drift
Fix closed Issue detection
```

Avoid combining unrelated changes such as:

```text
Add Views
Refactor CLI
Change labels
Rewrite tests
Update field synchronization
```

in a single development slice.

Focused changes are easier to:

- understand
- test
- review
- debug
- revert
- document

---

### Avoid Premature Abstraction

Do not introduce abstractions only because they may be useful in the future.

The preferred evolution is:

```text
First working implementation
        ↓
Second similar implementation
        ↓
Repeated pattern becomes visible
        ↓
Actual duplication or coupling appears
        ↓
Small refactor
```

A concrete implementation is preferable to a generic framework whose future requirements are still unknown.

---

### Preserve Architectural Boundaries

The main technical responsibilities should remain separated.

```text
Specification
→ Desired state

State
→ Current GitHub state

Planner
→ Decide what should happen

Executor
→ Execute planned actions

GitHub adapters
→ Communicate with GitHub

CLI
→ User interaction and orchestration
```

Do not move GitHub API calls into planners.

Do not place synchronization decisions inside executors.

Do not expose raw API responses unnecessarily outside GitHub adapters.

---

## Requirements

The development environment requires:

- Python 3.12
- Git
- `uv`
- a GitHub account
- a GitHub personal access token for integration testing

Verify Python:

```bash
python --version
```

Expected major and minor version:

```text
Python 3.12
```

Verify `uv`:

```bash
uv --version
```

Verify Git:

```bash
git --version
```

---

## Clone the Repository

Clone the project:

```bash
git clone <repository-url>
cd github-bootstrap
```

Verify the repository:

```bash
git status
```

---

## Install Dependencies

GitHub Bootstrap uses `uv` for Python dependency and environment management.

Install the project and development dependencies:

```bash
uv sync --dev
```

The project uses a `src` layout, with the main package located under:

```text
src/github_bootstrap/
```

Run the CLI through the managed environment:

```bash
uv run github-bootstrap --help
```

---

## GitHub Authentication

Integration with GitHub requires a personal access token.

Configure it as an environment variable:

```bash
export GITHUB_TOKEN="your-token"
```

Never commit the token.

Verify that the variable exists:

```bash
echo "$GITHUB_TOKEN"
```

Verify GitHub connectivity:

```bash
uv run github-bootstrap github-check
```

The token must provide the permissions required by the GitHub resources being managed.

Depending on the operation, GitHub Bootstrap may require access to:

- repositories
- Issues
- labels
- milestones
- Projects V2

Use test repositories for development whenever a new capability performs real GitHub mutations.

---

## Project Structure

A simplified repository structure is:

```text
github-bootstrap/
├── src/
│   └── github_bootstrap/
│       ├── cli.py
│       ├── specification/
│       ├── state/
│       ├── planner/
│       ├── executor/
│       └── github/
│
├── tests/
├── docs/
├── pyproject.toml
├── Makefile
└── README.md
```

The main responsibilities are:

```text
specification/
→ YAML representation and desired-state models

state/
→ snapshots of current GitHub resources

planner/
→ synchronization decisions

executor/
→ execution of planned actions

github/
→ REST and GraphQL integration

cli.py
→ command-line entry point and current orchestration
```

For a detailed explanation, see:

```text
docs/ARCHITECTURE.md
docs/TECHNICAL-GUIDE.md
```

---

## Development Commands

The most important development commands are described below.

### Run the CLI

```bash
uv run github-bootstrap --help
```

---

### Check GitHub Connectivity

```bash
uv run github-bootstrap github-check
```

---

### Run a Synchronization Dry Run

```bash
uv run github-bootstrap sync --dry-run
```

This command should normally be used before executing real synchronization.

---

### Execute Synchronization

```bash
uv run github-bootstrap sync
```

This command performs real mutations against GitHub.

Use it carefully during development.

---

### Run Tests

Run the complete test suite:

```bash
uv run pytest
```

For a focused test file:

```bash
uv run pytest path/to/test_file.py
```

For a specific test:

```bash
uv run pytest path/to/test_file.py::test_name
```

Focused tests are useful during implementation.

Before committing, run the complete verification pipeline.

---

## Verification Pipeline

The main development verification command is:

```bash
make verify
```

This should be executed before every commit that changes application code.

The verification pipeline currently includes checks such as:

```text
Ruff
MyPy
Pytest
```

Depending on project configuration, pre-commit hooks may perform additional checks.

The expected workflow is:

```text
Implementation
      ↓
Focused tests
      ↓
make verify
      ↓
Commit
```

A change should not normally be committed while `make verify` is failing.

---

## Ruff

Ruff is used for Python linting and formatting checks.

The exact commands are normally executed through the Makefile.

When troubleshooting locally, use the project's configured commands rather than introducing different formatting rules.

Typical operations may include:

```bash
uv run ruff check .
```

and:

```bash
uv run ruff format --check .
```

Follow the configuration defined in:

```text
pyproject.toml
```

---

## MyPy

MyPy is used for static type checking.

The project favors explicit typing for synchronization models, planners, state objects, and API boundaries.

Run through:

```bash
make verify
```

or the configured project-specific type-check command.

When fixing a typing error, prefer correcting the model or contract rather than suppressing the error without justification.

---

## Pytest

Pytest is used for automated tests.

Tests should focus primarily on behavior.

For planners, the most important structure is:

```text
Given
Desired specification
+
Current GitHub state

When
Planner executes

Then
Expected synchronization actions are produced
```

For example:

```text
Given
An Issue already exists

When
The Issue synchronization plan is created

Then
No Create Issue action is produced
```

Tests should protect behavior that could otherwise cause incorrect GitHub mutations.

---

## Testing Strategy

Not every component requires the same type of testing.

The recommended testing strategy is layered.

### Specification Tests

Verify:

- YAML parsing
- default values
- required properties
- field type conversion
- dates
- iteration configuration

Example:

```text
YAML
→ ProjectSpecification
```

---

### State Tests

Verify that GitHub responses are correctly represented as internal state.

Examples include:

```text
Issue response
→ IssueSnapshot

Project field response
→ FieldSnapshot

Iteration response
→ IterationSnapshot
```

State tests are particularly important when API payloads contain IDs used by later synchronization operations.

---

### Planner Tests

Planner tests should receive high priority.

The planner determines what operations will be performed against GitHub.

Typical cases are:

```text
Resource missing
→ Create action

Resource exists
→ No create action

Resource differs
→ Drift action or update action
```

Planner behavior should remain deterministic.

The same specification and current state should always produce the same plan.

---

### Executor Tests

Executor tests should verify that planned actions are translated into the correct API calls.

The executor should not duplicate planner logic.

A test should generally verify:

```text
Given
A valid PlanAction

When
The executor handles the action

Then
The correct GitHub adapter operation is called
```

---

### GitHub Adapter Tests

GitHub adapter tests should focus on:

- request construction
- response parsing
- GraphQL variables
- REST payloads
- internal model conversion

Avoid leaking raw GitHub API structures into unrelated tests.

---

### CLI and Orchestration Tests

Tests around synchronization orchestration should verify dependency ordering.

The current real synchronization flow is:

```text
Phase 1
Project

      ↓
Rediscover State

Phase 2
Labels
Milestones
Fields

      ↓
Rediscover State

Phase 3
Issues
Project Items
Field Values
```

Changes to orchestration should preserve this dependency model unless intentionally redesigned.

---

## Dry-Run Validation

A dry run is an important part of development.

Run:

```bash
uv run github-bootstrap sync --dry-run
```

Review the output carefully.

Typical executable actions look like:

```text
+ Create project 'Example Development'
+ Create milestone 'Sprint 1'
+ Create issue 'Implement feature'
```

Drift may appear as:

```text
! Label 'domain' exists with drift: color differs
```

When developing a new planner capability, verify that the dry-run output accurately represents the intended behavior before executing real synchronization.

---

## End-to-End Validation

Unit tests are necessary but not sufficient for important GitHub integration features.

GitHub Bootstrap depends on external API behavior, especially GitHub Projects V2 and GraphQL.

Significant new capabilities should therefore be validated against a controlled test repository.

A recommended E2E process is:

```text
Create or reset test environment
        ↓
Create controlled YAML specification
        ↓
Run sync --dry-run
        ↓
Review plan
        ↓
Run sync
        ↓
Inspect GitHub
        ↓
Run sync again
        ↓
Check for duplicates or unexpected behavior
```

Verify at least:

- expected resources were created
- generated data is correct
- dependencies were resolved
- Issues were correctly added to the Project
- field values were assigned
- no unexpected duplicate resources were created
- a second synchronization behaves safely

---

## Clean Repository E2E Testing

When validating a capability that affects initial bootstrap, test against a clean environment whenever practical.

This is important because an existing repository may hide dependency problems.

For example, testing only against a Project where fields already exist may fail to reveal that new fields are unavailable during the same synchronization.

A clean bootstrap test should verify:

```text
No Project
No custom fields
No configured milestones
No managed Issues
        ↓
Single sync
        ↓
Complete supported environment
```

This validation led to the current multi-phase synchronization model.

---

## Idempotency Testing

Every managed resource should be tested for duplicate creation.

The basic test is:

```text
First sync
→ Resource created

Second sync
→ Resource recognized
→ No duplicate created
```

Important identity rules currently include:

```text
Project
→ title

Label
→ name

Milestone
→ title

Field
→ name

Issue
→ title

Iteration
→ title
```

When changing state discovery, verify that these identity rules continue to work.

---

## Closed Issue Testing

Issue discovery must consider both open and closed Issues.

A closed Issue declared in the specification must not automatically be interpreted as missing.

The important behavior is:

```text
Issue exists and is OPEN
→ Reuse

Issue exists and is CLOSED
→ Reuse

Issue does not exist
→ Create
```

This behavior prevents duplicate Issues after completed work is closed in GitHub.

---

## Drift Testing

Drift detection compares desired state against existing state.

For every resource with drift support, consider tests for:

```text
Exact match
→ No drift

Relevant property differs
→ Drift detected
```

Examples include:

```text
Label color differs

Label description differs

Single-select options differ
```

Do not assume that drift detection implies automatic reconciliation.

Test those behaviors separately.

---

## Working With the Specification

Development and E2E testing typically use:

```text
.github-project.yaml
```

A specification may contain real environment configuration and should be reviewed before committing it.

For local-only test specifications, use appropriate Git exclusion mechanisms when the file should not become part of the repository.

Never include:

- GitHub tokens
- credentials
- private secrets

inside the YAML specification.

Before synchronization, review changes with:

```bash
git diff
```

and:

```bash
uv run github-bootstrap sync --dry-run
```

---

## Adding a New Capability

The preferred workflow for a new managed resource is:

```text
1. Define desired state
2. Parse the specification
3. Define current state
4. Discover GitHub resources
5. Implement planner
6. Implement execution
7. Register execution handler
8. Add tests
9. Run make verify
10. Validate with GitHub E2E
11. Update documentation
12. Commit
```

Do not begin by creating empty packages or generic base classes unless they are required by the first working slice.

For the detailed extension process, see:

```text
docs/TECHNICAL-GUIDE.md
```

---

## Recommended Slice Workflow

For each new capability, use the following sequence.

### Step 1 — Define the Behavior

Write down exactly what the slice should achieve.

Example:

```text
GitHub Bootstrap should create missing repository labels.
```

Avoid starting with broad objectives such as:

```text
Fully synchronize every possible label behavior.
```

---

### Step 2 — Implement the Minimum Complete Path

Build only what is required for the capability to work end-to-end.

Example:

```text
Label Specification
        ↓
Label Discovery
        ↓
Label Planner
        ↓
Label Executor
        ↓
Labels API
```

---

### Step 3 — Run Focused Tests

During implementation:

```bash
uv run pytest path/to/relevant/tests
```

Keep the feedback loop fast.

---

### Step 4 — Run Full Verification

Before considering the implementation complete:

```bash
make verify
```

All checks should pass.

---

### Step 5 — Validate the Plan

For synchronization features:

```bash
uv run github-bootstrap sync --dry-run
```

Ensure the output represents the intended behavior.

---

### Step 6 — Validate Against GitHub

When the change affects real API behavior:

```bash
uv run github-bootstrap sync
```

Use a controlled test environment.

Inspect the result directly in GitHub.

---

### Step 7 — Run Again

Execute another dry run or synchronization as appropriate.

Verify that the resource is recognized and no unexpected duplicate is created.

---

### Step 8 — Commit the Slice

Commit only the files that belong to the completed change.

Inspect:

```bash
git status
```

Then:

```bash
git diff
```

Stage intentionally:

```bash
git add <files>
```

Verify staged changes:

```bash
git diff --staged
```

Then commit.

---

## Git Workflow

Keep the working tree understandable.

Before starting a new slice:

```bash
git status
```

Before committing:

```bash
git status
git diff
```

After staging:

```bash
git diff --staged
```

This reduces accidental commits of:

- test specifications
- temporary files
- credentials
- debugging changes
- unrelated modifications

---

## Commit Strategy

Commits should represent coherent changes.

A commit should answer:

```text
What capability or correction was introduced?
```

Examples from the project style include:

```text
[PROJECT] Create initial project iterations

[ISSUES] Discover closed repository issues

[SYNC] Bootstrap project in multiple phases

[DOCS] Add user guide
```

Useful commit categories include:

```text
[PROJECT]
[ISSUES]
[SYNC]
[FIELDS]
[LABELS]
[MILESTONES]
[CLI]
[DOCS]
[TEST]
[FIX]
```

The category should reflect the primary purpose of the change.

Avoid overly generic messages such as:

```text
Update code

Fix things

Changes

WIP
```

Prefer:

```text
[ISSUES] Discover closed repository issues
```

over:

```text
[FIX] Fix bug
```

when the specific subsystem and behavior are known.

---

## Commit Scope

Do not automatically stage the entire repository.

Prefer:

```bash
git add src/github_bootstrap/github/issues.py
```

over:

```bash
git add .
```

when only one file belongs to the change.

For a coherent multi-file slice, stage those files explicitly.

Example:

```bash
git add \
  src/github_bootstrap/specification/models.py \
  src/github_bootstrap/specification/parser.py \
  src/github_bootstrap/planner/fields.py \
  src/github_bootstrap/executor/fields.py \
  src/github_bootstrap/github/fields.py \
  tests/
```

Always inspect staged files before committing:

```bash
git diff --staged --name-only
```

---

## Pre-Commit Hooks

The repository may execute automated checks during `git commit`.

Typical hooks can include:

```text
Ruff
MyPy
Pytest
YAML validation
TOML validation
End-of-file checks
Trailing whitespace checks
Merge conflict checks
Large file checks
```

A hook may modify a file automatically.

When this happens:

```text
Commit attempt
        ↓
Hook modifies file
        ↓
Commit stops
        ↓
Review modified file
        ↓
Stage it again
        ↓
Commit again
```

Do not assume a failed commit means the implementation is incorrect.

Inspect the hook output carefully.

---

## Debugging Workflow

When a synchronization fails, avoid changing multiple layers immediately.

Identify the stage first.

A useful diagnostic sequence is:

```text
Did the YAML parse correctly?
        ↓
Was current state discovered correctly?
        ↓
Did the planner produce the correct action?
        ↓
Did the executor receive the action?
        ↓
Was the correct API request sent?
        ↓
What did GitHub return?
```

This follows the actual synchronization pipeline.

---

## Debugging Planner Problems

When the wrong action appears in dry-run output, investigate:

```text
Specification
+
State
+
Planner
```

Typical causes include:

- incorrect resource identity
- incomplete discovered state
- wrong state mapping key
- normalization differences
- stale state
- missing planner condition

Do not debug the executor first when the plan itself is already wrong.

---

## Debugging Executor Problems

When the plan is correct but execution fails, investigate:

```text
PlanAction
+
ExecutionContext
+
Executor
+
GitHub API adapter
```

Verify required identifiers such as:

```text
owner_id
repository_id
project_id
issue_id
project_item_id
field_id
option_id
iteration_id
```

---

## Debugging GitHub API Errors

GitHub API failures should be analyzed from the actual response.

Typical categories include:

```text
401
→ authentication problem

403
→ permission or authorization problem

404
→ resource or identifier problem

422
→ invalid request data

GraphQL errors
→ query, mutation, identifier, permission, or schema problem
```

When an API format is uncertain, verify GitHub's current official documentation before modifying the integration.

Do not silently ignore API errors.

---

## Temporary Debugging Code

Temporary diagnostic output may be useful during development.

For example:

```python
print(payload)
```

However, remove temporary debugging output before committing unless it provides intentional user-facing behavior.

Before commit, search the diff:

```bash
git diff
```

for accidental diagnostic changes.

---

## Documentation Updates

Documentation is part of the product.

Update documentation when a change affects:

- YAML syntax
- supported resources
- synchronization behavior
- user workflow
- known limitations
- architecture
- extension patterns

Relevant documents include:

```text
README.md
docs/USER-GUIDE.md
docs/SPECIFICATION-REFERENCE.md
docs/ARCHITECTURE.md
docs/TECHNICAL-GUIDE.md
docs/DEVELOPMENT-GUIDE.md
docs/ROADMAP.md
```

A code change does not require modifying every document.

Update only the documents whose contract or explanation changed.

---

## Definition of Done

A normal feature slice can be considered complete when:

```text
[ ] The intended behavior is implemented
[ ] Relevant tests pass
[ ] make verify passes
[ ] Dry-run output is correct when applicable
[ ] Real GitHub behavior is validated when required
[ ] Repeated synchronization does not create unexpected duplicates
[ ] Temporary debugging code is removed
[ ] Relevant documentation is updated
[ ] Changes are committed coherently
```

For high-risk GitHub integration changes, also verify:

```text
[ ] Clean repository bootstrap behavior
[ ] Existing repository behavior
[ ] Relevant drift behavior
```

---

## Known Development Constraints

The current MVP has several incomplete capabilities that developers should understand before interpreting synchronization results.

### Native Status Reconciliation

GitHub Bootstrap detects option drift for the native Status field but does not currently reconcile those options automatically.

A developer should not interpret:

```text
Status options differ
```

as a failure of the synchronization engine.

This is a known product limitation.

---

### Project Views

Project Views are currently configured manually.

Do not expect `.github-project.yaml` to create:

```text
Current Sprint
Backlog
Roadmap
```

until View management is implemented.

---

### Project Item Field Drift

Existing Project item field values are not yet fully reconciled.

A repeated dry run may continue to show:

```text
Synchronize issue '...' with project
```

even when some values already match.

This behavior should be considered when testing idempotency.

Resource duplication and perfect no-op planning are separate concerns.

---

### Resource Deletion

Removing a resource from the specification does not currently imply deletion from GitHub.

Do not test the specification as a complete destructive desired-state engine.

The current product primarily supports:

```text
Creation
Association
Assignment
Selected drift detection
```

---

## Preparing for the Web Interface

A future Web UI should reuse synchronization logic rather than execute the CLI as a subprocess.

Before implementing the UI, the expected refactor is:

```text
Current

CLI
└── Synchronization orchestration
```

toward:

```text
CLI ─────┐
         │
         ▼
SynchronizationService
         ▲
         │
Web UI ──┘
```

When performing this refactor:

- preserve existing CLI behavior
- move reusable orchestration into the application layer
- keep presentation concerns in the CLI
- avoid moving GitHub API logic into the service
- keep planner and executor boundaries intact

The refactor should be performed as a separate vertical slice.

---

## Recommended Development Sequence for Future Capabilities

The current likely evolution of GitHub Bootstrap is:

```text
1. Complete baseline documentation

2. Extract reusable synchronization application service

3. Build basic Web UI

4. Deploy the Web UI

5. Improve native Status reconciliation

6. Add Project Views synchronization

7. Improve Project item field-value drift detection

8. Add additional reconciliation capabilities as real needs appear
```

This sequence is directional rather than mandatory.

Product needs should determine which capability is implemented next.

---

## Quick Development Checklist

Before coding:

```text
[ ] git status is understood
[ ] The slice has a clear scope
[ ] Existing architecture is understood
```

During coding:

```text
[ ] Keep the change focused
[ ] Run focused tests
[ ] Avoid speculative abstractions
```

Before real synchronization:

```text
[ ] Review the target specification
[ ] Run sync --dry-run
[ ] Confirm the target repository and Project
```

Before committing:

```text
[ ] make verify passes
[ ] git diff has been reviewed
[ ] Temporary debugging code is removed
[ ] No credentials are staged
[ ] Documentation is updated when necessary
[ ] Staged files belong to one coherent change
```

After significant integration work:

```text
[ ] Validate against GitHub
[ ] Run synchronization again
[ ] Check for duplicates
[ ] Record newly discovered limitations
```

---

## Further Documentation

For general usage:

```text
docs/USER-GUIDE.md
```

For the YAML specification:

```text
docs/SPECIFICATION-REFERENCE.md
```

For architectural concepts:

```text
docs/ARCHITECTURE.md
```

For technical implementation and extension guidance:

```text
docs/TECHNICAL-GUIDE.md
```

For current capabilities, limitations, and future development:

```text
docs/ROADMAP.md
```

The central development principle of GitHub Bootstrap is:

```text
Build the smallest useful capability end-to-end,
verify it thoroughly,
and evolve the architecture from demonstrated needs.
```
