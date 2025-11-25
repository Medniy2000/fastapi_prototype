from dataclasses import dataclass
from typing import Optional

from uuid import UUID

from src.app.application.common.dto.base import AppBaseDTO


@dataclass
class UserShortDTO(AppBaseDTO):
    id: int
    uuid: UUID
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    is_active: bool


@dataclass
class CreateUserByEmailDTO(AppBaseDTO):
    """DTO for creating user by email and password."""

    email: str
    password: str


@dataclass
class CreateUserByPhoneDTO(AppBaseDTO):
    """DTO for creating user by phone and verification code."""

    phone: str
    verification_code: str
