from typing import Optional

from pydantic import validate_email

from src.app.application.common.services.base import BaseApplicationService
from src.app.application.container import container as app_services_container, ApplicationServicesContainer
from src.app.application.dto.user import CreateUserByEmailDTO, CreateUserByPhoneDTO, UserShortDTO
from src.app.domain.auth.container import container as domain_auth_svc_container, DomainAuthServiceContainer
from src.app.domain.common.exceptions import AlreadyExistsError
from src.app.domain.common.utils.common import mask_string
from src.app.domain.users.container import container as domain_users_svc_container, DomainUsersServiceContainer
from src.app.domain.users.value_objects.users_vob import EmailPasswordPair, PhoneNumberCodePair
from src.app.infrastructure.repositories.container import container as repo_container


class AppUserService(BaseApplicationService):

    # Application Layer Services
    app_svc_container: ApplicationServicesContainer = app_services_container

    # Domain Layer Services
    dom_users_svc_container: DomainUsersServiceContainer = domain_users_svc_container
    dom_auth_svc_container: DomainAuthServiceContainer = domain_auth_svc_container

    # Repositories
    repository = repo_container.users_repository

    @classmethod
    async def create_user_by_email(cls, email: str, password: str) -> Optional[UserShortDTO]:
        _, validated_email = validate_email(email)
        input_dto = CreateUserByEmailDTO(email=validated_email, password=password)

        email_password_vo = EmailPasswordPair(email=input_dto.email, password=input_dto.password)

        # Use domain service for password hashing
        password_hashed = domain_auth_svc_container.auth_service.get_password_hashed(password=input_dto.password)

        # Check business rule: email uniqueness
        is_email_exists = await cls.app_svc_container.users_service.is_exists(
            filter_data={"email": email_password_vo.email}
        )
        if is_email_exists or not email:
            raise AlreadyExistsError(
                message="Already exists",
                details=[
                    {"key": "email", "value": mask_string(email_password_vo.email, keep_start=1, keep_end=4)},
                ],
            )

        # Prepare persistence data
        data = {
            "email": email_password_vo.email,
            "password_hashed": password_hashed,
        }
        user_dto = await cls.create(data, is_return_require=True, out_dataclass=UserShortDTO)

        return user_dto

    @classmethod
    async def create_user_by_phone(cls, phone: str, verification_code: str) -> Optional[UserShortDTO]:
        # Create application DTO
        input_dto = CreateUserByPhoneDTO(phone=phone, verification_code=verification_code)

        # Convert to domain value object for validation
        phone_code_vo = PhoneNumberCodePair(phone=input_dto.phone, verification_code=input_dto.verification_code)

        # Check business rule: phone uniqueness
        is_phone_exists = await cls.app_svc_container.users_service.is_exists(
            filter_data={"phone": phone_code_vo.phone}
        )
        if is_phone_exists:
            raise AlreadyExistsError(
                message="Already exists",
                details=[
                    {"key": "phone", "value": mask_string(phone_code_vo.phone, keep_start=2, keep_end=2)},
                ],
            )

        # Prepare persistence data
        data = {
            "phone": phone_code_vo.phone,
            "verification_code": phone_code_vo.verification_code,
        }
        user_dto = await cls.create(data, is_return_require=True, out_dataclass=UserShortDTO)
        return user_dto
