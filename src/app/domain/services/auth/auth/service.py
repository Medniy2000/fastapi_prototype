from copy import deepcopy
from typing import Any

import bcrypt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from pydantic import validate_email

from src.app.domain.services.base import AbstractBaseService
from src.app.domain.services.container import container as services_container


class AuthService(AbstractBaseService):
    users_service = services_container.users_service

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        password_byte_enc = plain_password.encode("utf-8")
        hashed_password_enc = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password_enc)

    @classmethod
    def get_password_hashed(cls, password: str) -> str:
        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
        return hashed_password.decode("utf-8")

    @classmethod
    async def create_auth_user(cls, data: dict) -> Any:
        data_ = deepcopy(data)
        email = data_.get("email") or ""
        try:
            email_validated = validate_email(email)[1]
            is_email_exists = await cls.users_service.is_exists(filter_data={"email": email_validated})
            if is_email_exists or not email:
                raise HTTPException(status_code=422, detail="User already exists with email")
            data["email"] = email_validated
        except Exception as e:
            print(e)
            raise HTTPException(status_code=422, detail="Invalid value for email")

        password = data_.pop("password", None) or ""
        password_hashed = cls.get_password_hashed(password)
        data_["password_hashed"] = password_hashed
        return await cls.users_service.create(data_, is_return_require=True)

    @classmethod
    async def get_auth_user(cls, email: str, password: str) -> Any:
        try:
            email_validated = validate_email(email)[1]
        except Exception:
            raise HTTPException(status_code=422, detail=f"Invalid value {email}")

        user = await cls.users_service.get_first(filter_data={"email": email_validated})
        is_password_verified = cls.verify_password(password, getattr(user, "password_hashed"))
        if not user or not is_password_verified:
            raise HTTPException(status_code=422, detail="username or password is incorrect")
        return user
