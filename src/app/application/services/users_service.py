from pydantic import validate_email

from src.app.application.common.services.base import BaseApplicationService
from src.app.application.container import container as app_services_container, ApplicationServicesContainer
from src.app.application.dto.user import UserShortDTO
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
    async def create_user_by_email(cls, email: str, password: str) -> UserShortDTO:
        _, validated_email = validate_email(email)
        validated_data = EmailPasswordPair(email=validated_email, password=password)
        password_hashed = domain_auth_svc_container.auth_service.get_password_hashed(password=password)
        is_email_exists = await cls.app_svc_container.users_service.is_exists(
            filter_data={"email": validated_data.email}
        )
        if is_email_exists or not email:
            raise AlreadyExistsError(
                message="Already exists",
                details=[
                    {"key": "email", "value": mask_string(validated_data.email, keep_start=1, keep_end=4)},
                ],
            )

        data = {
            "email": validated_data.email,
            "password_hashed": password_hashed,
        }
        user_dto =  await cls.create(data, is_return_require=True, out_dataclass=UserShortDTO)
        return user_dto


    @classmethod
    async def create_user_by_phone(cls, phone: str, verification_code: str) -> UserShortDTO:
        validated_data = PhoneNumberCodePair(phone=phone, verification_code=verification_code)
        is_phone_exists = await cls.app_svc_container.users_service.is_exists(
            filter_data={"phone": validated_data.phone}
        )
        if is_phone_exists:
            raise AlreadyExistsError(
                message="Already exists",
                details=[
                    {"key": "phone", "value": mask_string(validated_data.phone, keep_start=2, keep_end=2)},
                ],
            )
        user_dto = await cls.create(validated_data.to_dict(), is_return_require=True, out_dataclass=UserShortDTO)
        return user_dto
