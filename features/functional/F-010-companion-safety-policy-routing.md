# F-010: Companion Safety/Policy Routing

## Type
Functional

## Description
The Companion flow routes sensitive request categories (such as mental health distress signals, medical/legal advice requests, political opinion generation, and policy-risk content) to a Safety/Policy layer before LLM response.

## Requirement Trace
- Source File: docs/langgraph-design.md
- Source Reference: Companion Agent section specifying safety/policy routing conditions.

## Notes
- Companion uses LLM-only tooling by default unless future tools are added.
