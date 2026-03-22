Feature: Archive
  As a user
  I want to move closed tickets to an archive directory
  So that my active tickets directory stays clean

  Background:
    Given the test tickets directory

  Scenario: Archives closed tickets
    Given ticket "env-quy6" has status "closed"
    And ticket "env-3w68" has status "closed"
    When I run ticket-archive
    Then the command should succeed
    And the output should contain "Archived env-quy6"
    And the output should contain "Archived env-3w68"
    And the output should contain "Archived env-90ef"
    And the output should contain "3 ticket(s) archived"
    And ticket "env-quy6" should exist in the archive
    And ticket "env-3w68" should exist in the archive
    And ticket "env-90ef" should exist in the archive
    And ticket "env-quy6" should not exist in the tickets directory
    And ticket "env-3w68" should not exist in the tickets directory

  Scenario: Does not archive open tickets
    Given ticket "env-quy6" has status "closed"
    When I run ticket-archive
    Then the command should succeed
    And ticket "env-quy6" should exist in the archive
    And ticket "env-5c1o" should not exist in the archive
    And ticket "env-5c1o" should exist in the tickets directory

  Scenario: No closed tickets
    Given ticket "env-90ef" has status "open"
    When I run ticket-archive
    Then the command should succeed
    And the output should contain "No closed tickets to archive"
    And the archive directory should not exist

  Scenario: Creates archive directory on first use
    Given ticket "env-quy6" has status "closed"
    When I run ticket-archive
    Then the command should succeed
    And the archive directory should exist

  Scenario: Archived ticket file is intact
    Given ticket "env-quy6" has status "closed"
    When I run ticket-archive
    Then the command should succeed
    And the archived ticket "env-quy6" should contain "status: closed"
    And the archived ticket "env-quy6" should contain "Assess if plant needs repotting"

  Scenario: Running archive twice is idempotent
    Given ticket "env-quy6" has status "closed"
    When I run ticket-archive
    And I run ticket-archive
    Then the command should succeed
    And the output should contain "No closed tickets to archive"
