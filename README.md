# GitHub Bootstrap

GitHub Bootstrap is a Python tool for declaratively creating and synchronizing the GitHub project infrastructure used to manage software development.

A project is described in a YAML specification and synchronized with GitHub through a command-line interface.

The tool is designed to bootstrap and maintain environments based on:

* GitHub Projects V2
* Labels
* Milestones
* Custom project fields
* Iterations
* Issues
* Project items
* Project field values

GitHub Bootstrap is currently used to manage the development environment of projects such as Knowledge Platform.

---

## Core Idea

GitHub Bootstrap treats a YAML specification as the desired state of a GitHub development environment.

```text
.github-project.yaml
        ↓
Validation
        ↓
Specification models
        ↓
Current GitHub state
        ↓
Synchronization plan
        ↓
Execution
        ↓
GitHub REST / GraphQL APIs
```

The synchronization process compares the desired configuration with the current GitHub state and creates the missing resources.

---

## Current Capabilities

GitHub Bootstrap can currently manage:

* Project V2 creation
* Repository labels
* Repository milestones
* Text fields
* Number fields
* Date fields
* Single-select fields
* Iteration fields
* Initial project iterations
* Repository issues
* Issue labels and milestones
* Adding issues to Project V2
* Project item field values
* Existing issue detection
* Drift detection for selected resources
* Multi-phase bootstrap from a clean repository

Supported project item field values include:

* `TEXT`
* `NUMBER`
* `DATE`
* `SINGLE_SELECT`
* `ITERATION`

---

## Requirements

* Python 3.12
* `uv`
* A GitHub personal access token with the required repository and Projects permissions

Set the GitHub token as an environment variable:

```bash
export GITHUB_TOKEN="your-token"
```

> Do not commit GitHub tokens to the repository.

---

## Installation

Clone the repository and install the development environment:

```bash
git clone <repository-url>
cd github-bootstrap

uv sync --dev
```

Verify the installation:

```bash
uv run github-bootstrap version
```

Check the GitHub connection:

```bash
uv run github-bootstrap github-check
```

---

## Quick Start

Create a `.github-project.yaml` file in the project root.

Example:

```yaml
organization: example-org
repository: example-repository

project:
  title: Example Development

labels:
  - name: feature
    color: "1D76DB"
    description: New functionality

milestones:
  - title: Sprint 1
    description: Initial development sprint
    due_on: 2026-08-15

fields:
  - name: Component
    type: text

  - name: Story Points
    type: number

  - name: Due Date
    type: date

  - name: Priority
    type: single_select
    options:
      - Low
      - Medium
      - High
      - Critical

  - name: Status
    type: single_select
    options:
      - Backlog
      - Ready
      - In Progress
      - In Review
      - Done

  - name: Sprint
    type: iteration
    configuration:
      duration: 14
      start_date: 2026-08-01
      iterations:
        - title: Sprint 1
        - title: Sprint 2
        - title: Sprint 3

issues:
  - title: Implement first feature
    body: |
      Implement the first product feature.

    labels:
      - feature

    milestone: Sprint 1

    fields:
      Status: Backlog
      Priority: High
      Component: Core
      Story Points: 5
      Due Date: 2026-08-10
      Sprint: Sprint 1
```

Review the synchronization plan:

```bash
uv run github-bootstrap sync --dry-run
```

Apply the synchronization:

```bash
uv run github-bootstrap sync
```

---

## Synchronization Workflow

A real synchronization is executed in phases so resources created earlier are available to later operations.

```text
Phase 1
Project V2
    ↓
Rediscover state

Phase 2
Labels
Milestones
Project Fields
    ↓
Rediscover state

Phase 3
Issues
Project Items
Project Field Values
```

This allows a clean repository to be bootstrapped with a single `sync` command.

---

## Recommended Workflow

Use the following sequence when configuring a project.

First, review the synchronization plan:

```bash
uv run github-bootstrap sync --dry-run
```

Review the planned actions and any detected drift.

Then execute the synchronization:

```bash
uv run github-bootstrap sync
```

Finally, verify the resulting Project V2 and repository resources directly in GitHub.

---

## Known Limitations

The current MVP has several known limitations.

### Native Status Field

GitHub automatically creates a native `Status` field for new Projects V2.

GitHub Bootstrap currently detects differences between the YAML specification and the native `Status` options, but does not automatically update those options.

The initial `Status` configuration must therefore be adjusted manually when required.

A typical workflow is:

* Backlog
* Ready
* In Progress
* In Review
* Done

After configuring the native `Status` field, run synchronization again to assign the desired `Status` values to project items.

### Project Views

Project views such as:

* Current Sprint
* Backlog
* Roadmap

are currently configured manually.

### Project Item Field Drift

GitHub Bootstrap assigns project item field values but does not yet compare all existing item values against the desired specification.

As a result, existing issues may appear as synchronization actions even when their values already match the desired state.

### Project Repository Linking

Issues can be added to a Project V2, but the Project itself is not currently linked automatically to the repository's **Projects** tab.

---

## Development

Install dependencies:

```bash
uv sync --dev
```

Run the complete verification pipeline:

```bash
make verify
```

The verification pipeline currently includes:

* Ruff
* MyPy
* Pytest

The recommended development workflow is:

```text
Small vertical slice
        ↓
Implementation
        ↓
Tests
        ↓
make verify
        ↓
Real GitHub E2E validation
        ↓
Commit
```

---

## Architecture

GitHub Bootstrap follows a layered and incremental architecture inspired by:

* Hexagonal Architecture
* Clean Architecture
* Vertical Slice Architecture
* Domain-Driven Design principles

The main synchronization flow is:

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
GitHub REST / GraphQL
```

See the architecture documentation for more details.

---

## Documentation

Detailed documentation is maintained under `docs/`.

Planned documentation:

```text
docs/
├── USER-GUIDE.md
├── SPECIFICATION-REFERENCE.md
├── ARCHITECTURE.md
├── TECHNICAL-GUIDE.md
├── DEVELOPMENT-GUIDE.md
└── ROADMAP.md
```

---

## Project Status

GitHub Bootstrap currently provides a functional MVP capable of bootstrapping and synchronizing a real GitHub development environment.

The current focus is:

* Product documentation
* Reusable application orchestration
* Basic web interface
* Deployment
* Improved reconciliation capabilities
