# F-009: News Topic Search and Summary

## Type
Functional

## Description
The News Agent retrieves news, supports topic-based search, and returns summarized content using a dedicated news tool.

## Requirement Trace
- Source File: docs/architecture.md
- Source Reference: Specialist Agents > News Agent responsibilities.
- Source File: docs/langgraph-design.md
- Source Reference: News Agent tools (`NewsSearchTool`) and memory defaults for `news_topics`.

## Notes
- If topics are absent, the agent returns general top headlines.
