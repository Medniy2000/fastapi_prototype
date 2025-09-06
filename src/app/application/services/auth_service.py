from copy import deepcopy
from typing import Any

from fastapi import HTTPException, status
from pydantic import validate_email

from src.app.application.common.services.base import AbstractBaseApplicationService
from src.app.application.container import container as app_services_container, ApplicationServicesContainer
from src.app.domain.users.container import container as domain_services_container, DomainServicesContainer


class AuthService(AbstractBaseApplicationService):
    app_svc_container: ApplicationServicesContainer = app_services_container
    dom_svc_container: DomainServicesContainer = domain_services_container

    auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    @classmethod
    async def create_auth_user(cls, data: dict) -> Any:
        data_ = deepcopy(data)
        email = data_.get("email") or ""
        try:
            email_validated = validate_email(email)[1]
            is_email_exists = await cls.app_svc_container.users_service.is_exists(
                filter_data={"email": email_validated}
            )
            if is_email_exists or not email:
                raise HTTPException(status_code=422, detail="User already exists with email")
            data["email"] = email_validated
        except Exception:
            raise HTTPException(status_code=422, detail="Invalid value for email")

        password = data_.pop("password", None) or ""
        password_hashed = cls.dom_svc_container.auth_service.get_password_hashed(password)
        data_["password_hashed"] = password_hashed
        return await cls.app_svc_container.users_service.create(data_, is_return_require=True)

    @classmethod
    async def get_auth_user(cls, email: str, password: str) -> Any:
        try:
            email_validated = validate_email(email)[1]
        except Exception:
            raise HTTPException(status_code=422, detail=f"Invalid value {email}")

        user = await cls.app_svc_container.users_service.get_first(filter_data={"email": email_validated})
        is_password_verified = cls.dom_svc_container.auth_service.verify_password(
            password, getattr(user, "password_hashed")
        )
        if not user or not is_password_verified:
            raise HTTPException(status_code=422, detail="username or password is incorrect")
        return user
