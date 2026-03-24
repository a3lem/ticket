## Why

Ticket status currently displays as words (`[open]`, `[in_progress]`, `[completed]`, `[rejected]`) which vary in width and dominate the line visually. Replacing status with single-character checkboxes (`[ ]`, `[/]`, `[x]`, `[~]`) makes listings more compact and scannable, borrowing a notation familiar from markdown task lists.

The previous attempt at reformatting (unified-listing-format, rejected) failed because it added verbosity. This change reduces it.

## What Changes

- Status display changes from word labels to checkbox notation in all listing commands
- `[ ]` = open, `[/]` = in_progress, `[x]` = closed/completed, `[~]` = closed/rejected
- Checkbox moves from the metadata side to the title side of the `-` separator
- Format becomes: `<id> [type?][prio?] - [status] <title> [<- deps?]`
- Type hidden when `task`, priority hidden when P2 (already implemented)
- Applies to `tk ls`, `tk ready`, `tk blocked`, `tk closed`

## Capabilities

### Modified Capabilities

- `hierarchical-listing`: Status rendering and field ordering change across all listing commands

## Impact

- Plugin (`plugins/ticket-ls`): `format_line()` function
- Core script (`ticket`): `cmd_ready()`, `cmd_blocked()`, `cmd_closed()` printf format strings
- Behave tests: all assertions matching listing output format
- Plugin rule (`rules/tk-for-tracking-issues.md`): listing format documentation
