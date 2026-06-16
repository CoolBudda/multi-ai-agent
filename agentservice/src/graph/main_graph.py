from __future__ import annotations

from dataclasses import dataclass

from src.agents.orchestrator_agent import (
	OrchestratorDispatchError,
	compute_routing_decision,
	dispatch_to_target_domain,
)
from src.models.events import (
	build_direct_specialist_access_denied_payload,
	build_downstream_failure_payload,
)
from src.models.state import ErrorResponse, OrchestratorRequest, OrchestratorResponse, SupportedDomain
from src.services.routing_service import RoutingRecordService


@dataclass(slots=True)
class OrchestratorGraph:
	routing_service: RoutingRecordService
	confidence_threshold: float = 0.6

	def run_orchestrator_ingress(
		self,
		request: OrchestratorRequest,
		*,
		force_downstream_failure: bool = False,
	) -> OrchestratorResponse:
		decision, _decision_event = compute_routing_decision(
			request,
			confidence_threshold=self.confidence_threshold,
		)
		self.routing_service.create_open_record(
			request_id=request["request_id"],
			routed_to=decision["selected_domain"],
			routing_decision=decision,
			user_message="Request accepted through orchestrator.",
		)

		try:
			domain_response = dispatch_to_target_domain(
				request,
				decision,
				force_failure=force_downstream_failure,
			)
		except OrchestratorDispatchError as exc:
			record, _record_event = self.routing_service.mark_failed(
				request_id=request["request_id"],
				failure_code=exc.failure_code,
				user_message=exc.user_message,
			)
			return {
				"request_id": request["request_id"],
				"initial_handler": "orchestrator",
				"routed_to": decision["selected_domain"],
				"routing_record_id": record["record_id"],
				"selected_domain": decision["selected_domain"],
				"fallback_to_companion": decision["fallback_to_companion"],
				"threshold_passed": decision["threshold_passed"],
				"tie_detected": decision["tie_detected"],
				"rationale": decision["rationale"],
				"routing_decision": decision,
				"status": "failed",
				"response": build_downstream_failure_payload(
					request_id=request["request_id"],
					failure_code=exc.failure_code,
				),
				"routing_record": record,
			}

		record, _record_event = self.routing_service.mark_succeeded(
			request_id=request["request_id"],
			user_message="Request completed successfully.",
		)
		return {
			"request_id": request["request_id"],
			"initial_handler": "orchestrator",
			"routed_to": decision["selected_domain"],
			"routing_record_id": record["record_id"],
			"selected_domain": decision["selected_domain"],
			"fallback_to_companion": decision["fallback_to_companion"],
			"threshold_passed": decision["threshold_passed"],
			"tie_detected": decision["tie_detected"],
			"rationale": decision["rationale"],
			"routing_decision": decision,
			"status": "succeeded",
			"response": domain_response,
			"routing_record": record,
		}

	def deny_direct_specialist_access(
		self,
		*,
		agent: SupportedDomain,
		request_id: str,
	) -> ErrorResponse:
		self.routing_service.create_open_record(
			request_id=request_id,
			routed_to=agent,
			user_message="Direct specialist access attempted.",
		)
		self.routing_service.mark_rejected(
			request_id=request_id,
			rejection_code="direct_specialist_access_denied",
			user_message="Direct specialist invocation is denied.",
		)
		return build_direct_specialist_access_denied_payload(request_id=request_id, agent=agent)
