# Technical Guide

## Overview

This document describes the internal structure of GitHub Bootstrap and provides practical guidance for maintaining and extending the application.

It is intended for developers who need to:

* Understand the current codebase
* Modify existing synchronization capabilities
* Add support for new GitHub resources
* Extend drift detection or reconciliation
* Introduce new interfaces such as a Web UI

For the high-level architectural model, see:

```text
docs/ARCHITECTURE.md
```

For the YAML contract, see:

```text
docs/SPECIFICATION-REFERENCE.md
```

---

## Technical Model

GitHub Bootstrap implements a declarative synchronization pipeline.

```text
YAML Specification
        ↓
Specification Models
        ↓
GitHub State Discovery
        ↓
Planner
        ↓
Plan Actions
        ↓
Executor
        ↓
GitHub REST / GraphQL
```

The system maintains a strict distinction between:

```text
Desired State
```

and:

```text
Current State
```

The planner compares both representations and determines the required synchronization actions.

---

# Project Structure

The source code follows a `src` layout.

A simplified structure is:

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
├── tests/
├── docs/
├── pyproject.toml
├── Makefile
└── README.md
```

The exact file structure may evolve as new capabilities are introduced.

The important technical boundaries are:

| Package         | Responsibility                        |
| --------------- | ------------------------------------- |
| `specification` | Desired state and YAML interpretation |
| `state`         | Discovered GitHub state               |
| `planner`       | Synchronization decisions             |
| `executor`      | Execution of planned actions          |
| `github`        | GitHub REST and GraphQL integration   |
| `cli`           | Current application entry point       |

---

# CLI

The CLI is currently the main application interface.

The primary synchronization command is:

```bash
uv run github-bootstrap sync
```

A dry run is executed with:

```bash
uv run github-bootstrap sync --dry-run
```

The CLI currently coordinates:

* Specification loading
* Specification validation
* GitHub client initialization
* GitHub state discovery
* Synchronization planning
* Phased execution
* Output rendering

The CLI should not become the permanent home for reusable synchronization logic.

The intended evolution is:

```text
CLI
 ↓
SynchronizationService
 ↓
Synchronization Pipeline
```

A future Web UI should use the same application service instead of duplicating or invoking CLI orchestration.

---

# Specification Package

The `specification` package represents the desired state.

Its responsibilities include:

* YAML loading
* Parsing
* Validation
* Specification models

The main aggregate is conceptually:

```text
ProjectSpecification
├── organization
├── repository
├── project
├── labels
├── milestones
├── fields
└── issues
```

Each managed resource should have an explicit model.

Examples include:

* `Project`
* `Label`
* `Milestone`
* `Field`
* `Iteration`
* `Issue`

---

## Specification Models

Specification models should:

* Describe user intent
* Use meaningful internal types
* Remain independent from raw GitHub API payloads
* Contain only the data required to express the desired state

They should not:

* Execute HTTP requests
* Know GraphQL queries
* Perform synchronization
* Depend on executor implementations

Example:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Label:
    name: str
    color: str
    description: str | None = None
```

The implementation should remain simple unless stronger domain behavior is required.

---

## Parser

The parser converts raw YAML data into specification models.

```text
Raw Mapping
    ↓
Parser
    ↓
ProjectSpecification
```

The parser translates external configuration values into internal types.

For example:

```yaml
due_on: 2026-08-15
```

can become a Python `date`.

Similarly:

```yaml
type: iteration
```

must produce the correct field model and configuration.

The parser should fail clearly when the configuration cannot be interpreted.

---

## Validation

Validation protects the synchronization pipeline from invalid specifications.

The application should detect configuration errors before performing GitHub mutations.

Validation can include:

* Required values
* Supported field types
* Compatible field configuration
* Valid resource references
* Valid dates
* Valid field value types

The governing principle is:

```text
Invalid Specification
        ↓
Fail Before GitHub Mutation
```

Validation must remain separate from API execution.

---

# State Package

The `state` package represents what currently exists in GitHub.

The central state model is conceptually:

```text
GitHubState
├── ProjectState
├── LabelState
├── MilestoneState
├── FieldState
├── IssueState
└── ProjectItemState
```

State models are snapshots.

They should contain enough information for planners to make synchronization decisions without exposing unnecessary raw REST or GraphQL payloads.

---

## Snapshots

Some state models contain richer resource snapshots.

Examples include:

* `IssueSnapshot`
* `FieldSnapshot`
* `FieldOptionSnapshot`
* `IterationSnapshot`

A simplified Issue snapshot may look like:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class IssueSnapshot:
    id: str
    number: int
    title: str
```

The GitHub node ID is important because Project V2 operations commonly require GraphQL node identifiers.

---

## Resource Identity

Current resource discovery commonly uses human-readable properties.

| Resource  | Identity property |
| --------- | ----------------- |
| Project   | `title`           |
| Label     | `name`            |
| Milestone | `title`           |
| Field     | `name`            |
| Issue     | `title`           |
| Iteration | `title`           |

Internal state mappings may still be indexed by GitHub IDs.

For example, `IssueState` may store snapshots by node ID. When the planner requires title-based lookup, it should build that index explicitly:

```python
existing_issues = {
    snapshot.title.strip().lower(): snapshot
    for snapshot in issue_state.issues.values()
}
```

Do not assume that a state mapping key is the resource name or title.

Inspect the state model before implementing identity matching.

---

# GitHub Package

The `github` package contains adapters responsible for external API operations.

Examples include:

* `ProjectsAPI`
* `RepositoriesAPI`
* `LabelsAPI`
* `MilestonesAPI`
* `FieldsAPI`
* `IssuesAPI`

These components encapsulate GitHub-specific behavior.

Typical operations include:

* Find a resource
* Create a resource
* Add an Issue to a Project
* Set a Project field value
* Discover field options
* Discover iterations

Other application layers should not construct raw GraphQL queries or REST requests directly.

---

## REST API Usage

The GitHub REST API is primarily used for repository-level resources.

Examples include:

* Labels
* Milestones
* Repository Issues
* Repository operations

A typical adapter flow is:

```text
Internal Call
    ↓
HTTP Request
    ↓
GitHub REST API
    ↓
Response Parsing
    ↓
Internal State
```

REST-specific response details should remain inside the adapter whenever practical.

---

## GraphQL API Usage

GitHub Projects V2 relies heavily on GraphQL.

GraphQL is used for capabilities such as:

* Project discovery
* Project creation
* Project fields
* Project items
* Project field values
* GitHub node IDs

A typical flow is:

```text
Executor
   ↓
FieldsAPI
   ↓
GraphQL Mutation
   ↓
GitHub
```

GraphQL identifiers should be translated into execution context or snapshot models rather than passed through unrelated application layers.

---

# Planner Package

The planner converts desired state and current state into synchronization decisions.

```text
Specification + State
        ↓
Planner
        ↓
Plan
```

Resource planners should be deterministic.

Given the same specification and current state, they should produce the same plan.

They must not execute GitHub API calls.

---

## Resource Planners

Typical planners include:

* `plan_projects`
* `plan_labels`
* `plan_milestones`
* `plan_fields`
* `plan_issues`

Each planner should focus on one resource or one cohesive synchronization concern.

For example:

```text
Desired Labels
      +
Current LabelState
      ↓
Label Planner
      ↓
Create Actions or Drift
```

This keeps synchronization rules close to the resource they manage.

---

## Plan Actions

A plan contains explicit actions.

A plan action conceptually contains:

```text
operation
resource
description
payload
```

Example:

```text
operation:
  create

resource:
  label

description:
  Create label 'domain'

payload:
  label configuration
```

Actions should contain the information required by the executor without forcing it to repeat planning decisions.

---

## Executable Actions and Drift

The plan separates executable work from detected differences.

Conceptually:

```text
Plan
├── executable_actions()
├── drift_actions()
└── has_drift()
```

Executable actions can be applied automatically.

Drift actions communicate differences for which automatic reconciliation may not exist yet.

This distinction must remain explicit.

Unsupported updates must not be silently treated as successful synchronization.

---

# Executor Package

The executor applies plan actions.

```text
Plan
  ↓
Executor
  ↓
Handler Registry
  ↓
Resource Executor
  ↓
GitHub API
```

The executor should not decide whether a resource needs to be created.

That decision belongs to the planner.

The separation is:

```text
Planner:
Should this action happen?

Executor:
How is this action performed?
```

---

## Executor Registry

The executor registry associates resource names with execution handlers.

Conceptually:

```text
project
  → Project executor

label
  → Label executor

milestone
  → Milestone executor

field
  → Field executor

issue
  → Issue executor
```

When adding an executable resource, verify that its handler is registered.

A common implementation error is:

```text
Planner creates action
        ↓
Executor registry has no handler
```

The planner and executor registry must evolve together.

---

## Execution Context

Execution sometimes requires identifiers that do not exist in the YAML specification.

Examples include:

* `owner_id`
* `repository_id`
* `project_id`

These values belong in the execution context.

```python
from dataclasses import dataclass


@dataclass
class ExecutionContext:
    owner_id: str
    repository_id: str
    project_id: str | None = None
```

The context allows executors to share required runtime identifiers without placing execution-specific data in specification models.

It should contain runtime execution information, not general application state.

---

# Multi-Phase Execution

Real synchronization is executed in phases because later resources depend on resources created earlier.

The current model is:

```text
Phase 1
Project

Phase 2
Labels
Milestones
Fields
Iterations

Phase 3
Issues
Project Items
Field Values
```

State is rediscovered between phases.

---

## Project Phase

The Project phase ensures that the Project V2 exists.

```text
Current State
    ↓
create_project_plan()
    ↓
Execute
    ↓
Rediscover State
```

After this phase, the Project ID becomes available for field and Project item operations.

---

## Infrastructure Phase

The infrastructure phase handles:

* Labels
* Milestones
* Fields
* Iterations

```text
Rediscovered State
       ↓
create_infrastructure_plan()
       ↓
Execute
       ↓
Rediscover State
```

Issues can then reference resources created during this phase.

---

## Issue Phase

The final phase handles:

* Issue creation
* Existing Issue reuse
* Project membership
* Project field values

```text
Rediscovered State
       ↓
create_issue_plan()
       ↓
Execute
```

This phase has access to newly available:

* Milestones
* Fields
* Iterations
* Project identifiers

---

## Full Plan and Phase-Specific Plans

A full planner remains useful for dry runs:

```python
create_plan(specification, state)
```

It produces the best plan that can be determined from the current state without executing mutations.

Real synchronization can instead use phase-specific planners such as:

```python
create_project_plan(...)
create_infrastructure_plan(...)
create_issue_plan(...)
```

This distinction exists because a dry run does not mutate GitHub and rediscover state between phases.

---

# State Discovery

State discovery should be centralized enough that every synchronization phase uses a consistent view of GitHub.

Conceptually, a function such as:

```python
_load_github_state(...)
```

may gather:

* Project
* Labels
* Milestones
* Fields
* Issues
* Project items

When introducing a resource, determine whether it belongs in global state discovery or should be discovered locally.

Prefer global discovery when multiple planners need the information.

Prefer local discovery when the data is highly specialized and used by one execution operation.

---

# Issue Synchronization

Issues are more complex than simple repository resources because they participate in both the repository and Project V2.

Their lifecycle is:

```text
Issue Specification
       ↓
Find Repository Issue
       ↓
Create if Missing
       ↓
Add to Project
       ↓
Find Project Item
       ↓
Assign Project Field Values
```

Existing Issues must be discovered across both states:

```text
OPEN
CLOSED
```

Otherwise, a closed Issue can incorrectly appear missing and be recreated as a duplicate.

---

## Existing Issue Lookup

Current Issue identity is based primarily on title.

Because `IssueState` may be indexed by node ID, planners should build a title lookup from snapshots.

```python
existing_issues = {
    snapshot.title.strip().lower(): snapshot
    for snapshot in issue_state.issues.values()
}
```

Normalization prevents simple case and surrounding whitespace differences from breaking lookup.

Any future change to Issue identity should be deliberate and documented.

---

## Project Item Synchronization

A repository Issue and a Project item are related but distinct GitHub resources.

```text
Repository Issue
        ↓
Add to Project
        ↓
Project Item
```

Project field values belong to the Project item, not directly to the repository Issue.

This distinction is essential when implementing field assignment.

---

# Project Fields

Project fields currently support:

* `TEXT`
* `NUMBER`
* `DATE`
* `SINGLE_SELECT`
* `ITERATION`

Each field type requires a different GraphQL value representation.

The executor or GitHub adapter should contain this type-specific translation.

The planner should remain focused on desired values rather than GraphQL mutation syntax.

---

## Single-Select Fields

Single-select values use GitHub option IDs.

The specification contains a human-readable value:

```yaml
Priority: High
```

GitHub requires the ID of the `High` option.

The translation flow is:

```text
Configured Value
"High"
    ↓
FieldSnapshot Options
    ↓
Option ID
    ↓
GraphQL Mutation
```

The same principle applies to iteration values.

---

## Iteration Fields

The specification can define an initial iteration configuration.

```yaml
- name: Sprint
  type: iteration
  configuration:
    duration: 14
    start_date: 2026-08-01
    iterations:
      - title: Sprint 1
      - title: Sprint 2
```

The field adapter converts this configuration into the format required by GitHub.

```text
start_date
    +
duration
    +
ordered titles
    ↓
GitHub Iteration Configuration
```

For example:

```text
Sprint 1 → 2026-08-01
Sprint 2 → 2026-08-15
```

This calculation belongs near the GitHub field creation logic because it translates the internal model into an external API contract.

---

## Native Status Field

GitHub automatically creates a native `Status` field for new Projects V2.

The architecture treats it as a discovered field.

A specification can declare desired options, but current synchronization only detects option drift.

```text
Desired Status Options
        +
Native Status Options
        ↓
Planner
        ↓
Drift Action
```

Automatic option reconciliation is not currently implemented.

A future implementation should extend the existing lifecycle:

```text
Discovery
    ↓
Drift Detection
    ↓
Update Planning
    ↓
Update Execution
    ↓
GitHub Mutation
```

This behavior should not be implemented directly in the CLI.

---

# Error Handling

Errors should be raised as close as possible to the layer that understands them.

| Error                           | Responsible layer        |
| ------------------------------- | ------------------------ |
| Invalid YAML structure          | Specification or parser  |
| Unsupported field configuration | Specification validation |
| GitHub API failure              | GitHub adapter           |
| Unknown execution resource      | Executor registry        |

User-facing interfaces such as the CLI should translate these failures into understandable output.

Do not catch errors too early and discard useful context.

---

# Testing Strategy

Tests should follow the synchronization layers.

Typical test groups include:

* Specification parsing tests
* State model tests
* Planner tests
* GitHub adapter tests
* Executor tests
* CLI or orchestration tests

The most valuable planner tests normally follow this structure:

```text
Given desired state
and current state

When planning

Then expected actions are produced
```

Example:

```text
Given:
Issue exists

When:
Issue plan is created

Then:
No Create Issue action is produced
```

For important synchronization behavior, supplement unit tests with real GitHub end-to-end validation.

---

## Real E2E Validation

GitHub Bootstrap manages an external platform whose API behavior cannot be fully represented by unit tests.

Significant capabilities should therefore be validated against a controlled test repository.

A typical E2E workflow is:

```text
Create Clean Repository
        ↓
Apply Specification
        ↓
sync --dry-run
        ↓
sync
        ↓
Inspect GitHub Resources
        ↓
sync Again
        ↓
Verify Idempotency
```

Validate at least that:

* Resources are created
* Dependencies are resolved
* Field values are assigned
* No unexpected duplicates appear
* The second synchronization behaves safely

External behaviors discovered through E2E testing should be documented when they affect architecture or usage.

---

# Development Workflow

For a normal code change:

```text
Implement a Small Slice
        ↓
Run Focused Tests
        ↓
make verify
        ↓
Run Dry Run When Relevant
        ↓
Run Controlled E2E When Necessary
        ↓
Commit
```

The standard verification command is:

```bash
make verify
```

Do not accumulate multiple unrelated capabilities in one implementation cycle.

---

# Adding a New Managed Resource

New resources should be implemented vertically.

Suppose GitHub Bootstrap needs to support a resource called `ExampleResource`.

Do not begin by creating a generic framework. Implement the smallest complete vertical slice.

---

## Step 1 — Define the Specification

Add the minimum model required to describe the resource.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ExampleResource:
    name: str
```

Add it to the relevant parent specification:

```text
ProjectSpecification
└── example_resources
```

Keep the model focused on desired state.

---

## Step 2 — Extend the Parser

Teach the YAML parser how to create the new model.

Example configuration:

```yaml
example_resources:
  - name: Example
```

Add parsing tests that verify:

```text
YAML
 ↓
Correct Specification Model
```

---

## Step 3 — Define Current State

Create the state representation required by the planner.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ExampleResourceSnapshot:
    id: str
    name: str


@dataclass(frozen=True)
class ExampleResourceState:
    resources: dict[str, ExampleResourceSnapshot]
```

Store only the information required for synchronization decisions.

---

## Step 4 — Implement GitHub Discovery

Add an API adapter or extend an existing one.

Conceptually:

```python
ExampleResourcesAPI.find(...)
```

Convert raw GitHub responses into internal state models.

Do not return arbitrary API dictionaries to the planner.

---

## Step 5 — Add State Discovery

Include the resource in the appropriate state-loading process.

Determine when it must be discovered:

```text
Before Infrastructure Planning
```

or:

```text
Before Issue Synchronization
```

Respect resource dependency ordering.

---

## Step 6 — Implement the Planner

Compare desired and current state.

Typical behavior is:

```text
Missing
  → Create action

Exists and matches
  → No action

Exists and differs
  → Drift or update action
```

Example:

```python
def plan_example_resources(
    specification: ProjectSpecification,
    state: ExampleResourceState,
) -> Plan:
    ...
```

Planner tests should verify every important decision rule.

---

## Step 7 — Implement Execution

Create the resource executor.

```text
PlanAction
    ↓
ExampleResourceExecutor
    ↓
ExampleResourcesAPI.create()
```

The executor should translate an already-decided action into an API operation.

Do not repeat planning logic inside the executor unless required for safe interaction with GitHub.

---

## Step 8 — Register the Executor

Add the resource to the execution registry.

Verify that:

```text
Resource name produced by planner
              =
Resource name registered by executor
```

A mismatch can cause runtime failures even when planning works correctly.

---

## Step 9 — Add Tests

At minimum, consider tests for:

* Specification parsing
* State discovery
* Missing resource planning
* Existing resource idempotency
* Drift detection
* Execution

Do not add tests only to increase the test count.

Focus on behavior that could cause incorrect GitHub mutations if broken.

---

## Step 10 — Validate End-to-End

Test the resource against a controlled GitHub environment.

Verify:

```text
First Sync
  → Resource Created

Second Sync
  → No Duplicate

Changed Specification
  → Expected Drift or Reconciliation
```

Only after this validation should the capability be considered operational.

---

# Adding Drift Reconciliation

A resource may initially support:

```text
Create
  +
Detect Drift
```

It may later evolve to:

```text
Create
  +
Detect Drift
  +
Reconcile Drift
```

The preferred extension flow is:

```text
Existing Drift Detection
        ↓
Define Supported Update Operation
        ↓
Planner Produces Executable Update Action
        ↓
Executor Handles Update
        ↓
API Adapter Performs Mutation
```

Do not place update behavior inside drift reporting.

Drift should remain observable even when automatic reconciliation is unsupported.

---

# Adding Project Views

Project Views are a known future capability.

A clean implementation would likely introduce:

* View specification
* View state
* View discovery
* View planner
* View executor

Conceptually:

```text
YAML View
    +
Existing Project Views
        ↓
View Planner
        ↓
Create or Update View
```

A possible future specification could be:

```yaml
views:
  - name: Current Sprint
    layout: board
    group_by: Status
    filter: sprint:"Sprint 1"
```

This is only an architectural direction.

The final YAML contract should be designed when implementation begins and after the GitHub API constraints have been verified.

---

# Adding a Web Interface

The Web UI should not execute the CLI as a subprocess.

Avoid:

```text
Web Request
    ↓
Shell Command
    ↓
github-bootstrap sync
```

Instead, extract reusable application orchestration.

Target:

```text
CLI ─────┐
         │
         ▼
SynchronizationService
         ▲
         │
Web UI ──┘
```

The service should expose operations conceptually similar to:

* Load specification
* Validate specification
* Build synchronization plan
* Execute synchronization

Both interfaces should use the same service.

This prevents synchronization behavior from diverging between CLI and Web.

---

# Refactoring Rule

Refactor when a concrete implementation need exists.

Good reasons include:

* CLI and Web require the same orchestration
* Repeated API logic
* Repeated planner logic
* Unclear resource ownership
* Difficult testing caused by coupling

Weak reasons include:

* A hypothetical future resource might need it
* A generic abstraction appears cleaner
* The pattern exists only once

The project should preserve explicit, small, working components.

---

# Technical Extension Checklist

Before considering a new managed resource complete, verify:

* [ ] Specification model exists
* [ ] Parser supports it
* [ ] Validation is sufficient
* [ ] Current state can be discovered
* [ ] Internal state model exists
* [ ] Planner produces correct actions
* [ ] Executor supports those actions
* [ ] Executor is registered
* [ ] GitHub API integration is isolated
* [ ] Unit tests cover synchronization decisions
* [ ] `make verify` passes
* [ ] Real E2E behavior is validated
* [ ] Second synchronization does not create duplicates
* [ ] Documentation is updated

---

# Current Extension Points

The most relevant future technical extensions are:

* Synchronization application service
* Web UI
* Native `Status` reconciliation
* Project Views
* Project item field-value drift detection
* Resource update operations
* Project-to-repository linking

These capabilities should be implemented as independent vertical slices.

The current architecture does not need to be redesigned before adding them.

---

# Technical Principles Summary

When extending GitHub Bootstrap:

* Keep specification separate from GitHub APIs.
* Keep current state separate from desired state.
* Keep planning separate from execution.
* Keep raw API responses inside adapters.
* Make resource dependencies explicit.
* Implement capabilities vertically.
* Rediscover state when previous phases change dependencies.
* Treat dry run as a first-class capability.
* Validate important behavior against real GitHub APIs.
* Refactor only when real duplication or coupling appears.

The fundamental technical model remains:

```text
Specification
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

---

# Further Documentation

For the architectural overview:

```text
docs/ARCHITECTURE.md
```

For the complete YAML contract:

```text
docs/SPECIFICATION-REFERENCE.md
```

For user operations:

```text
docs/USER-GUIDE.md
```

For development practices:

```text
docs/DEVELOPMENT-GUIDE.md
```

For known limitations and future work:

```text
docs/ROADMAP.md
```
