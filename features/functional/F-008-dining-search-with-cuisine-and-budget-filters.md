# F-008: Dining Search with Cuisine and Budget Filters

## Type
Functional

## Description
The Dining Agent searches restaurants with availability, cuisine, and budget filters, using dedicated restaurant search tools.

## Requirement Trace
- Source File: docs/architecture.md
- Source Reference: Specialist Agents > Dining Agent responsibilities.
- Source File: docs/langgraph-design.md
- Source Reference: Dining Agent tools (`RestaurantSearchTool`) and memory default behavior for cuisine.

## Notes
- When cuisine preference is missing, the agent returns diverse results.
