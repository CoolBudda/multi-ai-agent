from __future__ import annotations

from src.api.routes.chat import post_assistant_request
from src.graph.main_graph import OrchestratorGraph
from src.services.routing_service import RoutingRecordService


def _graph() -> OrchestratorGraph:
    return OrchestratorGraph(routing_service=RoutingRecordService())


def test_route_response_contains_contract_fields_for_successful_specialist_route() -> None:
    status, body = post_assistant_request(
        {
            "request_id": "req-contract-1",
            "user_id": "u-contract",
            "session_id": "s-contract",
            "message": "Schedule a meeting in my calendar",
            "metadata": {},
        },
        orchestrator_graph=_graph(),
    )

    assert status == 200
    assert body["request_id"] == "req-contract-1"
    assert body["selected_domain"] in {"calendar", "travel", "dining", "news", "companion"}
    assert isinstance(body["fallback_to_companion"], bool)
    assert isinstance(body["threshold_passed"], bool)
    assert isinstance(body["tie_detected"], bool)

    rationale = body["rationale"]
    assert isinstance(rationale["threshold"], float)
    assert rationale["tie_window"] == 0.03
    assert rationale["reason_code"] in {
        "highest_above_threshold",
        "tie_break_selected",
        "below_threshold_fallback",
    }
    assert len(rationale["top_candidates"]) >= 2


def test_route_response_routing_record_includes_decision_payload() -> None:
    service = RoutingRecordService()
    graph = OrchestratorGraph(routing_service=service)

    status, body = post_assistant_request(
        {
            "request_id": "req-contract-2",
            "user_id": "u-contract",
            "session_id": "s-contract",
            "message": "Find flight travel options",
            "metadata": {},
        },
        orchestrator_graph=graph,
    )

    record = service.get_record("req-contract-2")
    assert status == 200
    assert record is not None
    assert record["routing_decision"] is not None
    assert record["routing_decision"]["selected_domain"] == body["selected_domain"]


def test_route_response_contract_includes_fallback_reason_fields() -> None:
    status, body = post_assistant_request(
        {
            "request_id": "req-contract-fallback",
            "user_id": "u-contract",
            "session_id": "s-contract",
            "message": "hello",
            "metadata": {},
        },
        orchestrator_graph=_graph(),
    )

    assert status == 200
    assert body["selected_domain"] == "companion"
    assert body["fallback_to_companion"] is True
    assert body["rationale"]["reason_code"] == "below_threshold_fallback"
