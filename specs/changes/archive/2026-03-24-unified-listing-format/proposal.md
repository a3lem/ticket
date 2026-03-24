## Why

The four listing commands (`ls`, `ready`, `blocked`, `closed`) each use a different format string with inconsistent field sets. The `<-` arrow used for dependencies is ambiguous -- the fork author misread the direction while writing documentation.

AI agents are the primary consumers of this output. Claude's own task management tools use `blocked-by` / `blocks` terminology. Aligning with that vocabulary and using a consistent, parseable format across all listing commands reduces misinterpretation.

## What Changes

- Unified output format across `ls`, `ready`, `blocked`, `closed` using `::` delimiters
- Replace `<-` arrow with explicit `[blocked-by: ...]` label
- Add priority display to `ls` and `closed` (currently only in `ready`/`blocked`)
- Hide default priority (P2) to reduce noise
- Add `[tags: ...]` display to all listing commands
- Consistent field ordering: ID, priority, status, title, blocked-by, tags

## Capabilities

### New Capabilities

- `listing-format`: The grammar and field rendering rules for ticket listing output

### Modified Capabilities

_None. There is no existing reference spec for listing output._

## Impact

- Core script (`ticket`): `cmd_ready()`, `cmd_blocked()`, `cmd_closed()` format strings
- Plugin (`plugins/ticket-ls`): `emit()` function format string
- Behave tests: any assertions matching exact listing output
- Plugin rule (`rules/tk-for-tracking-issues.md`): listing format documentation
