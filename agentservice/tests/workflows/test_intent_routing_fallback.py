from __future__ import annotations

from src.api.routes.chat import post_assistant_request
from src.graph.main_graph import OrchestratorGraph
from src.services.routing_service import RoutingRecordService


def test_ambiguous_request_routes_to_companion_with_fallback_reason() -> None:
    service = RoutingRecordService()
    graph = OrchestratorGraph(routing_service=service)

    status, body = post_assistant_request(
        {
            "request_id": "req-fallback-ambiguous",
            "user_id": "u-fallback",
            "session_id": "s-fallback",
            "message": "Can you maybe help me with something sometime",
            "metadata": {},
        },
        orchestrator_graph=graph,
    )

    record = service.get_record("req-fallback-ambiguous")
    assert status == 200
    assert body["selected_domain"] == "companion"
    assert body["fallback_to_companion"] is True
    assert body["rationale"]["reason_code"] == "below_threshold_fallback"
    assert record is not None
    assert record["routing_decision"] is not None
    assert record["routing_decision"]["selected_domain"] == "companion"


def test_out_of_domain_request_routes_to_companion() -> None:
    graph = OrchestratorGraph(routing_service=RoutingRecordService())

    status, body = post_assistant_request(
        {
            "request_id": "req-fallback-outdomain",
            "user_id": "u-fallback",
            "session_id": "s-fallback",
            "message": "What is the best strategy board game ever made?",
            "metadata": {},
        },
        orchestrator_graph=graph,
    )

    assert status == 200
    assert body["selected_domain"] == "companion"
    assert body["fallback_to_companion"] is True
    assert body["threshold_passed"] is False
