from __future__ import annotations

from dataclasses import dataclass

from src.models.events import build_routing_decision_computed_event, now_iso
from src.models.state import OrchestratorRequest, RoutingDecision, SupportedDomain

DEFAULT_CONFIDENCE_THRESHOLD = 0.6

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
	confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> tuple[RoutingDecision, dict[str, object]]:
	message = request["message"].lower()
	target_domain, confidence, rationale = _detect_target_domain(message)
	fallback_applied = confidence < confidence_threshold

	if fallback_applied:
		target_domain = "companion"
		rationale = "No specialist confidence exceeded threshold; defaulted to companion."

	decision: RoutingDecision = {
		"request_id": request["request_id"],
		"initial_handler": "orchestrator",
		"target_domain": target_domain,
		"confidence": confidence,
		"fallback_applied": fallback_applied,
		"rationale": rationale,
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
		"domain": decision["target_domain"],
		"text": f"Handled by {decision['target_domain']} for request {request['request_id']}.",
	}


def _detect_target_domain(message: str) -> tuple[SupportedDomain, float, str]:
	scored: list[tuple[SupportedDomain, float]] = []
	for domain, patterns in _DOMAIN_PATTERNS.items():
		if not patterns:
			continue
		score = sum(1.0 for pattern in patterns if pattern in message)
		if score > 0:
			scored.append((domain, min(0.95, 0.35 + (score * 0.25))))

	if not scored:
		return "companion", 0.3, "No domain-specific signal detected."

	top_domain, top_score = sorted(scored, key=lambda item: item[1], reverse=True)[0]
	return top_domain, top_score, f"Detected {top_domain} intent by keyword signals."
