## ADDED Requirements

### Requirement: Single-root discovery (walk up)
When invoked from within a sub-project, the system SHALL walk up parent directories to find the nearest `.tickets/` directory, consistent with current behavior.

#### Scenario: Run tk from sub-project directory
- **GIVEN** a monorepo with `libs/kls-agent-core/.tickets/` and `apps/gateway/.tickets/`
- **WHEN** the user runs `tk ls` from `libs/kls-agent-core/src/`
- **THEN** only tickets from `libs/kls-agent-core/.tickets/` are listed

### Requirement: Multi-root discovery (walk down)
When invoked with `--all`, the system SHALL discover all `.tickets/` directories by walking down from the repository root.

#### Scenario: Aggregate all ticket roots
- **GIVEN** a monorepo with `.tickets/` directories in `libs/kls-agent-core/`, `libs/kls-tasks/`, and `apps/gateway/`
- **WHEN** the user runs `tk ls --all`
- **THEN** tickets from all three roots are listed, grouped by project path

#### Scenario: Repository root detection
- **WHEN** the system resolves the repository root for multi-root discovery
- **THEN** it uses the git root (`git rev-parse --show-toplevel`) if available
- **AND** falls back to the filesystem root if not in a git repository

### Requirement: Project filtering
The system SHALL support filtering by project path when multiple roots are discovered.

#### Scenario: Filter by project
- **GIVEN** a monorepo with multiple `.tickets/` directories
- **WHEN** the user runs `tk ls --all --project kls-agent-core`
- **THEN** only tickets from roots whose path contains `kls-agent-core` are listed

### Requirement: Cross-root ID resolution
The system SHALL resolve ticket IDs across all discovered roots when using `--all` mode.

#### Scenario: Show ticket from another root
- **GIVEN** multi-root mode is active
- **WHEN** the user runs `tk show kap-3ny` and that ticket exists in `libs/kls-agent-core/.tickets/`
- **THEN** the ticket is displayed regardless of the user's current directory

#### Scenario: Ambiguous ID across roots
- **GIVEN** two roots each contain a ticket whose ID partially matches the input
- **WHEN** the user runs `tk show abc`
- **THEN** the system reports the ambiguity with full paths to each match

### Requirement: Cross-root deps and links
Dependencies and links SHALL resolve across ticket roots. A ticket in one root MAY reference a ticket ID in another root.

#### Scenario: Dependency across roots
- **GIVEN** ticket `gw-bqa` in `apps/gateway/.tickets/` has `deps: [kap-nm1]`
- **AND** ticket `kap-nm1` exists in `libs/kls-agent-core/.tickets/`
- **WHEN** the user runs `tk ready --all`
- **THEN** `gw-bqa` appears as blocked if `kap-nm1` is not closed

### Requirement: TICKETS_DIR override
When `TICKETS_DIR` is set explicitly, the system SHALL use only that directory, bypassing both walk-up and walk-down discovery. `--all` SHALL be ignored.

#### Scenario: Explicit TICKETS_DIR with --all
- **GIVEN** `TICKETS_DIR` is set to `/tmp/my-tickets`
- **WHEN** the user runs `tk ls --all`
- **THEN** only tickets from `/tmp/my-tickets` are listed

### Requirement: Create in nearest root
`tk create` without `--all` SHALL create tickets in the nearest `.tickets/` directory (walk-up), initializing one in the current directory if none is found.

#### Scenario: Create ticket in sub-project
- **GIVEN** the user is in `libs/kls-agent-core/src/`
- **AND** `libs/kls-agent-core/.tickets/` exists
- **WHEN** the user runs `tk create "Fix parsing bug"`
- **THEN** the ticket is created in `libs/kls-agent-core/.tickets/`
