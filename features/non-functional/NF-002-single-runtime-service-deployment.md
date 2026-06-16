# NF-002: Single Runtime Service Deployment

## Type
Non-Functional

## Description
All agents run inside a single backend ECS Fargate service hosting the LangGraph runtime to reduce deployment complexity and latency.

## Requirement Trace
- Source File: docs/deployment.md
- Source Reference: Overview and ECS Fargate Service sections.
- Source File: docs/architecture.md
- Source Reference: Runtime Architecture; "All agents execute inside the same backend service."

## Notes
- Documented benefits include simpler deployment and lower infrastructure cost.
