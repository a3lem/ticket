# Listing Format

## ADDED Requirements

### Requirement: Unified line grammar
All listing commands (`ls`, `ready`, `blocked`, `closed`) SHALL render each ticket as a single line following this grammar:

```
ID [Pn][status] :: title :: [blocked-by: dep1, dep2] [tags: t1, t2]
```

The `::` delimiter separates the title from surrounding metadata. Metadata fields after the title are optional and omitted when empty.

#### Scenario: Ticket with dependencies and tags
- **GIVEN** a ticket `env-90ef` with status `open`, priority `1`, deps `[env-r3hf, env-ed27]`, and tags `[transplanting, care]`
- **WHEN** the ticket appears in any listing command
- **THEN** the output line is `env-90ef [P1][open] :: Set plant in new pot :: [blocked-by: env-r3hf, env-ed27] [tags: transplanting, care]`

#### Scenario: Ticket with no dependencies or tags
- **GIVEN** a ticket `env-quy6` with status `open`, priority `2`, no deps, no tags
- **WHEN** the ticket appears in any listing command
- **THEN** the output line is `env-quy6 [open] :: Assess if plant needs repotting`
- **AND** there is no trailing `::` delimiter

#### Scenario: Ticket with deps but no tags
- **GIVEN** a ticket with deps `[env-b0wz]` and no tags
- **WHEN** the ticket appears in any listing command
- **THEN** the output line ends with `:: [blocked-by: env-b0wz]`

#### Scenario: Ticket with tags but no deps
- **GIVEN** a ticket with no deps and tags `[api, urgent]`
- **WHEN** the ticket appears in any listing command
- **THEN** the output line ends with `:: [tags: api, urgent]`

### Requirement: Default priority suppression
The system SHALL omit the priority field when it equals the default value (2).

#### Scenario: Default priority hidden
- **GIVEN** a ticket with priority `2`
- **WHEN** the ticket appears in any listing command
- **THEN** the line starts with `ID [status]` (no `[P2]`)

#### Scenario: Non-default priority shown
- **GIVEN** a ticket with priority `0`
- **WHEN** the ticket appears in any listing command
- **THEN** the line starts with `ID [P0][status]`

### Requirement: Closed ticket status display
The `closed` command and `ls --status=closed` SHALL display the close reason in place of the status field.

#### Scenario: Completed ticket
- **GIVEN** a closed ticket with close_reason `completed` (or no close_reason set)
- **WHEN** the ticket appears in `closed` or `ls --status=closed`
- **THEN** the status field reads `[completed]`

#### Scenario: Rejected ticket
- **GIVEN** a closed ticket with close_reason `rejected`
- **WHEN** the ticket appears in `closed` or `ls --status=closed`
- **THEN** the status field reads `[rejected]`

### Requirement: Command-specific field omission
Each listing command SHALL omit fields that are irrelevant to its purpose.

#### Scenario: ready omits blocked-by
- **WHEN** `tk ready` renders a ticket
- **THEN** the `[blocked-by: ...]` field is never present (all deps are resolved by definition)

#### Scenario: blocked always shows blocked-by
- **WHEN** `tk blocked` renders a ticket
- **THEN** the `[blocked-by: ...]` field is always present (listing only includes tickets with unresolved deps)

#### Scenario: closed omits blocked-by
- **WHEN** `tk closed` renders a ticket
- **THEN** the `[blocked-by: ...]` field is never present

#### Scenario: ls shows all applicable fields
- **WHEN** `tk ls` renders a ticket
- **THEN** all non-empty fields are shown, including `[blocked-by: ...]` when deps exist
