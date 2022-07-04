import asyncpg
import dataclasses

from .render import render
from .dcbuilder import DcBuilder
from .args import ValidSqlArg
from .relation import Relation
from .clauses import OrderBy, Where, Limit

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
        """Retrieves or instantiaties a DcBuilder instance."""
        return self.__sql_builder_cache__.get(
            cls
        ) or self.__sql_builder_cache__.setdefault(cls, DcBuilder(cls))

    def hydrate(self, cls: Type[Relation], mapping: Optional[Mapping]):
        """Instantiates a Relation instance from a mapping"""
        return None if mapping is None else cls(**mapping)

    def get_pkey(self, obj: Relation):
        return (getattr(obj, pkey_attr) for pkey_attr in obj.__table_pkeys__)

    async def create(
        self, cls: Type[Relation], **kwargs: dict[str, ValidSqlArg]
    ) -> Optional[Relation]:
        """Creates a new Relation instance based on kwargs input.

        If named argument update_on_collision is set to True,
        values will be updated on collision.
        """
        template_query, template_args = self.sql_builder(cls).insert(**kwargs)
        query, query_args = render(template_query, template_args)

        return self.hydrate(cls, await self._fetchrow(query, query_args))

    async def update(
        self,
        cls: Type[Relation],
        where: Optional[Where] = None,
        **kwargs: dict[str, ValidSqlArg]
    ) -> list[Relation]:
        """Updates a Relation instance based on kwargs input.

        Returns the updated Relation instances.
        """
        template_query, template_args = self.sql_builder(cls).update(where, **kwargs)
        query, query_args = render(template_query, template_args)

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
        """Retrieves a single Relation instance.

        Returns None if no match if found.
        """

        template_query, template_args = self.sql_builder(cls).select(where, limit)
        query, query_args = render(template_query, template_args)

        return self.hydrate(cls, await self._fetchrow(query, query_args))

    async def get(
        self,
        cls: Type[Relation],
        where: Optional[Where] = None,
        order_by: Optional[OrderBy] = None,
        limit: Optional[Limit] = None,
    ) -> list[Relation]:
        """Retrieves single Relation instances.
        """

        template_query, template_args = self.sql_builder(cls).select(
            where, order_by, limit
        )
        query, query_args = render(template_query, template_args)

        return [self.hydrate(cls, row) for row in await self._fetch(query, query_args)]
