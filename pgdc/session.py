import asyncpg
import dataclasses

from .render import render
from .builders import SqlBuilder, SqlSelect, SqlInsert, SqlUpdate, SqlDelete
from .args import ValidSqlArg
from .mixins import Relation
from .where import Where, Limit

from typing import Optional, Type, Union

PKeyType = tuple[Union[str, int]]


class Session:
    __object_registry__: dict[PKeyType, list[Relation]] = {}

    __select_sql_cache__: dict[Type[Relation], SqlBuilder] = {}
    __insert_sql_cache__: dict[Type[Relation], SqlBuilder] = {}
    __upsert_sql_cache__: dict[Type[Relation], SqlBuilder] = {}
    __delete_sql_cache__: dict[Type[Relation], SqlBuilder] = {}

    def __init__(self, pool):
        self.pool: asyncpg.pool = pool

    async def _execute(self, query: str, args: list[ValidSqlArg]) -> asyncpg.Record:
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def _fetchrow(
        self,
        query: str,
        args: list[ValidSqlArg],
    ) -> asyncpg.Record:
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def _fetch(self, query: str, args: list[ValidSqlArg]) -> list[asyncpg.Record]:
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def create(
        self, cls: Type[Relation], **kwargs: dict[str, ValidSqlArg]
    ) -> Optional[Relation]:

        if cls not in self.__insert_sql_cache__:
            attrs = list(dataclasses.fields(cls).keys())
            self.__insert_sql_cache__[cls] = SqlInsert(
                cls.__table_name__, attrs, cls.__table_pkey__
            )

        template, args = self.__insert_sql_cache__[cls].get_query(**kwargs)
        row = await self._fetchrow(render(template, args))
        if row is None:
            return None

        new_obj = cls(**dict(zip(attrs, row[0])))

        self.__object_registry__[new_obj.get_pkey()] = new_obj

        return new_obj

    async def update(
        self,
        cls: Type[Relation],
        where: Optional[Where] = None,
        **kwargs: dict[str, ValidSqlArg]
    ) -> list[Relation]:
        attrs = list(cls.__dataclass_fields__.keys())
        b = SqlUpdate(cls.__table_name__, attrs, where, **kwargs)
        rows = await cls.__db_session__.fetch(b)
        return [cls(**dict(zip(attrs, row[0]))) for row in rows]

    async def delete(cls: Type[Relation], where: Optional[Where] = None) -> str:
        self, b = SqlDelete(cls.__table_name__, where)
        result = await cls.__db_session__.execute(b)
        return result

    async def get_one(
        self,
        cls: Type[Relation],
        where: Optional[Where] = None,
        limit: Optional[int] = None,
    ) -> Optional[Relation]:

        if cls not in self.__select_sql_cache__:
            attrs = list(dataclasses.fields(cls).keys())
            self.__select_sql_cache__[cls] = SqlSelect(cls.__table_name__, attrs)

        template, args = self.__select_sql_cache__[cls].query(where, limit)
        row = await self._fetchrow(render(template, args))
        if row is None:
            return None

        selected_obj = cls(**row)
        self.__object_registry__[selected_obj.get_pkey()] = selected_obj
        return selected_obj

    async def get(
        self,
        cls: Type[Relation],
        where: Optional[Where] = None,
        limit: Optional[int] = None,
    ) -> list[Relation]:
        if cls not in self.__select_sql_cache__:
            attrs = [
                f.name for f in dataclasses.fields(cls) if not f.name.startswith("__")
            ]
            self.__select_sql_cache__[cls] = SqlSelect(cls.__table_name__, attrs)

        template_query, template_args = self.__select_sql_cache__[cls].query(
            where, limit
        )

        query, query_args = render(template_query, template_args)
        rows = await self._fetch(query, query_args)
        selected_objects = [cls(**row) for row in rows]
        for selected_obj in selected_objects:
            self.__object_registry__.setdefault(cls, {})[self.get_pkey(selected_obj)] = selected_obj

        debug(self.__object_registry__)
        return selected_objects

    def get_pkey(self, obj: Relation):
        return (getattr(obj, pkey_attr) for pkey_attr in obj.__table_pkey__)
