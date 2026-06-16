from __future__ import annotations

from src.graph.main_graph import OrchestratorGraph
from src.services.routing_service import RoutingRecordService


def _request(message: str, request_id: str) -> dict[str, object]:
    return {
        "request_id": request_id,
        "user_id": "u-workflow",
        "session_id": "s-workflow",
        "message": message,
        "metadata": {},
    }


def test_orchestrator_is_first_handler_for_all_accepted_domains() -> None:
    service = RoutingRecordService()
    graph = OrchestratorGraph(routing_service=service)

    checks = [
        ("Schedule calendar invite", "calendar"),
        ("Search travel flights", "travel"),
        ("Book dining reservation", "dining"),
        ("Get news article summary", "news"),
        ("Just chat with me", "companion"),
    ]

    for index, (message, expected_domain) in enumerate(checks, start=1):
        response = graph.run_orchestrator_ingress(_request(message, f"req-workflow-{index}"))
        assert response["initial_handler"] == "orchestrator"
        assert response["routed_to"] == expected_domain
        assert response["status"] == "succeeded"
