Feature: Query All
  As a user
  I want to query tickets with all fields as JSON
  So that I can build further tooling on top with jq

  Background:
    Given the test tickets directory

  Scenario: Outputs valid JSONL
    When I run ticket-query-all
    Then the command should succeed
    And the output should be valid JSONL

  Scenario: Every line has all frontmatter fields
    When I run ticket-query-all
    Then the command should succeed
    And every JSONL line should have field "id"
    And every JSONL line should have field "status"
    And every JSONL line should have field "deps"
    And every JSONL line should have field "links"
    And every JSONL line should have field "type"
    And every JSONL line should have field "priority"
    And every JSONL line should have field "created"

  Scenario: Includes title extracted from heading
    When I run ticket-query-all
    Then the command should succeed
    And every JSONL line should have field "title"
    And the JSONL output should contain a title "Assess if plant needs repotting"

  Scenario: Includes body field
    When I run ticket-query-all
    Then the command should succeed
    And every JSONL line should have field "body"

  Scenario: Body contains ticket content
    When I run ticket-query-all
    Then the command should succeed
    And the JSONL output for ticket "env-quy6" should have body containing "roots circling"

  Scenario: Ticket with empty body has empty string
    When I run ticket-query-all
    Then the command should succeed
    And the JSONL output for ticket "env-b0wz" should have empty body

  Scenario: Arrays are proper JSON arrays
    When I run ticket-query-all
    Then the command should succeed
    And the JSONL deps field should be a JSON array
    And the JSONL links field should be a JSON array
    And the JSONL tags field should be a JSON array

  Scenario: Priority is a number
    When I run ticket-query-all
    Then the command should succeed
    And the JSONL priority field should be a number

  Scenario: jq filter argument works
    When I run ticket-query-all with filter '.id == "env-quy6"'
    Then the command should succeed
    And the output should contain "env-quy6"
    And the output should not contain "env-3w68"

  Scenario: Empty tickets directory produces no output
    Given an empty tickets directory
    When I run ticket-query-all
    Then the command should succeed
    And the output should be empty
