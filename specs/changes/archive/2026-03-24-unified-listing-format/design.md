## Context

Four listing commands produce output in different formats:

| Command | Format | Location | Type |
|---------|--------|----------|------|
| `ls` | `ID [status] - title <- [deps]` | `plugins/ticket-ls:59` | plugin |
| `ready` | `ID [Pn][status] - title` | `ticket:776` | builtin |
| `blocked` | `ID [Pn][status] - title <- [blockers]` | `ticket:928` | builtin |
| `closed` | `ID [reason] - title` | `ticket:826` | builtin |

Differences: `ls` and `closed` omit priority. `ls` and `blocked` use `<-` for deps. `closed` shows close reason in place of status. No command shows tags.

## Goals / Non-Goals

**Goals:**
- Single format grammar across all four commands
- Replace ambiguous `<-` with explicit `[blocked-by: ...]`
- Display priority in all commands (hidden when default)
- Display tags in all commands

**Non-Goals:**
- Shared format function between core and plugins (plugin architecture doesn't support it)
- Column-aligned output (variable field presence makes fixed columns impractical)
- Changing the `dep tree` output format

## Decisions

### Use `::` as section delimiter

The format uses `::` to separate the title from surrounding metadata:

```
ID [Pn] [status] :: title :: [blocked-by: dep1, dep2] [tags: t1, t2]
```

`::` was chosen over `-` (appears in titles), `--` (used as en-dash in titles), and `|` (shell pipe association). `::` has no shell or natural-language baggage.

**Alternatives considered:**
- `|` pipe -- cognitive friction in terminal context
- `--` double dash -- collides with en-dash convention in titles
- Two-space gap -- not a reliable split point for programmatic parsing

### Metadata placement: structured fields before title, optional fields after

ID, priority, and status come before `::`. These are always present (or deliberately hidden) and form the "address" of the ticket. Blocked-by and tags come after the title's closing `::`, because they're optional and variable-length.

This means the title is always in the same position (after the first `::`), readable to humans, while trailing metadata can be scanned or ignored.

### Hide default priority

Priority 2 is the default. Showing `[P2]` on every ticket adds noise without information. Only non-default priorities (`[P0]`, `[P1]`, `[P3]`, `[P4]`) are rendered.

This changes the current `ready` and `blocked` behavior which always show `[Pn]`.

### Use `[blocked-by: ...]` instead of `<-`

Aligns with Claude's built-in task management vocabulary (`addBlockedBy`, `addBlocks`). Unambiguous direction. The `[key: values]` pattern is reused for tags, giving a consistent optional-metadata grammar.

### One format string per command, no shared abstraction

The plugin system runs plugins as standalone executables. There's no mechanism for a plugin to import a function from the core script. Each of the four locations will have its own printf/sprintf implementing the same format by convention.

This means format changes require updating four places. Acceptable given the format should be stable once established.

## Changes by Location

### `plugins/ticket-ls` (line 57-59)

Currently:
```awk
dep_str = (deps_display != "[]") ? " <- " deps_display : ""
printf "%-8s [%s] - %s%s\n", id, display_status, title, dep_str
```

Needs:
- Read `priority` field (already parsed but unused in output)
- Read `tags` field (already parsed for filtering)
- Build priority string: `[P<n>]` when != 2, empty otherwise
- Build blocked-by string: `[blocked-by: dep1, dep2]` when deps exist
- Build tags string: `[tags: t1, t2]` when tags exist
- Build trailing metadata: concatenation of blocked-by + tags, prefixed with ` :: ` if non-empty
- New printf: `printf "%s %s[%s] :: %s%s\n", id, pri_str, display_status, title, trail_str`

Note: drops the `%-8s` fixed-width ID field since `::` delimiters make column alignment unnecessary.

### `ticket:776` (`cmd_ready`)

Currently:
```awk
output[++count] = sprintf("%s|%s|%s|%s", priorities[id], id, status, titles[id])
...
printf "%-8s [P%s][%s] - %s\n", f[2], f[1], f[3], f[4]
```

Needs:
- Add `all_tags[id]` to the pipe-delimited output string
- Conditional priority: omit `[P2]`, show others
- Build tags trailing string
- No blocked-by (ready tickets have all deps resolved)
- New printf pattern with `::` delimiters

### `ticket:826` (`cmd_closed`)

Currently:
```awk
output[++count] = sprintf("%-8s [%s] - %s", id, display_reason, title)
```

Needs:
- Read `priority` field (not currently parsed in this awk block)
- Read `tags` field (already parsed for filtering)
- Conditional priority string
- Build tags trailing string
- No blocked-by (closed tickets don't show deps)
- New sprintf with `::` delimiters

### `ticket:928` (`cmd_blocked`)

Currently:
```awk
output[++count] = sprintf("%s|%s|%s|%s|[%s]", priorities[id], id, status, titles[id], blockers)
...
printf "%-8s [P%s][%s] - %s <- %s\n", f[2], f[1], f[3], f[4], f[5]
```

Needs:
- Add `all_tags[id]` to pipe-delimited output string
- Conditional priority
- Replace `<- %s` with `[blocked-by: ...]` in trailing metadata
- Build tags trailing string
- New printf with `::` delimiters

## Test Impact

Tests that match exact output format will break. Affected scenarios:

| Feature file | Scenario | Current assertion | Change needed |
|---|---|---|---|
| `ticket_listing.feature:27` | List shows ticket format correctly | `list-0001\s+\[open\]\s+-\s+My ticket` | Match `::` delimiter |
| `ticket_listing.feature:72` | List shows dependencies | `<- [list-0002]` | Match `[blocked-by: list-0002]` |
| `ticket_listing.feature:118` | Ready shows priority in output | `\[P2\]\[open\]\s+-\s+` | P2 now hidden; match `[open] ::` |
| `ticket_listing.feature:137` | Blocked shows tickets with unclosed deps | `<- [block-002]` | Match `[blocked-by: block-002]` |
| `ticket_listing.feature:166-167` | Blocked shows only unclosed blockers | `<- [block-002]` | Match `[blocked-by: block-002]` |

Tests that only check `output should contain "ID"` or `output should contain "title"` are unaffected.

## Risks / Trade-offs / Limitations

- **Four-place update** → Risk of format drift between commands. Mitigated by tests covering all four commands' output format.
- **Breaking change** → Any downstream scripts parsing `<-` will break. The `tk-for-tracking-issues.md` rule file documents the listing format and must be updated.
- **Fixed-width ID dropped** → Output won't column-align IDs when they vary in length. Acceptable since `::` provides visual structure instead.
