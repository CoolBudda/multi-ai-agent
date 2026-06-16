# Implementation Plan: Intent Detection and Agent Routing

**Branch**: `initial` | **Date**: 2026-06-16 | **Spec**: `/specs/002-intent-agent-routing/spec.md`

**Input**: Feature specification from `/specs/002-intent-agent-routing/spec.md`

## Summary

Implement deterministic, single-destination intent routing in the Orchestrator by evaluating domain confidence scores against a configurable threshold, applying a tie window of `<= 0.03`, and enforcing fixed specialist precedence (`calendar > travel > dining > news`) before companion fallback. The design introduces typed routing decision artifacts, explicit rationale logging fields, and contract-level behavior for threshold/fallback/tie outcomes.

## Technical Context

**Language/Version**: Python 3.12+ (agent backend), TypeScript 5.x (webapp), HCL/Terraform (infra)

**Primary Dependencies**: LangGraph/StateGraph orchestration patterns, LangChain tool conventions, pytest, Next.js App Router, AWS EventBridge-oriented event signaling via service layer

**Storage**: Existing runtime state + service-backed persistence/logging for routing rationale; no new datastore introduced by this feature

**Testing**: pytest (agent/workflow/service tests), plus existing CI lint/type checks

**Target Platform**: Linux containers on AWS ECS Fargate for backend runtime; Next.js web client for user ingress

**Project Type**: Multi-component web platform (Python orchestration service + Next.js frontend + Terraform infrastructure)

**Performance Goals**: Preserve current latency envelope for routing step while meeting spec success targets (>=95% expected first-pass in-scope routing, 100% low-confidence fallback, 100% deterministic replay under fixed config)

**Constraints**: Orchestrator-only ingress, no specialist direct invocation from client layers, deterministic tie handling, companion fallback when no specialist exceeds threshold, rationale trace must be recorded for each request

**Scale/Scope**: Applies to all single-domain requests across calendar/travel/dining/news plus companion fallback; explicitly excludes multi-domain parallel orchestration behavior (covered by separate feature)

## Routing Constants (Feature 002)

The implementation and tests for this feature must use the following deterministic policy constants:

- `SPECIALIST_THRESHOLD = 0.60` (specialist confidence must be strictly greater than threshold)
- `TIE_WINDOW = 0.03` (top-confidence delta `<= 0.03` is treated as a tie)
- `SPECIALIST_PRECEDENCE = ["calendar", "travel", "dining", "news"]`
- `FALLBACK_DOMAIN = "companion"` when no specialist exceeds threshold

These constants are intentionally feature-scoped and are mirrored in contract and workflow validation to avoid configuration drift.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Phase 0 Gate Review

- [x] Routing gate: design keeps all intent detection and routing in Orchestrator; no direct specialist entry points are introduced.
- [x] Boundary gate: intent scoring/routing logic stays in orchestrator path; domain-specific business logic remains in specialist agents.
- [x] Side-effect gate: this feature changes routing only and does not bypass evented side-effect + approval requirements.
- [x] Memory gate: specialist memory retrieval/startup defaults are unchanged; routing does not block on memory fields.
- [x] Quality gate: typed routing artifacts, deterministic rule tests, and explicit rationale capture are planned.

### Post-Phase 1 Re-Check

- [x] Routing gate: data model and contract enforce a single resolved destination per request with companion fallback.
- [x] Boundary gate: routing decision model is orchestrator-scoped and does not shift domain ownership.
- [x] Side-effect gate: contracts/quickstart preserve event naming and do not add unapproved write paths.
- [x] Memory gate: artifacts confirm no new memory prerequisites; specialists continue safe-default behavior.
- [x] Quality gate: research resolves technical unknowns and defines testable threshold/tie/fallback scenarios.

## Project Structure

### Documentation (this feature)

```text
specs/002-intent-agent-routing/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── orchestrator-intent-routing.openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
agentservice/
├── src/
│   ├── agents/
│   ├── api/
│   ├── graph/
│   ├── models/
│   ├── services/
│   └── tools/
└── tests/
    ├── agents/
    ├── services/
    ├── tools/
    └── workflows/

webapp/
└── src/
    ├── app/
    ├── features/
    ├── lib/
    └── types/

agenterrafrom/
├── modules/
└── environments/dev/
```

**Structure Decision**: Keep the established multi-component repository layout. This feature is backend-orchestrator centric and will primarily touch agent service routing/state/tests while preserving existing frontend and Terraform boundaries.

## Complexity Tracking

No constitution violations or governance exceptions are required for this plan.
