from __future__ import annotations

from src.api.routes.chat import post_agent_invoke
from src.graph.main_graph import OrchestratorGraph
from src.services.routing_service import RoutingRecordService


def _graph() -> OrchestratorGraph:
    return OrchestratorGraph(routing_service=RoutingRecordService())


def test_direct_specialist_invocation_is_denied_for_each_domain() -> None:
    for domain in ["calendar", "travel", "dining", "news", "companion"]:
        status, body = post_agent_invoke(
            domain,
            {"request_id": f"req-deny-{domain}"},
            orchestrator_graph=_graph(),
        )
        assert status == 403
        assert body["error_code"] == "direct_specialist_access_denied"
        assert "Orchestrator" in body["message"]


def test_direct_specialist_denial_does_not_execute_specialist_dispatch() -> None:
    service = RoutingRecordService()
    graph = OrchestratorGraph(routing_service=service)

    status, body = post_agent_invoke(
        "travel",
        {"request_id": "req-no-dispatch"},
        orchestrator_graph=graph,
    )

    record = service.get_record("req-no-dispatch")
    assert status == 403
    assert body["error_code"] == "direct_specialist_access_denied"
    assert record is not None
    assert record["status"] == "rejected"
