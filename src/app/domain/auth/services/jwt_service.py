import datetime as dt
from datetime import timedelta
from typing import Optional

from jose import jwt
from loguru import logger

from src.app.domain.common.exceptions import AuthenticationError
from src.app.config.settings import settings
from src.app.domain.auth.value_objects import TokenType, TokenPair, DecodedToken
from src.app.domain.common.services.base import AbstractBaseDomainService
from src.app.domain.common.utils.common import generate_str


class DomainJWTService(AbstractBaseDomainService):
    """Domain service for JWT token operations."""

    SECRET = settings.SECRET_KEY
    ACCESS_TOKEN_EXPIRES_MINUTES = settings.ACCESS_TOKEN_EXPIRES_MINUTES
    REFRESH_TOKEN_EXPIRES_DAYS = settings.REFRESH_TOKEN_EXPIRES_DAYS
    ALGORITHM = settings.ALGORITHM

    @classmethod
    def _get_auth_exception(cls) -> AuthenticationError:
        return AuthenticationError(
            message="Token is invalid",
            details=[],
            extra={"headers": {"WWW-Authenticate": "Bearer"}},
        )

    @classmethod
    def _decode(cls, token: str) -> Optional[dict]:
        """Decode a JWT token and return the payload."""
        try:
            payload = jwt.decode(token=token, key=cls.SECRET, algorithms=[cls.ALGORITHM])
            return payload
        except Exception as e:
            logger.info(f"Token decode error: {e}")
            raise cls._get_auth_exception()

    @classmethod
    def create_access_token(cls, data: dict) -> str:
        """Create a new access token with the given data."""
        user_data = data.copy()
        expire = dt.datetime.now(dt.UTC) + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRES_MINUTES)
        payload = {"user": user_data, "type": TokenType.ACCESS.value, "exp": expire}
        encoded_jwt = jwt.encode(payload, cls.SECRET, algorithm=cls.ALGORITHM)
        return encoded_jwt

    @classmethod
    def create_refresh_token(cls, data: dict) -> str:
        """Create a new refresh token with the given data."""
        user_data = data.copy()
        expire = dt.datetime.now(dt.UTC) + timedelta(days=cls.REFRESH_TOKEN_EXPIRES_DAYS)
        payload = {"user": user_data, "type": TokenType.REFRESH.value, "exp": expire}
        encoded_jwt = jwt.encode(payload, cls.SECRET, algorithm=cls.ALGORITHM)
        return encoded_jwt

    @classmethod
    def create_token_pair(cls, uuid: str) -> TokenPair:
        """Create a pair of access and refresh tokens for the given user UUID."""
        access_sid: str = generate_str(size=6)
        refresh_sid: str = f"{generate_str(size=8)}#{access_sid}"

        access_token_payload = {
            "uuid": uuid,
            "sid": access_sid,
        }
        refresh_token_payload = {
            "uuid": uuid,
            "sid": refresh_sid,
        }

        access_token = cls.create_access_token(access_token_payload)
        refresh_token = cls.create_refresh_token(refresh_token_payload)

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    @classmethod
    def verify_access_token(cls, token: str) -> DecodedToken:
        """Verify an access token and return the decoded data."""
        payload = cls._decode(token) or {}
        token_type = payload.get("type", "") or ""

        if payload and token_type == TokenType.ACCESS.value:
            return DecodedToken.from_payload(payload, TokenType.ACCESS)

        raise cls._get_auth_exception()

    @classmethod
    def verify_refresh_token(cls, token: str) -> DecodedToken:
        """Verify a refresh token and return the decoded data."""
        payload = cls._decode(token) or {}
        token_type = payload.get("type", "") or ""

        if payload and token_type == TokenType.REFRESH.value:
            return DecodedToken.from_payload(payload, TokenType.REFRESH)

        raise cls._get_auth_exception()
