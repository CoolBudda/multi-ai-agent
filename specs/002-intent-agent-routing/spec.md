# Feature Specification: Intent Detection and Agent Routing

**Feature Branch**: `[002-intent-agent-routing]`

**Created**: 2026-06-16

**Status**: Draft

**Input**: User description: "The Orchestrator classifies user requests by domain and routes each request to the appropriate specialist agent. Routing is based on detected intent and confidence. Falls back to companion when no domain exceeds the confidence threshold."

## Clarifications

### Session 2026-06-16

- Q: How should near-equal top confidence scores be handled? -> A: Treat scores as tied when the top two confidences differ by <= 0.03, then apply deterministic tie-break order.
- Q: What deterministic tie-break order should be used for tied specialist domains? -> A: Calendar > Travel > Dining > News; route to Companion only when no specialist exceeds threshold.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Route Requests to the Correct Specialist (Priority: P1)

As a user, I want my request to be interpreted and sent to the correct specialist agent so I receive a domain-appropriate answer without manual handoff.

**Why this priority**: Correct first-pass routing is the core value of orchestration and directly determines response relevance.

**Independent Test**: Can be fully tested by submitting representative single-domain requests and verifying they are routed to the expected specialist agent and return domain-relevant outcomes.

**Acceptance Scenarios**:

1. **Given** a user request clearly about scheduling, **When** the Orchestrator classifies intent, **Then** the request is routed to the Calendar specialist.
2. **Given** a user request clearly about flights, **When** the Orchestrator classifies intent, **Then** the request is routed to the Travel specialist.

---

### User Story 2 - Safe Fallback for Low Confidence (Priority: P2)

As a user, I want unclear or unsupported requests to still receive a helpful response instead of failure, by being routed to the Companion agent.

**Why this priority**: Reliable fallback prevents dead ends and preserves a continuous user experience when intent confidence is low.

**Independent Test**: Can be fully tested by submitting ambiguous or out-of-domain requests and verifying Companion is selected whenever no domain confidence passes the routing threshold.

**Acceptance Scenarios**:

1. **Given** a user request with low confidence across all specialist domains, **When** routing is evaluated, **Then** the request is routed to Companion.
2. **Given** an out-of-domain request, **When** routing is evaluated, **Then** Companion handles the request and no specialist is invoked.

---

### User Story 3 - Deterministic Routing Decisions (Priority: P3)

As an operator, I want routing outcomes to be deterministic for equivalent inputs so behavior is predictable, testable, and auditable.

**Why this priority**: Determinism reduces routing regressions and simplifies operational troubleshooting.

**Independent Test**: Can be tested by replaying equivalent requests and verifying the same routing decision and rationale are produced each time.

**Acceptance Scenarios**:

1. **Given** two equivalent user requests, **When** intent classification runs under the same configuration, **Then** both requests produce the same target agent decision.
2. **Given** multiple candidate domains near the confidence boundary, **When** routing applies threshold and tie rules, **Then** exactly one deterministic route is selected.

---

### Edge Cases

- User message is empty or effectively non-informative.
- Top two confidence scores are equal or differ by <= 0.03 and require deterministic tie-break ordering.
- The configured confidence threshold changes between deployments.
- Request includes mixed-topic wording but does not clearly satisfy multi-domain routing criteria.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST classify each incoming user request into the supported domain set and produce a confidence value for each candidate domain.
- **FR-002**: System MUST route a request to exactly one specialist agent when one domain exceeds the configured confidence threshold and is the highest-confidence match.
- **FR-003**: System MUST route a request to the Companion agent when no specialist domain exceeds the configured confidence threshold.
- **FR-004**: System MUST treat the top two confidence scores as tied when their absolute difference is <= 0.03, and MUST apply deterministic tie-breaking order when more than one domain is eligible.
- **FR-004a**: System MUST apply specialist tie-break precedence in this exact order when eligible domains are tied: Calendar, then Travel, then Dining, then News.
- **FR-005**: System MUST record the routing decision rationale (detected intent, confidence comparison, threshold outcome, and chosen destination) in request processing context for traceability.
- **FR-006**: System MUST not invoke specialist agents directly from client-facing layers; all routing decisions MUST be executed through the Orchestrator.
- **FR-007**: System MUST return a user-facing response path for every request, including fallback cases, without leaving requests unrouted.

### Constitution Alignment *(mandatory)*

- The feature preserves Orchestrator-first routing by requiring all classification and route selection to occur within the Orchestrator flow.
- Domain ownership boundaries remain explicit: specialists receive routed requests only for their own domain responsibilities.
- No new side-effecting actions are introduced by this feature; existing approval-gated write actions remain unchanged.
- Memory retrieval behavior for specialists remains unchanged; this feature only determines destination routing and does not block on memory availability.
- Routing behavior changes require typed state updates and test coverage for threshold handling, fallback behavior, and deterministic tie outcomes.

### Key Entities *(include if feature involves data)*

- **User Request**: Incoming user message plus context used for intent analysis.
- **Intent Classification**: Domain candidates with confidence values derived from a request.
- **Routing Decision**: Final destination agent and the rationale explaining threshold and tie-rule outcomes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 95% of representative in-scope requests are routed to the expected specialist domain on first pass.
- **SC-002**: 100% of requests with no domain above threshold are routed to Companion without user-visible failure.
- **SC-003**: 100% of replayed equivalent requests under the same configuration produce the same routing destination.
- **SC-004**: In user acceptance evaluation, at least 90% of users report their request was handled by the appropriate assistant path on first attempt.

## Validation Evidence

### Automated Evidence (2026-06-16)

- Command: `pytest tests/agents/test_orchestrator_agent.py tests/workflows/test_intent_routing_specialist.py tests/workflows/test_intent_routing_fallback.py tests/workflows/test_intent_routing_tie_break.py tests/workflows/test_routing_decision_record.py tests/api/test_orchestrator_route_contract.py tests/services/test_routing_policy.py -q`
- Result: `29 passed, 0 failed`

Mapped results:

- **SC-001**: PASS on automated specialist-routing suite (all in-scope specialist routing assertions passed).
- **SC-002**: PASS on fallback suite (all low-confidence/out-of-domain assertions routed to Companion).
- **SC-003**: PASS on deterministic replay and tie-break suites (equivalent inputs produced identical destination/rationale under fixed config).
- **SC-004**: Pending manual UAT measurement (requires user survey/acceptance sampling outside automated test scope).

## Assumptions

- Domain set includes Calendar, Travel, Dining, News, and Companion as fallback.
- Multi-domain parallel execution behavior is specified in a separate feature and is out of scope for this feature.
- A configurable confidence threshold already exists in orchestration configuration and can be applied consistently.
- Existing response generation can consume routing context without requiring new user-facing interaction patterns.
