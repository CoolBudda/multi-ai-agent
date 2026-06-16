# Feature Specification: Orchestrator Single Entry Point

**Feature Branch**: `001-orchestrator-entry-point`

**Created**: 2026-06-16

**Status**: Draft

**Input**: User description: "The system accepts all incoming user requests through a central Orchestrator Agent. Specialist agents are not directly exposed to clients."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Route All Requests Through Orchestrator (Priority: P1)

As an end user, I submit any assistant request through one public entry path and receive a valid response without needing to know which specialist capability handles it.

**Why this priority**: This is the core behavior that enforces policy, consistency, and routing control.

**Independent Test**: Can be fully tested by submitting multiple request types through the public entry path and verifying every request is accepted by the Orchestrator flow and returns a response.

**Acceptance Scenarios**:

1. **Given** a user sends a calendar-related request, **When** the request reaches the system, **Then** the Orchestrator receives the request first and routes it for handling.
2. **Given** a user sends a travel-related request, **When** the request reaches the system, **Then** the Orchestrator receives the request first and routes it for handling.
3. **Given** a user request has no domain above the configured confidence threshold, **When** intent detection completes, **Then** the Orchestrator routes the request to the Companion handler.

---

### User Story 2 - Prevent Direct Specialist Access (Priority: P2)

As a platform operator, I need specialist agents to be inaccessible to clients so all policy, safety, and governance checks occur at the Orchestrator entry point.

**Why this priority**: This prevents policy bypass and inconsistent behavior.

**Independent Test**: Can be fully tested by attempting direct client access to specialist entry points and verifying access is denied while Orchestrator access remains available.

**Acceptance Scenarios**:

1. **Given** a client attempts to invoke a specialist agent directly, **When** the request is submitted, **Then** the system rejects the attempt with a user-facing message indicating only the central entry path is supported.
2. **Given** a client uses the approved entry path for the same intent, **When** the request is submitted, **Then** the request is accepted and processed through the Orchestrator.

---

### User Story 3 - Preserve Request Traceability (Priority: P3)

As an operations analyst, I need each request to have a traceable routing record showing it entered through the Orchestrator so audits and incident reviews can validate policy compliance.

**Why this priority**: Traceability is required to prove governance compliance and diagnose routing issues.

**Independent Test**: Can be fully tested by submitting requests and verifying each one has a routing record that identifies the Orchestrator as the initial handler.

**Acceptance Scenarios**:

1. **Given** a request is processed successfully, **When** routing records are reviewed, **Then** the record identifies the Orchestrator as the first processing step.
2. **Given** a request fails during downstream handling, **When** routing records are reviewed, **Then** the record still identifies the Orchestrator as the first processing step.

### Edge Cases

- A request has ambiguous intent and does not clearly match a specialist domain.
- A malformed or incomplete request is submitted through the public entry path.
- A legacy client still attempts to call a specialist endpoint that existed previously.
- A downstream specialist is temporarily unavailable after Orchestrator routing begins.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept all client-initiated assistant requests only through the Orchestrator entry path.
- **FR-002**: The system MUST ensure the Orchestrator is the first processing component for every accepted request.
- **FR-003**: The system MUST prevent client access to specialist agents as standalone entry points.
- **FR-004**: When a client attempts direct specialist access, the system MUST return a clear user-facing rejection and no specialist processing may start.
- **FR-005**: The system MUST preserve current user-facing capability coverage by routing requests from the Orchestrator to the appropriate specialist behavior.
- **FR-006**: The system MUST create a request-level routing record that can demonstrate the initial handling step for every request.
- **FR-007**: Routing records MUST be available for both successful and failed requests.
- **FR-008**: If downstream handling fails after Orchestrator intake, the system MUST return a user-facing failure message and retain the routing record.
- **FR-009**: The system MUST apply routing and policy controls consistently across all supported request domains.
- **FR-010**: If no specialist domain exceeds the configured intent confidence threshold, the system MUST route the request to the Companion handler as the default fallback.

### Constitution Alignment *(mandatory)*

- Orchestrator-first routing is the primary behavior: no client path may bypass the Orchestrator.
- Domain ownership remains unchanged: this feature only governs ingress routing and does not shift specialist business responsibilities.
- Cross-domain coordination remains event-driven after Orchestrator intake; no direct client-to-specialist interactions are allowed.
- This feature does not introduce new memory dependencies; existing memory retrieval behavior in specialist flows remains unchanged.
- Tests must verify ingress behavior, specialist access restrictions, and request traceability for both success and failure paths.

### Key Entities *(include if feature involves data)*

- **Client Request**: A user-submitted input containing message content, user/session identifiers, and request metadata.
- **Routing Decision**: A record of the Orchestrator's selected handling path for a given client request.
- **Routing Record**: An auditable trace entry showing request entry point, initial handler, routing outcome, and final status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of accepted client requests are recorded as entering through the Orchestrator as the first handling step in a stratified sample of at least 200 accepted requests per release candidate (minimum 40 per supported domain).
- **SC-002**: 100% of attempted direct specialist client calls are rejected without specialist execution during validation testing.
- **SC-003**: At least 95% of requests complete successfully through Orchestrator-managed routing during a 1-hour validation run at 50 requests/minute with no injected downstream faults and service error rate <= 2%.
- **SC-004**: 100% of sampled failed requests retain a routing record that identifies the Orchestrator as initial handler and includes final failure status.

## Assumptions

- Existing specialist capabilities and domain boundaries remain in place; this feature changes ingress control only.
- Existing client integrations can use the designated Orchestrator entry path.
- Existing routing policy and intent handling rules remain valid unless separately revised.
- Existing operational logging and review workflows can consume the routing records defined by this feature.
