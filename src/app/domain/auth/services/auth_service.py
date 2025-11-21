import bcrypt
from passlib.context import CryptContext

from src.app.domain.common.services.base import AbstractBaseDomainService


class DomainAuthService(AbstractBaseDomainService):
    """Domain service for password operations."""

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
