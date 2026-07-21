# Architecture

## Overview

GitHub Bootstrap is designed as a declarative synchronization tool.

Its responsibility is to transform a YAML specification into a synchronized GitHub development environment.

The high-level flow is:

```text
.github-project.yaml
        ↓
Specification loading
        ↓
Validation and parsing
        ↓
Current GitHub state discovery
        ↓
Synchronization planning
        ↓
Plan execution
        ↓
GitHub REST / GraphQL APIs
```

The architecture is influenced by:

* Hexagonal Architecture
* Clean Architecture
* Vertical Slice Architecture
* Domain-Driven Design principles

The implementation favors:

* Small, cohesive components
* Explicit responsibilities
* Low coupling
* Incremental evolution
* Minimal abstractions
* Testable synchronization behavior

---

## Architectural Goal

The central architectural goal is to separate:

```text
What the project should look like
```

from:

```text
How GitHub must be called to create it
```

The YAML specification describes the desired state.

GitHub Bootstrap discovers the current state, compares both states, creates a synchronization plan, and executes the required operations.

Conceptually:

```text
Desired State
      +
Current State
      ↓
Planner
      ↓
Synchronization Plan
      ↓
Executor
      ↓
GitHub
```

This separation is the foundation of the synchronization model.

---

## Main Architectural Flow

A synchronization begins at an interface such as the CLI and moves through the core synchronization workflow.

```text
CLI
 ↓
Specification
 ↓
GitHub State Discovery
 ↓
Planner
 ↓
Plan
 ↓
Executor
 ↓
GitHub APIs
```

Each stage has a distinct responsibility.

---

# CLI

The CLI is the current entry point of the application.

Its responsibilities include:

* Receiving command-line arguments
* Loading the specification
* Initializing the GitHub client
* Orchestrating synchronization phases
* Displaying synchronization plans
* Displaying detected drift
* Reporting execution results

The CLI should not contain GitHub-specific synchronization logic.

Its primary role is orchestration and presentation.

The current synchronization command is:

```bash
uv run github-bootstrap sync
```

The dry-run variant is:

```bash
uv run github-bootstrap sync --dry-run
```

The current orchestration is expected to evolve into a reusable application service before additional interfaces such as a Web UI are introduced.

Target direction:

```text
CLI ────────┐
            │
Web UI ─────┼── Synchronization Service
            │
Other UI ───┘
```

---

# Specification Layer

The specification layer represents the desired GitHub environment.

The main source is:

```text
.github-project.yaml
```

The specification can contain declarations for:

* Project
* Labels
* Milestones
* Fields
* Iterations
* Issues
* Project field values

The specification layer converts YAML data into explicit internal models.

Conceptually:

```text
YAML
 ↓
Parser
 ↓
Specification Models
```

Examples of specification models include:

* `ProjectSpecification`
* `Project`
* `Label`
* `Milestone`
* `Field`
* `Iteration`
* `Issue`

Specification models do not know how the GitHub APIs work.

They only describe the desired state.

---

## Validation

Validation ensures that the specification can be converted into a valid internal representation before synchronization begins.

```text
Raw YAML
   ↓
Parsing
   ↓
Validation
   ↓
ProjectSpecification
```

Validation should fail early when the specification is invalid.

Examples include:

* Unsupported field types
* Missing required properties
* Invalid iteration configuration
* Invalid values

This prevents partially executing an invalid specification against GitHub.

---

# GitHub State Discovery

Before planning synchronization, GitHub Bootstrap retrieves the current state of the target environment.

The resulting state represents what currently exists in GitHub.

```text
GitHub APIs
     ↓
State Discovery
     ↓
GitHubState
```

The aggregate state currently includes resources such as:

* `ProjectState`
* `LabelState`
* `MilestoneState`
* `FieldState`
* `IssueState`
* `ProjectItemState`

These models are snapshots of the current GitHub environment.

They are intentionally separate from specification models.

```text
Specification models
        ↓
Desired state

State models
        ↓
Current state
```

The planner compares both representations.

---

## Resource State Models

Each managed resource has a state representation.

Examples:

```text
Label specification
        versus
LabelState
```

```text
Milestone specification
        versus
MilestoneState
```

```text
Field specification
        versus
FieldState
```

For richer resources, snapshots are used.

Examples include:

* `IssueSnapshot`
* `FieldSnapshot`
* `FieldOptionSnapshot`
* `IterationSnapshot`

These snapshots provide planners and executors with the required information without exposing raw GitHub API responses throughout the application.

---

# Planner

The planner determines what must happen.

It receives:

```text
Desired Specification
        +
Current GitHub State
```

and produces:

```text
Plan
```

Conceptually:

```text
Specification
      +
GitHub State
      ↓
Planner
      ↓
PlanAction[]
```

The planner does not execute GitHub API calls.

Its responsibility is decision-making.

Examples include:

```text
Project missing
      ↓
Create project
```

```text
Label missing
      ↓
Create label
```

```text
Milestone missing
      ↓
Create milestone
```

```text
Issue missing
      ↓
Create issue
```

```text
Issue exists but is not in Project
      ↓
Synchronize issue with Project
```

```text
Resource differs
      ↓
Report drift
```

---

# Synchronization Plan

A synchronization plan contains the result of the planner's decisions.

Conceptually:

```text
Plan
├── Executable actions
└── Drift
```

## Executable Actions

Executable actions represent operations currently supported by GitHub Bootstrap.

Examples include:

* Create Project
* Create label
* Create milestone
* Create field
* Create Issue
* Synchronize Project item
* Assign Project field value

## Drift

Drift represents a detected difference that may not yet have an automatic reconciliation mechanism.

Examples include:

* Label color differs
* Label description differs
* Single-select options differ

The plan therefore separates:

```text
Can execute now
```

from:

```text
Difference detected
```

This allows the MVP to expose incomplete reconciliation explicitly without blocking supported operations.

---

# Executor

The executor receives planned actions and performs the required GitHub mutations.

Conceptually:

```text
PlanAction
    ↓
Executor
    ↓
Resource-specific handler
    ↓
GitHub API
```

The executor delegates operations to resource-specific handlers.

Examples include executors for:

* Projects
* Labels
* Milestones
* Fields
* Issues

A registry maps planned resource operations to their corresponding executor.

This prevents all execution logic from accumulating in a single large component.

---

## Execution Context

Some operations depend on identifiers produced or discovered earlier in the synchronization.

For example:

```text
Create field
      ↓
Requires Project ID
```

```text
Add Issue to Project
      ↓
Requires Project ID and Issue ID
```

```text
Set field value
      ↓
Requires Project item ID and field ID
```

An execution context carries the identifiers required during synchronization.

Conceptually:

```text
ExecutionContext
├── owner_id
├── repository_id
└── project_id
```

The context can evolve as required resources become available.

---

# GitHub API Adapters

GitHub Bootstrap communicates with GitHub through both REST and GraphQL APIs.

The API adapter layer encapsulates these external interactions.

Examples include:

* `ProjectsAPI`
* `LabelsAPI`
* `MilestonesAPI`
* `FieldsAPI`
* `IssuesAPI`
* `RepositoriesAPI`

The rest of the application should not depend directly on raw HTTP requests.

Instead:

```text
Planner
   ↓
Executor
   ↓
API Adapter
   ↓
GitHub
```

---

## REST and GraphQL Responsibilities

GitHub Bootstrap uses both API styles because different GitHub resources are exposed through different interfaces.

A simplified separation is:

```text
GitHub REST API
├── Repository labels
├── Milestones
├── Repository Issues
└── Repository-level resources
```

```text
GitHub GraphQL API
├── Projects V2
├── Project fields
├── Project items
└── Project field values
```

Issues may also require GraphQL discovery when GitHub node identifiers are needed for Project V2 operations.

API-specific details should remain encapsulated inside the adapter layer.

The rest of the system should operate using internal models and identifiers rather than raw GitHub payloads.

---

# Multi-Phase Synchronization

A major architectural characteristic of GitHub Bootstrap is phased synchronization.

A single initial GitHub state snapshot is insufficient when resources created during the same synchronization are dependencies of later resources.

For example:

```text
Project does not exist
        ↓
Fields cannot be created
```

```text
Milestone does not exist
        ↓
Issue cannot reference it
```

```text
Issue does not exist
        ↓
It cannot be added to the Project
```

Real synchronization is therefore executed in phases.

---

## Phase 1 — Project

The first phase ensures that the Project V2 exists.

```text
Discover state
      ↓
Plan Project
      ↓
Execute Project actions
```

After execution, GitHub state is discovered again.

---

## Phase 2 — Infrastructure

The second phase creates resources that later operations may depend on.

This includes:

* Labels
* Milestones
* Fields
* Iterations

Conceptually:

```text
Rediscovered State
       ↓
Infrastructure Plan
       ↓
Execution
```

After this phase, state is discovered again.

---

## Phase 3 — Issues and Project Items

The final phase handles:

* Issues
* Project membership
* Project field values

Conceptually:

```text
Rediscovered State
       ↓
Issue Plan
       ↓
Issue creation
       ↓
Project item synchronization
       ↓
Field value assignment
```

The complete synchronization flow is:

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

This allows a clean GitHub environment to be bootstrapped with one real synchronization command.

---

# Dry-Run Architecture

Dry run behaves differently from real execution.

The command:

```bash
uv run github-bootstrap sync --dry-run
```

builds a synchronization plan without executing mutations.

Conceptually:

```text
Specification
      +
Current GitHub State
      ↓
Planner
      ↓
Display Plan
```

Because nothing is created during a dry run, no rediscovery between execution phases is required.

The dry-run output represents what can be determined from the current GitHub state.

---

# Resource Lifecycle

Most managed resources follow the same general lifecycle.

```text
Specification
      ↓
Parser
      ↓
Desired Resource Model
      ↓
State Discovery
      ↓
Current Resource State
      ↓
Planner
      ↓
PlanAction
      ↓
Executor
      ↓
GitHub API
```

This pattern is the primary extension mechanism of GitHub Bootstrap.

---

## Example: Label Synchronization

A label follows approximately this flow:

```text
YAML Label
      ↓
Label Specification Model
      ↓
LabelsAPI.find()
      ↓
LabelState
      ↓
Label Planner
      ↓
Create Action or Drift
      ↓
Label Executor
      ↓
LabelsAPI.create()
```

The same conceptual pattern is reused for other resource types.

---

## Example: Issue Synchronization

Issues require additional coordination because they can also become Project items.

Conceptually:

```text
Issue Specification
       ↓
Issue Discovery
       ↓
Existing Issue?
    ┌──────┴──────┐
    │             │
   No            Yes
    │             │
 Create          Reuse
    └──────┬──────┘
           ↓
Add to Project
           ↓
Project Item
           ↓
Assign Field Values
```

Issue discovery includes both open and closed Issues.

This prevents closed Issues from being recreated as duplicates during later synchronization runs.

---

# Resource Identity

Several resources are currently identified through human-readable properties.

| Resource  | Identity |
| --------- | -------- |
| Project   | `title`  |
| Label     | `name`   |
| Milestone | `title`  |
| Field     | `name`   |
| Issue     | `title`  |
| Iteration | `title`  |

This simplifies the MVP but has consequences.

Renaming one of these values may cause the resource to be interpreted as a new resource rather than an update to the existing one.

Future synchronization improvements may introduce stronger identity mechanisms where necessary.

---

# Idempotency

GitHub Bootstrap aims for repeated synchronization to be safe.

Conceptually:

```text
sync
 ↓
Desired environment created

sync again
 ↓
No duplicate resources
```

Current idempotency support includes detection of existing:

* Projects
* Labels
* Milestones
* Fields
* Issues
* Project items

However, complete idempotent reconciliation is not yet implemented for every property.

For example, Project item field values may still be planned for synchronization even when an existing value already matches.

---

# Drift

Drift represents a difference between the desired specification and the current GitHub state.

Example:

```text
Desired label color
5319E7

Current label color
FF0000
```

The planner can report:

```text
Label exists with drift: color differs
```

Drift detection and drift reconciliation are intentionally separate concerns.

The architecture allows a resource to:

```text
Detect drift
```

without necessarily:

```text
Correcting drift
```

This makes it possible to introduce reconciliation capabilities incrementally.

---

# Design Principles

## Small Vertical Slices

New capabilities should be implemented end-to-end.

For example:

```text
Specification
      ↓
Parser
      ↓
State
      ↓
API
      ↓
Planner
      ↓
Executor
      ↓
Tests
      ↓
Real E2E Validation
```

Avoid implementing many incomplete abstractions at once.

---

## Explicit Dependencies

Resource dependencies should remain visible.

For example:

```text
Project
   ↓
Field
   ↓
Project Item
   ↓
Field Value
```

Do not hide these relationships behind unnecessary generic abstractions.

---

## Separation of Planning and Execution

Planning determines:

```text
What should happen?
```

Execution determines:

```text
How is it performed?
```

Keeping these concerns separate enables:

* Dry runs
* Plan inspection
* Easier testing
* Incremental reconciliation
* Future UI integration

---

## Internal Models Over Raw API Payloads

Raw REST and GraphQL payloads should remain inside the GitHub adapter layer as much as possible.

The rest of the system should use:

* Specification models
* State models
* Snapshots
* Plan actions
* Execution context

This reduces coupling to GitHub API response formats.

---

## Incremental Reconciliation

Not every resource needs to support complete create, update, and delete behavior immediately.

A resource can evolve through stages:

```text
Discovery
    ↓
Creation
    ↓
Idempotency
    ↓
Drift Detection
    ↓
Drift Reconciliation
    ↓
Deletion
```

This progression matches the incremental product strategy used by GitHub Bootstrap.

---

# Extending the Architecture

A new managed resource normally requires the following components:

1. Specification model
2. Parser support
3. State model
4. GitHub API adapter
5. State discovery
6. Planner
7. Executor
8. Executor registration
9. Unit tests
10. Real E2E validation

The exact components may vary depending on the resource.

For example, a future Project View capability could follow:

```text
View Specification
      ↓
View State Discovery
      ↓
View Planner
      ↓
View Executor
      ↓
GitHub GraphQL Adapter
```

The existing architecture should be extended using the same synchronization lifecycle unless a concrete problem requires a different model.

---

# Future Application Layer

The current CLI performs part of the synchronization orchestration directly.

Before introducing a Web UI, the intended evolution is to extract this orchestration into a reusable application service.

Target architecture:

```text
CLI ───┐
       │
       ├── SynchronizationService
       │
Web ───┘
```

More generally:

```text
┌─────────────┐
│     CLI     │
└──────┬──────┘
       │
┌──────▼──────────────────┐
│ Synchronization Service │
└──────┬──────────────────┘
       │
       ▼
Synchronization Core
       │
       ▼
┌─────────────┐
│ GitHub APIs │
└─────────────┘

┌─────────────┐
│   Web UI    │
└──────┬──────┘
       │
       └──────────────► Synchronization Service
```

UI layers should handle input and presentation.

The synchronization service should own the application workflow.

---

# Current Architectural Boundaries

The current MVP intentionally does not fully manage:

* Native `Status` option reconciliation
* Project Views
* Complete Project item field-value drift
* Resource deletion
* Automatic repository-to-Project linking

These are extension points rather than reasons to redesign the core architecture.

Each capability can be introduced through additional vertical slices.

---

# Architecture Evolution Rule

A new abstraction should be introduced only when the existing design creates real duplication, coupling, or complexity.

The preferred evolution strategy is:

```text
Working implementation
        ↓
Repeated pattern
        ↓
Observed duplication or coupling
        ↓
Small refactor
        ↓
Reusable abstraction
```

Avoid designing abstractions only for hypothetical future resources.

---

# Summary

The core architectural model of GitHub Bootstrap is:

```text
Desired State
        +
Current GitHub State
        ↓
Planner
        ↓
Synchronization Plan
        ↓
Executor
        ↓
GitHub
```

The product is structured around a repeatable resource lifecycle:

```text
Specification
      ↓
State Discovery
      ↓
Planning
      ↓
Execution
```

Real synchronization is executed in phases to resolve dependencies between resources.

The architecture is intentionally designed so additional capabilities can be introduced incrementally without changing the fundamental synchronization model.

For implementation-level details, see:

```text
docs/TECHNICAL-GUIDE.md
```

For the YAML contract, see:

```text
docs/SPECIFICATION-REFERENCE.md
```

For development practices, see:

```text
docs/DEVELOPMENT-GUIDE.md
```
