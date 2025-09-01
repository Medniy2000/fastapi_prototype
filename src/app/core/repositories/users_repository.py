from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from src.app.core.models.users import User
from src.app.core.repositories.base import BaseSQLAsyncDrivenBaseRepository


@dataclass
class UserAggregate:
    id: int
    uuid: str
    meta: Dict[str, Any] | Any
    created_at: datetime
    updated_at: datetime
    birthday: datetime | None
    first_name: str | None
    last_name: str | None
    email: str
    password_hashed: str | None
    photo: str | None
    is_active: bool
    is_guest: bool | None
    phone: str | None
    street: str | None
    city: str | None
    state: str | None
    zip_code: str | None
    country: str | None


class UsersRepository(BaseSQLAsyncDrivenBaseRepository):
    MODEL = User
    OUT_ENTITY = UserAggregate
