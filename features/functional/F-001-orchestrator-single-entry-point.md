# F-001: Orchestrator Single Entry Point

## Type
Functional

## Description
The system accepts all incoming user requests through a central Orchestrator Agent. Specialist agents are not directly exposed to clients.

## Requirement Trace
- Source File: docs/architecture.md
- Source Reference: Core Principles > Single Entry Point; "All requests enter through the Orchestrator Agent. No specialist agent is directly exposed to clients."

## Notes
- Enforces centralized routing and policy handling through one entry path.
