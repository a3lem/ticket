## 1. Spec & Design

- [x] Write proposal
- [x] Write spec delta (listing-format capability)
- [x] Write design document
- [ ] Run spec-critic

## 2. Implement format change

- [ ] Update `plugins/ticket-ls` emit function (tf-55on)
- [ ] Update `cmd_ready` printf in core script (tf-3f71)
- [ ] Update `cmd_blocked` printf in core script (tf-fdxf)
- [ ] Update `cmd_closed` sprintf in core script (tf-mqc2)

## 3. Update tests

- [ ] Update `ticket_listing.feature` format assertions (tf-3012)

## 4. Update documentation

- [ ] Update CHANGELOG.md
- [ ] Update ticket-ls plugin version to 1.2.0
- [ ] Update `tk-for-tracking-issues.md` in plugin marketplace (external repo, read-only from sandbox)

## 5. Verification

- [ ] Tests for requirement: unified-line-grammar
- [ ] Tests for requirement: default-priority-suppression
- [ ] Tests for requirement: closed-ticket-status-display
- [ ] Tests for requirement: command-specific-field-omission

## Notes

Epic: tf-fa18

One outstanding item: `tk-for-tracking-issues.md` in the plugin marketplace (`my-claude-plugins` repo) still references the old `<-` format. That repo is read-only from the sandbox. Update it separately.
