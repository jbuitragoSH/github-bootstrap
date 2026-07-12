# Vertical Slice Development

## Purpose

GitHub Bootstrap implements each GitHub resource as a complete vertical slice.

A vertical slice delivers one observable product capability from the YAML specification to the GitHub API.

Examples:

* Create a Project V2.
* Synchronize repository labels.
* Synchronize milestones.
* Create custom fields.
* Create issues.

Each slice must remain small, functional, tested, and independently reviewable.

---

## Standard Flow

Every resource follows this flow:

```text
YAML Specification
        │
        ▼
Loader
        │
        ▼
Validator
        │
        ▼
Parser
        │
        ▼
Domain Specification
        │
        ▼
GitHub Current State
        │
        ▼
Resource Planner
        │
        ▼
PlanAction
        │
        ▼
Executor Dispatcher
        │
        ▼
Resource Executor
        │
        ▼
GitHub Resource API
        │
        ▼
GitHub GraphQL
```

---

## Layer Responsibilities

### Specification

Defines the desired state declared in YAML.

Responsibilities:

* Load YAML.
* Validate structure and required fields.
* Parse external data into typed domain models.

The specification layer does not call GitHub.

---

### GitHub API

Communicates with GitHub through GraphQL.

Responsibilities:

* Read the current state.
* Create or modify GitHub resources.
* Convert GraphQL responses into internal models.

All HTTP communication must pass through `GitHubClient.execute()`.

Resource APIs must not use `httpx` directly.

---

### State

Represents the current state retrieved from GitHub.

Examples:

* `ProjectState`
* `LabelState`

State objects contain data only. They do not plan or execute changes.

---

### Planner

Compares the desired specification with the current GitHub state.

Responsibilities:

* Detect missing or outdated resources.
* Produce synchronization actions.
* Remain free of side effects.

A planner must not:

* call GitHub;
* print output;
* access the CLI;
* execute actions.

---

### Plan

Contains the actions required to synchronize GitHub.

The plan orchestrator delegates planning to resource-specific planners.

Examples:

```text
plan_projects()
plan_labels()
plan_milestones()
```

Resource planning logic must not live directly in the plan orchestrator.

---

### Executor

Executes the generated plan.

Responsibilities:

* Dispatch each action to the correct resource executor.
* Provide the shared `ExecutionContext`.
* Avoid resource-specific business logic.

The main executor must remain an orchestrator.

---

### Resource Executor

Executes actions for one GitHub resource.

Examples:

```text
execute_project_action()
execute_label_action()
execute_milestone_action()
```

A resource executor translates a `PlanAction` into a call to the corresponding GitHub API.

---

## Resource Lifecycle

A new GitHub resource should normally be implemented in this order:

1. Add the specification model.
2. Validate and parse the YAML definition.
3. Add the GitHub model when needed.
4. Add the current-state model.
5. Implement the GitHub read operation.
6. Implement the resource planner.
7. Add planner tests.
8. Implement the GitHub write operation.
9. Implement the resource executor.
10. Register the executor.
11. Add executor tests.
12. Integrate the resource into `sync`.
13. Run a real dry run.
14. Run a real synchronization against GitHub.

Not every resource requires every step. For example, a read-only supporting resource may not need a planner or executor.

---

## Slice Rules

Each slice must answer one clear question.

Examples:

* Can GitHub Bootstrap read repository labels?
* Can GitHub Bootstrap plan missing labels?
* Can GitHub Bootstrap create a label?
* Can GitHub Bootstrap synchronize labels end to end?

A slice must not mix unrelated refactors or resources.

Architectural improvements discovered during a slice should be added to the architectural backlog unless they are required to complete the current capability.

---

## Completion Criteria

A slice is complete only when:

* the intended capability works;
* Ruff passes;
* MyPy passes;
* Pytest passes;
* `make verify` is green;
* the commit has one clear responsibility.

For integration slices, the capability must also be tested against GitHub.

---

## Commit Discipline

Use small and descriptive commits.

Examples:

```text
[SPEC] Parse milestone specifications
[MILESTONES] Add milestone state loading
[PLANNER] Add milestone synchronization planning
[EXECUTOR] Execute milestone actions
[SYNC] Synchronize milestones
```

Do not commit partially implemented functionality.

---

## Current Proven Slice

Repository label synchronization is the first fully validated vertical slice.

It currently supports:

```text
.github-project.yaml
        │
        ▼
ProjectSpecification
        │
        ▼
LabelState
        │
        ▼
plan_labels()
        │
        ▼
PlanAction
        │
        ▼
execute_label_action()
        │
        ▼
LabelsAPI.create()
        │
        ▼
GitHub GraphQL
```

The flow has been verified through:

```bash
uv run github-bootstrap sync --dry-run
uv run github-bootstrap sync
```

A missing label was planned and created successfully in GitHub.

This implementation is the reference pattern for future resources.
