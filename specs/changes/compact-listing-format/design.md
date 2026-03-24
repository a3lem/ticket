## Context

Four places render listing lines: `plugins/ticket-ls` (`format_line()`), `cmd_ready()`, `cmd_blocked()`, and `cmd_closed()` in the core script. Each has its own printf format string.

The recent `ticket-ls` v1.3.0 changes already parse `type` and `priority` and conditionally display them. The core commands (`ready`, `blocked`) show `[P<n>][status]` but don't show type. `closed` shows `[completed]`/`[rejected]` as words.

## Decisions

### Status mapping

| Internal state | Checkbox |
|---------------|----------|
| `open` | `[ ]` |
| `in_progress` | `[/]` |
| `closed` + completed | `[x]` |
| `closed` + rejected | `[~]` |

### Format string

All commands use the same line structure:

```
%s%s - %s %s%s
 │  │    │  │ └─ dep_str (" <- [dep1, dep2]" or "")
 │  │    │  └─── title
 │  │    └────── checkbox
 │  └─────────── meta_str ("[type][Pn] " or "[type] " or "[Pn] " or "")
 └────────────── id
```

With tree indent prepended.

### Add type/priority to ready and blocked

Currently `ready` and `blocked` show `[P<n>][status]` but not type. Align them with `ls` by adding type display and switching to the shared format. Priority display changes from always-shown `[P<n>]` to hidden-when-P2.

### closed keeps word-based filtering, changes display

`tk closed --rejected` and `tk closed --completed` filter by close_reason. The display changes from `[completed]`/`[rejected]` to `[x]`/`[~]`, but the filtering flags remain unchanged.

## Risks / Trade-offs / Limitations

**Breaking change for scripts** → Any tool parsing `[open]`, `[in_progress]`, `[completed]`, `[rejected]` from listing output breaks. `--flat` does not help since the format change applies regardless. Acceptable given the tool's audience (primarily AI agents, which adapt immediately).

**Ambiguity of `[x]` and `[~]` in closed listing** → `tk closed` previously told you *why* a ticket was closed. Now you need to know the notation. The `--completed` and `--rejected` filter flags remain as the explicit way to separate them.
