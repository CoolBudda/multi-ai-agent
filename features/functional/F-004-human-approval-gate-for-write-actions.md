# F-004: Human Approval Gate for Write Actions

## Type
Functional

## Description
The workflow applies an approval gate before executing operations that require human confirmation. Requests needing approval are paused and resumed after user decision.

## Requirement Trace
- Source File: docs/architecture.md
- Source Reference: Approval Service > Purpose and workflow.
- Source File: docs/langgraph-design.md
- Source Reference: Main Graph (`approval_gate`, `approval_node`) and `approval_node` behavior.

## Notes
- Approval state is tracked as pending, approved, or rejected.
