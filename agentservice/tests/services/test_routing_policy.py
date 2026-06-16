from __future__ import annotations

from src.models.routing import default_routing_policy, resolve_routing


def test_resolve_routing_selects_highest_above_threshold() -> None:
    policy = default_routing_policy()
    resolution = resolve_routing(
        [
            {"domain": "calendar", "confidence": 0.82},
            {"domain": "travel", "confidence": 0.33},
            {"domain": "dining", "confidence": 0.12},
            {"domain": "news", "confidence": 0.18},
        ],
        policy=policy,
    )

    assert resolution["selected_domain"] == "calendar"
    assert resolution["threshold_passed"] is True
    assert resolution["fallback_to_companion"] is False
    assert resolution["reason_code"] == "highest_above_threshold"


def test_resolve_routing_uses_companion_fallback_when_below_threshold() -> None:
    policy = default_routing_policy()
    policy["specialist_threshold"] = 0.9

    resolution = resolve_routing(
        [
            {"domain": "calendar", "confidence": 0.62},
            {"domain": "travel", "confidence": 0.45},
            {"domain": "dining", "confidence": 0.19},
            {"domain": "news", "confidence": 0.08},
        ],
        policy=policy,
    )

    assert resolution["selected_domain"] == "companion"
    assert resolution["fallback_to_companion"] is True
    assert resolution["reason_code"] == "below_threshold_fallback"


def test_resolve_routing_applies_precedence_for_ties_within_window() -> None:
    policy = default_routing_policy()

    resolution = resolve_routing(
        [
            {"domain": "travel", "confidence": 0.88},
            {"domain": "calendar", "confidence": 0.87},
            {"domain": "dining", "confidence": 0.30},
            {"domain": "news", "confidence": 0.29},
        ],
        policy=policy,
    )

    assert resolution["tie_detected"] is True
    assert resolution["tie_resolved_by_precedence"] is True
    assert resolution["selected_domain"] == "calendar"
    assert resolution["reason_code"] == "tie_break_selected"
