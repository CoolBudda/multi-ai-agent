from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest

from src.services.memory_service import MemoryService, MemoryServiceWriteError


class FakeMemoryRepository:
    def __init__(
        self,
        *,
        records: dict[str, dict[str, Any]] | None = None,
        fail_read: bool = False,
        fail_write: bool = False,
    ) -> None:
        self.records: dict[str, dict[str, Any]] = records or {}
        self.fail_read = fail_read
        self.fail_write = fail_write

    def get_preferences(self, user_id: str) -> dict[str, Any] | None:
        if self.fail_read:
            raise RuntimeError("read failed")
        return self.records.get(user_id)

    def update_preference(self, user_id: str, field_name: str, value: Any) -> dict[str, Any]:
        if self.fail_write:
            raise RuntimeError("write failed")
        current = self.records.setdefault(user_id, {"user_id": user_id})
        current[field_name] = value
        return current


def test_reads_preferences_by_user_id_from_dynamodb() -> None:
    repo = FakeMemoryRepository(records={"u-1": {"user_id": "u-1", "preferred_airline": "Delta"}})
    service = MemoryService(repo)

    preferences, _ = service.read_preferences("u-1")

    assert preferences["preferred_airline"] == "Delta"


def test_emits_memory_preference_loaded_event_on_successful_retrieval() -> None:
    repo = FakeMemoryRepository(records={"u-1": {"user_id": "u-1", "seat_preference": "Aisle"}})
    service = MemoryService(repo)

    _, event = service.read_preferences("u-1")

    assert event["event_name"] == "memory.preference.loaded"
    assert event["user_id"] == "u-1"
    assert event["error_code"] is None


def test_returns_empty_object_when_no_preference_record_exists() -> None:
    service = MemoryService(FakeMemoryRepository())

    preferences, event = service.read_preferences("missing-user")

    assert preferences == {}
    assert event["preferences"] == {}


def test_missing_fields_do_not_block_defaultable_agent_behavior() -> None:
    repo = FakeMemoryRepository(records={"u-1": {"user_id": "u-1", "preferred_airline": "Delta"}})
    service = MemoryService(repo)

    preferences, _ = service.retrieve_user_preferences_at_agent_start(
        "u-1",
        defaults={"meeting_start_time": "09:00", "seat_preference": "Window"},
    )

    assert preferences["preferred_airline"] == "Delta"
    assert preferences["meeting_start_time"] == "09:00"
    assert preferences["seat_preference"] == "Window"


def test_writes_single_preference_field_and_supports_read_back() -> None:
    repo = FakeMemoryRepository(records={"u-1": {"user_id": "u-1"}})
    service = MemoryService(repo)

    service.write_preference_update("u-1", "favorite_cuisine", "Thai")
    read_back, _ = service.read_preferences("u-1")

    assert read_back["favorite_cuisine"] == "Thai"


def test_read_failure_returns_empty_preferences_object() -> None:
    service = MemoryService(FakeMemoryRepository(fail_read=True))

    preferences, event = service.read_preferences("u-1")

    assert preferences == {}
    assert event["error_code"] == "memory.read.failed"


def test_write_failure_surfaces_error_and_emits_failure_event() -> None:
    service = MemoryService(FakeMemoryRepository(fail_write=True))

    with pytest.raises(MemoryServiceWriteError) as exc_info:
        service.write_preference_update("u-1", "preferred_airline", "Delta")

    assert str(exc_info.value) == "Could not update preferences. Please retry."
    assert exc_info.value.failure_event["event_name"] == "memory.preference.failed"
    assert exc_info.value.failure_event["error_code"] == "memory.write.failed"


def test_service_layer_retrieval_is_available_to_specialist_agent_start_flow() -> None:
    repo = FakeMemoryRepository(records={"u-1": {"user_id": "u-1", "news_topics": ["ai"]}})
    service = MemoryService(repo)

    preferences, _ = service.retrieve_user_preferences_at_agent_start(
        "u-1",
        defaults={"meeting_start_time": "09:00"},
    )

    assert preferences["news_topics"] == ["ai"]
    assert preferences["meeting_start_time"] == "09:00"


def test_dynamodb_read_write_operations_against_user_preferences_table() -> None:
    stored_records: dict[str, dict[str, Any]] = {}
    repo = Mock()

    def _mock_update_preference(user_id: str, field_name: str, value: Any) -> dict[str, Any]:
        record = stored_records.setdefault(user_id, {"user_id": user_id})
        record[field_name] = value
        return record

    repo.update_preference.side_effect = _mock_update_preference
    repo.get_preferences.side_effect = lambda user_id: stored_records.get(user_id)

    service = MemoryService(repo)

    updated = service.write_preference_update("u-1", "preferred_airline", "Delta")
    read_back, loaded_event = service.read_preferences("u-1")

    assert updated["preferred_airline"] == "Delta"
    assert read_back["preferred_airline"] == "Delta"
    assert loaded_event["event_name"] == "memory.preference.loaded"
    repo.update_preference.assert_called_once_with("u-1", "preferred_airline", "Delta")
    repo.get_preferences.assert_called_once_with("u-1")


def test_workflow_write_update_path_surfaces_write_failure() -> None:
    repo = Mock()
    repo.update_preference.side_effect = RuntimeError("write failed")
    service = MemoryService(repo)

    def _mock_workflow_write_update(
        memory_service: MemoryService,
        user_id: str,
        field_name: str,
        value: Any,
    ) -> dict[str, Any]:
        try:
            updated = memory_service.write_preference_update(user_id, field_name, value)
            return {"status": "ok", "preferences": updated}
        except MemoryServiceWriteError as exc:
            return {
                "status": "failed",
                "user_message": exc.user_message,
                "failure_event": exc.failure_event,
            }

    result = _mock_workflow_write_update(service, "u-1", "preferred_airline", "Delta")

    assert result["status"] == "failed"
    assert result["user_message"] == "Could not update preferences. Please retry."
    assert result["failure_event"]["event_name"] == "memory.preference.failed"
    assert result["failure_event"]["error_code"] == "memory.write.failed"
