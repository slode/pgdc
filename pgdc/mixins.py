from typing import Any, Optional, Union, Iterable, Protocol, TypeVar, Type
from dataclasses import dataclass, astuple, asdict

from .builders import SqlSelect, SqlInsert, SqlUpdate, SqlDelete
from .where import Where, Limit
from .args import ValidSqlArg


class Relatable(Protocol):
    __table_name__: str
    __table_pkey__: list[str]
    __db_session__: Any

    # From dataclasses.dataclass
    __dataclass_fields__: dict


class Relation:
    @classmethod
    async def create(cls: Type[Relatable], **kwargs: dict[str, ValidSqlArg]) -> Optional[Relatable]:
        attrs = list(cls.__dataclass_fields__.keys())
        b = SqlInsert(cls.__table_name__, attrs, **kwargs)
        row = await cls.__db_session__.fetchrow(b)
        return None if row is None else cls(**dict(zip(attrs, row[0])))

    @classmethod
    async def update(
        cls: Type[Relatable], where: Optional[Where] = None, **kwargs: dict[str, ValidSqlArg]
    ) -> list[Relatable]:
        attrs = list(cls.__dataclass_fields__.keys())
        b = SqlUpdate(cls.__table_name__, attrs, where, **kwargs)
        rows = await cls.__db_session__.fetch(b)
        return [cls(**dict(zip(attrs, row[0]))) for row in rows]

    @classmethod
    async def delete(cls: Type[Relatable], where: Optional[Where] = None) -> str:
        b = SqlDelete(cls.__table_name__, where)
        result = await cls.__db_session__.execute(b)
        return result

    @classmethod
    async def get_one(
        cls: Type[Relatable], where: Optional[Where] = None, limit: Optional[int] = None
    ) -> Optional[Relatable]:
        b = SqlSelect(
            cls.__table_name__, cls.__dataclass_fields__.keys(), where, Limit(limit)
        )
        row = await cls.__db_session__.fetchrow(b)
        return None if row is None else cls(**row)

    @classmethod
    async def get(
        cls: Type[Relatable], where: Optional[Where] = None, limit: Optional[int] = None
        ) -> list[Relatable]:
        b = SqlSelect(
            cls.__table_name__, cls.__dataclass_fields__.keys(), where, Limit(limit)
        )
        rows = await cls.__db_session__.fetch(b)
        return [cls(**row) for row in rows]
