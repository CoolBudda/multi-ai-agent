# Phase 0 Research - Orchestrator Single Entry Point

## Clarification Resolution Log

### 1) Incomplete user stack context ("I am building with...")
- Decision: Use repository-defined stack as the technical baseline: Python 3.12+ and LangGraph for backend, Next.js/TypeScript for frontend, Terraform on AWS for infrastructure.
- Rationale: Repository architecture docs, README, and manifests already define the canonical stack and align with constitution constraints.
- Alternatives considered: Pause planning for user clarification; infer an entirely new stack. Both were rejected because existing project standards are explicit and sufficient for planning.

### 2) Client ingress contract shape for orchestrator-only routing
- Decision: Define a single public POST endpoint for assistant requests and explicitly define specialist direct-invocation attempts as forbidden with a clear user-facing rejection message.
- Rationale: Directly satisfies FR-001 to FR-004 and SC-001/SC-002 with a testable API-level boundary.
- Alternatives considered: Soft deprecation of specialist endpoints; network-only deny rules without application-level message. Rejected because acceptance criteria requires clear user-facing rejection and deterministic behavior.

### 3) Routing traceability implementation boundary
- Decision: Introduce a dedicated routing record model (request id, initial handler, route target, outcome status, failure reason) and require creation at orchestrator intake for both success and failure paths.
- Rationale: Satisfies FR-006 to FR-008 and SC-004 while remaining implementation-agnostic about the final persistence sink.
- Alternatives considered: Rely on ad hoc logs only; emit trace only on success. Rejected due to auditability gaps and explicit failure-path requirement.

### 4) Event naming compatibility with constitution
- Decision: Keep event naming aligned to `<domain>.<action>.<status>` and model orchestrator ingress events under an `orchestrator` domain.
- Rationale: Preserves constitution principle III and keeps operational telemetry predictable.
- Alternatives considered: Generic non-domain event labels. Rejected because they weaken consistency and governance checks.

### 5) Scope of changes across backend/frontend/infra
- Decision: Limit this feature to backend ingress/routing boundaries and tests; avoid mandatory frontend or Terraform schema changes in plan scope unless implementation reveals strict dependency.
- Rationale: Feature requirements target routing behavior and access control, not deployment topology or UI redesign.
- Alternatives considered: Include broad webapp and infrastructure changes in this feature. Rejected as unnecessary scope expansion and higher risk.

## Best-Practice Findings Applied

- Keep specialist agent responsibilities unchanged; only orchestrator ingress and routing governance is modified.
- Preserve service-layer boundaries for memory/approval/external integrations.
- Encode rejection behavior and routing traceability in typed models and tests, not only in prose.
- Validate both accepted and rejected ingress paths with independent tests.

## Unresolved Clarifications

None. All technical context placeholders have been resolved using repository standards and feature requirements.
