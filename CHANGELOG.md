# Fork Changelog

## 2026-03-24

### Changed
- Listing format overhaul across `ls`, `ready`, `blocked`, `closed`:
  - Checkbox status indicators: `[ ]` open, `[/]` in progress, `[x]` completed, `[~]` rejected
  - Type and priority shown inline (e.g. `[epic] [P0]`), omitted for defaults (task, P2)
  - Hierarchical tree rendering with box-drawing characters (├──, └──); parent tickets shown as context headings when children match a filter
  - `--flat` flag to disable tree rendering on all listing commands

### Added
- Parent close guard: a ticket cannot be closed unless all its descendants are closed or rejected (transitive — includes grandchildren and deeper)
- Guard applies to both `close` and `status <id> closed` commands

### Plugins
- ticket-ls 1.3.0: checkbox status, type/priority display, tree rendering, `--flat` flag

## 2026-03-22

### Added
- `close --reason` flag to distinguish completed vs rejected tickets (defaults to `completed`)
- `close_reason` YAML field written on close, cleared on reopen
- `closed --completed` and `closed --rejected` filters
- `ticket-list` plugin supports `--status=closed:rejected` and `--status=closed:completed` filters
- Closed tickets display `[completed]` or `[rejected]` instead of `[closed]` in listings
- ticket-list 1.1.0: close_reason display and filtering

## 2026-03-11

### Added
- Fish shell completions for all commands and flags
