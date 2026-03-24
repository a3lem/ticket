Feature: Ticket Listing
  As a user
  I want to list tickets in various ways
  So that I can see what work needs to be done

  Background:
    Given a clean tickets directory

  Scenario: List all tickets
    Given a ticket exists with ID "list-0001" and title "First ticket"
    And a ticket exists with ID "list-0002" and title "Second ticket"
    When I run "ticket ls"
    Then the command should succeed
    And the output should contain "list-0001"
    And the output should contain "list-0002"

  Scenario: List command alias works
    Given a ticket exists with ID "list-0001" and title "First ticket"
    When I run "ticket list"
    Then the command should succeed
    And the output should contain "list-0001"

  Scenario: List shows ticket format correctly
    Given a ticket exists with ID "list-0001" and title "My ticket"
    When I run "ticket ls"
    Then the command should succeed
    And the output should match pattern "list-0001 - \[ \] My ticket"

  Scenario: List shows rejected checkbox for closed rejected tickets
    Given a ticket exists with ID "list-0001" and title "Done ticket"
    And ticket "list-0001" has status "closed"
    And ticket "list-0001" has close_reason "rejected"
    When I run "ticket ls"
    Then the command should succeed
    And the output should contain "[~]"

  Scenario: List shows completed checkbox for closed tickets without close_reason
    Given a ticket exists with ID "list-0001" and title "Done ticket"
    And ticket "list-0001" has status "closed"
    When I run "ticket ls"
    Then the command should succeed
    And the output should contain "[x]"

  Scenario: List filters by closed:rejected
    Given a ticket exists with ID "list-0001" and title "Completed ticket"
    And a ticket exists with ID "list-0002" and title "Rejected ticket"
    And ticket "list-0001" has status "closed"
    And ticket "list-0001" has close_reason "completed"
    And ticket "list-0002" has status "closed"
    And ticket "list-0002" has close_reason "rejected"
    When I run "ticket ls --status=closed:rejected"
    Then the command should succeed
    And the output should contain "list-0002"
    And the output should not contain "list-0001"

  Scenario: List with status filter
    Given a ticket exists with ID "list-0001" and title "Open ticket"
    And a ticket exists with ID "list-0002" and title "Closed ticket"
    And ticket "list-0002" has status "closed"
    When I run "ticket ls --status=open"
    Then the command should succeed
    And the output should contain "list-0001"
    And the output should not contain "list-0002"

  Scenario: List shows dependencies
    Given a ticket exists with ID "list-0001" and title "Main ticket"
    And a ticket exists with ID "list-0002" and title "Dep ticket"
    And ticket "list-0001" depends on "list-0002"
    When I run "ticket ls"
    Then the command should succeed
    And the output should contain "<- [list-0002]"

  Scenario: List with no tickets returns nothing
    When I run "ticket ls"
    Then the output should be empty

  Scenario: Ready shows tickets with no deps and with closed deps
    Given a ticket exists with ID "ready-001" and title "Ready ticket"
    And a ticket exists with ID "ready-002" and title "Unblocked ticket"
    And a ticket exists with ID "ready-003" and title "Dependency"
    And ticket "ready-002" depends on "ready-003"
    And ticket "ready-003" has status "closed"
    When I run "ticket ready"
    Then the command should succeed
    And the output should contain "ready-001"
    And the output should contain "ready-002"

  Scenario: Ready excludes tickets with unclosed deps
    Given a ticket exists with ID "ready-001" and title "Blocked ticket"
    And a ticket exists with ID "ready-002" and title "Open dependency"
    And ticket "ready-001" depends on "ready-002"
    When I run "ticket ready"
    Then the command should succeed
    And the output should not contain "ready-001"
    And the output should contain "ready-002"

  Scenario: Ready shows tickets when deps are closed
    Given a ticket exists with ID "ready-001" and title "Main ticket"
    And a ticket exists with ID "ready-002" and title "Closed dependency"
    And ticket "ready-001" depends on "ready-002"
    And ticket "ready-002" has status "closed"
    When I run "ticket ready"
    Then the command should succeed
    And the output should contain "ready-001"

  Scenario: Ready excludes closed tickets
    Given a ticket exists with ID "ready-001" and title "Closed ticket"
    And ticket "ready-001" has status "closed"
    When I run "ticket ready"
    Then the command should succeed
    And the output should not contain "ready-001"

  Scenario: Ready shows priority in output
    Given a ticket exists with ID "ready-001" and title "Priority ticket"
    When I run "ticket ready"
    Then the command should succeed
    And the output should match pattern "ready-001 - \[ \] Priority ticket"

  Scenario: Ready sorts by priority then ID
    Given a ticket exists with ID "ready-003" and title "Low priority" with priority 3
    And a ticket exists with ID "ready-001" and title "High priority" with priority 1
    And a ticket exists with ID "ready-002" and title "Also high priority" with priority 1
    When I run "ticket ready"
    Then the command should succeed
    And the output line 1 should contain "ready-001"
    And the output line 2 should contain "ready-002"
    And the output line 3 should contain "ready-003"

  Scenario: Blocked shows tickets with unclosed deps
    Given a ticket exists with ID "block-001" and title "Blocked ticket"
    And a ticket exists with ID "block-002" and title "Blocker ticket"
    And ticket "block-001" depends on "block-002"
    When I run "ticket blocked"
    Then the command should succeed
    And the output should contain "block-001"
    And the output should contain "<- [block-002]"

  Scenario: Blocked excludes tickets with all deps closed
    Given a ticket exists with ID "block-001" and title "Unblocked ticket"
    And a ticket exists with ID "block-002" and title "Closed blocker"
    And ticket "block-001" depends on "block-002"
    And ticket "block-002" has status "closed"
    When I run "ticket blocked"
    Then the command should succeed
    And the output should not contain "block-001"

  Scenario: Blocked excludes closed tickets
    Given a ticket exists with ID "block-001" and title "Closed blocked"
    And a ticket exists with ID "block-002" and title "Blocker"
    And ticket "block-001" depends on "block-002"
    And ticket "block-001" has status "closed"
    When I run "ticket blocked"
    Then the command should succeed
    And the output should not contain "block-001"

  Scenario: Blocked shows only unclosed blockers
    Given a ticket exists with ID "block-001" and title "Blocked ticket"
    And a ticket exists with ID "block-002" and title "Open blocker"
    And a ticket exists with ID "block-003" and title "Closed blocker"
    And ticket "block-001" depends on "block-002"
    And ticket "block-001" depends on "block-003"
    And ticket "block-003" has status "closed"
    When I run "ticket blocked"
    Then the command should succeed
    And the output should contain "<- [block-002]"
    And the output should not contain "block-003"

  Scenario: Closed shows recently closed tickets
    Given a ticket exists with ID "done-0001" and title "Done ticket"
    And ticket "done-0001" has status "closed"
    When I run "ticket closed"
    Then the command should succeed
    And the output should contain "done-0001"
    And the output should contain "[x]"
    And the output should contain "Done ticket"

  Scenario: Closed shows rejected checkbox
    Given a ticket exists with ID "done-0001" and title "Done ticket"
    And ticket "done-0001" has status "closed"
    And ticket "done-0001" has close_reason "rejected"
    When I run "ticket closed"
    Then the command should succeed
    And the output should contain "[~]"

  Scenario: Closed --rejected filters to rejected only
    Given a ticket exists with ID "done-0001" and title "Completed ticket"
    And a ticket exists with ID "done-0002" and title "Rejected ticket"
    And ticket "done-0001" has status "closed"
    And ticket "done-0001" has close_reason "completed"
    And ticket "done-0002" has status "closed"
    And ticket "done-0002" has close_reason "rejected"
    When I run "ticket closed --rejected"
    Then the command should succeed
    And the output should contain "done-0002"
    And the output should not contain "done-0001"

  Scenario: Closed --completed filters to completed only
    Given a ticket exists with ID "done-0001" and title "Completed ticket"
    And a ticket exists with ID "done-0002" and title "Rejected ticket"
    And ticket "done-0001" has status "closed"
    And ticket "done-0001" has close_reason "completed"
    And ticket "done-0002" has status "closed"
    And ticket "done-0002" has close_reason "rejected"
    When I run "ticket closed --completed"
    Then the command should succeed
    And the output should contain "done-0001"
    And the output should not contain "done-0002"

  Scenario: Closed respects limit
    Given a ticket exists with ID "done-0001" and title "First done"
    And a ticket exists with ID "done-0002" and title "Second done"
    And ticket "done-0001" has status "closed"
    And ticket "done-0002" has status "closed"
    When I run "ticket closed --limit=1"
    Then the command should succeed
    And the output line count should be 1

  Scenario: Closed excludes open tickets
    Given a ticket exists with ID "done-0001" and title "Open ticket"
    When I run "ticket closed"
    Then the command should succeed
    And the output should not contain "done-0001"

  # === Hierarchical listing (tree rendering) ===

  Scenario: List shows parent with children indented
    Given a ticket exists with ID "tree-0001" and title "Epic ticket"
    And a ticket exists with ID "tree-0002" and title "Child one" with parent "tree-0001"
    And a ticket exists with ID "tree-0003" and title "Child two" with parent "tree-0001"
    When I run "ticket ls"
    Then the command should succeed
    And the output line 1 should contain "tree-0001"
    And the output line 1 should contain "Epic ticket"
    And the output line 2 should contain "tree-0002"
    And the output line 3 should contain "tree-0003"
    And the output should match pattern "[├└]── tree-0002"
    And the output should match pattern "[├└]── tree-0003"

  Scenario: List shows orphan tickets at root level
    Given a ticket exists with ID "tree-0001" and title "Standalone ticket"
    When I run "ticket ls"
    Then the command should succeed
    And the output should match pattern "^tree-0001"

  Scenario: List shows nested children with deeper indentation
    Given a ticket exists with ID "tree-0001" and title "Epic ticket"
    And a ticket exists with ID "tree-0002" and title "Feature ticket" with parent "tree-0001"
    And a ticket exists with ID "tree-0003" and title "Task ticket" with parent "tree-0002"
    When I run "ticket ls"
    Then the command should succeed
    And the output should match pattern "^tree-0001"
    And the output should match pattern "[├└]── tree-0002"
    And the output should match pattern "[├└]── tree-0003"

  Scenario: List --flat disables tree rendering
    Given a ticket exists with ID "tree-0001" and title "Epic ticket"
    And a ticket exists with ID "tree-0002" and title "Child ticket" with parent "tree-0001"
    When I run "ticket ls --flat"
    Then the command should succeed
    And the output should contain "tree-0001"
    And the output should contain "tree-0002"
    And the output should not match pattern "  tree-0002"

  Scenario: Ready shows tree with parent as context heading
    Given a ticket exists with ID "tree-0001" and title "Epic ticket"
    And ticket "tree-0001" has status "in_progress"
    And a ticket exists with ID "tree-0002" and title "Ready child" with parent "tree-0001"
    And a ticket exists with ID "tree-0003" and title "Blocked child" with parent "tree-0001"
    And a ticket exists with ID "tree-0004" and title "Blocker ticket"
    And ticket "tree-0003" depends on "tree-0004"
    When I run "ticket ready"
    Then the command should succeed
    And the output should contain "tree-0001"
    And the output should contain "tree-0002"
    And the output should match pattern "[├└]── tree-0002"
    And the output should not contain "tree-0003"

  Scenario: Blocked shows tree with parent as context heading
    Given a ticket exists with ID "tree-0001" and title "Epic ticket"
    And a ticket exists with ID "tree-0002" and title "Blocked child" with parent "tree-0001"
    And a ticket exists with ID "tree-0003" and title "Blocker ticket"
    And ticket "tree-0002" depends on "tree-0003"
    When I run "ticket blocked"
    Then the command should succeed
    And the output should contain "tree-0001"
    And the output should match pattern "[├└]── tree-0002"
    And the output should contain "<- [tree-0003]"

  Scenario: Parent not shown when all children filtered out
    Given a ticket exists with ID "tree-0001" and title "Epic ticket"
    And a ticket exists with ID "tree-0002" and title "Ready child" with parent "tree-0001"
    When I run "ticket blocked"
    Then the command should succeed
    And the output should not contain "tree-0001"
    And the output should not contain "tree-0002"

  Scenario: Ready --flat disables tree rendering
    Given a ticket exists with ID "tree-0001" and title "Epic ticket"
    And a ticket exists with ID "tree-0002" and title "Ready child" with parent "tree-0001"
    When I run "ticket ready --flat"
    Then the command should succeed
    And the output should contain "tree-0001"
    And the output should contain "tree-0002"
    And the output should not match pattern "  tree-0002"
