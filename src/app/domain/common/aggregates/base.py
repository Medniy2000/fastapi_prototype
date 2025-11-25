from typing import List

from src.app.domain.common.events.base import DomainEvent


class BaseAggregate:

    def __init__(self) -> None:
        self._events: List[DomainEvent] = []

    def add_event(self, event: DomainEvent) -> None:
        """Add a domain event to the aggregate."""
        self._events.append(event)

    def events_clear(self) -> None:
        """Clear all domain events."""
        self._events.clear()

    def get_events(self) -> List[DomainEvent]:
        """Get all domain events."""
        return self._events.copy()

    def events_load(self, raw_events: List[dict]) -> List[DomainEvent]:
        """Get all domain events."""
        pass

    def has_events(self) -> bool:
        """Check if aggregate has any events."""
        return len(self._events) > 0
