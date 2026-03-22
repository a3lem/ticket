# ticket (forked)

## This fork

This is my personal fork of Greg Wedow's [*ticket* (`tk`)](https://github.com/wedow/ticket), a CLI-based issue tracker for AI agents, where issues/tasks are called 'tickets'.

There are several relatively popular CLIs for issue tracking that are designed specially for AI agents. In case you're new to the idea of -- basically, instead of using your agent's builtin `Todo*/Task*` tools for task management, you give it a CLI for creating and managing issues. The main advantages are that issues/tasks persist across sessions, can be kept under version control, and can be understood by different agent harnesses.

`tk` gets a lot right, as I argue in this [discussion thread](https://github.com/wedow/ticket/discussions/51).

- Tickets are stored as plain markdown files with YAML fontmatter stored in `.tickets/` (similar to [*beans*](https://github.com/hmans/beans))
- The core is simple. It's a single bash file with a lot of awk. My bash isn't great, not to speak of awk. But I can reason about how it works.
- Every CLI feature is verified by one or more behavioral tests.
- Easy to extend with plugins. In fact, that's how I started out, until I noticed I needed a few changes in the core.
- In my tests, Claude Code spent 86% fewer tokens on task management with `tk` than with the most-starred option, Steve Yegge's [*beads*](https://github.com/steveyegge/beads).

## Differences with upstream

Check out the [changelog](./CHANGELOG.md)

### Highlights

- `close --reason rejected` to distinguish completed from rejected tickets
- Fish shell completions

## "I want to use this too"

I'm maintaining this fork for myself. With every change, I ask myself if I can't achieve the same result with a 'plugin' instead. That way, I hope to keep changes with respect to the upstream to a minimum, so that I can merge my changes in, but only after extensive dogfooding.

### Requirements

`tk` is a portable bash script requiring only coreutils, so it works out of the box on any POSIX system with bash installed. The `query` command requires `jq`. Uses `rg` (ripgrep) if available, falls back to `grep`.


### Install

To install, just clone the repo and (assuming you've got [`just`](https://github.com/casey/just) installed) run `just install`.

### Agent Setup

#### Claude Code

I use the *ticket* plugin in my [personal plugin marketplace](https://github.com/a3lem/my-claude-plugins/tree/main/plugins/ticket-cli). Used to be that it contributed a SKILL.md. Noticing that Claude sometimes ignores skills, I turned it into a rule that gets injected into the system prompt by a hook upon starting a session or after clearing it.

#### Future

On my backlog is a new `tk agent setup --claude` command, which will handle generating and installing skills/hooks into the project director.

### Alternative

Add this line to your `CLAUDE.md` or `AGENTS.md`:

```
This project uses a CLI ticket system for task management. Run `tk help` when you need to use it.
```

Claude Opus picks it up naturally from there. Other models may need additional guidance.

## CLI Reference

```bash
tk - minimal ticket system with dependency tracking

Usage: tk <command> [args]

Commands:
  create [title] [options] Create ticket, prints ID
    -d, --description      Description text
    --design               Design notes
    --acceptance           Acceptance criteria
    -t, --type             Type (bug|feature|task|epic|chore) [default: task]
    -p, --priority         Priority 0-4, 0=highest [default: 2]
    -a, --assignee         Assignee [default: git user.name]
    --external-ref         External reference (e.g., gh-123, JIRA-456)
    --parent               Parent ticket ID
    --tags                 Comma-separated tags (e.g., --tags ui,backend,urgent)
  start <id>               Set status to in_progress
  close <id> [--reason R]   Close ticket (reason: completed|rejected) [default: completed]
  reopen <id>              Reopen ticket (clears close reason)
  status <id> <status>     Update status (open|in_progress|closed)
  dep <id> <dep-id>        Add dependency (id depends on dep-id)
  dep tree [--full] <id>   Show dependency tree (--full disables dedup)
  dep cycle                Find dependency cycles in open tickets
  undep <id> <dep-id>      Remove dependency
  link <id> <id> [id...]   Link tickets together (symmetric)
  unlink <id> <target-id>  Remove link between tickets
  ls|list [--status=X] [-a X] [-T X]   List tickets
  ready [-a X] [-T X]      List open/in-progress tickets with deps resolved
  blocked [-a X] [-T X]    List open/in-progress tickets with unresolved deps
  closed [--limit=N] [-a X] [-T X] [--completed] [--rejected]
                           List recently closed tickets (default 20, by mtime)
  show <id>                Display ticket
  add-note <id> [text]     Append timestamped note (or pipe via stdin)
  super <cmd> [args]       Bypass plugins, run built-in command directly

Bundled plugins (ticket-extras):
  edit <id>                Open ticket in $EDITOR
  ls|list [--status=X] [-a X] [-T X]   List tickets
  query [jq-filter]        Output tickets as JSON, optionally filtered (requires jq)
  migrate-beads            Import tickets from .beads/issues.jsonl (requires jq)

Searches parent directories for .tickets/ (override with TICKETS_DIR env var)
Supports partial ID matching (e.g., 'tk show 5c4' matches 'nw-5c46')
```

> [!NOTE]
> Everything after this point is kept as-is from the upstream README

## Plugins

Executables named `tk-<cmd>` or `ticket-<cmd>` in your PATH are invoked automatically. This allows you to add custom commands or override built-in ones.

```bash
# Create a simple plugin
cat > ~/.local/bin/tk-hello <<'EOF'
#!/bin/bash
# tk-plugin: Say hello
echo "Hello from plugin!"
EOF
chmod +x ~/.local/bin/tk-hello

# Now it's available
tk hello        # runs tk-hello
tk help         # lists it under "Plugins"
```

**Plugin descriptions** (shown in `tk help`):
- Scripts: comment `# tk-plugin: description` in first 10 lines
- Binaries: `--tk-describe` flag outputs `tk-plugin: description`

**Plugin environment variables:**
- `TICKETS_DIR` - path to the .tickets directory (may be empty)
- `TK_SCRIPT` - absolute path to the tk script

**Calling built-ins from plugins:**
```bash
#!/bin/bash
# tk-plugin: Custom create with extras
id=$("$TK_SCRIPT" super create "$@")
echo "Created $id, doing extra stuff..."
```

Use `tk super <cmd>` to bypass plugins and run the built-in directly.

## Testing

The tests are written in the Behavior-Driven Development library [behave](https://behave.readthedocs.io/en/latest/) and require Python.

If you have `uv` [installed](https://docs.astral.sh/uv/getting-started/installation/) simply:

```sh
make test
```

## Migrating from Beads

```bash
tk migrate-beads

# review new files if you like
git status

# check state matches expectations
tk ready
tk blocked

# compare against
bd ready
bd blocked

# all good, let's go
git rm -rf .beads
git add .tickets
git commit -am "ditch beads"
```

For a thorough system-wide Beads cleanup, see [banteg's uninstall script](https://gist.github.com/banteg/1a539b88b3c8945cd71e4b958f319d8d).

## License

MIT
