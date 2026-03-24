# Hierarchical Listing

## Overview / Purpose

Tree-based rendering of tickets in listing commands (`tk ls`, `tk ready`, `tk blocked`). Tickets with parent-child relationships are displayed as indented trees. A flat mode is available to disable tree rendering.

## Scenarios

### Requirement: Tree rendering in listings
`tk ls` SHALL render tickets as an indented tree based on parent-child relationships. Root tickets (no parent) appear at the top level. Children are indented under their parent. Indentation is 2 spaces per nesting level.

#### Scenario: Parent with children
- **GIVEN** ticket `kap-rq8` exists with no parent
- **AND** tickets `kap-3ny` and `kap-6ym` exist with `parent: kap-rq8`
- **WHEN** the user runs `tk ls`
- **THEN** the output shows:
  ```
  kap-rq8  [open] - Agent Libraries v1
    kap-3ny  [open] - Add idempotency key enforcement
    kap-6ym  [open] - Add CANCELLED status
  ```

#### Scenario: Orphan tickets at root level
- **GIVEN** ticket `kap-29e` has no parent
- **AND** ticket `kap-29e` has no children
- **WHEN** the user runs `tk ls`
- **THEN** `kap-29e` appears at root level, unindented

#### Scenario: Nested children
- **GIVEN** ticket `kap-rq8` exists with no parent
- **AND** ticket `kap-we0` has `parent: kap-rq8`
- **AND** ticket `kap-5wz` has `parent: kap-we0`
- **WHEN** the user runs `tk ls`
- **THEN** the output shows:
  ```
  kap-rq8  [open] - Agent Libraries v1
    kap-we0  [open] - Postgres schema and migrations
      kap-5wz  [open] - Add CHECK constraint on status column
  ```

### Requirement: Flat listing mode
`tk ls --flat` SHALL render tickets as a flat list without parent-child indentation, preserving the current output format and sort order identically.

#### Scenario: Flat flag disables tree
- **GIVEN** tickets with parent-child relationships exist
- **WHEN** the user runs `tk ls --flat`
- **THEN** all tickets appear at the same indentation level
- **AND** output format and sort order are identical to current `tk ls` behavior

### Requirement: Tree rendering in ready and blocked
`tk ready` and `tk blocked` SHALL render tickets as indented trees, consistent with `tk ls`. Both commands apply the same tree rendering logic; the only difference is which tickets match (resolved deps for `ready`, unresolved deps for `blocked`).

#### Scenario: Ready with tree view
- **GIVEN** ticket `kap-rq8` is a parent with status `in_progress` and has unresolved deps
- **AND** child `kap-3ny` has status `open` with all deps resolved
- **AND** child `kap-6ym` has status `open` with unresolved deps
- **WHEN** the user runs `tk ready`
- **THEN** the output shows:
  ```
  kap-rq8  [in_progress] - Agent Libraries v1
    kap-3ny  [open] - Add idempotency key enforcement
  ```
- **AND** `kap-6ym` does not appear

#### Scenario: Blocked with tree view
- **GIVEN** ticket `kap-rq8` is a parent with status `open` and all deps resolved
- **AND** child `kap-3ny` has status `open` with unresolved dep `kap-ext`
- **AND** child `kap-6ym` has status `open` with all deps resolved
- **WHEN** the user runs `tk blocked`
- **THEN** the output shows:
  ```
  kap-rq8  [open] - Agent Libraries v1
    kap-3ny  [open] - Add idempotency key enforcement <- [kap-ext]
  ```
- **AND** `kap-6ym` does not appear

### Requirement: Parent visibility in filtered views
In `tk ready` and `tk blocked`, a parent ticket SHALL appear as a structural heading if any of its children match the filter, even if the parent itself does not match. The parent is rendered in the same format as matching tickets -- indentation alone distinguishes hierarchy. No additional visual marker is used.

#### Scenario: Non-matching parent shown as context
- **GIVEN** ticket `kap-rq8` has status `in_progress` and has unresolved deps (not ready)
- **AND** child `kap-3ny` has status `open` with all deps resolved (ready)
- **WHEN** the user runs `tk ready`
- **THEN** `kap-rq8` appears as a parent line above `kap-3ny`
- **AND** `kap-3ny` is indented under `kap-rq8`

#### Scenario: All children filtered out
- **GIVEN** ticket `kap-rq8` is a parent
- **AND** all children of `kap-rq8` have unresolved deps
- **WHEN** the user runs `tk ready`
- **THEN** `kap-rq8` does not appear in the output
