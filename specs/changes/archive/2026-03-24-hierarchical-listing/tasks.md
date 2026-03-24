## 1. Core awk: parse parent field

- [x] Add `parent` field parsing to `cmd_ready()` awk block
- [x] Add `parent` field parsing to `cmd_blocked()` awk block
- [x] Store `parents[id]` in all core listing commands

## 2. Core awk: tree rendering in ready/blocked

- [x] Implement two-pass output in `cmd_ready()`: filter → ancestor marking → DFS print
- [x] Implement two-pass output in `cmd_blocked()`: filter → ancestor marking → DFS print
- [x] Add `--flat` flag to `cmd_ready()` and `cmd_blocked()`

## 3. Plugin: tree rendering in ticket-ls

- [x] Add `parent` field parsing to `plugins/ticket-ls` awk block
- [x] Implement two-pass tree output in plugin
- [x] Add `--flat` flag to plugin argument parser

## 4. Verification

- [x] Tests for requirement: Tree rendering in listings
- [x] Tests for requirement: Flat listing mode
- [x] Tests for requirement: Tree rendering in ready and blocked
- [x] Tests for requirement: Parent visibility in filtered views

## Notes

- `cmd_closed()` stays flat (per design)
- Tree rendering logic is identical across core and plugin; duplication is acceptable given awk's lack of module system
