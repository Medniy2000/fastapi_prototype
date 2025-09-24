from sqlalchemy import text

from src.app.infrastructure.extensions.psql_ext.psql_ext import get_session
from src.app.infrastructure.repositories.base.abstract import AbstractRepository


class CommonPSQLRepository(AbstractRepository):

    @classmethod
    async def is_healthy(cls) -> bool:
        stmt = """SELECT 1;"""

        async with get_session() as session:
            result = await session.execute(statement=text(stmt), params={})
            result = result.scalars().first()
            return result == 1
