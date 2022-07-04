import asyncpg
import dataclasses

from .render import render
from .dcbuilder import DcBuilder
from .args import ValidSqlArg
from .mixins import Relation
from .where import OrderBy, Where, Limit

from typing import Optional, Type, Union, Mapping

PKeyType = tuple[Union[str, int]]


class Session:
    __object_registry__: dict[PKeyType, list[Relation]] = {}
    __sql_builder_cache__: dict[Type[Relation], DcBuilder] = {}

    def __init__(self, pool: asyncpg.Pool, debug: bool = False):
        self.pool: asyncpg.pool = pool
        self.debug = debug

    async def _execute(self, query: str, args: list[ValidSqlArg]) -> str:
        if self.debug:
            print(query, args)
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def _fetchrow(
        self,
        query: str,
        args: list[ValidSqlArg],
    ) -> Optional[asyncpg.Record]:
        if self.debug:
            print(query, args)
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def _fetch(self, query: str, args: list[ValidSqlArg]) -> list[asyncpg.Record]:
        if self.debug:
            print(query, args)
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    def sql_builder(self, cls: Type[Relation]):
        if cls not in self.__sql_builder_cache__:
            self.__sql_builder_cache__[cls] = DcBuilder(cls)

        return self.__sql_builder_cache__[cls]

    def hydrate(self, cls: Type[Relation], mapping: Mapping):
        return cls(**mapping)

    def get_pkey(self, obj: Relation):
        return (getattr(obj, pkey_attr) for pkey_attr in obj.__table_pkeys__)

    async def create(
        self, cls: Type[Relation], **kwargs: dict[str, ValidSqlArg]
    ) -> Optional[Relation]:
        template_query, template_args = self.sql_builder(cls).insert(**kwargs)
        query, query_args = render(template_query, template_args)
        row = await self._fetchrow(query, query_args)
        return None if row is None else self.hydrate(cls, row)

    async def update(
        self,
        cls: Type[Relation],
        where: Optional[Where] = None,
        **kwargs: dict[str, ValidSqlArg]
    ) -> list[Relation]:
        template_query, template_args = self.sql_builder(cls).update(where, **kwargs)
        query, query_args = render(template_query, template_args)
        attrs = self.sql_builder(cls).attrs
        return [self.hydrate(cls, row) for row in await self._fetch(query, query_args)]

    async def delete(self, cls: Type[Relation], where: Optional[Where] = None) -> str:
        template_query, template_args = self.sql_builder(cls).delete(where)
        query, query_args = render(template_query, template_args)
        return await self._execute(query, query_args)

    async def get_one(
        self,
        cls: Type[Relation],
        where: Optional[Where] = None,
        limit: Optional[int] = None,
    ) -> Optional[Relation]:

        template_query, template_args = self.sql_builder(cls).select(where, limit)
        query, query_args = render(template_query, template_args)
        row = await self._fetchrow(query, query_args)
        return None if row is None else self.hydrate(cls, row)

    async def get(
        self,
        cls: Type[Relation],
        where: Optional[Where] = None,
        order_by: Optional[OrderBy] = None,
        limit: Optional[Limit] = None,
    ) -> list[Relation]:

        template_query, template_args = self.sql_builder(cls).select(
            where, order_by, limit
        )
        query, query_args = render(template_query, template_args)
        return [self.hydrate(cls, row) for row in await self._fetch(query, query_args)]
