# Specification Reference

## Overview

GitHub Bootstrap uses a YAML specification to describe the desired state of a GitHub development environment.

The default specification file is:

```text
.github-project.yaml
```

The specification can define:

* Target organization
* Target repository
* GitHub Project V2
* Repository labels
* Repository milestones
* Custom project fields
* Project iterations
* Repository Issues
* Issue labels
* Issue milestones
* Project item field values

A simplified specification looks like this:

```yaml
organization: example-org
repository: example-repository

project:
  title: Example Development

labels: []
milestones: []
fields: []
issues: []
```

---

## General Rules

The specification is declarative.

It describes what the GitHub environment should contain rather than the individual API operations required to create it.

GitHub Bootstrap follows this general process:

```text
Specification
      ↓
Validation
      ↓
Current GitHub state
      ↓
Synchronization plan
      ↓
Execution
```

Resource names and titles are currently used to identify several existing GitHub resources.

Changes should therefore be introduced carefully, especially when renaming managed resources.

---

## Root Properties

The root of the specification supports the following properties.

| Property       | Type   | Required | Description                                                        |
| -------------- | ------ | -------: | ------------------------------------------------------------------ |
| `organization` | string |      Yes | GitHub organization or owner containing the repository and Project |
| `repository`   | string |      Yes | Target GitHub repository                                           |
| `project`      | object |      Yes | GitHub Project V2 configuration                                    |
| `labels`       | list   |       No | Repository labels                                                  |
| `milestones`   | list   |       No | Repository milestones                                              |
| `fields`       | list   |       No | GitHub Project V2 fields                                           |
| `issues`       | list   |       No | Repository Issues and their Project field values                   |

Example:

```yaml
organization: example-org
repository: example-repository

project:
  title: Example Development
```

---

# Project

The `project` section defines the GitHub Project V2 managed by GitHub Bootstrap.

## Properties

| Property | Type   | Required | Description   |
| -------- | ------ | -------: | ------------- |
| `title`  | string |      Yes | Project title |

Example:

```yaml
project:
  title: Example Development
```

GitHub Bootstrap searches for an existing Project with the configured title.

If no matching Project exists, it is created.

The Project becomes the target for:

* Custom fields
* Project items
* Project item field values

---

# Labels

The `labels` section defines repository labels.

Example:

```yaml
labels:
  - name: feature
    color: "1D76DB"
    description: New functionality

  - name: bug
    color: "D73A4A"
    description: Something is not working
```

## Properties

| Property      | Type   | Required | Description        |
| ------------- | ------ | -------: | ------------------ |
| `name`        | string |      Yes | Label name         |
| `color`       | string |      Yes | GitHub label color |
| `description` | string |       No | Label description  |

## Name

Example:

```yaml
name: feature
```

The label name is used to identify an existing repository label.

Changing the name can therefore cause GitHub Bootstrap to treat the renamed label as a different resource.

## Color

Example:

```yaml
color: "1D76DB"
```

Use the hexadecimal RGB value without the `#` prefix.

Recommended:

```yaml
color: "1D76DB"
```

Avoid:

```yaml
color: "#1D76DB"
```

Quoting the value is recommended.

## Description

Example:

```yaml
description: New functionality
```

The description is optional.

GitHub Bootstrap can detect differences between the configured description and the existing GitHub label.

## Label Drift

Existing labels can be reported as drift when properties differ.

Examples:

```text
! Label 'feature' exists with drift: color differs
```

```text
! Label 'documentation' exists with drift: description differs
```

Drift detection does not necessarily imply that the difference will be automatically corrected.

---

# Milestones

The `milestones` section defines repository milestones.

Example:

```yaml
milestones:
  - title: Sprint 1
    description: Initial development sprint
    due_on: 2026-08-15
```

## Properties

| Property      | Type   | Required | Description           |
| ------------- | ------ | -------: | --------------------- |
| `title`       | string |      Yes | Milestone title       |
| `description` | string |       No | Milestone description |
| `due_on`      | date   |       No | Milestone due date    |

## Title

Example:

```yaml
title: Sprint 1
```

The title is used to identify an existing milestone.

## Description

Example:

```yaml
description: Initial development sprint
```

The description is optional.

## Due Date

Example:

```yaml
due_on: 2026-08-15
```

The expected format is:

```text
YYYY-MM-DD
```

GitHub Bootstrap converts the value to the timestamp format required by the GitHub API.

## Complete Example

```yaml
milestones:
  - title: Sprint 1
    description: Academic Knowledge Core foundation
    due_on: 2026-08-15

  - title: Sprint 2
    description: Application layer foundation
    due_on: 2026-08-29
```

---

# Project Fields

The `fields` section defines fields for the GitHub Project V2.

GitHub Bootstrap currently supports:

* `text`
* `number`
* `date`
* `single_select`
* `iteration`

Example:

```yaml
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

  - name: Sprint
    type: iteration
    configuration:
      duration: 14
      start_date: 2026-08-01
      iterations:
        - title: Sprint 1
        - title: Sprint 2
```

## Common Properties

All field definitions use the following common properties.

| Property | Type   | Required | Description        |
| -------- | ------ | -------: | ------------------ |
| `name`   | string |      Yes | Project field name |
| `type`   | string |      Yes | Project field type |

Supported `type` values are:

```text
text
number
date
single_select
iteration
```

---

## Text Fields

A text field stores free-form text.

Definition:

```yaml
- name: Component
  type: text
```

Issue value:

```yaml
fields:
  Component: Academic Knowledge Core
```

---

## Number Fields

A number field stores numeric values.

Definition:

```yaml
- name: Story Points
  type: number
```

Issue value:

```yaml
fields:
  Story Points: 5
```

Integer and decimal values are supported by the specification model.

Examples:

```yaml
fields:
  Story Points: 5
```

```yaml
fields:
  Story Points: 2.5
```

---

## Date Fields

A date field stores a calendar date.

Definition:

```yaml
- name: Due Date
  type: date
```

Issue value:

```yaml
fields:
  Due Date: 2026-08-10
```

Expected format:

```text
YYYY-MM-DD
```

---

## Single-Select Fields

A single-select field contains a predefined set of options.

Example:

```yaml
- name: Priority
  type: single_select
  options:
    - Low
    - Medium
    - High
    - Critical
```

### Properties

| Property  | Type            | Required | Description             |
| --------- | --------------- | -------: | ----------------------- |
| `name`    | string          |      Yes | Field name              |
| `type`    | string          |      Yes | Must be `single_select` |
| `options` | list of strings |      Yes | Available field options |

An Issue can reference one of the options:

```yaml
fields:
  Priority: High
```

The configured value must match an option available in the corresponding GitHub Project field.

---

## Native Status Field

GitHub Projects V2 automatically creates a native field named `Status`.

A specification can describe the desired options:

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

GitHub Bootstrap currently does not automatically replace the native `Status` options.

A new Project may initially contain options such as:

* Todo
* In Progress
* Done

The desired options must therefore currently be configured manually in GitHub.

After the required options exist, GitHub Bootstrap can assign values such as:

```yaml
fields:
  Status: Backlog
```

---

## Iteration Fields

Iteration fields represent recurring time periods such as development sprints.

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

### Properties

| Property        | Type   | Required | Description             |
| --------------- | ------ | -------: | ----------------------- |
| `name`          | string |      Yes | Field name              |
| `type`          | string |      Yes | Must be `iteration`     |
| `configuration` | object |      Yes | Iteration configuration |

### Iteration Configuration

The `configuration` object supports:

| Property     | Type    | Required | Description                       |
| ------------ | ------- | -------: | --------------------------------- |
| `duration`   | integer |      Yes | Iteration duration in days        |
| `start_date` | date    |      Yes | Start date of the first iteration |
| `iterations` | list    |       No | Initial iterations to create      |

Example:

```yaml
configuration:
  duration: 14
  start_date: 2026-08-01
  iterations:
    - title: Sprint 1
    - title: Sprint 2
    - title: Sprint 3
```

### Duration

Example:

```yaml
duration: 14
```

The duration is expressed in days.

### Start Date

Example:

```yaml
start_date: 2026-08-01
```

Expected format:

```text
YYYY-MM-DD
```

The first iteration starts on this date.

Subsequent initial iterations are calculated sequentially using the configured duration.

For example:

```text
Sprint 1 → 2026-08-01
Sprint 2 → 2026-08-15
Sprint 3 → 2026-08-29
```

for a duration of 14 days.

### Initial Iterations

Initial iterations are declared as:

```yaml
iterations:
  - title: Sprint 1
  - title: Sprint 2
  - title: Sprint 3
```

Each iteration currently requires only a title.

An Issue can reference an iteration by title:

```yaml
fields:
  Sprint: Sprint 1
```

---

# Issues

The `issues` section defines repository Issues that should exist and can optionally be synchronized with the GitHub Project.

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

## Properties

| Property    | Type            | Required | Description                    |
| ----------- | --------------- | -------: | ------------------------------ |
| `title`     | string          |      Yes | Issue title                    |
| `body`      | string          |       No | Issue description              |
| `labels`    | list of strings |       No | Repository labels to associate |
| `milestone` | string          |       No | Milestone title                |
| `fields`    | mapping         |       No | Project item field values      |

---

## Issue Title

Example:

```yaml
title: Implement Academic Program aggregate
```

The Issue title is currently used to identify existing Issues.

GitHub Bootstrap searches both open and closed Issues.

This prevents a closed Issue with the same title from being recreated during a later synchronization.

Because the title currently acts as an identity key, avoid renaming managed Issues without understanding the synchronization consequences.

---

## Issue Body

The body can be a single line:

```yaml
body: Implement the initial aggregate.
```

For longer content, use YAML block syntax:

```yaml
body: |
  Implement the initial Academic Program aggregate.

  Scope:
  - identity
  - basic state
  - domain invariants
```

---

## Issue Labels

Example:

```yaml
labels:
  - domain
  - architecture
```

The referenced labels should exist in the target repository.

For predictable synchronization, define managed labels in the same specification when appropriate.

Example:

```yaml
labels:
  - name: domain
    color: "5319E7"
    description: Domain model work
```

Then reference the label from an Issue:

```yaml
issues:
  - title: Implement aggregate
    labels:
      - domain
```

---

## Issue Milestone

Example:

```yaml
milestone: Sprint 1
```

The value references a milestone by title.

The milestone should already exist or be declared in the same specification.

Because synchronization runs in phases, milestones created during the current synchronization are available before Issue creation.

---

# Issue Field Values

The `fields` mapping inside an Issue assigns values to its Project item.

Example:

```yaml
fields:
  Status: Backlog
  Priority: High
  Component: Academic Knowledge Core
  Story Points: 5
  Due Date: 2026-08-05
  Sprint: Sprint 1
```

The mapping key is the Project field name.

The value depends on the corresponding field type.

---

## Text Value

Field:

```yaml
- name: Component
  type: text
```

Issue value:

```yaml
fields:
  Component: Academic Knowledge Core
```

---

## Number Value

Field:

```yaml
- name: Story Points
  type: number
```

Issue value:

```yaml
fields:
  Story Points: 5
```

---

## Date Value

Field:

```yaml
- name: Due Date
  type: date
```

Issue value:

```yaml
fields:
  Due Date: 2026-08-05
```

---

## Single-Select Value

Field:

```yaml
- name: Priority
  type: single_select
  options:
    - Low
    - Medium
    - High
```

Issue value:

```yaml
fields:
  Priority: High
```

The value must correspond to an available field option.

---

## Iteration Value

Field:

```yaml
- name: Sprint
  type: iteration
  configuration:
    duration: 14
    start_date: 2026-08-01
    iterations:
      - title: Sprint 1
```

Issue value:

```yaml
fields:
  Sprint: Sprint 1
```

The value references an iteration by title.

---

# Complete Example

The following example combines the currently supported resources.

```yaml
organization: example-org
repository: example-repository

project:
  title: Example Development

labels:
  - name: domain
    color: "5319E7"
    description: Domain model work

  - name: application
    color: "1D76DB"
    description: Application layer work

  - name: architecture
    color: "0E8A16"
    description: Architectural work

  - name: documentation
    color: "0075CA"
    description: Documentation work

milestones:
  - title: Sprint 1
    description: Initial product foundation
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
  - title: Implement Academic Program aggregate
    body: |
      Implement the initial Academic Program aggregate.

      Scope:
      - aggregate root
      - identity
      - basic properties
      - initial invariants

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

  - title: Implement Academic Program use cases
    body: |
      Implement the initial application use cases for Academic Program.

      Scope:
      - create academic program
      - retrieve academic program
      - basic validation

    labels:
      - application

    milestone: Sprint 1

    fields:
      Status: Backlog
      Priority: High
      Component: Academic Knowledge Core
      Story Points: 5
      Due Date: 2026-08-14
      Sprint: Sprint 1
```

---

# Synchronization Dependencies

Some resources depend on resources created earlier in the synchronization process.

Conceptually:

```text
Project
   ↓
Project Fields
   ↓
Issue
   ↓
Project Item
   ↓
Project Field Values
```

GitHub Bootstrap resolves these dependencies through phased synchronization.

```text
Phase 1
Project

Phase 2
Labels
Milestones
Fields

Phase 3
Issues
Project Items
Field Values
```

This makes it possible to bootstrap the currently supported environment from a clean repository using a single synchronization command.

---

# Resource Identity

GitHub Bootstrap currently identifies several resources using human-readable properties.

| Resource  | Identity |
| --------- | -------- |
| Project   | `title`  |
| Label     | `name`   |
| Milestone | `title`  |
| Field     | `name`   |
| Issue     | `title`  |
| Iteration | `title`  |

This has an important consequence:

> Renaming a resource can be interpreted differently from updating the same resource.

Treat managed names and titles as stable identifiers unless explicit rename support exists for that resource type.

---

# Drift

Drift occurs when an existing GitHub resource differs from the desired specification.

Example:

```text
Desired State

Priority:
  Low
  Medium
  High

Current GitHub State

Priority:
  Low
  Medium
  High
  Critical
```

GitHub Bootstrap can detect drift for selected resource types.

Example output:

```text
Drift detected:
! Field 'Priority' exists with drift: options differ
```

Not all detected drift is automatically reconciled.

The specification therefore represents the desired state, but the current MVP does not yet provide complete convergence for every supported property.

---

# Known Specification Limitations

## Native Status

The desired `Status` options can be declared:

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

However, GitHub Bootstrap does not currently modify the native GitHub `Status` options automatically.

---

## Project Views

Project views are not currently part of the specification.

Views such as:

* Current Sprint
* Backlog
* Roadmap

must currently be configured manually.

---

## Existing Project Item Values

Issue field values can be assigned, but complete field-value drift detection is not yet implemented.

Repeated synchronizations may therefore continue to produce Issue synchronization actions.

---

## Resource Deletion

The current specification should not be interpreted as authoritative deletion configuration.

Removing an item from the YAML does not necessarily mean GitHub Bootstrap will delete the corresponding GitHub resource.

Current synchronization primarily focuses on:

* Creation
* Association
* Assignment
* Selected drift detection

---

# Recommended Practices

Keep `.github-project.yaml` under version control when it does not contain secrets.

Use it as the canonical description of the managed GitHub environment.

Always review changes with:

```bash
uv run github-bootstrap sync --dry-run
```

before executing:

```bash
uv run github-bootstrap sync
```

Prefer small specification changes.

A recommended workflow is:

```text
Add or modify one capability
        ↓
Dry run
        ↓
Review plan and drift
        ↓
Synchronize
        ↓
Verify in GitHub
```

Avoid changing many resource names at once.

Do not store GitHub tokens or credentials in the YAML specification.

---

# Further Documentation

For operational usage, see:

```text
docs/USER-GUIDE.md
```

For the internal architecture, see:

```text
docs/ARCHITECTURE.md
```

For extension and implementation details, see:

```text
docs/TECHNICAL-GUIDE.md
```

For local development, see:

```text
docs/DEVELOPMENT-GUIDE.md
```

For current limitations and future capabilities, see:

```text
docs/ROADMAP.md
```
