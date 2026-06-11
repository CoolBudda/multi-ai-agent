from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from src.models.events import (
	MemoryPreferenceFailedEvent,
	MemoryPreferenceLoadedEvent,
	build_memory_preference_failed_event,
	build_memory_preference_loaded_event,
)
from src.models.state import UserPreferences

ALLOWED_PREFERENCE_FIELDS = {
	"preferred_airline",
	"seat_preference",
	"meeting_start_time",
	"favorite_cuisine",
	"news_topics",
}


class MemoryRepository(Protocol):
	def get_preferences(self, user_id: str) -> dict[str, Any] | None:
		...

	def update_preference(self, user_id: str, field_name: str, value: Any) -> dict[str, Any]:
		...


@dataclass(slots=True)
class MemoryServiceWriteError(RuntimeError):
	user_message: str
	failure_event: MemoryPreferenceFailedEvent

	def __post_init__(self) -> None:
		super().__init__(self.user_message)


class MemoryService:
	"""Service-layer facade for user preference persistence and retrieval."""

	def __init__(self, repository: MemoryRepository) -> None:
		self._repository = repository

	def read_preferences(self, user_id: str) -> tuple[UserPreferences, MemoryPreferenceLoadedEvent]:
		try:
			raw_preferences = self._repository.get_preferences(user_id)
		except Exception:
			empty: UserPreferences = {}
			return (
				empty,
				build_memory_preference_loaded_event(
					user_id,
					empty,
					error_code="memory.read.failed",
				),
			)

		preferences = _coerce_preferences(raw_preferences)
		return preferences, build_memory_preference_loaded_event(user_id, preferences)

	def retrieve_user_preferences_at_agent_start(
		self,
		user_id: str,
		defaults: UserPreferences | None = None,
	) -> tuple[UserPreferences, MemoryPreferenceLoadedEvent]:
		preferences, event = self.read_preferences(user_id)
		return apply_preferences_or_defaults(preferences, defaults or {}), event

	def write_preference_update(self, user_id: str, field_name: str, value: Any) -> UserPreferences:
		if field_name not in ALLOWED_PREFERENCE_FIELDS:
			raise ValueError(f"Unsupported preference field: {field_name}")

		try:
			updated = self._repository.update_preference(user_id, field_name, value)
		except Exception:
			failure_event = build_memory_preference_failed_event(
				user_id,
				action="write_preference_update",
				error_code="memory.write.failed",
			)
			raise MemoryServiceWriteError(
				"Could not update preferences. Please retry.",
				failure_event,
			) from None

		return _coerce_preferences(updated)


def apply_preferences_or_defaults(
	preferences: UserPreferences,
	defaults: UserPreferences,
) -> UserPreferences:
	merged: UserPreferences = dict(preferences)
	for key, value in defaults.items():
		if key not in merged or merged[key] is None:
			merged[key] = value
	return merged


def _coerce_preferences(raw_preferences: dict[str, Any] | None) -> UserPreferences:
	if not raw_preferences:
		return {}

	coerced: UserPreferences = {}
	for key in ALLOWED_PREFERENCE_FIELDS | {"user_id"}:
		if key in raw_preferences and raw_preferences[key] is not None:
			coerced[key] = raw_preferences[key]
	return coerced

