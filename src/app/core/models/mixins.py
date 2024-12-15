import datetime as dt
import uuid as uuid

from sqlalchemy import Column, Integer, DateTime, String


class PKMixin(object):
    """
    A mixin that adds a surrogate pk(s) fields
    """

    __table_args__ = {"extend_existing": True}

    id = Column(Integer, index=True, primary_key=True, unique=True, autoincrement=True)
    uuid = Column(String(length=36), primary_key=True, unique=True, default=lambda: uuid.uuid4().__str__())


class DTMixin(object):
    """
    A mixin that adds a created_at, updated_at fields
    """

    __table_args__ = {"extend_existing": True}

    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=dt.datetime.utcnow,
        onupdate=dt.datetime.utcnow,
    )
