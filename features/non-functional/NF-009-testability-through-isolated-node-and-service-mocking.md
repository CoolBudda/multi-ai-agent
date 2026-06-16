# NF-009: Testability Through Isolated Node and Service Mocking

## Type
Non-Functional

## Description
Testing must use isolated node-level tests with Pytest fixtures and mocked service-layer dependencies, avoiding live external API calls in unit tests.

## Requirement Trace
- Source File: docs/langgraph-design.md
- Source Reference: Testing Conventions section.

## Notes
- State fixture setup is explicitly documented with `AssistantState` baseline.
