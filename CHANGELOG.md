# Fork Changelog

## 2026-03-22

### Added
- `close --reason` flag to distinguish completed vs rejected tickets (defaults to `completed`)
- `close_reason` YAML field written on close, cleared on reopen
- `closed --completed` and `closed --rejected` filters
- `ticket-list` plugin supports `--status=closed:rejected` and `--status=closed:completed` filters
- Closed tickets display `[completed]` or `[rejected]` instead of `[closed]` in listings
- ticket-list 1.1.0: close_reason display and filtering
