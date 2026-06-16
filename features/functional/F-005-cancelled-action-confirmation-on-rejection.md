# F-005: Cancelled Action Confirmation on Rejection

## Type
Functional

## Description
If a user rejects an approval request, the final response explicitly confirms cancellation and states that no changes were made.

## Requirement Trace
- Source File: docs/langgraph-design.md
- Source Reference: `approval_node` (rejected path) and `build_response_node` returning "Your request was cancelled. No changes were made."

## Notes
- Rejection also emits `<domain>.<action>.rejected` events.
