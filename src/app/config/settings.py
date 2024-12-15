import os
import pathlib
import secrets
from enum import Enum
from typing import List, Union

from environs import Env
from pydantic.v1 import BaseSettings as PydanticSettings
from slugify import slugify

env = Env()


class SettingsBase(PydanticSettings):
    LAUNCH_MODE = env.str("LAUNCH_MODE", "PROD")

    ROOT_DIR = os.path.abspath(os.path.dirname("src"))
    STATIC_DIR = f"{pathlib.Path().resolve().parent.parent}/static"

    if env.bool("READ_ENV", default=True):
        env.read_env(f"{ROOT_DIR}/.env")

    # Base Settings
    # --------------------------------------------------------------------------
    PROJECT_NAME: str = env.str("PROJECT_NAME", "Project")
    PROJECT_NAME_SLUG: str = slugify(PROJECT_NAME)
    TEAM_CONTACT_EMAIL: str = env.str("TEAM_CONTACT_EMAIL", "yourteam@example.com")
    SECRET_KEY: str = env.str("SECRET_KEY", secrets.token_urlsafe(32))

    # General Settings
    # --------------------------------------------------------------------------
    DEFAULT_BATCH_SIZE: int = env.int("DEFAULT_BATCH_SIZE", 500)
    DEBUG: bool = env.bool("DEBUG", False)

    # API Settings
    # --------------------------------------------------------------------------
    API: str = "/api"
    CORS_ORIGIN_WHITELIST: List[str] = env.list("CORS_ORIGIN_WHITELIST", ["*"])
    API_DEFAULT_LIMIT: int = env.int("API_DEFAULT_LIMIT", 25)
    API_LIMIT_ALLOWED_VALUES_LIST: List[int] = env.list("API_LIMIT_ALLOWED_VALUES_LIST", [1, 5, 10, 15, 25])
    SHOW_API_DOCS: bool = env.bool("SHOW_API_DOCS", False)

    # Auth settings
    # --------------------------------------------------------------------------
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRES_MINUTES = env.int("ACCESS_TOKEN_EXPIRES_MINUTES", 30)
    REFRESH_TOKEN_EXPIRES_DAYS = env.int("REFRESH_TOKEN_EXPIRES_DAYS", 7)

    # Database Settings
    # --------------------------------------------------------------------------
    SHOW_SQL: bool = env.bool("SHOW_SQL", False)
    DB_HOST: str = env.str("DB_HOST")
    DB_PORT: int = env.int("DB_PORT")
    DB_NAME: str = env.str("DB_NAME")
    DB_USER: str = env.str("DB_USER")
    DB_PASSWORD: str = env.str("DB_PASSWORD")
    DB_DRIVER: str = env.str("DB_DRIVER", "postgresql+asyncpg")
    DB_URL: str = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    DB_URL_SYNC: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    CONNECTIONS_POOL_MIN_SIZE: int = env.int("CONNECTIONS_POOL_MIN_SIZE", 5)
    CONNECTIONS_POOL_MAX_OVERFLOW: int = env.int("CONNECTIONS_POOL_MAX_OVERFLOW", 25)

    # Redis Settings
    # --------------------------------------------------------------------------
    REDIS_URL = env.str("REDIS_URL", "")

    # Message Broker settings
    # --------------------------------------------------------------------------
    MESSAGE_BROKER_URL: str = env.str("MESSAGE_BROKER_URL")
    EXCHANGER: str = env.str("EXCHANGER", "DEFAULT_EXCHANGER")
    QUEUE: str = env.str("QUEUE", "DEFAULT_QUEUE")


class SettingsLocal(SettingsBase):
    pass


class SettingsTest(SettingsBase):
    pass


class SettingsProd(SettingsBase):
    DEBUG: bool = False


class LaunchMode(str, Enum):
    LOCAL = "LOCAL"
    PRODUCTION = "PROD"
    TEST = "TEST"


LAUNCH_MODE = os.environ.get("LAUNCH_MODE")

SettingsType = Union[SettingsLocal, SettingsTest, SettingsProd]


def _get_settings() -> SettingsType:
    if LAUNCH_MODE == LaunchMode.LOCAL.value:
        settings_class = SettingsLocal  # type: ignore
    elif LAUNCH_MODE == LaunchMode.TEST.value:
        settings_class = SettingsTest  # type: ignore
    else:
        settings_class = SettingsProd  # type: ignore
    return settings_class()


settings = _get_settings()
