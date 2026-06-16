# Phase 0 Research - Intent Detection and Agent Routing

## Clarification Resolution Log

### 1) Deterministic tie handling when scores are nearly equal
- Decision: Treat top scores as tied when `abs(top1 - top2) <= 0.03`, then resolve using fixed specialist precedence `calendar > travel > dining > news`.
- Rationale: Matches clarified functional requirements (`FR-004`, `FR-004a`) and prevents non-deterministic destination drift near confidence boundaries.
- Alternatives considered: Random tie resolution; last-winner sticky routing; lexical ordering. Rejected because they are either non-deterministic or operationally opaque.

### 2) Confidence threshold evaluation model
- Decision: Route to a specialist only when the selected specialist confidence is strictly greater than the configured threshold. Otherwise route to companion fallback.
- Rationale: Aligns with feature wording ("exceeds threshold") and preserves safe fallback behavior for uncertain classification.
- Alternatives considered: Greater-than-or-equal comparison; per-domain thresholds. Rejected to avoid boundary ambiguity and configuration complexity for this feature scope.

### 3) Routing rationale trace requirements
- Decision: Persist routing rationale in orchestrator request context with the following minimum fields: candidate confidences, threshold value, tie-window check, tie-break outcome, selected destination, and fallback flag.
- Rationale: Satisfies `FR-005` traceability and supports deterministic replay verification (`SC-003`).
- Alternatives considered: Free-form textual log only; destination-only record. Rejected because they are insufficient for audit and regression debugging.

### 4) Scope boundary with multi-domain routing
- Decision: Keep this feature strictly single-destination routing; do not invoke parallel multi-domain orchestration here.
- Rationale: Feature assumptions explicitly defer multi-domain behavior to a separate feature and avoid requirement overlap.
- Alternatives considered: Opportunistic dual-domain invocation when scores are close. Rejected because it violates "exactly one route" requirements for this feature.

### 5) Integration boundary with specialist execution and service layer
- Decision: Orchestrator emits a single routing decision event/context object and dispatches one target agent through existing orchestration interfaces; specialists remain unchanged.
- Rationale: Preserves constitution principles for orchestrator-first control and domain isolation via service boundaries.
- Alternatives considered: Let specialists self-evaluate intent confidence; direct cross-agent handoff. Rejected due to boundary and governance violations.

## Best-Practice Findings Applied

- Keep routing policy centralized and typed in orchestrator state models.
- Encode threshold, tie-window, and precedence as explicit configuration constants with deterministic unit tests.
- Treat companion fallback as a first-class route with rationale capture, not an exception path.
- Record machine-readable rationale data for each routing decision to support replay and audit.

## Unresolved Clarifications

None. All technical context and requirement ambiguities for planning are resolved.

## Operator Notes (Finalized Behavior)

- Specialist routing requires strict threshold exceedance (`selected_confidence > 0.60`).
- Near-tie detection uses `tie_window = 0.03` for the top confidence delta.
- Tie precedence is fixed and deterministic: `calendar > travel > dining > news`.
- Companion fallback is selected only when no specialist exceeds threshold.
- Routing records persist a policy snapshot per request (`threshold`, `tie_window`, `precedence_order`) for replay and audits.
- Routing decision events and routing record lifecycle events use stable event names in `<domain>.<action>.<status>` format.
