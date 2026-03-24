## Context

All four listing commands (`ls`, `ready`, `blocked`, `closed`) use awk to parse ticket files in a single pass, collect data in arrays, then sort and print in the END block. None of them currently read the `parent` field.

`ls` lives in a plugin (`plugins/ticket-ls`). `ready`, `blocked`, and `closed` live in the core script. All follow the same pattern: parse frontmatter, store fields in associative arrays keyed by ID, filter in END, sort, print.

The `dep tree` command already implements tree rendering with a stack-based DFS in awk (lines ~460-526), but it traverses dependency edges, not parent-child edges. Its rendering logic (indentation, `├──`/`└──` connectors) is a useful reference but uses box-drawing characters that are heavier than what we want for listings.

## Goals / Non-Goals

**Goals:**
- Tree rendering in `ls`, `ready`, `blocked` based on parent-child relationships
- `--flat` flag for backward-compatible flat output
- Minimal diff to existing awk blocks

**Non-Goals:**
- Multi-root / monorepo support (separate change)
- Changing sort order within a tree level
- `closed` command tree rendering (closed tickets are sorted by mtime, not by logical grouping; parent may still be open)

## Decisions

### Parse parent field in all listing awk blocks

Add `in_front && /^parent:/ { parent = $2 }` to the frontmatter parsing section of each command's awk block. Store in `parents[id]` associative array alongside existing arrays.

### Two-pass output in END block

Current flow: filter → collect in `output[]` → sort → print.

New flow: filter → collect in `matched[id]` → walk ancestry to mark parents as visible → build `children[parent]` adjacency list → DFS print from roots.

1. **Filter pass**: same as current. Instead of appending to `output[]`, set `matched[id] = 1` and store the formatted line in `lines[id]`.
2. **Ancestor marking**: for each matched ticket, walk `parents[id]` up to the root, setting `visible[id] = 1` for each ancestor. This ensures parent headings appear even when they don't match the filter.
3. **Build children list**: for each visible ticket, append to `children[parents[id]]`. Roots (no parent or parent not visible) go into `roots[]`.
4. **Sort roots** by the same criteria as current (priority then ID for `ready`/`blocked`, ID only for `ls`).
5. **DFS print**: recursive function starting from each root. At each node, sort children by the same criteria, then print with `indent` spaces prefix. Increment indent by 2 per level.

### Indentation style: plain spaces, no connectors

2 spaces per nesting level, prepended to the existing format string. No `├──`/`└──` box-drawing characters. The `dep tree` command uses connectors because it renders a dependency DAG where visual edge-tracing matters. Parent-child is a simpler containment hierarchy where indentation suffices.

### `--flat` flag in plugin and core

The plugin (`ticket-ls`) adds `--flat` to its argument parser. When set, it passes `-v flat=1` to awk, which skips the tree logic and uses the current flat output path. Core commands (`ready`, `blocked`) accept `--flat` the same way.

Default behavior changes from flat to tree. `--flat` is the escape hatch.

### Plugin gets tree logic too

`ticket-ls` needs the same two-pass approach. It currently doesn't parse `parent`. Adding the parent parse and tree rendering to the plugin's awk block keeps behavior consistent between `tk ls` (plugin) and `tk ready`/`tk blocked` (core).

### `closed` stays flat

`tk closed` sorts by file mtime and limits output. Tree rendering doesn't apply well here: the parent ticket may still be open, and the mtime order would conflict with grouping. `closed` remains flat.

## Risks / Trade-offs / Limitations

**Performance** → The ancestor-marking walk is O(n × depth) in the worst case. For typical ticket sets (< 200 tickets, depth < 5), this is negligible. The awk blocks already do O(n²) insertion sorts.

**Sorting within tree** → Children are sorted by the same criteria as roots. This means priority ordering is preserved within each parent group. If a high-priority child is under a low-priority parent, the parent still appears where its own priority dictates. This is correct -- you want to see the parent in its natural position, not promoted by its children.

**`--flat` as default break** → Changing the default from flat to tree is a breaking change for scripts parsing `tk ls` output. Mitigated by `--flat` flag and by the fact that the line format itself doesn't change (only leading whitespace is added).
