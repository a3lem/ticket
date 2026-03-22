"""Step definitions for ticket CLI BDD tests."""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from behave import given, when, then, register_type, use_step_matcher
import parse


# Use regex matcher for more flexible step definitions
use_step_matcher("re")


# ============================================================================
# Helper Functions
# ============================================================================

def get_ticket_script(context):
    """Get the ticket script path, defaulting to ./ticket or using TICKET_SCRIPT env var."""
    ticket_script = os.environ.get('TICKET_SCRIPT')
    if ticket_script:
        return ticket_script
    return str(Path(context.project_dir) / 'ticket')


def create_ticket(context, ticket_id, title, priority=2, parent=None):
    """Helper to create a ticket file."""
    tickets_dir = Path(context.test_dir) / '.tickets'
    tickets_dir.mkdir(parents=True, exist_ok=True)

    ticket_path = tickets_dir / f'{ticket_id}.md'
    content = f'''---
id: {ticket_id}
status: open
deps: []
links: []
created: 2024-01-01T00:00:00Z
type: task
priority: {priority}
'''
    if parent:
        content += f'parent: {parent}\n'
    content += f'''---
# {title}

Description
'''
    ticket_path.write_text(content)

    if not hasattr(context, 'tickets'):
        context.tickets = {}
    context.tickets[ticket_id] = ticket_path
    return ticket_path


# ============================================================================
# Given Steps
# ============================================================================

@given(r'a clean tickets directory')
def step_clean_tickets_directory(context):
    """Ensure we start with a clean .tickets directory."""
    tickets_dir = Path(context.test_dir) / '.tickets'
    if tickets_dir.exists():
        import shutil
        shutil.rmtree(tickets_dir)
    tickets_dir.mkdir(parents=True, exist_ok=True)


@given(r'the tickets directory does not exist')
def step_tickets_dir_not_exist(context):
    """Ensure .tickets directory does not exist."""
    tickets_dir = Path(context.test_dir) / '.tickets'
    if tickets_dir.exists():
        import shutil
        shutil.rmtree(tickets_dir)


@given(r'a ticket exists with ID "(?P<ticket_id>[^"]+)" and title "(?P<title>[^"]+)" with priority (?P<priority>\d+)')
def step_ticket_exists_with_priority(context, ticket_id, title, priority):
    """Create a ticket with given ID, title, and priority."""
    create_ticket(context, ticket_id, title, priority=int(priority))


@given(r'a ticket exists with ID "(?P<ticket_id>[^"]+)" and title "(?P<title>[^"]+)" with parent "(?P<parent_id>[^"]+)"')
def step_ticket_exists_with_parent(context, ticket_id, title, parent_id):
    """Create a ticket with given ID, title, and parent."""
    create_ticket(context, ticket_id, title, parent=parent_id)


@given(r'a ticket exists with ID "(?P<ticket_id>[^"]+)" and title "(?P<title>[^"]+)"')
def step_ticket_exists(context, ticket_id, title):
    """Create a ticket with given ID and title (basic, no extra params)."""
    # This is the most generic form - the more specific ones should be defined first
    create_ticket(context, ticket_id, title)


@given(r'ticket "(?P<ticket_id>[^"]+)" has status "(?P<status>[^"]+)"')
def step_ticket_has_status(context, ticket_id, status):
    """Set ticket status."""
    ticket_path = Path(context.test_dir) / '.tickets' / f'{ticket_id}.md'
    content = ticket_path.read_text()
    content = re.sub(r'^status: \w+', f'status: {status}', content, flags=re.MULTILINE)
    ticket_path.write_text(content)


@given(r'ticket "(?P<ticket_id>[^"]+)" has close_reason "(?P<reason>[^"]+)"')
def step_ticket_has_close_reason(context, ticket_id, reason):
    """Set ticket close_reason."""
    ticket_path = Path(context.test_dir) / '.tickets' / f'{ticket_id}.md'
    content = ticket_path.read_text()
    if re.search(r'^close_reason:', content, re.MULTILINE):
        content = re.sub(r'^close_reason: \w+', f'close_reason: {reason}', content, flags=re.MULTILINE)
    else:
        # Insert before closing ---
        content = content.replace('---\n#', f'close_reason: {reason}\n---\n#', 1)
    ticket_path.write_text(content)


@given(r'ticket "(?P<ticket_id>[^"]+)" depends on "(?P<dep_id>[^"]+)"')
def step_ticket_depends_on(context, ticket_id, dep_id):
    """Add dependency to ticket."""
    ticket_path = Path(context.test_dir) / '.tickets' / f'{ticket_id}.md'
    content = ticket_path.read_text()

    # Parse current deps
    deps_match = re.search(r'^deps: \[(.*?)\]', content, re.MULTILINE)
    if deps_match:
        current_deps = deps_match.group(1)
        if current_deps:
            deps_list = [d.strip() for d in current_deps.split(',')]
            if dep_id not in deps_list:
                deps_list.append(dep_id)
        else:
            deps_list = [dep_id]
        new_deps = ', '.join(deps_list)
        content = re.sub(r'^deps: \[.*?\]', f'deps: [{new_deps}]', content, flags=re.MULTILINE)

    ticket_path.write_text(content)


@given(r'ticket "(?P<ticket_id>[^"]+)" is linked to "(?P<link_id>[^"]+)"')
def step_ticket_linked_to(context, ticket_id, link_id):
    """Create bidirectional link between tickets."""
    # Update first ticket
    ticket_path = Path(context.test_dir) / '.tickets' / f'{ticket_id}.md'
    content = ticket_path.read_text()
    links_match = re.search(r'^links: \[(.*?)\]', content, re.MULTILINE)
    if links_match:
        current_links = links_match.group(1)
        if current_links:
            links_list = [l.strip() for l in current_links.split(',')]
            if link_id not in links_list:
                links_list.append(link_id)
        else:
            links_list = [link_id]
        new_links = ', '.join(links_list)
        content = re.sub(r'^links: \[.*?\]', f'links: [{new_links}]', content, flags=re.MULTILINE)
    ticket_path.write_text(content)

    # Update second ticket
    link_path = Path(context.test_dir) / '.tickets' / f'{link_id}.md'
    content = link_path.read_text()
    links_match = re.search(r'^links: \[(.*?)\]', content, re.MULTILINE)
    if links_match:
        current_links = links_match.group(1)
        if current_links:
            links_list = [l.strip() for l in current_links.split(',')]
            if ticket_id not in links_list:
                links_list.append(ticket_id)
        else:
            links_list = [ticket_id]
        new_links = ', '.join(links_list)
        content = re.sub(r'^links: \[.*?\]', f'links: [{new_links}]', content, flags=re.MULTILINE)
    link_path.write_text(content)


@given(r'ticket "(?P<ticket_id>[^"]+)" has a notes section')
def step_ticket_has_notes(context, ticket_id):
    """Ensure ticket has a notes section."""
    ticket_path = Path(context.test_dir) / '.tickets' / f'{ticket_id}.md'
    content = ticket_path.read_text()
    if '## Notes' not in content:
        content += '\n## Notes\n'
        ticket_path.write_text(content)


@given(r'I am in subdirectory "(?P<subdir>[^"]+)"')
def step_in_subdirectory(context, subdir):
    """Change to a subdirectory (creating it if needed)."""
    subdir_path = Path(context.test_dir) / subdir
    subdir_path.mkdir(parents=True, exist_ok=True)
    context.working_dir = str(subdir_path)


@given(r'a separate tickets directory exists at "(?P<dir_path>[^"]+)" with ticket "(?P<ticket_id>[^"]+)" titled "(?P<title>[^"]+)"')
def step_separate_tickets_dir(context, dir_path, ticket_id, title):
    """Create a separate tickets directory with a ticket."""
    tickets_dir = Path(context.test_dir) / dir_path
    tickets_dir.mkdir(parents=True, exist_ok=True)

    ticket_path = tickets_dir / f'{ticket_id}.md'
    content = f'''---
id: {ticket_id}
status: open
deps: []
links: []
created: 2024-01-01T00:00:00Z
type: task
priority: 2
---
# {title}

Description
'''
    ticket_path.write_text(content)


# ============================================================================
# When Steps
# ============================================================================

@when(r'I run "(?P<command>(?:[^"\\]|\\.)+)" in non-TTY mode')
def step_run_command_non_tty(context, command):
    """Run a command simulating non-TTY mode."""
    # Unescape \" to " in the command string
    command = command.replace('\\"', '"')

    ticket_script = get_ticket_script(context)
    cmd = command.replace('ticket ', f'{ticket_script} ', 1)

    result = subprocess.run(
        cmd,
        shell=True,
        cwd=context.test_dir,
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL  # Simulate non-TTY
    )

    context.result = result
    context.stdout = result.stdout.strip()
    context.stderr = result.stderr.strip()
    context.returncode = result.returncode


@when(r'I run "(?P<command>(?:[^"\\]|\\.)+)" with no stdin')
def step_run_command_no_stdin(context, command):
    """Run a command with stdin closed."""
    ticket_script = get_ticket_script(context)
    cmd = command.replace('ticket ', f'{ticket_script} ', 1)

    result = subprocess.run(
        cmd,
        shell=True,
        cwd=context.test_dir,
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL
    )

    context.result = result
    context.stdout = result.stdout.strip()
    context.stderr = result.stderr.strip()
    context.returncode = result.returncode


@when(r'I run "(?P<command>(?:[^"\\]|\\.)+)" with TICKETS_DIR set to "(?P<tickets_dir>[^"]+)"')
def step_run_command_with_env(context, command, tickets_dir):
    """Run a ticket CLI command with custom TICKETS_DIR."""
    command = command.replace('\\"', '"')
    ticket_script = get_ticket_script(context)
    cmd = command.replace('ticket ', f'{ticket_script} ', 1)

    # Use working_dir if set (from subdirectory step), otherwise test_dir
    cwd = getattr(context, 'working_dir', context.test_dir)

    # Resolve tickets_dir relative to test_dir
    env = os.environ.copy()
    env['TICKETS_DIR'] = str(Path(context.test_dir) / tickets_dir)

    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        env=env
    )

    context.result = result
    context.stdout = result.stdout.strip()
    context.stderr = result.stderr.strip()
    context.returncode = result.returncode
    context.last_command = command


@when(r'I run "(?P<command>(?:[^"\\]|\\.)+)"')
def step_run_command(context, command):
    """Run a ticket CLI command."""
    # Unescape \" to " in the command string
    command = command.replace('\\"', '"')

    ticket_script = get_ticket_script(context)
    cmd = command.replace('ticket ', f'{ticket_script} ', 1)

    # Use working_dir if set (from subdirectory step), otherwise test_dir
    cwd = getattr(context, 'working_dir', context.test_dir)

    # Include plugin directory in PATH if plugins were created
    env = os.environ.copy()
    if hasattr(context, 'plugin_dir'):
        env['PATH'] = context.plugin_dir + ':' + env.get('PATH', '')

    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,  # Non-interactive tests
        env=env
    )

    context.result = result
    context.stdout = result.stdout.strip()
    context.stderr = result.stderr.strip()
    context.returncode = result.returncode
    context.last_command = command

    # If this was a create command, track the created ticket ID
    if 'ticket create' in command and result.returncode == 0:
        context.last_created_id = result.stdout.strip()


# ============================================================================
# Then Steps
# ============================================================================

@then(r'the command should succeed')
def step_command_succeed(context):
    """Assert command returned exit code 0."""
    assert context.returncode == 0, \
        f"Command failed with exit code {context.returncode}\nstdout: {context.stdout}\nstderr: {context.stderr}"


@then(r'the command should fail')
def step_command_fail(context):
    """Assert command returned non-zero exit code."""
    assert context.returncode != 0, \
        f"Command succeeded but was expected to fail\nstdout: {context.stdout}"


@then(r'the output should be "(?P<expected>[^"]*)"')
def step_output_equals(context, expected):
    """Assert output exactly matches expected string."""
    actual = context.stdout
    assert actual == expected, f"Expected '{expected}' but got '{actual}'"


@then(r'the output should be empty')
def step_output_empty(context):
    """Assert output is empty."""
    assert context.stdout == '', f"Expected empty output but got: {context.stdout}"


@then(r'the output should contain "(?P<text>[^"]+)"')
def step_output_contains(context, text):
    """Assert output contains text."""
    output = context.stdout + context.stderr
    assert text in output, f"Expected output to contain '{text}'\nActual output: {output}"


@then(r'the output should not contain "(?P<text>[^"]+)"')
def step_output_not_contains(context, text):
    """Assert output does not contain text."""
    output = context.stdout + context.stderr
    assert text not in output, f"Expected output to NOT contain '{text}'\nActual output: {output}"


@then(r'the output should match a ticket ID pattern')
def step_output_matches_id_pattern(context):
    """Assert output matches ticket ID pattern (prefix-hash)."""
    # Prefix can be alphanumeric (from directory name), hash is 4 hex chars
    pattern = r'^[a-z0-9]+-[a-z0-9]{4}$'
    assert re.match(pattern, context.stdout), \
        f"Output '{context.stdout}' does not match ticket ID pattern"


@then(r'the output should match pattern "(?P<pattern>[^"]+)"')
def step_output_matches_pattern(context, pattern):
    """Assert output matches regex pattern."""
    assert re.search(pattern, context.stdout), \
        f"Output does not match pattern '{pattern}'\nActual output: {context.stdout}"


@then(r'the output should match box-drawing tree format')
def step_output_matches_tree_format(context):
    """Assert output contains box-drawing characters for tree."""
    output = context.stdout
    has_tree_chars = any(c in output for c in ['├', '└', '│', '─'])
    assert has_tree_chars, f"Output does not contain box-drawing characters:\n{output}"


@then(r'a ticket file should exist with title "(?P<title>[^"]+)"')
def step_ticket_file_exists_with_title(context, title):
    """Assert a ticket file exists with given title."""
    tickets_dir = Path(context.test_dir) / '.tickets'
    ticket_id = context.last_created_id
    ticket_path = tickets_dir / f'{ticket_id}.md'

    assert ticket_path.exists(), f"Ticket file {ticket_path} does not exist"
    content = ticket_path.read_text()
    assert f'# {title}' in content, f"Ticket does not have title '{title}'\nContent: {content}"


@then(r'the tickets directory should exist')
def step_tickets_dir_exists(context):
    """Assert .tickets directory exists."""
    tickets_dir = Path(context.test_dir) / '.tickets'
    assert tickets_dir.exists(), f".tickets directory does not exist"


@then(r'tickets directory should exist in current subdirectory')
def step_tickets_dir_exists_in_subdir(context):
    """Assert .tickets directory exists in the current working subdirectory."""
    cwd = getattr(context, 'working_dir', context.test_dir)
    tickets_dir = Path(cwd) / '.tickets'
    assert tickets_dir.exists(), f".tickets directory does not exist in {cwd}"


@then(r'the created ticket should contain "(?P<text>[^"]+)"')
def step_created_ticket_contains(context, text):
    """Assert the most recently created ticket contains text."""
    ticket_id = context.last_created_id
    ticket_path = Path(context.test_dir) / '.tickets' / f'{ticket_id}.md'
    content = ticket_path.read_text()
    assert text in content, f"Ticket does not contain '{text}'\nContent: {content}"


@then(r'the created ticket should have field "(?P<field>[^"]+)" with value "(?P<value>[^"]+)"')
def step_created_ticket_has_field(context, field, value):
    """Assert the most recently created ticket has a field with value."""
    ticket_id = context.last_created_id
    ticket_path = Path(context.test_dir) / '.tickets' / f'{ticket_id}.md'
    content = ticket_path.read_text()

    pattern = rf'^{re.escape(field)}:\s*(.+)$'
    match = re.search(pattern, content, re.MULTILINE)
    assert match, f"Field '{field}' not found in ticket\nContent: {content}"
    actual = match.group(1).strip()
    assert actual == value, f"Field '{field}' has value '{actual}', expected '{value}'"


@then(r'the created ticket should have a valid created timestamp')
def step_created_ticket_has_timestamp(context):
    """Assert the created ticket has a valid timestamp."""
    ticket_id = context.last_created_id
    ticket_path = Path(context.test_dir) / '.tickets' / f'{ticket_id}.md'
    content = ticket_path.read_text()

    pattern = r'^created:\s*\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z'
    assert re.search(pattern, content, re.MULTILINE), \
        f"No valid created timestamp found\nContent: {content}"


@then(r'ticket "(?P<ticket_id>[^"]+)" should have field "(?P<field>[^"]+)" with value "(?P<value>[^"]+)"')
def step_ticket_has_field_value(context, ticket_id, field, value):
    """Assert ticket has a field with specific value."""
    ticket_path = Path(context.test_dir) / '.tickets' / f'{ticket_id}.md'
    content = ticket_path.read_text()

    pattern = rf'^{re.escape(field)}:\s*(.+)$'
    match = re.search(pattern, content, re.MULTILINE)
    assert match, f"Field '{field}' not found in ticket\nContent: {content}"
    actual = match.group(1).strip()
    assert actual == value, f"Field '{field}' has value '{actual}', expected '{value}'"


@then(r'ticket "(?P<ticket_id>[^"]+)" should not have field "(?P<field>[^"]+)"')
def step_ticket_not_has_field(context, ticket_id, field):
    """Assert ticket does not have a field (or field is empty)."""
    ticket_path = Path(context.test_dir) / '.tickets' / f'{ticket_id}.md'
    content = ticket_path.read_text()
    pattern = rf'^{re.escape(field)}:\s*(.+)$'
    match = re.search(pattern, content, re.MULTILINE)
    assert not match, f"Field '{field}' found with value '{match.group(1).strip()}', expected it to be absent"


@then(r'ticket "(?P<ticket_id>[^"]+)" should have "(?P<dep_id>[^"]+)" in deps')
def step_ticket_has_dep(context, ticket_id, dep_id):
    """Assert ticket has a dependency."""
    ticket_path = Path(context.test_dir) / '.tickets' / f'{ticket_id}.md'
    content = ticket_path.read_text()

    deps_match = re.search(r'^deps:\s*\[([^\]]*)\]', content, re.MULTILINE)
    assert deps_match, f"deps field not found\nContent: {content}"
    deps = deps_match.group(1)
    assert dep_id in deps, f"Dependency '{dep_id}' not in deps: [{deps}]"


@then(r'ticket "(?P<ticket_id>[^"]+)" should not have "(?P<dep_id>[^"]+)" in deps')
def step_ticket_not_has_dep(context, ticket_id, dep_id):
    """Assert ticket does not have a dependency."""
    ticket_path = Path(context.test_dir) / '.tickets' / f'{ticket_id}.md'
    content = ticket_path.read_text()

    deps_match = re.search(r'^deps:\s*\[([^\]]*)\]', content, re.MULTILINE)
    assert deps_match, f"deps field not found\nContent: {content}"
    deps = deps_match.group(1)
    assert dep_id not in deps, f"Dependency '{dep_id}' should not be in deps: [{deps}]"


@then(r'ticket "(?P<ticket_id>[^"]+)" should have "(?P<link_id>[^"]+)" in links')
def step_ticket_has_link(context, ticket_id, link_id):
    """Assert ticket has a link."""
    ticket_path = Path(context.test_dir) / '.tickets' / f'{ticket_id}.md'
    content = ticket_path.read_text()

    links_match = re.search(r'^links:\s*\[([^\]]*)\]', content, re.MULTILINE)
    assert links_match, f"links field not found\nContent: {content}"
    links = links_match.group(1)
    assert link_id in links, f"Link '{link_id}' not in links: [{links}]"


@then(r'ticket "(?P<ticket_id>[^"]+)" should not have "(?P<link_id>[^"]+)" in links')
def step_ticket_not_has_link(context, ticket_id, link_id):
    """Assert ticket does not have a link."""
    ticket_path = Path(context.test_dir) / '.tickets' / f'{ticket_id}.md'
    content = ticket_path.read_text()

    links_match = re.search(r'^links:\s*\[([^\]]*)\]', content, re.MULTILINE)
    assert links_match, f"links field not found\nContent: {content}"
    links = links_match.group(1)
    assert link_id not in links, f"Link '{link_id}' should not be in links: [{links}]"


@then(r'ticket "(?P<ticket_id>[^"]+)" should contain "(?P<text>[^"]+)"')
def step_ticket_contains(context, ticket_id, text):
    """Assert ticket file contains text."""
    ticket_path = Path(context.test_dir) / '.tickets' / f'{ticket_id}.md'
    content = ticket_path.read_text()
    assert text in content, f"Ticket does not contain '{text}'\nContent: {content}"


@then(r'ticket "(?P<ticket_id>[^"]+)" should contain a timestamp in notes')
def step_ticket_has_timestamp_in_notes(context, ticket_id):
    """Assert ticket has a timestamp in notes section."""
    ticket_path = Path(context.test_dir) / '.tickets' / f'{ticket_id}.md'
    content = ticket_path.read_text()

    pattern = r'\*\*\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\*\*'
    assert re.search(pattern, content), \
        f"No timestamp found in notes\nContent: {content}"


@then(r'the output line (?P<line_num>\d+) should contain "(?P<text>[^"]+)"')
def step_output_line_contains(context, line_num, text):
    """Assert specific line of output contains text."""
    line_num = int(line_num)
    lines = context.stdout.split('\n')
    assert len(lines) >= line_num, \
        f"Output has only {len(lines)} lines, expected at least {line_num}"
    line = lines[line_num - 1]
    assert text in line, f"Line {line_num} does not contain '{text}'\nLine: {line}"


@then(r'the output line count should be (?P<count>\d+)')
def step_output_line_count(context, count):
    """Assert output has specific number of lines."""
    count = int(count)
    lines = [l for l in context.stdout.split('\n') if l.strip()]
    assert len(lines) == count, \
        f"Expected {count} lines but got {len(lines)}\nOutput: {context.stdout}"


@then(r'the output should be valid JSONL')
def step_output_valid_jsonl(context):
    """Assert output is valid JSON Lines format."""
    lines = context.stdout.strip().split('\n')
    for line in lines:
        if line.strip():
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                raise AssertionError(f"Invalid JSONL line: {line}\nError: {e}")


@then(r'the JSONL output should have field "(?P<field>[^"]+)"')
def step_jsonl_has_field(context, field):
    """Assert JSONL output has a specific field."""
    lines = context.stdout.strip().split('\n')
    assert lines, "No JSONL output"

    for line in lines:
        if line.strip():
            data = json.loads(line)
            assert field in data, f"Field '{field}' not found in JSONL\nData: {data}"
            break


@then(r'the JSONL (?P<field>\w+) field should be a JSON array')
def step_jsonl_field_is_array(context, field):
    """Assert a field in JSONL is an array."""
    lines = context.stdout.strip().split('\n')
    assert lines, "No JSONL output"

    for line in lines:
        if line.strip():
            data = json.loads(line)
            if field in data:
                assert isinstance(data[field], list), \
                    f"'{field}' field is not an array: {type(data[field])}"
                return
    raise AssertionError(f"No JSONL line with '{field}' field found")


@then(r'the dep tree output should have (?P<first_id>[^\s]+) before (?P<second_id>[^\s]+)')
def step_dep_tree_order(context, first_id, second_id):
    """Assert that first_id appears before second_id in dep tree output."""
    output = context.stdout
    lines = output.split('\n')

    first_line = -1
    second_line = -1

    for i, line in enumerate(lines):
        if first_id in line:
            first_line = i
        if second_id in line:
            second_line = i

    assert first_line != -1, f"'{first_id}' not found in output:\n{output}"
    assert second_line != -1, f"'{second_id}' not found in output:\n{output}"
    assert first_line < second_line, \
        f"Expected '{first_id}' (line {first_line + 1}) before '{second_id}' (line {second_line + 1})\nOutput:\n{output}"


# ============================================================================
# Plugin Steps
# ============================================================================

def create_plugin(context, name, content):
    """Helper to create a plugin script in a temporary bin directory."""
    if not hasattr(context, 'plugin_dir'):
        context.plugin_dir = tempfile.mkdtemp(prefix='ticket_plugins_')

    plugin_path = Path(context.plugin_dir) / name
    plugin_path.write_text(content)
    plugin_path.chmod(0o755)
    return plugin_path


def run_with_plugin_path(context, command):
    """Run a command with the plugin directory in PATH."""
    command = command.replace('\\"', '"')
    ticket_script = get_ticket_script(context)
    cmd = command.replace('ticket ', f'{ticket_script} ', 1)

    cwd = getattr(context, 'working_dir', context.test_dir)

    env = os.environ.copy()
    if hasattr(context, 'plugin_dir'):
        env['PATH'] = context.plugin_dir + ':' + env.get('PATH', '')

    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        env=env
    )

    context.result = result
    context.stdout = result.stdout.strip()
    context.stderr = result.stderr.strip()
    context.returncode = result.returncode
    context.last_command = command

    if 'ticket create' in command and result.returncode == 0:
        context.last_created_id = result.stdout.strip()


@given(r'a plugin "(?P<name>[^"]+)" that outputs "(?P<output>[^"]+)"')
def step_plugin_outputs(context, name, output):
    """Create a plugin that outputs a fixed string."""
    content = f'''#!/usr/bin/env bash
# tk-plugin: Test plugin
echo "{output}"
'''
    create_plugin(context, name, content)


@given(r'a plugin "(?P<name>[^"]+)" that outputs its arguments')
def step_plugin_echo_args(context, name):
    """Create a plugin that echoes its arguments."""
    content = '''#!/usr/bin/env bash
# tk-plugin: Echo arguments
echo "$@"
'''
    create_plugin(context, name, content)


@given(r'a plugin "(?P<name>[^"]+)" that outputs TICKETS_DIR')
def step_plugin_outputs_tickets_dir(context, name):
    """Create a plugin that outputs the TICKETS_DIR env var."""
    content = '''#!/usr/bin/env bash
# tk-plugin: Output TICKETS_DIR
echo "$TICKETS_DIR"
'''
    create_plugin(context, name, content)


@given(r'a plugin "(?P<name>[^"]+)" that outputs TK_SCRIPT')
def step_plugin_outputs_tk_script(context, name):
    """Create a plugin that outputs the TK_SCRIPT env var."""
    content = '''#!/usr/bin/env bash
# tk-plugin: Output TK_SCRIPT
echo "$TK_SCRIPT"
'''
    create_plugin(context, name, content)


@given(r'a plugin "(?P<name>[^"]+)" with description "(?P<desc>[^"]+)"')
def step_plugin_with_description(context, name, desc):
    """Create a plugin with a specific description."""
    content = f'''#!/usr/bin/env bash
# tk-plugin: {desc}
echo "plugin executed"
'''
    create_plugin(context, name, content)


@given(r'a plugin "(?P<name>[^"]+)" that outputs "(?P<output>[^"]+)" without metadata')
def step_plugin_no_metadata(context, name, output):
    """Create a plugin without tk-plugin metadata comment."""
    content = f'''#!/usr/bin/env bash
echo "{output}"
'''
    create_plugin(context, name, content)


@given(r'a plugin "(?P<name>[^"]+)" that calls super create')
def step_plugin_calls_super(context, name):
    """Create a plugin that calls the built-in create via super."""
    content = '''#!/usr/bin/env bash
# tk-plugin: Wrapper that calls super
exec "$TK_SCRIPT" super create "$@"
'''
    create_plugin(context, name, content)


# Override the run step for plugin scenarios to include plugin PATH
@when(r'I run "(?P<command>(?:[^"\\]|\\.)+)" with plugins')
def step_run_with_plugins(context, command):
    """Run a command with plugins in PATH."""
    run_with_plugin_path(context, command)


# ============================================================================
# Plugin Command Steps (ticket-tags, ticket-archive, ticket-query-all)
# ============================================================================

def run_plugin(context, args):
    """Run a plugin command and store results in context."""
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        env=context.env,
    )
    context.result = result
    context.stdout = result.stdout.strip()
    context.stderr = result.stderr.strip()
    context.returncode = result.returncode


# --- Given steps for test fixture tickets ---

@given(r'the test tickets directory')
def step_test_tickets_dir(context):
    """Copy test fixture tickets into the scenario's tickets directory."""
    from features.environment import TESTS_DIR
    src = TESTS_DIR / '.tickets'
    import shutil
    shutil.copytree(str(src), context.tickets_dir)


@given(r'an empty tickets directory')
def step_empty_tickets_dir(context):
    """Create an empty tickets directory."""
    import shutil
    if os.path.exists(context.tickets_dir):
        shutil.rmtree(context.tickets_dir)
    os.makedirs(context.tickets_dir)


@given(r'ticket "(?P<ticket_id>[^"]+)" is archived')
def step_archive_ticket(context, ticket_id):
    """Move a ticket to the archive subdirectory."""
    import shutil
    archive_dir = os.path.join(context.tickets_dir, 'archive')
    os.makedirs(archive_dir, exist_ok=True)
    src = os.path.join(context.tickets_dir, f'{ticket_id}.md')
    dest = os.path.join(archive_dir, f'{ticket_id}.md')
    shutil.move(src, dest)


# --- When steps for plugin commands ---

@when(r'I run ticket-query-all')
def step_run_query_all(context):
    run_plugin(context, ['ticket-query-all'])


@when(r"I run ticket-query-all with filter '(?P<filter>[^']+)'")
def step_run_query_all_filter(context, filter):
    run_plugin(context, ['ticket-query-all', filter])


@when(r'I run ticket-tags')
def step_run_tags(context):
    run_plugin(context, ['ticket-tags'])


@when(r'I run ticket-tags with (?P<args>.+)')
def step_run_tags_with_args(context, args):
    run_plugin(context, ['ticket-tags'] + args.split())


@when(r'I run ticket-archive')
def step_run_archive(context):
    run_plugin(context, ['ticket-archive'])


# --- Then steps for JSONL validation ---

@then(r'every JSONL line should have field "(?P<field>[^"]+)"')
def step_every_jsonl_has_field(context, field):
    lines = [l for l in context.stdout.strip().splitlines() if l.strip()]
    for i, line in enumerate(lines):
        obj = json.loads(line)
        assert field in obj, f"Line {i + 1} missing field '{field}': {line}"


@then(r'the JSONL output should contain a title "(?P<title>[^"]+)"')
def step_jsonl_contains_title(context, title):
    lines = [l for l in context.stdout.strip().splitlines() if l.strip()]
    titles = [json.loads(l)['title'] for l in lines]
    assert title in titles, f"Title '{title}' not found. Titles: {titles}"


@then(r'the JSONL output for ticket "(?P<ticket_id>[^"]+)" should have body containing "(?P<text>[^"]+)"')
def step_jsonl_body_contains(context, ticket_id, text):
    lines = [l for l in context.stdout.strip().splitlines() if l.strip()]
    for line in lines:
        obj = json.loads(line)
        if obj['id'] == ticket_id:
            assert text in obj['body'], \
                f"Body of {ticket_id} does not contain '{text}': {obj['body']!r}"
            return
    raise AssertionError(f"Ticket {ticket_id} not found in output")


@then(r'the JSONL output for ticket "(?P<ticket_id>[^"]+)" should have empty body')
def step_jsonl_body_empty(context, ticket_id):
    lines = [l for l in context.stdout.strip().splitlines() if l.strip()]
    for line in lines:
        obj = json.loads(line)
        if obj['id'] == ticket_id:
            assert obj['body'] == '', \
                f"Body of {ticket_id} is {obj['body']!r}, expected empty string"
            return
    raise AssertionError(f"Ticket {ticket_id} not found in output")


@then(r'the JSONL (?P<field>\w+) field should be a number')
def step_jsonl_field_is_number(context, field):
    lines = [l for l in context.stdout.strip().splitlines() if l.strip()]
    for i, line in enumerate(lines):
        obj = json.loads(line)
        assert isinstance(obj[field], (int, float)), \
            f"Line {i + 1}: '{field}' is {type(obj[field]).__name__}, expected number"


# --- Then steps for tag output ---

@then(r'the first output line should start with "(?P<text>[^"]+)"')
def step_first_line_starts_with(context, text):
    first = context.stdout.strip().splitlines()[0]
    assert first.startswith(text), f"First line is {first!r}, expected to start with {text!r}"


@then(r'the output line for tag "(?P<tag>[^"]+)" should list "(?P<id1>[^"]+)" before "(?P<id2>[^"]+)"')
def step_tag_line_order(context, tag, id1, id2):
    for line in context.stdout.strip().splitlines():
        if line.startswith(f'{tag} '):
            pos1 = line.index(id1)
            pos2 = line.index(id2)
            assert pos1 < pos2, f"Expected {id1} before {id2} in: {line!r}"
            return
    raise AssertionError(f"No output line for tag {tag!r}")


# --- Then steps for archive ---

def _archive_dir(context):
    return os.path.join(context.tickets_dir, 'archive')


@then(r'ticket "(?P<ticket_id>[^"]+)" should exist in the archive')
def step_ticket_in_archive(context, ticket_id):
    path = os.path.join(_archive_dir(context), f'{ticket_id}.md')
    assert os.path.exists(path), f"Expected {path} to exist"


@then(r'ticket "(?P<ticket_id>[^"]+)" should not exist in the archive')
def step_ticket_not_in_archive(context, ticket_id):
    path = os.path.join(_archive_dir(context), f'{ticket_id}.md')
    assert not os.path.exists(path), f"Expected {path} to not exist"


@then(r'ticket "(?P<ticket_id>[^"]+)" should exist in the tickets directory')
def step_ticket_in_tickets_dir(context, ticket_id):
    path = os.path.join(context.tickets_dir, f'{ticket_id}.md')
    assert os.path.exists(path), f"Expected {path} to exist"


@then(r'ticket "(?P<ticket_id>[^"]+)" should not exist in the tickets directory')
def step_ticket_not_in_tickets_dir(context, ticket_id):
    path = os.path.join(context.tickets_dir, f'{ticket_id}.md')
    assert not os.path.exists(path), f"Expected {path} to not exist"


@then(r'the archive directory should exist')
def step_archive_dir_exists(context):
    assert os.path.isdir(_archive_dir(context)), "Archive directory does not exist"


@then(r'the archive directory should not exist')
def step_archive_dir_not_exists(context):
    assert not os.path.exists(_archive_dir(context)), "Archive directory should not exist"


@then(r'the archived ticket "(?P<ticket_id>[^"]+)" should contain "(?P<text>[^"]+)"')
def step_archived_ticket_contains(context, ticket_id, text):
    path = os.path.join(_archive_dir(context), f'{ticket_id}.md')
    with open(path) as f:
        content = f.read()
    assert text in content, f"Archived ticket does not contain '{text}':\n{content}"
