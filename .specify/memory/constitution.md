<!--
Sync Impact Report
- Version change: N/A -> 1.0.0
- Modified principles:
	- N/A (initial ratification) -> I. Orchestrator-First Routing
	- N/A (initial ratification) -> II. Domain Isolation via Services
	- N/A (initial ratification) -> III. Evented Side Effects + Approval Gate
	- N/A (initial ratification) -> IV. Memory-First Context with Safe Defaults
	- N/A (initial ratification) -> V. Typed, Tested, Deterministic Delivery
- Added sections:
	- Implementation Constraints
	- Delivery Workflow & Quality Gates
- Removed sections:
	- None
- Templates requiring updates:
	- ✅ .specify/templates/plan-template.md
	- ✅ .specify/templates/spec-template.md
	- ✅ .specify/templates/tasks-template.md
	- ⚠ pending: .specify/templates/commands/*.md (directory not present)
- Follow-up TODOs:
	- None
-->

# Speckit-Magent Constitution

## Core Principles

### I. Orchestrator-First Routing
All user requests MUST enter through the Orchestrator. Specialist agents MUST NOT be
invoked directly by API or UI layers. If intent confidence is below the configured
threshold for specialist routing, the request MUST be routed to the Companion agent as
the default fallback. Rationale: centralized routing enforces consistent policy,
fallback behavior, and observability.

### II. Domain Isolation via Services
Each specialist agent MUST own exactly one business domain and MUST NOT embed logic from
another domain. Shared capabilities (memory, approvals, event publishing, external API
clients) MUST be implemented in the service layer. Agent nodes SHOULD remain pure; all
external I/O MUST occur in tool nodes except memory retrieval at agent start via the
service layer. Rationale: domain ownership and service boundaries prevent hidden coupling.

### III. Evented Side Effects + Approval Gate
Cross-agent coordination MUST be event-driven, not direct agent-to-agent calls. Events
MUST use the naming pattern <domain>.<action>.<status>. Any real-world write operation
(calendar invite, booking, reservation, or equivalent side effect) MUST pass through the
Approval Service before execution. Rejected approvals MUST emit <domain>.<action>.rejected
and workflows MUST terminate without retry unless a new explicit user request is received.
Rationale: explicit events and approval gates reduce unsafe automation.

### IV. Memory-First Context with Safe Defaults
Calendar, Travel, Dining, and News agents MUST retrieve relevant user preferences from
the Memory Service at the start of execution through the service layer. If required
memory fields are absent, agents MUST continue with sensible defaults and MUST NOT block
execution. Agents SHOULD ask users for missing preferences only when response quality is
materially affected. Rationale: resilient behavior maintains flow without sacrificing
personalization.

### V. Typed, Tested, Deterministic Delivery
Python code MUST use explicit type hints, and agent state MUST use TypedDict or Pydantic
models. Feature changes that affect behavior MUST include or update tests in mirrored test
paths. Terraform changes MUST be spec-driven, modular under agenterrafrom/modules, and
validated with terraform validate plus a plan for the target environment. Sensitive values
MUST NOT be committed in plaintext. Rationale: type safety, repeatable tests, and
deterministic infrastructure reduce regressions and deployment risk.

## Implementation Constraints

- Backend runtime MUST target Python 3.12+ with LangGraph-based orchestration.
- Frontend MUST use Next.js App Router with strict TypeScript and Tailwind CSS utilities.
- Client-side server state MUST use TanStack Query; domain-local UI state MUST live in
	feature-scoped slices, while global slices remain in shared stores.
- All backend external integrations MUST be called through dedicated services, never
	directly from agent nodes.
- Service failures MUST emit <domain>.<action>.failed and return a user-facing recovery
	message; silent failure is prohibited.

## Delivery Workflow & Quality Gates

Work MUST proceed as Spec -> Plan -> Tasks -> Implementation.

- Each plan MUST pass a Constitution Check before Phase 0 research and after Phase 1
	design, with explicit evidence for all five principles.
- Each feature spec MUST include independent user stories, edge cases, functional
	requirements, and measurable success criteria.
- Tasks MUST be grouped by user story, include concrete file paths, and call out
	principle-driven work (events, approvals, service boundaries, tests).
- Pull requests MUST include test results relevant to the changed behavior and note any
	governance exceptions in a dedicated Complexity Tracking section.

## Governance

This constitution supersedes conflicting engineering practices in this repository.
Amendments require: (1) a documented proposal, (2) updates to impacted templates and
workflow docs, and (3) explicit version bump rationale.

Versioning policy (semantic):
- MAJOR: incompatible governance changes or principle removals/redefinitions.
- MINOR: new principle/section or materially expanded mandatory guidance.
- PATCH: wording clarifications, typo fixes, and non-semantic refinements.

Compliance review expectations:
- Every implementation plan and pull request MUST include a constitution compliance check.
- Exceptions MUST be time-boxed, documented, and approved in review.
- Governance and template alignment MUST be re-validated when constitution text changes.

**Version**: 1.0.0 | **Ratified**: 2026-06-16 | **Last Amended**: 2026-06-16
