from copy import deepcopy
from typing import Any

from pydantic import validate_email

from src.app.application.common.services.base import AbstractBaseApplicationService
from src.app.application.container import container as app_services_container, ApplicationServicesContainer
from src.app.domain.common.exceptions import AlreadyExistsError, ValidationError
from src.app.domain.common.utils.common import mask_string
from src.app.domain.auth.container import container as domain_auth_svc_container, DomainAuthServiceContainer
from src.app.domain.auth.value_objects import TokenPair, DecodedToken
from src.app.domain.users.container import container as domain_users_svc_container, DomainUsersServiceContainer


class AppAuthService(AbstractBaseApplicationService):
    # Application Layer Services
    app_svc_container: ApplicationServicesContainer = app_services_container

    # Domain Layer Services
    dom_users_svc_container: DomainUsersServiceContainer = domain_users_svc_container
    dom_auth_svc_container: DomainAuthServiceContainer = domain_auth_svc_container

    async def send_verification_code(self, phone_number: str) -> None:
        pass

    @classmethod
    async def create_auth_user(cls, data: dict) -> Any:
        data_ = deepcopy(data)
        email = data_.get("email") or ""

        email_validated = validate_email(email)[1]
        is_email_exists = await cls.app_svc_container.users_service.is_exists(
            filter_data={"email": email_validated}
        )
        if is_email_exists or not email:
            raise AlreadyExistsError(
                message="User already exists",
                details=[{"key": "email", "value": email_validated}],
            )
        data["email"] = email_validated

        password = data_.pop("password", None) or ""
        password_hashed = cls.dom_auth_svc_container.auth_service.get_password_hashed(password)
        data_["password_hashed"] = password_hashed
        return await cls.app_svc_container.users_service.create(data_, is_return_require=True)

    @classmethod
    async def get_auth_user_by_email_password(cls, email: str, password: str) -> Any:
        try:
            email_validated = validate_email(email)[1]
        except Exception:
            raise ValidationError(
                message="Invalid value",
                details=[{"key": "email", "value": mask_string(email, keep_start=1, keep_end=4)}],
            )

        user = await cls.app_svc_container.users_service.get_first(filter_data={"email": email_validated})
        is_password_verified = cls.dom_auth_svc_container.auth_service.verify_password(
            password, getattr(user, "password_hashed")
        )
        if not user or not is_password_verified:
            raise ValidationError(
                message="One(or more) value(s) invalid",
                details=[
                    {"key": "email", "value": mask_string(email, keep_start=1, keep_end=4)},
                    {"key": "password", "value": mask_string(password, keep_start=1, keep_end=2)},
                ],
            )
        return user

    @classmethod
    async def get_auth_user_by_phone_number(cls, phone_number: str, verification_code: str) -> Any:
        user = await cls.app_svc_container.users_service.get_first(filter_data={"phone": phone_number})
        return user

    @classmethod
    def create_tokens_for_user(cls, uuid: str) -> TokenPair:
        """Create access and refresh tokens for a user."""
        return cls.dom_auth_svc_container.jwt_service.create_token_pair(uuid)

    @classmethod
    def verify_access_token(cls, token: str) -> DecodedToken:
        """Verify an access token and return decoded data."""
        return cls.dom_auth_svc_container.jwt_service.verify_access_token(token)

    @classmethod
    def verify_refresh_token(cls, token: str) -> DecodedToken:
        """Verify a refresh token and return decoded data."""
        return cls.dom_auth_svc_container.jwt_service.verify_refresh_token(token)

    @classmethod
    async def refresh_tokens(cls, refresh_token: str) -> tuple[Any, TokenPair]:
        """Verify refresh token, get user, and create new token pair."""
        decoded = cls.verify_refresh_token(refresh_token)
        user = await cls.app_svc_container.users_service.get_first(filter_data={"uuid": decoded.uuid})
        new_tokens = cls.create_tokens_for_user(str(getattr(user, "uuid", "")))
        return user, new_tokens
