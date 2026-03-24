## Why

In a monorepo, sub-projects have distinct concerns but share a single `.tickets/` directory. All tickets end up in one pool, with only ID prefixes hinting at which project they belong to. This contrasts with spexl, where each sub-project has its own `specs/` directory.

Per-project `.tickets/` directories give tickets a natural home. An aggregated view from the repo root shows the full picture when needed.

## What Changes

- `find_tickets_dir()` gains a recursive mode that walks down from the repo root to discover all `.tickets/` directories
- `--all` flag triggers multi-root aggregation
- `--project` flag filters by project path substring
- Listing commands group output by project root when multiple roots are active
- `ticket_path()` resolves IDs across all discovered roots in `--all` mode
- Cross-root deps and links resolve correctly
- `TICKETS_DIR` override bypasses all discovery, `--all` is ignored when set

## Capabilities

### New Capabilities

- `multi-root-discovery`: Discovering and aggregating multiple `.tickets/` directories across a monorepo

### Modified Capabilities

_None. There are no existing reference specs._

## Impact

- Core script (`ticket`): `find_tickets_dir()`, `init_tickets_dir()`, `ticket_path()`, all listing commands
- Plugin (`plugins/ticket-ls`): multi-root glob and project header rendering
- Cross-root references: deps/links referencing ticket IDs in other roots must resolve
- Behave tests: new scenarios for multi-root discovery, project filtering, cross-root resolution
