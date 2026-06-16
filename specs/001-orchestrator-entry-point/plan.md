# Implementation Plan: Orchestrator Single Entry Point

**Branch**: `001-orchestrator-entry-point` | **Date**: 2026-06-16 | **Spec**: `/specs/001-orchestrator-entry-point/spec.md`

**Input**: Feature specification from `/specs/001-orchestrator-entry-point/spec.md`

## Summary

Enforce a single client ingress through the Orchestrator so every accepted request is first handled by Orchestrator, specialist direct access is rejected, and routing traceability is recorded for success and failure outcomes. Implementation will add an explicit orchestrator ingress contract, direct-specialist access rejection behavior, and request-level routing records aligned to event naming and existing service boundaries.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript 5.x (frontend), HCL/Terraform (infra)

**Primary Dependencies**: LangGraph/LangChain patterns, pytest, Next.js 16, React 19, Tailwind CSS 4, AWS ECS/Fargate/ALB/EventBridge, Microsoft 365 service integration via service layer

**Storage**: DynamoDB-backed user preference storage through memory service; request routing records via structured runtime events/logs (final sink implementation in execution phase)

**Testing**: pytest for backend service/agent/workflow tests; webapp lint/build checks

**Target Platform**: AWS-hosted Linux container runtime (ECS Fargate) with Next.js web client

**Project Type**: Multi-component web application (Python agent service + Next.js frontend + Terraform infrastructure)

**Performance Goals**: Preserve normal operating behavior target from spec (>=95% sampled request success under normal conditions) while enforcing 100% orchestrator-first accepted ingress and 100% specialist direct-access rejection in validation tests

**Constraints**: No client bypass of Orchestrator; no specialist business-domain ownership changes; no direct agent-to-agent calls; event naming must remain `<domain>.<action>.<status>`; write-side operations continue through approval service

**Scale/Scope**: Feature applies to all supported domains (calendar/travel/dining/news/companion) and all client-initiated request paths

**User Context Note**: User-provided context was "I am building with..." (incomplete). Stack details are resolved from repository documentation and dependency manifests.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Phase 0 Gate Review

- [x] Routing gate: plan explicitly enforces Orchestrator as sole client ingress and rejects specialist direct entry.
- [x] Boundary gate: design keeps domain logic inside specialist agents and routes shared concerns through services.
- [x] Side-effect gate: design keeps event-driven flow and does not bypass approval requirements for write actions.
- [x] Memory gate: specialist memory retrieval behavior remains unchanged and continues to use defaults.
- [x] Quality gate: typed models/contracts and dedicated validation tests are included in design artifacts.

### Post-Phase 1 Re-Check

- [x] Routing gate: data model and API contract represent orchestrator-first intake plus specialist endpoint rejection.
- [x] Boundary gate: data model separates routing artifacts from domain execution ownership.
- [x] Side-effect gate: quickstart and contracts preserve evented transitions and rejection signaling.
- [x] Memory gate: no new memory dependencies introduced; specialist startup memory flow remains intact.
- [x] Quality gate: artifacts define contract, validation scenarios, and testable outcomes tied to FR/SC criteria.

## Project Structure

### Documentation (this feature)

```text
specs/001-orchestrator-entry-point/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── orchestrator-ingress.openapi.yaml
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

**Structure Decision**: Use the existing multi-component architecture (agent service + webapp + Terraform) and confine this feature's implementation changes to ingress API/graph boundaries, shared routing event models, and mirrored backend tests.

## Complexity Tracking

No constitution violations or governance exceptions are required for this plan.
