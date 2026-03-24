## 1. Plugin: checkbox format in ticket-ls

- [x] Add status-to-checkbox mapping in `format_line()`
- [x] Reorder format string: `<id> [type?][prio?] - [checkbox] <title> [<- deps?]`

## 2. Core: checkbox format in ready/blocked

- [x] Add type parsing to `cmd_ready()` and `cmd_blocked()` awk blocks
- [x] Add status-to-checkbox mapping to `cmd_ready()` print_tree
- [x] Add status-to-checkbox mapping to `cmd_blocked()` print_tree
- [x] Update flat-mode format strings in both commands

## 3. Core: checkbox format in closed

- [x] Change `cmd_closed()` display from `[completed]`/`[rejected]` to `[x]`/`[~]`
- [x] Add type/priority display to `cmd_closed()`

## 4. Verification

- [x] Update existing listing tests for new format
- [x] Add tests for checkbox status rendering
- [x] Add tests for type/priority display in ready/blocked/closed
