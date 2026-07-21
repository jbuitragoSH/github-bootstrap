# User Guide

## Overview

GitHub Bootstrap is a command-line tool for declaratively creating and synchronizing the GitHub project infrastructure used to manage software development.

Instead of configuring GitHub resources manually, the desired project environment is defined in a YAML specification.

GitHub Bootstrap compares that specification with the current GitHub state and creates or synchronizes the required resources.

The typical workflow is:

```text
.github-project.yaml
        ↓
Review configuration
        ↓
Dry run
        ↓
Review synchronization plan
        ↓
Synchronize
        ↓
Verify GitHub environment
```

---

## Requirements

Before using GitHub Bootstrap, ensure the following requirements are available:

* Python 3.12
* `uv`
* Git
* A GitHub account
* A GitHub personal access token with the required permissions

---

## Installation

Clone the GitHub Bootstrap repository:

```bash
git clone <github-bootstrap-repository-url>
cd github-bootstrap
```

Install the project and development dependencies:

```bash
uv sync --dev
```

Verify that the command-line application is available:

```bash
uv run github-bootstrap --help
```

---

## GitHub Authentication

GitHub Bootstrap communicates with GitHub through the GitHub REST and GraphQL APIs.

Authentication is performed using a GitHub personal access token.

Set the token as an environment variable:

```bash
export GITHUB_TOKEN="your-token"
```

The token must have sufficient permissions to manage the resources declared in the specification.

Depending on the repository and organization configuration, this can include permissions for:

* Repositories
* Issues
* Labels
* Milestones
* GitHub Projects V2

> Never commit the GitHub token to the repository.

To verify the connection with GitHub, run:

```bash
uv run github-bootstrap github-check
```

A successful response confirms that the token is valid and that GitHub Bootstrap can communicate with GitHub.

---

## Project Specification

GitHub Bootstrap reads the desired project configuration from:

```text
.github-project.yaml
```

The file should normally be located in the directory where the command is executed.

A specification can define:

* Target organization
* Target repository
* GitHub Project V2
* Labels
* Milestones
* Project fields
* Iterations
* Issues
* Issue field values

### Example

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

For the complete YAML contract, see:

```text
docs/SPECIFICATION-REFERENCE.md
```

---

## Basic Workflow

The recommended workflow is:

1. Create or update `.github-project.yaml`.
2. Run a dry run.
3. Review planned actions.
4. Review detected drift.
5. Execute synchronization.
6. Verify the resulting GitHub environment.

---

## Dry Run

Before modifying GitHub, always review the synchronization plan.

Run:

```bash
uv run github-bootstrap sync --dry-run
```

A dry run does not execute GitHub mutations.

It displays the actions GitHub Bootstrap would perform.

Example:

```text
Synchronization plan:
+ Create project 'Example Development'
+ Create label 'feature'
+ Create milestone 'Sprint 1'
+ Create field 'Priority'
+ Create issue 'Implement first feature'
```

A dry run can also report drift.

Example:

```text
Drift detected:
! Label 'feature' exists with drift: color differs
! Field 'Status' exists with drift: options differ
```

Review this output before executing synchronization.

---

## Synchronization

After reviewing the dry-run output, execute:

```bash
uv run github-bootstrap sync
```

GitHub Bootstrap performs synchronization in multiple phases.

```text
Phase 1
Project V2
    ↓
Rediscover GitHub state

Phase 2
Labels
Milestones
Project fields
    ↓
Rediscover GitHub state

Phase 3
Issues
Project items
Project field values
```

This phased execution allows a new repository environment to be bootstrapped with a single synchronization command.

For example, an Issue cannot be assigned a project field value until:

* The Project exists.
* The field exists.
* The Issue exists.
* The Issue has been added to the Project.

The phased synchronization process resolves these dependencies automatically.

---

## Synchronization Plans

GitHub Bootstrap separates executable synchronization actions from detected drift.

### Executable Actions

Executable actions represent operations that GitHub Bootstrap can currently perform.

Examples:

```text
+ Create label 'feature'
+ Create milestone 'Sprint 1'
+ Create field 'Priority'
+ Create issue 'Implement first feature'
+ Synchronize issue 'Implement first feature' with project
```

These actions are executed when running:

```bash
uv run github-bootstrap sync
```

### Drift

Drift means that a resource already exists but differs from the desired specification.

Example:

```text
! Label 'domain' exists with drift: color differs
```

Not every detected drift is automatically corrected.

The exact behavior depends on the resource type and the capabilities currently implemented by GitHub Bootstrap.

---

## Projects V2

The specification can define a GitHub Project V2.

Example:

```yaml
project:
  title: Example Development
```

During synchronization, GitHub Bootstrap searches for an existing Project with the configured title.

If no matching Project exists, it is created.

The Project then becomes the target for:

* Project fields
* Project items
* Issue field values

---

## Labels

Repository labels can be defined as:

```yaml
labels:
  - name: feature
    color: "1D76DB"
    description: New functionality
```

GitHub Bootstrap detects existing labels by name.

Missing labels are created.

Differences such as:

* Color
* Description

can currently be reported as drift.

Example:

```text
! Label 'feature' exists with drift: color differs
```

---

## Milestones

Milestones can be defined as:

```yaml
milestones:
  - title: Sprint 1
    description: Initial development sprint
    due_on: 2026-08-15
```

GitHub Bootstrap creates missing milestones and can associate them with Issues.

The `due_on` value uses the following format:

```text
YYYY-MM-DD
```

Example:

```text
2026-08-15
```

GitHub Bootstrap converts this value to the timestamp format required by the GitHub API.

---

## Project Fields

GitHub Bootstrap currently supports several Project V2 field types.

### Text

```yaml
- name: Component
  type: text
```

Example Issue value:

```yaml
fields:
  Component: Academic Knowledge Core
```

### Number

```yaml
- name: Story Points
  type: number
```

Example:

```yaml
fields:
  Story Points: 5
```

### Date

```yaml
- name: Due Date
  type: date
```

Example:

```yaml
fields:
  Due Date: 2026-08-10
```

### Single Select

```yaml
- name: Priority
  type: single_select
  options:
    - Low
    - Medium
    - High
    - Critical
```

Example:

```yaml
fields:
  Priority: High
```

The configured Issue value must match an existing field option.

### Iteration

Iteration fields can define their initial configuration.

Example:

```yaml
- name: Sprint
  type: iteration
  configuration:
    duration: 14
    start_date: 2026-08-01
    iterations:
      - title: Sprint 1
      - title: Sprint 2
      - title: Sprint 3
```

The configuration defines:

* Iteration duration
* Initial start date
* Initial iteration titles

Issue values can then reference an iteration by title:

```yaml
fields:
  Sprint: Sprint 1
```

---

## Issues

Issues can be declared directly in the specification.

Example:

```yaml
issues:
  - title: Implement Academic Program aggregate

    body: |
      Implement the initial Academic Program aggregate.

    labels:
      - domain

    milestone: Sprint 1

    fields:
      Status: Backlog
      Priority: High
      Component: Academic Knowledge Core
      Story Points: 5
      Due Date: 2026-08-05
      Sprint: Sprint 1
```

GitHub Bootstrap uses the Issue title to determine whether an Issue already exists.

Both open and closed Issues are considered during discovery.

This prevents a closed Issue from being recreated as a duplicate during a later synchronization.

---

## Existing Issues

When an Issue already exists, GitHub Bootstrap can reuse it instead of creating a new one.

The existing Issue can then be:

* Added to the Project.
* Associated with Project field values.

For example:

```text
+ Synchronize issue 'Implement Academic Program aggregate' with project
```

This means the Issue exists and GitHub Bootstrap is synchronizing its Project representation.

It does not mean that a new Issue will be created.

---

## Project Items

An Issue must exist as a Project item before Project V2 field values can be assigned.

GitHub Bootstrap automatically adds configured Issues to the target Project when required.

Conceptually:

```text
Repository Issue
        ↓
Add to Project V2
        ↓
Project Item
        ↓
Assign project field values
```

---

## Project Field Values

The following field values can currently be assigned to Project items:

* `TEXT`
* `NUMBER`
* `DATE`
* `SINGLE_SELECT`
* `ITERATION`

Example:

```yaml
fields:
  Status: Backlog
  Priority: High
  Component: Academic Knowledge Core
  Story Points: 5
  Due Date: 2026-08-10
  Sprint: Sprint 1
```

The referenced field and, where applicable, the referenced option or iteration must exist in the Project.

---

## Native Status Field

GitHub Projects V2 automatically creates a native `Status` field.

A new Project commonly starts with options such as:

* Todo
* In Progress
* Done

A GitHub Bootstrap specification may define a different desired workflow.

For example:

```yaml
- name: Status
  type: single_select
  options:
    - Backlog
    - Ready
    - In Progress
    - In Review
    - Done
```

GitHub Bootstrap currently detects differences between the existing native `Status` options and the desired specification, but does not automatically modify those options.

The initial configuration therefore requires a manual step.

Configure the native `Status` field in GitHub with:

* Backlog
* Ready
* In Progress
* In Review
* Done

Then run:

```bash
uv run github-bootstrap sync
```

GitHub Bootstrap can then assign values such as:

```yaml
Status: Backlog
```

to the configured Project items.

---

## Project Views

Project views are currently configured manually in GitHub.

A useful initial configuration is:

* Current Sprint
* Backlog
* Roadmap

### Current Sprint

Recommended layout:

```text
Board
```

Recommended grouping:

```text
Status
```

Recommended filter:

```text
sprint:"Sprint 1"
```

### Backlog

Recommended layout:

```text
Board
```

Recommended filter:

```text
status:Backlog,Ready
```

### Roadmap

Recommended layout:

```text
Roadmap
```

Recommended date field:

```text
Due Date
```

These views are not currently managed through `.github-project.yaml`.

---

## Idempotency

A core goal of GitHub Bootstrap is to make repeated synchronization safe.

Running:

```bash
uv run github-bootstrap sync
```

multiple times should not create duplicate resources when those resources can be correctly identified.

Current examples include:

* Projects
* Labels
* Milestones
* Fields
* Issues

Issue discovery includes both open and closed Issues.

However, idempotency and drift reconciliation are not yet complete for every resource type.

---

## Known Limitations

The current MVP has several known limitations.

### Native Status Options

The native GitHub Project `Status` field is not automatically reconfigured.

Its desired options must currently be configured manually.

### Project Views

Views such as:

* Current Sprint
* Backlog
* Roadmap

must currently be created manually.

### Project Item Field Drift

GitHub Bootstrap can assign Project item field values, but does not yet fully compare every existing field value against the desired specification.

Because of this, a dry run may report:

```text
+ Synchronize issue '...' with project
```

even when some or all field values already match.

### Resource Drift Reconciliation

Some resource differences are currently detected but not automatically corrected.

Examples can include:

* Label color differences
* Label description differences
* Single-select option differences

These differences are reported as drift.

### Project Repository Linking

GitHub Bootstrap can add repository Issues to a Project V2.

However, the Project itself is not currently linked automatically to the repository's **Projects** section.

This does not prevent Issues from being added to or managed by the Project.

---

## Recommended First-Time Setup

For a new repository, use the following workflow.

### 1. Create the Specification

Create:

```text
.github-project.yaml
```

Define the required:

* Project
* Labels
* Milestones
* Fields
* Iterations
* Issues

### 2. Run a Dry Run

```bash
uv run github-bootstrap sync --dry-run
```

Review:

* Planned actions
* Detected drift

### 3. Execute Synchronization

```bash
uv run github-bootstrap sync
```

This should create the infrastructure currently supported by GitHub Bootstrap.

### 4. Configure the Native Status Field

Open the newly created Project in GitHub.

Configure the desired workflow.

For example:

* Backlog
* Ready
* In Progress
* In Review
* Done

### 5. Synchronize Again

Run:

```bash
uv run github-bootstrap sync
```

This allows configured Issues to receive `Status` values that depend on the manually configured native field options.

### 6. Configure Project Views

Create the required views manually.

A recommended initial setup is:

* Current Sprint
* Backlog
* Roadmap

### 7. Verify the Environment

Confirm that the expected resources exist:

* Project
* Labels
* Milestones
* Fields
* Iterations
* Issues
* Project items
* Field values

---

## Updating an Existing Specification

To evolve a managed environment:

1. Modify `.github-project.yaml`.
2. Run a dry run.
3. Review the synchronization plan and detected drift.
4. Execute synchronization.
5. Verify the resulting GitHub state.

Example:

```bash
uv run github-bootstrap sync --dry-run
```

Then:

```bash
uv run github-bootstrap sync
```

Avoid making large specification changes without first reviewing the dry-run output.

---

## Troubleshooting

### Authentication Fails

Verify that:

```bash
echo "$GITHUB_TOKEN"
```

returns a configured value.

Then run:

```bash
uv run github-bootstrap github-check
```

Ensure the token has the necessary permissions.

### An Issue Is Duplicated

GitHub Bootstrap currently identifies existing Issues primarily by title.

Ensure the configured title matches the existing Issue title.

Current Issue discovery considers both open and closed Issues.

### A Field Value Is Not Assigned

Verify that:

* The field exists.
* The Issue is part of the Project.
* The configured value is valid.
* The single-select option exists.
* The iteration title exists.

For the native `Status` field, ensure the desired option was configured manually.

### Drift Is Reported After Synchronization

Some drift is detected but not automatically corrected.

Example:

```text
! Label 'domain' exists with drift: color differs
```

Review the reported difference.

Depending on the resource, either:

* Update the GitHub resource manually.
* Update the YAML specification.
* Accept the known drift until reconciliation support is implemented.

### Issues Continue Appearing as Synchronization Actions

Current Project item field-value reconciliation is incomplete.

An existing Issue may therefore continue to appear as:

```text
+ Synchronize issue '...' with project
```

This does not necessarily mean the Issue will be recreated.

Check the planned action description carefully.

A `Create issue` action and a `Synchronize issue` action represent different operations.

---

## Safe Usage Practices

Always use a dry run before synchronization:

```bash
uv run github-bootstrap sync --dry-run
```

Do not commit:

* GitHub tokens
* Personal access credentials
* Sensitive environment files

Use a controlled specification and introduce changes incrementally.

For major changes, validate the behavior first against a test repository when possible.

---

## Typical Operational Workflow

A normal working cycle is:

```text
Update .github-project.yaml
        ↓
sync --dry-run
        ↓
Review actions and drift
        ↓
sync
        ↓
Verify GitHub
        ↓
Use Project normally
```

GitHub Bootstrap is intended to manage the project infrastructure while GitHub remains the operational environment used by the development team.

---

## Further Documentation

For more detailed information, see:

```text
README.md
docs/SPECIFICATION-REFERENCE.md
docs/ARCHITECTURE.md
docs/TECHNICAL-GUIDE.md
docs/DEVELOPMENT-GUIDE.md
docs/ROADMAP.md
```
