from __future__ import annotations

from typing import TypedDict

from src.models.state import (
    CandidateScore,
    RoutingPolicySnapshot,
    RoutingReasonCode,
    SupportedDomain,
    SupportedSpecialistDomain,
)

SPECIALIST_THRESHOLD = 0.60
TIE_WINDOW = 0.03
SPECIALIST_PRECEDENCE: tuple[SupportedSpecialistDomain, ...] = (
    "calendar",
    "travel",
    "dining",
    "news",
)
FALLBACK_DOMAIN: SupportedDomain = "companion"


class RoutingResolution(TypedDict):
    selected_domain: SupportedDomain
    selected_confidence: float
    threshold_passed: bool
    tie_detected: bool
    tie_resolved_by_precedence: bool
    fallback_to_companion: bool
    reason_code: RoutingReasonCode
    top_candidates: list[CandidateScore]
    tie_break_winner: SupportedDomain | None


def default_routing_policy() -> RoutingPolicySnapshot:
    return {
        "specialist_threshold": SPECIALIST_THRESHOLD,
        "tie_window": TIE_WINDOW,
        "precedence_order": list(SPECIALIST_PRECEDENCE),
    }


def sort_candidates(candidates: list[CandidateScore]) -> list[CandidateScore]:
    return sorted(candidates, key=lambda item: (-item["confidence"], item["domain"]))


def resolve_routing(
    candidates: list[CandidateScore],
    *,
    policy: RoutingPolicySnapshot,
) -> RoutingResolution:
    ordered = sort_candidates(candidates)
    top_candidates = ordered[:2]
    top = ordered[0]

    tie_detected = False
    tie_resolved_by_precedence = False
    tie_break_winner: SupportedDomain | None = None
    selected_domain = top["domain"]
    selected_confidence = top["confidence"]

    if len(top_candidates) >= 2:
        delta = top_candidates[0]["confidence"] - top_candidates[1]["confidence"]
        tie_detected = delta <= policy["tie_window"]

    if tie_detected:
        tie_group = [
            candidate
            for candidate in ordered
            if (ordered[0]["confidence"] - candidate["confidence"]) <= policy["tie_window"]
            and candidate["domain"] in policy["precedence_order"]
        ]
        if tie_group:
            ranked_domains = {
                domain: index for index, domain in enumerate(policy["precedence_order"])
            }
            winner = sorted(tie_group, key=lambda item: ranked_domains[item["domain"]])[0]
            selected_domain = winner["domain"]
            selected_confidence = winner["confidence"]
            tie_break_winner = selected_domain
            tie_resolved_by_precedence = True

    threshold_passed = selected_domain != FALLBACK_DOMAIN and selected_confidence > policy["specialist_threshold"]
    fallback_to_companion = not threshold_passed

    if fallback_to_companion:
        selected_domain = FALLBACK_DOMAIN
        reason_code: RoutingReasonCode = "below_threshold_fallback"
    elif tie_resolved_by_precedence:
        reason_code = "tie_break_selected"
    else:
        reason_code = "highest_above_threshold"

    return {
        "selected_domain": selected_domain,
        "selected_confidence": selected_confidence,
        "threshold_passed": threshold_passed,
        "tie_detected": tie_detected,
        "tie_resolved_by_precedence": tie_resolved_by_precedence,
        "fallback_to_companion": fallback_to_companion,
        "reason_code": reason_code,
        "top_candidates": top_candidates,
        "tie_break_winner": tie_break_winner,
    }
