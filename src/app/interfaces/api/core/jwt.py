import datetime as dt
from datetime import timedelta
from typing import Optional, Dict

from fastapi import HTTPException, status
from jose import jwt
from loguru import logger

from src.app.config.settings import settings

from src.app.infrastructure.utils.common import generate_str


class JWTHelper:
    SECRET = settings.SECRET_KEY
    ACCESS_TOKEN_EXPIRES_MINUTES = settings.ACCESS_TOKEN_EXPIRES_MINUTES
    REFRESH_TOKEN_EXPIRES_DAYS = settings.REFRESH_TOKEN_EXPIRES_DAYS
    ALGORITHM = settings.ALGORITHM
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    @classmethod
    def _decode(cls, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token=token, key=cls.SECRET, algorithms=[settings.ALGORITHM])
            return payload
        except Exception as e:  # noqa
            logger.info(e)
            return None

    @classmethod
    async def create_access_token(cls, data: dict) -> str:
        user_data = data.copy()
        expire = dt.datetime.now(dt.UTC) + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRES_MINUTES)
        payload = {"user": user_data, "type": "access", "exp": expire}
        encoded_jwt = jwt.encode(payload, cls.SECRET, algorithm=cls.ALGORITHM)
        return encoded_jwt

    @classmethod
    async def create_refresh_token(cls, data: dict) -> str:
        user_data = data.copy()
        expire = dt.datetime.now(dt.UTC) + timedelta(days=cls.REFRESH_TOKEN_EXPIRES_DAYS)
        payload = {"user": user_data, "type": "refresh", "exp": expire}
        encoded_jwt = jwt.encode(payload, cls.SECRET, algorithm=cls.ALGORITHM)
        return encoded_jwt

    @classmethod
    async def create_tokens_pair(cls, uuid: str) -> Dict[str, str]:
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
        access_token = await cls.create_access_token(access_token_payload)
        refresh_token = await cls.create_refresh_token(refresh_token_payload)

        return {
            "access": access_token,
            "refresh": refresh_token,
        }

    @classmethod
    async def verify_access_token(cls, token: str) -> dict:
        payload = cls._decode(token) or {}
        token_type = payload.get("type", "") or ""
        if payload and token_type == "access":
            user_data = payload.get("user", {})
            return user_data
        raise cls.exception

    @classmethod
    async def verify_refresh_token(cls, token: str) -> dict:
        payload = cls._decode(token) or {}
        token_type = payload.get("type", "") or ""
        if payload and token_type == "refresh":
            user_data = payload.get("user", {})
            return user_data

        raise cls.exception

    @classmethod
    async def access_auth_data(cls, api_key: str) -> dict:
        return await cls.verify_access_token(api_key)  # type: ignore

    @classmethod
    async def refresh_auth_data(cls, api_key: str) -> dict:
        return await cls.verify_refresh_token(api_key)  # type: ignore
