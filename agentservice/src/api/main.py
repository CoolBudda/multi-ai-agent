from __future__ import annotations

from src.api.routes.chat import post_agent_invoke, post_assistant_request
from src.graph.main_graph import OrchestratorGraph
from src.services.routing_service import RoutingRecordService

_ROUTING_SERVICE = RoutingRecordService()
_ORCHESTRATOR_GRAPH = OrchestratorGraph(routing_service=_ROUTING_SERVICE)


def get_routing_service() -> RoutingRecordService:
	return _ROUTING_SERVICE


def get_orchestrator_graph() -> OrchestratorGraph:
	return _ORCHESTRATOR_GRAPH


def handle_assistant_request(payload: dict[str, object]) -> tuple[int, dict[str, object]]:
	return post_assistant_request(payload, orchestrator_graph=_ORCHESTRATOR_GRAPH)


def handle_agent_invoke(agent: str, payload: dict[str, object]) -> tuple[int, dict[str, object]]:
	return post_agent_invoke(agent, payload, orchestrator_graph=_ORCHESTRATOR_GRAPH)
