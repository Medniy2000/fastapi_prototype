import re
from dataclasses import dataclass

from src.app.domain.common.exceptions import ValidationError
from src.app.domain.common.utils.common import mask_string


@dataclass(frozen=True)
class EmailPasswordPair:
    """Value object representing a pair of email and password"""

    email: str
    password: str

    def __post_init__(self) -> None:
        self.__validate_email(value=self.email)
        self.__validate_password(value=self.password)

    @staticmethod
    def __validate_email(value: str) -> None:
        # TODO: implement validation
        pass

    @staticmethod
    def __validate_password(value: str) -> None:
        details = [
            {"key": "password", "value": mask_string(value, keep_start=1, keep_end=1)},
        ]
        if len(value) < 8:
            raise ValidationError(message="Must be at least 8 characters long", details=details)

        # Check for at least one uppercase letter
        if not re.search(r"[A-Z]", value):
            raise ValidationError(message="Must contain at least one uppercase letter", details=details)

        # Check for at least one lowercase letter
        if not re.search(r"[a-z]", value):
            raise ValidationError(message="Must contain at least one lowercase letter", details=details)

        # Check for at least one digit
        if not re.search(r"[0-9]", value):
            raise ValidationError(message="Must contain at least one digit", details=details)

        # Check for at least one special character
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValidationError(message="Must contain at least one special character", details=details)

    def to_dict(self) -> dict:
        return {
            "email": self.email,
            "password_hashed": self.password,
        }


@dataclass(frozen=True)
class PhoneNumberCodePair:
    """Value object representing a pair of phone number and code"""

    phone: str
    verification_code: str

    def __post_init__(self) -> None:
        self.__validate_phone(value=self.phone)
        self.__validate_verification_code(value=self.verification_code)

    @staticmethod
    def __validate_phone(value: str) -> None:
        pattern = r"^\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$"
        match = re.match(pattern, value)
        if not match or 8 > len(value) or len(value) > 16:
            raise ValidationError(
                message="Invalid value",
                details=[{"key": "phone", "value": mask_string(value, keep_start=2, keep_end=2)}],
            )

    pass

    @staticmethod
    def __validate_verification_code(value: str) -> None:
        pass

    def to_dict(self) -> dict:
        return {
            "phone": self.phone,
            "verification_code": self.verification_code,
        }
