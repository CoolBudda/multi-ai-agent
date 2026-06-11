---
description: "Transform requirements into one spec file per feature"
agent: "agent"
argument-hint: "requirements file path and optional output folder"
---
Transform the requirements document into a set of feature spec files.

Use the provided requirements file as the source of truth. Identify each distinct feature area and create one Markdown spec file per feature using the fixed schema below.

Input assumptions:
- The requirements document is the primary source.
- Do not invent features that are not supported by the requirements.
- If a requirement is ambiguous, preserve the ambiguity in an "Open Questions" section instead of guessing.
- Keep the spec set consistent across features.

Each spec MUST follow this template:

## Purpose
## Scope
## Requirements
## Inputs
## Outputs
## Business Rules
## Workflow
## Data Model
## Error Handling
## Acceptance Criteria
## Open Questions

Output rules:
- Create one spec file per feature.
- Use clear, stable file names derived from the feature name.
- Preserve the language and intent of the requirements.
- Include only information supported by the requirements document.
- Keep each spec focused on a single feature boundary.
- If a feature spans frontend, backend, and infrastructure concerns, include all of them in the same feature spec rather than splitting them arbitrarily.
- If the requirements imply cross-cutting concerns such as safety, memory, or deployment, capture them in the relevant feature specs inside the most appropriate template section.

Suggested file organization:
- Place generated specs in a `specs/` folder.
- Use Markdown for all output files.

When you finish, summarize which spec files were created and note any unresolved ambiguities that were carried into Open Questions.