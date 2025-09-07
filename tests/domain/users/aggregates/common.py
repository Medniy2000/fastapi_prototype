from dataclasses import dataclass
import datetime as dt
from typing import Any, Dict


@dataclass
class UserTestAggregate:
    id: int
    uuid: str
    meta: Dict[str, Any] | Any
    created_at: dt.datetime
    updated_at: dt.datetime
    birthday: dt.datetime | None
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
