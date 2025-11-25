from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events."""

    id: int
    created_at: datetime
    event: str
    payload: Dict[str, Any]

    def to_dict(self) -> dict:
        """Convert event to dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "event": self.event,
            "payload": self.payload,
        }