from __future__ import annotations

import re

from src.agents.orchestrator_agent import compute_routing_decision
from src.api.routes.chat import post_assistant_request
from src.graph.main_graph import OrchestratorGraph
from src.models.events import build_routing_decision_computed_event, build_routing_record_lifecycle_event
from src.services.routing_service import RoutingRecordService

EVENT_NAME_PATTERN = re.compile(r"^[a-z]+\.[a-z_]+\.[a-z_]+$")


def test_routing_record_contains_policy_snapshot_fields_for_traceability() -> None:
    service = RoutingRecordService()
    graph = OrchestratorGraph(routing_service=service)

    status, body = post_assistant_request(
        {
            "request_id": "req-record-policy",
            "user_id": "u-record",
            "session_id": "s-record",
            "message": "Schedule a meeting and flight",
            "metadata": {},
        },
        orchestrator_graph=graph,
    )

    record = service.get_record("req-record-policy")

    assert status == 200
    assert record is not None
    assert record["routing_decision"] is not None
    policy_snapshot = record["routing_decision"]["policy_snapshot"]
    assert policy_snapshot["specialist_threshold"] == 0.6
    assert policy_snapshot["tie_window"] == 0.03
    assert policy_snapshot["precedence_order"] == ["calendar", "travel", "dining", "news"]
    assert body["routing_record"]["routing_decision"]["policy_snapshot"] == policy_snapshot


def test_routing_event_names_follow_domain_action_status_format() -> None:
    request = {
        "request_id": "req-record-event",
        "user_id": "u-record",
        "session_id": "s-record",
        "message": "Find flight options",
        "metadata": {},
    }
    decision, _ = compute_routing_decision(request)
    decision_event = build_routing_decision_computed_event(decision)

    service = RoutingRecordService()
    record, _ = service.create_open_record(
        request_id="req-record-event",
        routed_to=decision["selected_domain"],
        routing_decision=decision,
        user_message="created",
    )
    lifecycle_event = build_routing_record_lifecycle_event(
        record,
        action="updated",
        status="succeeded",
    )

    assert EVENT_NAME_PATTERN.match(decision_event["event_name"]) is not None
    assert EVENT_NAME_PATTERN.match(lifecycle_event["event_name"]) is not None


def test_routing_decision_payload_ordering_is_deterministic_for_equivalent_inputs() -> None:
    base_request = {
        "user_id": "u-record",
        "session_id": "s-record",
        "message": "Schedule travel",
        "metadata": {},
    }

    decision_1, _ = compute_routing_decision({"request_id": "req-record-order-1", **base_request})
    decision_2, _ = compute_routing_decision({"request_id": "req-record-order-2", **base_request})

    assert decision_1["selected_domain"] == decision_2["selected_domain"]
    assert decision_1["rationale"]["top_candidates"] == decision_2["rationale"]["top_candidates"]
    assert decision_1["policy_snapshot"]["precedence_order"] == decision_2["policy_snapshot"]["precedence_order"]
