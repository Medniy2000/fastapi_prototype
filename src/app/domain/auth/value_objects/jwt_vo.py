from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass(frozen=True)
class TokenPayload:
    """Value object representing JWT token payload data."""

    uuid: str
    sid: str
    token_type: TokenType
    exp: datetime

    def to_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "sid": self.sid,
        }


@dataclass(frozen=True)
class TokenPair:
    """Value object representing a pair of access and refresh tokens."""

    access_token: str
    refresh_token: str

    def to_dict(self) -> dict:
        return {
            "access": self.access_token,
            "refresh": self.refresh_token,
        }


@dataclass(frozen=True)
class DecodedToken:
    """Value object representing decoded token data."""

    uuid: str
    sid: str
    token_type: TokenType
    exp: Optional[datetime] = None

    @classmethod
    def from_payload(cls, payload: dict, token_type: TokenType) -> "DecodedToken":
        user_data = payload.get("user", {})
        return cls(
            uuid=user_data.get("uuid", ""),
            sid=user_data.get("sid", ""),
            token_type=token_type,
            exp=payload.get("exp"),
        )

    def to_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "sid": self.sid,
        }
