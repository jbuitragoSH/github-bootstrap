# Roadmap

## Overview

This document summarizes the current state, known limitations, and likely evolution of GitHub Bootstrap.

The roadmap is intentionally lightweight.

It is not a fixed commitment or a complete product backlog. Its purpose is to provide enough context to understand:

- what GitHub Bootstrap can currently do
- which limitations are already known
- which capabilities are natural candidates for future development
- which architectural direction should be preserved as the product evolves

Detailed implementation work should be tracked through GitHub Issues and the project board.

---

## Product Vision

GitHub Bootstrap is intended to provide a declarative and repeatable way to create and maintain the GitHub project infrastructure required to develop software products.

The desired direction is:

```text
Project Specification
        ↓
GitHub Bootstrap
        ↓
Complete Development Environment
```

A project should increasingly be able to describe its development environment through configuration rather than repeated manual setup.

The long-term objective is not to replace GitHub.

GitHub remains the operational environment used by the development team.

GitHub Bootstrap provides the infrastructure automation required to initialize and maintain that environment.

---

## Current Product Status

GitHub Bootstrap currently provides a functional MVP capable of bootstrapping a real GitHub development environment.

The current synchronization model supports:

```text
Desired State
        +
Current GitHub State
        ↓
Synchronization Plan
        ↓
Execution
        ↓
GitHub
```

The product has been validated against real GitHub repositories and Projects V2.

A clean supported environment can be created through phased synchronization.

---

## Completed Capabilities

### GitHub Project V2

GitHub Bootstrap can:

- discover an existing Project
- create a missing Project
- use the Project as the target for fields and Issues

---

### Repository Labels

GitHub Bootstrap can:

- discover labels
- create missing labels
- detect selected label drift

Current drift detection includes differences such as:

- color
- description

---

### Repository Milestones

GitHub Bootstrap can:

- discover milestones
- create missing milestones
- configure descriptions
- configure due dates
- associate Issues with milestones

---

### Project Fields

The following Project V2 field types are supported:

```text
TEXT
NUMBER
DATE
SINGLE_SELECT
ITERATION
```

GitHub Bootstrap can:

- discover fields
- create missing fields
- discover single-select options
- discover iterations
- detect selected field drift

---

### Iterations

GitHub Bootstrap can create iteration fields with initial iteration configuration.

Supported configuration includes:

```text
duration
start date
initial iteration titles
```

Example:

```text
Sprint 1
Sprint 2
Sprint 3
```

Initial iteration dates are calculated from the configured start date and duration.

---

### Repository Issues

GitHub Bootstrap can:

- discover existing Issues
- discover both open and closed Issues
- create missing Issues
- assign labels
- assign milestones

Existing Issues are currently identified primarily by title.

The discovery of closed Issues prevents completed work from being recreated as duplicate Issues during later synchronization.

---

### Project Items

GitHub Bootstrap can:

- add repository Issues to Project V2
- discover existing Project items
- reuse existing Issues during Project synchronization

This establishes the connection:

```text
Repository Issue
        ↓
Project Item
```

---

### Project Item Field Values

GitHub Bootstrap can assign values for:

```text
TEXT
NUMBER
DATE
SINGLE_SELECT
ITERATION
```

This allows specifications to define operational project information such as:

```text
Status
Priority
Component
Story Points
Due Date
Sprint
```

---

### Drift Detection

GitHub Bootstrap separates executable synchronization actions from detected drift.

Conceptually:

```text
Plan
├── Executable Actions
└── Drift Actions
```

This allows unsupported reconciliation cases to remain visible without blocking supported synchronization operations.

---

### Multi-Phase Bootstrap

Real synchronization is executed in dependency-aware phases.

```text
Phase 1
Project
   ↓
Rediscover

Phase 2
Labels
Milestones
Fields
Iterations
   ↓
Rediscover

Phase 3
Issues
Project Items
Field Values
```

This allows a clean supported environment to be bootstrapped using a single synchronization command.

---

### Dry Run

GitHub Bootstrap supports synchronization planning without mutation.

```bash
uv run github-bootstrap sync --dry-run
```

The dry run exposes:

- executable actions
- detected drift

before modifying GitHub.

---

## Current Operational Workflow

A normal project bootstrap currently follows this process:

```text
Create .github-project.yaml
        ↓
Run sync --dry-run
        ↓
Review plan and drift
        ↓
Run sync
        ↓
Configure unsupported GitHub settings manually
        ↓
Run sync again when required
        ↓
Use the Project operationally
```

The current MVP has already been used to create the development environment for projects such as Knowledge Platform.

---

## Known Limitations

The following limitations are known and accepted in the current MVP.

They should not automatically trigger architectural redesign.

Each limitation can be addressed through an independent vertical slice when the product need justifies it.

---

### Native Status Option Reconciliation

GitHub automatically creates a native `Status` field for Projects V2.

The default options are typically similar to:

```text
Todo
In Progress
Done
```

A GitHub Bootstrap specification may declare a different workflow:

```text
Backlog
Ready
In Progress
In Review
Done
```

GitHub Bootstrap currently detects this difference as drift but does not automatically update the native field options.

The initial Status configuration must therefore be performed manually.

After configuration, synchronization can assign Status values to Project items.

---

### Project Views

Project Views are not currently part of the GitHub Bootstrap specification.

Views such as:

```text
Current Sprint
Backlog
Roadmap
```

must currently be configured manually.

The implementation of Views should only begin after the desired configuration model and GitHub API capabilities have been verified.

---

### Project Item Field-Value Drift

GitHub Bootstrap can assign Project item field values.

However, it does not yet fully discover and compare all existing values against the desired specification.

As a result, repeated synchronization may continue to produce actions such as:

```text
Synchronize issue '...' with project
```

even when some values already match.

This does not necessarily mean duplicate resources will be created.

---

### Limited Drift Reconciliation

Some differences can currently be detected but not automatically corrected.

Examples include:

- label color differences
- label description differences
- single-select option differences

The architecture intentionally separates:

```text
Drift Detection
```

from:

```text
Drift Reconciliation
```

Reconciliation can therefore be introduced incrementally.

---

### Resource Deletion

The specification is not currently a destructive desired-state contract.

Removing a resource from `.github-project.yaml` does not automatically delete the corresponding GitHub resource.

Current synchronization primarily focuses on:

```text
Creation
Association
Assignment
Selected Drift Detection
```

Deletion semantics require explicit product design before implementation.

---

### Project-to-Repository Linking

GitHub Bootstrap can add repository Issues to a Project V2.

However, it does not currently guarantee automatic linking of the Project itself to the repository's Projects section.

This does not prevent the Project from containing and managing repository Issues.

---

### Project Views and Workflow Configuration Remain Partially Manual

A fully automated new-project setup currently requires some manual GitHub configuration.

The main manual operations are:

```text
Configure native Status options
Create operational Project Views
```

These are clear candidates for future automation.

---

## Current Productization Milestone

The current productization effort is divided into three slices.

### Slice 1 — Document Current Product

Status:

```text
In Progress
```

Documentation baseline:

```text
README.md
docs/USER-GUIDE.md
docs/SPECIFICATION-REFERENCE.md
docs/ARCHITECTURE.md
docs/TECHNICAL-GUIDE.md
docs/DEVELOPMENT-GUIDE.md
docs/ROADMAP.md
```

The objective is to make the current product understandable, usable, maintainable, and extensible without depending on historical development context.

---

### Slice 2 — Extract Synchronization Application Service

Status:

```text
Planned
```

The current CLI owns part of the synchronization orchestration.

The intended evolution is:

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

The application service should become the reusable entry point for:

- loading and validating a specification
- building synchronization plans
- executing synchronization
- returning structured results

The existing CLI behavior should remain unchanged from the user's perspective.

---

### Slice 3 — Basic Web Interface

Status:

```text
Planned
```

The first Web UI should remain intentionally small.

Initial capabilities should include:

```text
Load or edit YAML specification

Validate specification

Run dry-run

Display synchronization plan

Display drift

Execute synchronization

Display execution result
```

The Web UI should reuse the synchronization application service.

It should not execute the CLI as a subprocess.

Initial architecture:

```text
CLI ────────┐
            │
            ▼
SynchronizationService
            ▲
            │
Web UI ─────┘
```

A lightweight server-side implementation is preferred for the MVP.

A possible initial stack is:

```text
FastAPI
Jinja2
HTML
Minimal CSS
```

A separate frontend framework should only be introduced when the interface requirements justify it.

---

## Near-Term Candidates

After the current productization milestone, the following capabilities are strong candidates for future vertical slices.

The order should be determined by actual product need.

---

### Native Status Reconciliation

Objective:

```text
Desired Status options
        +
Existing native Status field
        ↓
Update GitHub options
```

This would remove one of the most visible manual bootstrap steps.

The implementation should extend the existing field synchronization lifecycle rather than introduce special CLI logic.

---

### Project Views as Configuration

Possible capabilities include:

```text
View creation
Layout configuration
Filtering
Grouping
Ordering
```

A possible future specification could resemble:

```yaml
views:
  - name: Current Sprint
    layout: board
    group_by: Status
    filter: sprint:"Sprint 1"
```

This syntax is illustrative only.

The final specification should be defined when implementation begins and after GitHub API capabilities have been validated.

---

### Project Item Field Drift Detection

Objective:

```text
Desired Issue Field Values
        +
Current Project Item Values
        ↓
Compare
        ↓
Plan only required changes
```

This would improve dry-run accuracy and move Project item synchronization closer to true convergence.

---

### Field-Value Reconciliation

After current values can be reliably discovered, GitHub Bootstrap can perform targeted updates only where required.

Desired behavior:

```text
Current value matches
→ No action

Current value differs
→ Update action
```

---

### Label Reconciliation

Existing label drift could evolve from:

```text
Detect
```

to:

```text
Detect
+
Update
```

Candidate properties include:

```text
color
description
```

---

### Milestone Reconciliation

Possible future support includes updates to:

```text
description
due date
state
```

---

### Project Repository Linking

A future slice may explicitly connect managed Projects to their target repositories where supported by GitHub.

This should be implemented only after the exact GitHub model and API behavior are verified.

---

## Longer-Term Candidates

These capabilities are possible future directions but are not current priorities.

---

### Resource Deletion

A future reconciliation model may support explicit deletion.

This requires careful design.

Potential approaches include:

```text
Explicit delete flag

Managed-resource ownership

Strict reconciliation mode
```

GitHub Bootstrap should not infer destructive operations simply because an item disappears from the specification without an intentional contract.

---

### Multiple Projects

The current specification model is primarily centered around one target Project.

Future requirements may justify managing multiple Projects from one specification.

This should not be implemented until a real use case requires it.

---

### Richer Issue Synchronization

Possible future capabilities include:

- issue body updates
- label reconciliation
- milestone reconciliation
- issue state management
- explicit reopen behavior
- assignees
- relationships between Issues

These should be introduced individually.

---

### Additional GitHub Resources

Future managed resources could include:

```text
Repository settings
Teams
Permissions
Issue templates
Pull request templates
Workflows
Rulesets
Releases
```

GitHub Bootstrap should not attempt to manage all GitHub capabilities by default.

A new resource should be introduced only when it belongs to the project's infrastructure-management responsibility.

---

### Hosted Multi-Project Service

The basic Web UI may eventually evolve into a hosted service capable of managing multiple specifications and repositories.

Possible capabilities could include:

```text
Authentication

Multiple GitHub connections

Stored project specifications

Synchronization history

Scheduled synchronization

Audit logs
```

This is not part of the current MVP.

The initial Web UI should remain deliberately simple.

---

## Architectural Evolution

Future capabilities should preserve the fundamental model:

```text
Desired State
        +
Current State
        ↓
Planner
        ↓
Plan
        ↓
Executor
        ↓
GitHub
```

A new resource should normally follow:

```text
Specification
→ Parser
→ State Discovery
→ Planner
→ Executor
→ GitHub Adapter
→ Tests
→ E2E Validation
```

The architecture should evolve from demonstrated needs.

Do not introduce large generic frameworks for hypothetical future capabilities.

---

## Product Priorities

When deciding what to build next, prioritize capabilities that:

1. remove repeated manual project setup
2. improve synchronization correctness
3. improve visibility of planned changes
4. make the tool easier to operate
5. support real development workflows
6. reduce maintenance complexity

Avoid prioritizing features solely because the GitHub API makes them technically possible.

---

## Prioritization Model

A useful decision model is:

```text
Does this solve a real current problem?
        ↓
Does it belong to GitHub Bootstrap?
        ↓
Can it be implemented as a small vertical slice?
        ↓
Can its behavior be validated?
        ↓
Implement
```

A capability should generally be postponed when:

```text
The use case is hypothetical

The architecture is being generalized in advance

The feature does not improve the current workflow

The external API behavior is not yet understood
```

---

## Roadmap Management

This document should remain high-level.

Implementation-level work should be managed through GitHub Issues and the GitHub Project.

A useful relationship is:

```text
ROADMAP.md
→ Product direction

GitHub Milestones
→ Delivery horizon

GitHub Issues
→ Implementable work

Project Views
→ Operational execution
```

The roadmap should be updated when:

- a major capability becomes operational
- a known limitation is resolved
- a significant new direction is accepted
- the product architecture changes materially

It should not be updated for every small implementation detail.

---

## Current Recommended Sequence

The recommended near-term development sequence is:

```text
1. Complete product documentation

2. Extract synchronization application service

3. Build basic Web UI

4. Deploy the Web UI

5. Use the deployed product with real projects

6. Improve reconciliation based on actual operational needs
```

Likely reconciliation candidates after deployment are:

```text
Native Status options

Project Views

Project item field values
```

The exact order should be informed by real usage.

---

## Definition of MVP Completion

The current GitHub Bootstrap MVP can be considered productized when:

```text
[ ] The current product is documented

[ ] A user can understand how to configure and run it

[ ] A developer can understand how to extend it

[ ] Synchronization orchestration is reusable outside the CLI

[ ] A basic Web UI can validate, plan, and execute synchronization

[ ] The Web UI is deployed in a controlled environment

[ ] Known limitations are clearly documented
```

This does not mean every GitHub resource must be automatically reconciled.

The MVP is complete when the supported capabilities form a coherent, usable, maintainable product.

---

## Current Direction

The immediate development direction is:

```text
Documentation
        ↓
Reusable Application Service
        ↓
Basic Web UI
        ↓
Deployment
        ↓
Real Operational Usage
        ↓
Evidence-Based Evolution
```

This sequence preserves the central development philosophy of GitHub Bootstrap:

```text
Build the smallest useful capability,
validate it against real usage,
and expand only when the next need becomes clear.
```

---

## Further Documentation

For general product usage:

```text
docs/USER-GUIDE.md
```

For the YAML specification:

```text
docs/SPECIFICATION-REFERENCE.md
```

For the architectural model:

```text
docs/ARCHITECTURE.md
```

For internal implementation and extension guidance:

```text
docs/TECHNICAL-GUIDE.md
```

For development practices:

```text
docs/DEVELOPMENT-GUIDE.md
```
