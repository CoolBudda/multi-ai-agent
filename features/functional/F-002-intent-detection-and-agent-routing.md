# F-002: Intent Detection and Agent Routing

## Type
Functional

## Description
The Orchestrator classifies user requests by domain and routes each request to the appropriate specialist agent. Routing is based on detected intent and confidence.

## Requirement Trace
- Source File: docs/langgraph-design.md
- Source Reference: Main Graph (`detect_intent`, `route_request`); `detect_intent_node` and `route_request_node` definitions.

## Notes
- Falls back to companion when no domain exceeds the confidence threshold.
