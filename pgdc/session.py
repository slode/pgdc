import asyncpg
import dataclasses

from .render import render
from .builders import SqlBuilder
from .args import ValidSqlArg
from .mixins import Relation
from .where import Where, Limit

from typing import Optional, Type, Union, Mapping

PKeyType = tuple[Union[str, int]]


class Session:
    __object_registry__: dict[PKeyType, list[Relation]] = {}
    __sql_builder_cache__: dict[Type[Relation], SqlBuilder] = {}

    def __init__(self, pool: asyncpg.Pool):
        self.pool: asyncpg.pool = pool

    async def _execute(self, query: str, args: list[ValidSqlArg]) -> asyncpg.Record:
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def _fetchrow(
        self,
        query: str,
        args: list[ValidSqlArg],
    ) -> asyncpg.Record:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def _fetch(self, query: str, args: list[ValidSqlArg]) -> list[asyncpg.Record]:
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    def sql_builder(self, cls: Type[Relation]):
        if cls not in self.__sql_builder_cache__:
            attrs = tuple(
                f.name for f in dataclasses.fields(cls) if not f.name.startswith("__")
            )
            self.__sql_builder_cache__[cls] = SqlBuilder(
                cls.__table_name__, attrs, cls.__table_pkey__
            )
        return self.__sql_builder_cache__[cls]

    def hydrate(self, cls: Type[Relation], mapping: Mapping):
        return cls(**mapping)

    def get_pkey(self, obj: Relation):
        return (getattr(obj, pkey_attr) for pkey_attr in obj.__table_pkey__)

    async def create(
        self, cls: Type[Relation], **kwargs: dict[str, ValidSqlArg]
    ) -> Optional[Relation]:
        template_query, template_args = self.sql_builder(cls).insert(**kwargs)
        query, query_args = render(template_query, template_args)
        row = await self._fetchrow(query, query_args)
        attrs = self.sql_builder(cls).attrs
        return None if row is None else self.hydrate(cls, dict(zip(attrs, row[0])))

    async def update(
        self,
        cls: Type[Relation],
        where: Optional[Where] = None,
        **kwargs: dict[str, ValidSqlArg]
    ) -> list[Relation]:
        template_query, template_args = self.sql_builder(cls).update(where, **kwargs)
        query, query_args = render(template_query, template_args)
        attrs = self.sql_builder(cls).attrs
        return [
            self.hydrate(cls, dict(zip(attrs, row[0])))
            for row in await self._fetch(query, query_args)
        ]

    async def delete(self, cls: Type[Relation], where: Optional[Where] = None) -> str:
        template_query, template_args = self.sql_builder(cls).delete(where)
        query, query_args = render(template_query, template_args)
        return await self._execute(query, query_args)

    async def get_one(
        self,
        cls: Type[Relation],
        where: Optional[Where] = None,
        limit: Optional[int] = 1,
    ) -> Optional[Relation]:

        template_query, template_args = self.sql_builder(cls).select(where, limit)
        query, query_args = render(template_query, template_args)
        row = await self._fetchrow(query, query_args)
        return None if row is None else self.hydrate(cls, row)

    async def get(
        self,
        cls: Type[Relation],
        where: Optional[Where] = None,
        limit: Optional[int] = None,
    ) -> list[Relation]:

        template_query, template_args = self.sql_builder(cls).select(where, limit)
        query, query_args = render(template_query, template_args)
        return [self.hydrate(cls, row) for row in await self._fetch(query, query_args)]
