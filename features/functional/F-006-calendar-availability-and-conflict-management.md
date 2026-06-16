# F-006: Calendar Availability and Conflict Management

## Type
Functional

## Description
The Calendar Agent parses time expressions, checks availability, detects conflicts, and generates meeting proposals via Outlook calendar tooling.

## Requirement Trace
- Source File: docs/architecture.md
- Source Reference: Specialist Agents > Calendar Agent responsibilities and Outlook/Microsoft Graph integration.
- Source File: docs/langgraph-design.md
- Source Reference: Calendar Agent subgraph and `OutlookCalendarTool` definition.

## Notes
- Calendar operations are handled in the specialist subgraph and tool layer.
