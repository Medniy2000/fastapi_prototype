import re
from typing import Any
from pydantic import field_validator
from src.app.api.core.schemas.req_schemas import BaseReq


class TokenReq(BaseReq):
    email: str
    password: str


class SignUpReq(BaseReq):
    email: str
    password: str

    @field_validator("password", mode="before")
    def validate_password(cls, value: Any, values: Any, **kwargs: dict) -> str:  # noqa
        # Minimum length
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        # Check for at least one uppercase letter
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")

        # Check for at least one lowercase letter
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")

        # Check for at least one digit
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one digit.")

        # Check for at least one special character
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character.")

        return value
