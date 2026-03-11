# Fish completions for tk (ticket)

# Helper: list ticket IDs from .tickets/ directory
function __tk_ticket_ids
    set -l dir
    if test -n "$TICKETS_DIR"
        set dir $TICKETS_DIR
    else
        set dir (pwd)
        while test "$dir" != /
            if test -d "$dir/.tickets"
                set dir "$dir/.tickets"
                break
            end
            set dir (string replace -r '/[^/]*$' '' $dir)
        end
    end
    test -d "$dir" || return
    for f in $dir/*.md
        string replace -r '.*/(.*)\.md$' '$1' -- $f
    end
end

# Helper: discover plugin commands (tk-* and ticket-* in PATH)
function __tk_plugin_commands
    set -l seen
    for prefix in tk ticket
        for p in (complete -C "$prefix-" 2>/dev/null | string match -r "^$prefix-\S+")
            set -l cmd (string replace "$prefix-" '' $p)
            if not contains -- $cmd $seen
                set -a seen $cmd
                # Try to extract description
                set -l path (command -v "$prefix-$cmd" 2>/dev/null)
                if test -n "$path" -a -f "$path"
                    set -l desc (head -10 $path 2>/dev/null | string match -r '# tk-plugin: (.*)' | tail -1)
                    if test -n "$desc"
                        printf '%s\t%s\n' $cmd $desc
                    else
                        printf '%s\t%s\n' $cmd plugin
                    end
                end
            end
        end
    end
end

# Condition: no subcommand yet
function __tk_needs_command
    set -l cmd (commandline -opc)
    # Skip past 'super' if present
    if test (count $cmd) -ge 2 -a "$cmd[2]" = super
        test (count $cmd) -lt 3
        return
    end
    test (count $cmd) -lt 2
end

# Condition: current subcommand is $argv[1]
function __tk_using_command
    set -l cmd (commandline -opc)
    set -l start 2
    if test (count $cmd) -ge 2 -a "$cmd[2]" = super
        set start 3
    end
    test (count $cmd) -ge $start -a "$cmd[$start]" = $argv[1]
end

# Condition: dep subcommand tree/cycle
function __tk_dep_sub
    set -l cmd (commandline -opc)
    set -l start 2
    if test (count $cmd) -ge 2 -a "$cmd[2]" = super
        set start 3
    end
    set -l next (math $start + 1)
    test (count $cmd) -ge $next -a "$cmd[$start]" = dep -a "$cmd[$next]" = $argv[1]
end

# Disable file completions for tk
complete -c tk -f

# Top-level commands
complete -c tk -n __tk_needs_command -a create  -d 'Create ticket'
complete -c tk -n __tk_needs_command -a start   -d 'Set status to in_progress'
complete -c tk -n __tk_needs_command -a close   -d 'Set status to closed'
complete -c tk -n __tk_needs_command -a reopen  -d 'Set status to open'
complete -c tk -n __tk_needs_command -a status  -d 'Update status'
complete -c tk -n __tk_needs_command -a dep     -d 'Manage dependencies'
complete -c tk -n __tk_needs_command -a undep   -d 'Remove dependency'
complete -c tk -n __tk_needs_command -a link    -d 'Link tickets together'
complete -c tk -n __tk_needs_command -a unlink  -d 'Remove link between tickets'
complete -c tk -n __tk_needs_command -a ready   -d 'List tickets with deps resolved'
complete -c tk -n __tk_needs_command -a blocked -d 'List tickets with unresolved deps'
complete -c tk -n __tk_needs_command -a closed  -d 'List recently closed tickets'
complete -c tk -n __tk_needs_command -a show    -d 'Display ticket'
complete -c tk -n __tk_needs_command -a add-note -d 'Append timestamped note'
complete -c tk -n __tk_needs_command -a super   -d 'Bypass plugins, run built-in'
complete -c tk -n __tk_needs_command -a help    -d 'Show help'
# Also complete ls/list (typically provided by plugin)
complete -c tk -n __tk_needs_command -a ls      -d 'List tickets'
complete -c tk -n __tk_needs_command -a list    -d 'List tickets'

# Plugin commands (dynamic)
complete -c tk -n __tk_needs_command -a '(__tk_plugin_commands)'

# -- create --
complete -c tk -n '__tk_using_command create' -s d -l description -d 'Description text'
complete -c tk -n '__tk_using_command create' -l design -d 'Design notes'
complete -c tk -n '__tk_using_command create' -l acceptance -d 'Acceptance criteria'
complete -c tk -n '__tk_using_command create' -s t -l type -d 'Ticket type' -r -a 'bug feature task epic chore'
complete -c tk -n '__tk_using_command create' -s p -l priority -d 'Priority 0-4' -r -a '0 1 2 3 4'
complete -c tk -n '__tk_using_command create' -s a -l assignee -d 'Assignee' -r
complete -c tk -n '__tk_using_command create' -l external-ref -d 'External reference' -r
complete -c tk -n '__tk_using_command create' -l parent -d 'Parent ticket ID' -r -a '(__tk_ticket_ids)'
complete -c tk -n '__tk_using_command create' -l tags -d 'Comma-separated tags' -r

# -- Commands that take a ticket ID --
for subcmd in start close reopen show add-note
    complete -c tk -n "__tk_using_command $subcmd" -a '(__tk_ticket_ids)'
end

# -- status <id> <status> --
complete -c tk -n '__tk_using_command status' -a '(__tk_ticket_ids)'
complete -c tk -n '__tk_using_command status' -a 'open in_progress closed'

# -- dep subcommands --
complete -c tk -n '__tk_using_command dep' -a tree  -d 'Show dependency tree'
complete -c tk -n '__tk_using_command dep' -a cycle -d 'Find dependency cycles'
complete -c tk -n '__tk_using_command dep' -a '(__tk_ticket_ids)'
complete -c tk -n '__tk_dep_sub tree' -l full -d 'Disable dedup in tree'
complete -c tk -n '__tk_dep_sub tree' -a '(__tk_ticket_ids)'

# -- undep / link / unlink take ticket IDs --
for subcmd in undep link unlink
    complete -c tk -n "__tk_using_command $subcmd" -a '(__tk_ticket_ids)'
end

# -- Shared filter flags for listing commands --
for subcmd in ls list ready blocked closed
    complete -c tk -n "__tk_using_command $subcmd" -s a -d 'Filter by assignee' -r
    complete -c tk -n "__tk_using_command $subcmd" -l assignee -d 'Filter by assignee' -r
    complete -c tk -n "__tk_using_command $subcmd" -s T -d 'Filter by tag' -r
    complete -c tk -n "__tk_using_command $subcmd" -l tag -d 'Filter by tag' -r
end

# -- ls/list specific --
complete -c tk -n '__tk_using_command ls'   -l status -d 'Filter by status' -r -a 'open in_progress closed'
complete -c tk -n '__tk_using_command list' -l status -d 'Filter by status' -r -a 'open in_progress closed'

# -- closed specific --
complete -c tk -n '__tk_using_command closed' -l limit -d 'Max results' -r

# -- super: complete with built-in commands --
complete -c tk -n '__fish_seen_subcommand_from super; and test (count (commandline -opc)) -lt 3' \
    -a 'create start close reopen status dep undep link unlink ready blocked closed show add-note help'
