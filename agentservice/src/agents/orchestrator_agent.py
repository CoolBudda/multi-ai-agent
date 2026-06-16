from __future__ import annotations

from dataclasses import dataclass

from src.models.events import build_routing_decision_computed_event, now_iso
from src.models.routing import default_routing_policy, resolve_routing
from src.models.state import CandidateScore, OrchestratorRequest, RoutingDecision, SupportedDomain

_DOMAIN_PATTERNS: dict[SupportedDomain, tuple[str, ...]] = {
	"calendar": ("meeting", "schedule", "availability", "calendar"),
	"travel": ("flight", "airline", "trip", "travel"),
	"dining": ("restaurant", "dining", "reservation", "table"),
	"news": ("news", "headline", "article", "topic"),
	"companion": (),
}


@dataclass(slots=True)
class OrchestratorDispatchError(RuntimeError):
	failure_code: str
	user_message: str


def compute_routing_decision(
	request: OrchestratorRequest,
	*,
	confidence_threshold: float | None = None,
) -> tuple[RoutingDecision, dict[str, object]]:
	message = request["message"].lower()
	policy = default_routing_policy()
	if confidence_threshold is not None:
		policy["specialist_threshold"] = confidence_threshold

	candidates = _score_supported_domains(message)
	resolution = resolve_routing(candidates, policy=policy)

	decision: RoutingDecision = {
		"request_id": request["request_id"],
		"selected_domain": resolution["selected_domain"],
		"selected_confidence": resolution["selected_confidence"],
		"threshold_passed": resolution["threshold_passed"],
		"tie_detected": resolution["tie_detected"],
		"tie_resolved_by_precedence": resolution["tie_resolved_by_precedence"],
		"fallback_to_companion": resolution["fallback_to_companion"],
		"rationale": {
			"threshold": policy["specialist_threshold"],
			"tie_window": policy["tie_window"],
			"top_candidates": resolution["top_candidates"],
			"reason_code": resolution["reason_code"],
			"tie_break_winner": resolution["tie_break_winner"],
		},
		"policy_snapshot": policy,
		"decided_at": now_iso(),
	}
	return decision, build_routing_decision_computed_event(decision)


def dispatch_to_target_domain(
	request: OrchestratorRequest,
	decision: RoutingDecision,
	*,
	force_failure: bool = False,
) -> dict[str, object]:
	if force_failure:
		raise OrchestratorDispatchError(
			failure_code="orchestrator.dispatch.failed",
			user_message="The request entered through the Orchestrator but could not be completed. Please retry.",
		)

	return {
		"domain": decision["selected_domain"],
		"text": f"Handled by {decision['selected_domain']} for request {request['request_id']}.",
	}


def _score_supported_domains(message: str) -> list[CandidateScore]:
	scored: list[CandidateScore] = []
	for domain, patterns in _DOMAIN_PATTERNS.items():
		if not patterns:
			continue
		hit_count = sum(1 for pattern in patterns if pattern in message)
		confidence = 0.0 if hit_count == 0 else min(0.95, 0.40 + (hit_count * 0.25))
		scored.append({"domain": domain, "confidence": confidence})

	# Companion is always selected via policy fallback, never scored as a specialist candidate.
	return scored
