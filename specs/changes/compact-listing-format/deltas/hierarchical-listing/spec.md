## ADDED Requirements

### Requirement: Listing line format
Each ticket line in listing output SHALL follow this format:

```
<indent><id> [type?][prio?] - [status] <title> [<- deps?]
```

Where:
- `<indent>` is 2 spaces per nesting level (from tree rendering)
- `[type]` is shown only when type is not `task`
- `[prio]` is shown as `[P<n>]` only when priority is not 2
- `[status]` is a single-character checkbox: `[ ]` open, `[/]` in_progress, `[x]` completed, `[~]` rejected
- `<- [dep1, dep2]` is appended only when dependencies exist

When both type and priority are present, type comes first: `[epic][P0]`.

When neither type nor priority is present, the line reads: `<id> - [status] <title>`.

#### Scenario: Default task with default priority
- **GIVEN** ticket `tt-abc1` has type `task` and priority 2 and status `open`
- **WHEN** the user runs `tk ls`
- **THEN** the line reads: `tt-abc1 - [ ] My ticket title`

#### Scenario: Epic with non-default priority
- **GIVEN** ticket `tt-abc1` has type `epic` and priority 0 and status `open`
- **WHEN** the user runs `tk ls`
- **THEN** the line reads: `tt-abc1 [epic][P0] - [ ] My ticket title`

#### Scenario: Non-default type with default priority
- **GIVEN** ticket `tt-abc1` has type `feature` and priority 2 and status `open`
- **WHEN** the user runs `tk ls`
- **THEN** the line reads: `tt-abc1 [feature] - [ ] My ticket title`

#### Scenario: In-progress status
- **GIVEN** ticket `tt-abc1` has status `in_progress`
- **WHEN** the user runs `tk ls`
- **THEN** the status displays as `[/]`

#### Scenario: Completed status
- **GIVEN** ticket `tt-abc1` has status `closed` with close_reason `completed`
- **WHEN** the user runs `tk ls`
- **THEN** the status displays as `[x]`

#### Scenario: Rejected status
- **GIVEN** ticket `tt-abc1` has status `closed` with close_reason `rejected`
- **WHEN** the user runs `tk ls`
- **THEN** the status displays as `[~]`

#### Scenario: Ticket with dependencies
- **GIVEN** ticket `tt-abc1` has status `open` and depends on `tt-def2`
- **WHEN** the user runs `tk ls`
- **THEN** the line ends with `<- [tt-def2]`

### Requirement: Checkbox status in ready and blocked
`tk ready` and `tk blocked` SHALL use the same checkbox notation and line format as `tk ls`.

#### Scenario: Ready output format
- **GIVEN** ticket `tt-abc1` has status `open` with all deps resolved
- **WHEN** the user runs `tk ready`
- **THEN** the status displays as `[ ]`

#### Scenario: Blocked output format
- **GIVEN** ticket `tt-abc1` has status `open` with unresolved dep `tt-def2`
- **WHEN** the user runs `tk blocked`
- **THEN** the status displays as `[ ]`
- **AND** the line ends with `<- [tt-def2]`

### Requirement: Checkbox status in closed
`tk closed` SHALL use checkbox notation: `[x]` for completed, `[~]` for rejected.

#### Scenario: Closed completed output
- **GIVEN** ticket `tt-abc1` has status `closed` with close_reason `completed`
- **WHEN** the user runs `tk closed`
- **THEN** the status displays as `[x]`

#### Scenario: Closed rejected output
- **GIVEN** ticket `tt-abc1` has status `closed` with close_reason `rejected`
- **WHEN** the user runs `tk closed`
- **THEN** the status displays as `[~]`

## MODIFIED Requirements

### Requirement: Tree rendering in listings
`tk ls` SHALL render tickets as an indented tree based on parent-child relationships. Root tickets (no parent) appear at the top level. Children are indented under their parent. Indentation is 2 spaces per nesting level.

#### Scenario: Parent with children
- **GIVEN** ticket `kap-rq8` (type `epic`) exists with no parent
- **AND** tickets `kap-3ny` and `kap-6ym` exist with `parent: kap-rq8`
- **WHEN** the user runs `tk ls`
- **THEN** the output shows:
  ```
  kap-rq8 [epic] - [ ] Agent Libraries v1
    kap-3ny - [ ] Add idempotency key enforcement
    kap-6ym - [ ] Add CANCELLED status
  ```

#### Scenario: Orphan tickets at root level
- **GIVEN** ticket `kap-29e` has no parent
- **AND** ticket `kap-29e` has no children
- **WHEN** the user runs `tk ls`
- **THEN** `kap-29e` appears at root level, unindented

#### Scenario: Nested children
- **GIVEN** ticket `kap-rq8` (type `epic`) exists with no parent
- **AND** ticket `kap-we0` has `parent: kap-rq8`
- **AND** ticket `kap-5wz` has `parent: kap-we0`
- **WHEN** the user runs `tk ls`
- **THEN** the output shows:
  ```
  kap-rq8 [epic] - [ ] Agent Libraries v1
    kap-we0 - [ ] Postgres schema and migrations
      kap-5wz - [ ] Add CHECK constraint on status column
  ```

### Requirement: Tree rendering in ready and blocked
`tk ready` and `tk blocked` SHALL render tickets as indented trees, consistent with `tk ls`. Both commands apply the same tree rendering logic; the only difference is which tickets match (resolved deps for `ready`, unresolved deps for `blocked`).

#### Scenario: Ready with tree view
- **GIVEN** ticket `kap-rq8` is a parent with status `in_progress` and has unresolved deps
- **AND** child `kap-3ny` has status `open` with all deps resolved
- **AND** child `kap-6ym` has status `open` with unresolved deps
- **WHEN** the user runs `tk ready`
- **THEN** the output shows:
  ```
  kap-rq8 - [/] Agent Libraries v1
    kap-3ny - [ ] Add idempotency key enforcement
  ```
- **AND** `kap-6ym` does not appear

#### Scenario: Blocked with tree view
- **GIVEN** ticket `kap-rq8` is a parent with status `open` and all deps resolved
- **AND** child `kap-3ny` has status `open` with unresolved dep `kap-ext`
- **AND** child `kap-6ym` has status `open` with all deps resolved
- **WHEN** the user runs `tk blocked`
- **THEN** the output shows:
  ```
  kap-rq8 - [ ] Agent Libraries v1
    kap-3ny - [ ] Add idempotency key enforcement <- [kap-ext]
  ```
- **AND** `kap-6ym` does not appear
