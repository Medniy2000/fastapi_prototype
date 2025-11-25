from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.app.application.common.dto.base import AppBaseDTO


@dataclass
class TokenPairDTO(AppBaseDTO):
    """DTO for token pair (access and refresh tokens)."""

    access_token: str
    refresh_token: str

    def to_dict(self) -> dict:
        return {
            "access": self.access_token,
            "refresh": self.refresh_token,
        }


@dataclass
class DecodedTokenDTO(AppBaseDTO):
    """DTO for decoded token data."""

    uuid: str
    sid: str
    token_type: str
    exp: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "sid": self.sid,
            "token_type": self.token_type,
        }
