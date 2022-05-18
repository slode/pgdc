import asyncpg

from .render import render
from .builders import SqlBuilder
from .mixins import Relation

from typing import Optional, TypeVar

T = TypeVar("T")


class AsyncpgSession:
    def __init__(self, conn_string: str = "postgresql://user:example@localhost/user"):
        self.conn_string = conn_string
        self.pool: Optional[asyncpg.pool] = None

    async def connect(self):
        assert self.pool is None
        self.pool = await asyncpg.create_pool(self.conn_string)
        Relation.__db_session__ = self

    async def execute(self, sql: SqlBuilder) -> asyncpg.Record:
        query = render(sql)
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            return await conn.execute(query.sql, *query.arguments)

    async def fetchrow(self, sql: SqlBuilder) -> asyncpg.Record:
        query = render(sql)
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query.sql, *query.arguments)

    async def fetch(self, sql: SqlBuilder) -> list[asyncpg.Record]:
        query = render(sql)
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            return await conn.fetch(query.sql, *query.arguments)

    async def close(self):
        Relation.__db_session__ = None
        assert self.pool is not None
        await self.pool.close()
