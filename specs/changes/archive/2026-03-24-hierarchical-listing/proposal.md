## Why

`tk ls` produces a flat list regardless of parent-child relationships. The `--parent` option on `tk create` exists, but the primary listing view discards this structure. In a project with 40+ tickets, there's no visual indication of which tickets belong together.

Tree rendering makes the grouping visible where it matters -- in the default output of `tk ls`, `tk ready`, and `tk blocked`.

## What Changes

- `tk ls` renders tickets as an indented tree based on parent-child relationships
- `tk ready` and `tk blocked` gain the same tree rendering
- `tk ls --flat` preserves current flat output for scripts and backward compatibility
- Parent tickets appear as group headings in filtered views (`ready`, `blocked`) when any of their children match, even if the parent itself does not

## Capabilities

### New Capabilities

- `hierarchical-listing`: Rendering parent-child ticket relationships as indented trees in listing output

### Modified Capabilities

_None. There are no existing reference specs._

## Impact

- Core script (`ticket`): `cmd_ready()`, `cmd_blocked()`, `cmd_closed()` awk blocks
- Plugin (`plugins/ticket-ls`): `emit()` function, parent field parsing
- Behave tests: new scenarios for tree rendering, updated assertions for existing listing tests
