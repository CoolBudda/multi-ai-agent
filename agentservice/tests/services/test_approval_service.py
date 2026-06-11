from __future__ import annotations

from src.api.routes.chat import deliver_approval_request_to_frontend
from src.services.approval_service import (
    ApprovalService,
    ApprovalServiceUnavailableError,
    RejectedActionRetryBlockedError,
)


def _sample_payload() -> dict[str, object]:
    return {
        "action_type": "create_event",
        "domain": "calendar",
        "summary": "Schedule team sync at 10:00",
        "payload": {"start": "10:00", "end": "10:30"},
    }


def test_step_1_create_approval_request_from_write_action_payload() -> None:
    service = ApprovalService(id_factory=lambda: "req-1")

    request, _ = service.create_approval_request(_sample_payload())

    assert request["request_id"] == "req-1"
    assert request["action_type"] == "create_event"
    assert request["domain"] == "calendar"
    assert request["summary"] == "Schedule team sync at 10:00"


def test_step_2_emit_approval_required_and_delivery_path() -> None:
    service = ApprovalService(id_factory=lambda: "req-2")

    request, event = service.create_approval_request(_sample_payload())
    delivery = deliver_approval_request_to_frontend(event)

    assert event["event_name"] == "approval.required"
    assert event["request"] == request
    assert delivery["type"] == "approval_request"
    assert delivery["event_name"] == "approval.required"


def test_step_3_user_decision_intake_and_result_mapping() -> None:
    service = ApprovalService()

    approved_result, _ = service.await_user_decision("req-a", decision="approved")
    rejected_result, _ = service.await_user_decision("req-b", decision="rejected")

    assert approved_result == {"request_id": "req-a", "status": "approved"}
    assert rejected_result == {"request_id": "req-b", "status": "rejected"}


def test_step_4_emit_approval_completed_event_on_decision() -> None:
    service = ApprovalService()

    result, event = service.await_user_decision("req-3", decision="approved")

    assert event["event_name"] == "approval.completed"
    assert event["result"] == result


def test_step_5_execute_write_action_only_when_approved() -> None:
    service = ApprovalService(id_factory=lambda: "req-5")
    request, _ = service.create_approval_request(_sample_payload())
    result, _ = service.await_user_decision(request["request_id"], decision="approved")

    executed = {"value": False}

    def _write_action() -> str:
        executed["value"] = True
        return "ok"

    outcome = service.execute_or_cancel_write_action(request, result, _write_action)

    assert executed["value"] is True
    assert outcome["status"] == "executed"
    assert outcome["result"] == "ok"


def test_step_6_rejected_path_emits_domain_action_rejected_event() -> None:
    service = ApprovalService(id_factory=lambda: "req-6")
    request, _ = service.create_approval_request(_sample_payload())
    result, _ = service.await_user_decision(request["request_id"], decision="rejected")

    outcome = service.execute_or_cancel_write_action(request, result, lambda: "never")

    assert outcome["status"] == "cancelled"
    assert outcome["message"] == "Action cancelled. No changes were made."
    assert outcome["rejection_event"]["event_name"] == "calendar.create_event.rejected"


def test_step_7_prevent_automatic_retry_after_rejection() -> None:
    service = ApprovalService(id_factory=lambda: "req-7")
    request, _ = service.create_approval_request(_sample_payload())
    rejected_result, _ = service.await_user_decision(request["request_id"], decision="rejected")

    service.process_approval_outcome(request, rejected_result)

    try:
        service.process_approval_outcome(request, rejected_result)
        assert False, "expected RejectedActionRetryBlockedError"
    except RejectedActionRetryBlockedError:
        pass


def test_step_8_service_unavailable_or_expired_session_treated_as_rejected() -> None:
    service = ApprovalService()

    try:
        service.await_user_decision("req-8", decision="approved", service_available=False)
        assert False, "expected ApprovalServiceUnavailableError"
    except ApprovalServiceUnavailableError:
        pass

    expired_result, _ = service.await_user_decision(
        "req-9",
        decision=None,
        session_expired=True,
    )

    assert expired_result["status"] == "rejected"


def test_requirement_fr_001_write_actions_blocked_until_approval() -> None:
    service = ApprovalService(id_factory=lambda: "req-fr1")
    request, _ = service.create_approval_request(_sample_payload())
    rejected_result, _ = service.await_user_decision(request["request_id"], decision="rejected")

    called = {"value": False}

    def _write_action() -> str:
        called["value"] = True
        return "executed"

    service.execute_or_cancel_write_action(request, rejected_result, _write_action)

    assert called["value"] is False


def test_requirement_fr_002_summary_present_in_approval_request() -> None:
    service = ApprovalService(id_factory=lambda: "req-fr2")

    request, _ = service.create_approval_request(_sample_payload())

    assert request["summary"] == "Schedule team sync at 10:00"


def test_requirement_fr_003_execute_only_after_approved_decision() -> None:
    service = ApprovalService(id_factory=lambda: "req-fr3")
    request, _ = service.create_approval_request(_sample_payload())

    approved_result, _ = service.await_user_decision(request["request_id"], decision="approved")
    outcome = service.execute_or_cancel_write_action(request, approved_result, lambda: "done")

    assert outcome["status"] == "executed"


def test_requirement_fr_004_cancel_and_emit_rejected_event_on_reject() -> None:
    service = ApprovalService(id_factory=lambda: "req-fr4")
    request, _ = service.create_approval_request(_sample_payload())

    rejected_result, _ = service.await_user_decision(request["request_id"], decision="rejected")
    outcome = service.execute_or_cancel_write_action(request, rejected_result, lambda: "done")

    assert outcome["status"] == "cancelled"
    assert outcome["rejection_event"]["event_name"] == "calendar.create_event.rejected"


def test_requirement_fr_005_no_automatic_retry_after_reject() -> None:
    service = ApprovalService(id_factory=lambda: "req-fr5")
    request, _ = service.create_approval_request(_sample_payload())

    rejected_result, _ = service.await_user_decision(request["request_id"], decision="rejected")
    service.process_approval_outcome(request, rejected_result)

    try:
        service.process_approval_outcome(request, rejected_result)
        assert False, "expected RejectedActionRetryBlockedError"
    except RejectedActionRetryBlockedError:
        pass


def test_acceptance_rejected_actions_are_not_executed() -> None:
    service = ApprovalService(id_factory=lambda: "req-acc1")
    request, _ = service.create_approval_request(_sample_payload())
    rejected_result, _ = service.await_user_decision(request["request_id"], decision="rejected")

    called = {"value": False}

    def _write_action() -> str:
        called["value"] = True
        return "should-not-run"

    outcome = service.execute_or_cancel_write_action(request, rejected_result, _write_action)

    assert called["value"] is False
    assert outcome["status"] == "cancelled"


def test_acceptance_rejected_event_is_emitted_on_rejection() -> None:
    service = ApprovalService(id_factory=lambda: "req-acc2")
    request, _ = service.create_approval_request(_sample_payload())
    rejected_result, _ = service.await_user_decision(request["request_id"], decision="rejected")

    outcome = service.execute_or_cancel_write_action(request, rejected_result, lambda: "never")

    assert outcome["rejection_event"]["event_name"] == "calendar.create_event.rejected"
