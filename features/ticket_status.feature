Feature: Ticket Status Management
  As a user
  I want to change ticket statuses
  So that I can track progress on tasks

  Background:
    Given a clean tickets directory
    And a ticket exists with ID "test-0001" and title "Test ticket"

  Scenario: Set status to in_progress
    When I run "ticket status test-0001 in_progress"
    Then the command should succeed
    And the output should be "Updated test-0001 -> in_progress"
    And ticket "test-0001" should have field "status" with value "in_progress"

  Scenario: Set status to closed
    When I run "ticket status test-0001 closed"
    Then the command should succeed
    And the output should be "Updated test-0001 -> closed"
    And ticket "test-0001" should have field "status" with value "closed"

  Scenario: Set status to open
    Given ticket "test-0001" has status "closed"
    When I run "ticket status test-0001 open"
    Then the command should succeed
    And the output should be "Updated test-0001 -> open"
    And ticket "test-0001" should have field "status" with value "open"

  Scenario: Start command sets status to in_progress
    When I run "ticket start test-0001"
    Then the command should succeed
    And the output should be "Updated test-0001 -> in_progress"
    And ticket "test-0001" should have field "status" with value "in_progress"

  Scenario: Close command sets status to closed
    When I run "ticket close test-0001"
    Then the command should succeed
    And the output should be "Closed test-0001 (completed)"
    And ticket "test-0001" should have field "status" with value "closed"
    And ticket "test-0001" should have field "close_reason" with value "completed"

  Scenario: Close with explicit rejected reason
    When I run "ticket close --reason rejected test-0001"
    Then the command should succeed
    And the output should be "Closed test-0001 (rejected)"
    And ticket "test-0001" should have field "status" with value "closed"
    And ticket "test-0001" should have field "close_reason" with value "rejected"

  Scenario: Close with explicit completed reason
    When I run "ticket close --reason completed test-0001"
    Then the command should succeed
    And the output should be "Closed test-0001 (completed)"
    And ticket "test-0001" should have field "close_reason" with value "completed"

  Scenario: Close with invalid reason
    When I run "ticket close --reason wontfix test-0001"
    Then the command should fail
    And the output should contain "invalid close reason"

  Scenario: Reopen command sets status to open
    Given ticket "test-0001" has status "closed"
    When I run "ticket reopen test-0001"
    Then the command should succeed
    And the output should be "Updated test-0001 -> open"
    And ticket "test-0001" should have field "status" with value "open"

  Scenario: Reopen clears close_reason
    When I run "ticket close test-0001"
    And I run "ticket reopen test-0001"
    Then ticket "test-0001" should have field "status" with value "open"
    And ticket "test-0001" should not have field "close_reason"

  Scenario: Invalid status value
    When I run "ticket status test-0001 invalid"
    Then the command should fail
    And the output should contain "Error: invalid status 'invalid'"
    And the output should contain "open in_progress closed"

  Scenario: Status of non-existent ticket
    When I run "ticket status nonexistent open"
    Then the command should fail
    And the output should contain "Error: ticket 'nonexistent' not found"

  Scenario: Status command with partial ID
    When I run "ticket status 0001 in_progress"
    Then the command should succeed
    And ticket "test-0001" should have field "status" with value "in_progress"

  Scenario: Cannot close parent with open child
    Given a ticket exists with ID "par-0001" and title "Parent epic"
    And a ticket exists with ID "par-0002" and title "Child task" with parent "par-0001"
    When I run "ticket close par-0001"
    Then the command should fail
    And the output should contain "has open descendants"
    And the output should contain "par-0002"
    And ticket "par-0001" should have field "status" with value "open"

  Scenario: Cannot close parent via status command with open child
    Given a ticket exists with ID "par-0001" and title "Parent epic"
    And a ticket exists with ID "par-0002" and title "Child task" with parent "par-0001"
    When I run "ticket status par-0001 closed"
    Then the command should fail
    And the output should contain "has open descendants"

  Scenario: Can close parent when all children are closed
    Given a ticket exists with ID "par-0001" and title "Parent epic"
    And a ticket exists with ID "par-0002" and title "Child task" with parent "par-0001"
    And ticket "par-0002" has status "closed"
    When I run "ticket close par-0001"
    Then the command should succeed
    And the output should be "Closed par-0001 (completed)"

  Scenario: Can close parent when child is rejected
    Given a ticket exists with ID "par-0001" and title "Parent epic"
    And a ticket exists with ID "par-0002" and title "Child task" with parent "par-0001"
    When I run "ticket close --reason rejected par-0002"
    And I run "ticket close par-0001"
    Then the command should succeed

  Scenario: Cannot close grandparent with open grandchild
    Given a ticket exists with ID "par-0001" and title "Epic"
    And a ticket exists with ID "par-0002" and title "Feature" with parent "par-0001"
    And a ticket exists with ID "par-0003" and title "Task" with parent "par-0002"
    And ticket "par-0002" has status "closed"
    When I run "ticket close par-0001"
    Then the command should fail
    And the output should contain "has open descendants"
    And the output should contain "par-0003"

  Scenario: Can close ticket with no children
    When I run "ticket close test-0001"
    Then the command should succeed
