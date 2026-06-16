# F-007: Travel Flight Search with User Preferences

## Type
Functional

## Description
The Travel Agent performs flight search and travel recommendations while applying stored user preferences and calendar constraints.

## Requirement Trace
- Source File: docs/architecture.md
- Source Reference: Specialist Agents > Travel Agent responsibilities and inputs.
- Source File: docs/langgraph-design.md
- Source Reference: Travel Agent tools (`FlightSearchTool`) and memory defaults for airline/seat preference.

## Notes
- Calendar coordination is routed through the Orchestrator, not direct agent-to-agent calls.
