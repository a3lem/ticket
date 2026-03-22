Feature: ticket-tags counts tags across tickets

  Scenario: Count tags for open tickets only (default)
    Given the test tickets directory
    When I run ticket-tags
    Then the command should succeed
    And the output should contain "extraction [3]"
    And the output should contain "transplanting [2]"
    And the output should contain "preparation [2]"
    And the output should contain "assessment [1]"
    And the output should contain "aftercare [1]"

  Scenario: Output is sorted by count descending
    Given the test tickets directory
    When I run ticket-tags
    Then the command should succeed
    And the first output line should start with "extraction"

  Scenario: Ticket IDs shown after count
    Given the test tickets directory
    When I run ticket-tags
    Then the command should succeed
    And the output should contain "assessment [1] - env-quy6"

  Scenario: Most actionable tickets shown first
    Given the test tickets directory
    When I run ticket-tags with --include-closed
    Then the command should succeed
    And the output line for tag "transplanting" should list "env-o8i0" before "env-90ef"

  Scenario: Closed tickets excluded by default
    Given the test tickets directory
    When I run ticket-tags
    Then the command should succeed
    And the output should not contain "extraction [4]"

  Scenario: Include closed tickets
    Given the test tickets directory
    When I run ticket-tags with --include-closed
    Then the command should succeed
    And the output should contain "transplanting [3]"

  Scenario: Include archived tickets
    Given the test tickets directory
    And ticket "env-90ef" is archived
    When I run ticket-tags with --include-archived
    Then the command should succeed
    And the output should contain "transplanting [2]"
    And the output should not contain "transplanting [3]"

  Scenario: Include both closed and archived tickets
    Given the test tickets directory
    And ticket "env-90ef" is archived
    When I run ticket-tags with --include-closed --include-archived
    Then the command should succeed
    And the output should contain "transplanting [3]"

  Scenario: Empty tickets directory
    Given an empty tickets directory
    When I run ticket-tags
    Then the command should succeed
    And the output should be empty
