from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from src.app.core.models.mixins import PKMixin
from src.app.extensions.psql_ext.psql_ext import Base


class User(Base, PKMixin):
    __tablename__ = "users"  # noqa

    meta = Column(JSONB, default=dict)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=True,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    birthday = Column(
        DateTime,
        nullable=True,
        default=None,
    )
    first_name = Column(String(128))
    last_name = Column(String(128))
    email = Column(String(128))
    password_hashed = Column(String(128))
    photo = Column(Text, default=None, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    is_guest = Column(Boolean, nullable=True, default=None)
    phone = Column(String(64))
    street = Column(String(128))
    city = Column(String(64))
    state = Column(String(24))
    zip_code = Column(String(24))
    country = Column(String(64))
